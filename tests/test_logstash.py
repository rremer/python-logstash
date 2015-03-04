import logging
import sys
import unittest
from multiprocessing import Process, Queue

import json
import logstash
from kombu import Connection as KombuConn

# work around renamed python3 socketserver module
if sys.version_info[0] > 2:
    import socketserver
    SocketServer = socketserver
else:
    import SocketServer

# Add python3 assertion apis to python 2.6 env
if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    def assertIsInstance(self, obj, cls, msg=None):
        """Same as self.assertTrue(isinstance(obj, cls)), with a nicer
        default message."""
        if not isinstance(obj, cls):
            standardMsg = '%s is not an instance of %r' % (safe_repr(obj), cls)
            self.fail(self._formatMessage(msg, standardMsg))
    unittest.TestCase.assertIsInstance = assertIsInstance


class FormatterTestCase(unittest.TestCase):

    def setUp(self):
        self.current_version = logstash.__version__

        # for top-level dict 'version', invoke base args available
        self.version_args = {'0.4.3':{'required':{},
                                       'optional':{'message_type':'Logstash',
                                                   'tags':None,
                                                   'fqdn':False}}}

    def test_formatter_base_version_req_compatibility(self):
        """Fail if broken backwards-compatibility/required args."""
        for version in self.version_args.keys():
            required_args = self.version_args[version]['required']
            test_formatter = None
            try:
                error_msg = None
                test_formatter = (logstash.formatter.
                                  LogstashFormatterBase(**required_args))
            except TypeError as error:
                error_msg = error.message
            self.assertIsInstance(test_formatter,
                                  logstash.formatter.LogstashFormatterBase,
                                  msg=("Version %s invocation is not compatible"
                " with current version %s using args: %s:\n\n%s"
                % (version, self.current_version,
                   repr(required_args), error_msg)))

    def test_formatter_base_version_opt_compatibility(self):
        """Fail if broken backwards-compatibility/optional args."""
        for version in self.version_args.keys():
            required_args = list(self.version_args[version]['required'].items())
            optional_args = list(self.version_args[version]['optional'].items())
            invoc_args = dict(required_args + optional_args)
            test_formatter = None
            try:
                error_msg = None
                test_formatter = (logstash.formatter.
                                  LogstashFormatterBase(**invoc_args))
            except TypeError as error:
                error_msg = error.message
            self.assertIsInstance(test_formatter,
                                  logstash.formatter.LogstashFormatterBase,
                                  msg=("Version %s invocation is not compatible"
                " with current version %s using args: %s\n\n%s"
                % (version, self.current_version,
                   repr(invoc_args), error_msg)))

    def test_formatter_sanitization(self):
        """Assert proper sanitization of characters in json namespace."""
        pass


class HandlerAmqpTestCase(unittest.TestCase):

    def setUp(self):
        # get a free socket
        free_sock = socket()
        free_sock.bind(('localhost',0))
        free_sock = free_sock.getsockname()[1]


class HandlerTcpTestCase(unittest.TestCase):

    def setUp(self):
        # logstash event schema versions
        self.logstash_versions = RequestHandlerToQueue.version_dict

        # setup the logstash-consuming server
        self.server = SocketServer.TCPServer(('localhost', 0), RequestHandlerToQueue)
        hostport_tuple = self.server.socket.getsockname()
        self.host = hostport_tuple[0]
        self.port = hostport_tuple[1]

        # thread the server non-blocking
        self.server_thread = Process(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def tearDown(self):
        self.server_thread.terminate()

    def test_base_tcp_decoding(self):
        """Assert json decoding of TCP message."""

        test_str = u'test-runner: simple message'
        for version in list(self.logstash_versions.keys()):
           test_logger = logging.getLogger('python-logstash-logger')
           test_logger.setLevel(logging.INFO)
           for handler in test_logger.handlers:
               test_logger.removeHandler(handler)
           test_logger.addHandler(logstash.TCPLogstashHandler(self.host,
                                                              self.port,
                                                              version=version))
           test_logger.error(test_str)
           recv_str = self.server.RequestHandlerClass.recv_queue.get()
           try:
               recv_dict = json.loads(recv_str)
           except ValueError as e:
               self.fail("String '%s' could not be parsed as json." %recv_str)
           err_msg=("Parsed json: '%s' did not have matching message '%s'."
                    % (recv_str, test_str))
           version_keys = self.logstash_versions[version]
           try:
               recv_dict[version_keys['msg_str']]
           except KeyError:
               self.fail("Could not find '%s' in '%s'."
                         % (version_keys['msg_str'], recv_str))
           self.assertEqual(recv_dict[version_keys['msg_str']],
                            test_str, msg=err_msg)


class HandlerUdpTestCase(unittest.TestCase):

    def setUp(self):
        # logstash event schema versions
        self.logstash_versions = RequestHandlerToQueue.version_dict

        # setup the logstash-consuming server
        self.server = SocketServer.UDPServer(('localhost', 0), RequestHandlerToQueue)
        hostport_tuple = self.server.socket.getsockname()
        self.host = hostport_tuple[0]
        self.port = hostport_tuple[1]

        # thread the server non-blocking
        self.server_thread = Process(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def tearDown(self):
        self.server_thread.terminate()

    def test_base_udp_decoding(self):
        """Assert json decoding of UDP message."""

        test_str = u'test-runner: simple message'
        for version in list(self.logstash_versions.keys()):
           test_logger = logging.getLogger('python-logstash-logger')
           test_logger.setLevel(logging.INFO)
           for handler in test_logger.handlers:
               test_logger.removeHandler(handler)
           test_logger.addHandler(logstash.UDPLogstashHandler(self.host,
                                                              self.port,
                                                              version=version))
           test_logger.error(test_str)
           recv_str = self.server.RequestHandlerClass.recv_queue.get()
           try:
               recv_dict = json.loads(recv_str)
           except ValueError as e:
               self.fail("String '%s' could not be parsed as json." %recv_str)
           err_msg=("Parsed json: '%s' did not have matching message '%s'."
                    % (recv_str, test_str))
           version_keys = self.logstash_versions[version]
           try:
               print(list(recv_dict.keys()))
               recv_dict[version_keys['msg_str']]
           except KeyError:
               self.fail("Could not find '%s' in '%s'."
                         % (version_keys['msg_str'], recv_str))
           #TODO: determine if UDP just never calls the other version of LogstashFormatterVersion!
           self.assertEqual(recv_dict[version_keys['msg_str']],
                            test_str, msg=err_msg)


class RequestHandlerToQueue(SocketServer.BaseRequestHandler):
    """Store requests from any protocol server."""

    recv_queue = Queue()

    # this data should be inherited from LogstashFormatterVersion{0,1}
    # but until then, and since this class is used by all test cases...
    version_dict = {0:{'msg_str':'@message', 'time_str':'@timestamp'},
                    1:{'msg_str':'message', 'time_str':'@timestamp'}}

    def handle(self):
        request = self.request
        if isinstance(request, tuple):
            raw_str = self.request[0]
        else:
            raw_str = self.request.recv(1024)
        #except AttributeError as e:
        #    print(type(self.request))
        #    print(repr(self.request))
        #    print(e.message)
        coerced_str = raw_str.strip().decode('utf-8', 'ignore')
        self.recv_queue.put(coerced_str)

import sys
import unittest
import logstash


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


class HandlerAmqpTestCase(unittest.TestCase):
    pass


class HandlerTcpTestCase(unittest.TestCase):
    pass


class HandlerUdpTestCase(unittest.TestCase):
    pass


if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    def assertIsInstance(self, obj, cls, msg=None):
        """Same as self.assertTrue(isinstance(obj, cls)), with a nicer
        default message."""
        if not isinstance(obj, cls):
            standardMsg = '%s is not an instance of %r' % (safe_repr(obj), cls)
            self.fail(self._formatMessage(msg, standardMsg))
    unittest.TestCase.assertIsInstance = assertIsInstance

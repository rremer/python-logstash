import unittest
import logstash

class formatterTestCase(unittest.TestCase):
    def setUp(self):
        self.current_version = logstash.__version__

        # for top-level dict 'version', invoke base args available
        self.version_args = {'0.4.3':{'required':{},
                                       'optional':{'message_type':'Logstash',
                                                   'tags':None,
                                                   'fqdn':False}}}

    def test_formatter_base_version_req_compatibility(self):
        """Fail if broken backwards-compatibility/required args."""
        for version in self.version_args.iterkeys():
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
        for version in self.version_args.iterkeys():
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


class handlerAmqpTestCase(unittest.TestCase):
    pass

class handlerTcpTestCase(unittest.TestCase):
    pass

class handlerUdpTestCase(unittest.TestCase):
    pass

if __name__ == '__main__':
    logstashTestSuite = (unittest.TestLoader().
                         loadTestsfromTestCase(formatterTestCase()),
                         unittest.TestLoader().
                         loadTestsfromTestCase(handlerAmqpTestCase()),
                         unittest.TestLoader().
                         loadTestsfromTestCase(handlerTcpTestCase()),
                         unittest.TestLoader().
                         loadTestsfromTestCase(handlerUdpTestCase()))

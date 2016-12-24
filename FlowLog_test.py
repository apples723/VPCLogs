from datetime import datetime
import unittest
import boto3

import VPCLogParse 

RECORD_TESTS = [ 
    (
        '2 123456789010 eni-215653ab 10.215.1.5 10.5.6.7 '
        '443 12 6 01 123 1234567890 1234567890 ACCEPT OK'
    ),
    (
        '2 123456789010 eni-215653ab 10.215.1.5 10.5.3.7 '
        '443 12 6 01 123 1234567890 1234567890 ACCEPT OK'
    ),
    (
        '2 123456789010 eni-215653ae 10.215.1.5 10.5.6.7 '
        '443 12 6 01 123 1234567890 1234567890 REJECT OK'
    ),
]


class LogRecordTest(unittest.TestCase):
    def testLogRecord(self):
        test_record = VPCLogParse.LogRecord({'record': RECORD_TESTS[0]})
        actual = {x: getattr(test_record, x) for x in VPCLogParse.LogRecord.__slots__}
        expected = {
            'account_id': '123456789010',
            'action': 'ACCEPT',
            'bytes': 123,
            'dstaddr': '10.5.6.7',
            'dstport': 12,
            'end': datetime(2009, 2, 13, 23, 31, 30),
            'interface_id': 'eni-215653ab',
            'log_status': 'OK',
            'packets': 01,
            'protocol': 6,
            'srcaddr': '10.215.1.5',
            'srcport': 443,
            'start': datetime(2009, 2, 13, 23, 31, 30),
            'version': 2,
        }
        self.assertEqual(actual, expected)
    def testChekcLog(self):
        TestFile = "SampleData.txt"
        test_check = VPCLogParse.CheckLog(TestFile)
        actual = len(test_check)
        expected = 3
        self.assertEqual(actual, expected)
    def testOutput(self):
        TestFile = "SampleData.txt"
        test_output = VPCLogParse.CheckLog(TestFile)
        VPCLogParse.OutputJson(test_output, 'TestOutput.json')
        TestOutputFileData = open('TestOutput.json').read()
        actual = TestOutputFileData
        expected = "{\"RejectedIPCount\": 3}\n"
        self.assertEqual(actual, expected)
    def testS3Upload(self):
        TestFile = "TestOutput.json"
        TestBucket = "randomsterbucket/testoutput"
        actual = VPCLogParse.S3Upload(TestFile, TestBucket)
        expected = True
        self.assertEqual(actual, expected)
    
        
        
if __name__ == '__main__':
    unittest.main()

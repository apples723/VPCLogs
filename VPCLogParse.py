"""Script assumes you have the AWS SDK installed (Boto3) and you have configured
your credentials for access to AWS, and are using python 2.7 (wrote and tested on a mac) 

Usage:
    
    VPCLogParse.py -i <logfile> -o <output json file> -u <S3 Url>
     -i (required) VPC Log File
     -o (option) Output log file name - for saving to your machine
     -u (required) S3 Url - must be in following format "VPCLogsS3Bucket\RejectedCounts"
         where bucket name is "VPCLogsS3Bucket" and Key is "RejectCounts"

"""

import json
from calendar import timegm
from datetime import datetime, timedelta
import sys
import getopt
import boto3
import os
ACCEPT = 'ACCEPT'
REJECT = 'REJECT'
SKIPDATA = 'SKIPDATA'
NODATA = 'NODATA'

class LogRecord(object):
    """returns an objets of VPC log"""
   
    __slots__ = [
        'version',
        'account_id',
        'interface_id',
        'srcaddr',
        'dstaddr',
        'srcport',
        'dstport',
        'protocol',
        'packets',
        'bytes',
        'start',
        'end',
        'action',
        'log_status',
    ]

    def __init__(self, event):
        fields = event['record'].split()
        self.version = int(fields[0])
        self.account_id = fields[1]
        self.interface_id = fields[2]
        self.start = datetime.utcfromtimestamp(int(fields[10]))
        self.end = datetime.utcfromtimestamp(int(fields[11]))

        self.log_status = fields[13]
        if self.log_status in (NODATA, SKIPDATA):
            self.srcaddr = None
            self.dstaddr = None
            self.srcport = None
            self.dstport = None
            self.protocol = None
            self.packets = None
            self.bytes = None
            self.action = None
        else:
            self.srcaddr = fields[3]
            self.dstaddr = fields[4]
            self.srcport = int(fields[5])
            self.dstport = int(fields[6])
            self.protocol = int(fields[7])
            self.packets = int(fields[8])
            self.bytes = int(fields[9])
            self.action = fields[12]

def CheckLog(file):
    """reads through file to find rejected IP's""" 
    lines_list = open(file).read().splitlines()
    rejects = []

    for l in lines_list:
         record = LogRecord({ 'record' : l})
         if record.action == "REJECT":
             rejects.append(l)
    return rejects

def OutputJson(output, outputFile):
    """Outputs data parsed to json file""" 
    RejectsCount = len(output)
    JsonOutput = { "RejectedIPCount" : RejectsCount }
    JsonDump = json.dumps(JsonOutput)
    OutputFile = open(outputFile, 'w')
    print >> OutputFile, JsonDump
    OutputFile.close()
def S3Upload(uploadFile, uploadUrl):
    """Uploads file that was parsed to S3 bucket specified"""
    S3 = boto3.client('s3')
    #Split url into bucket name and key
    ToSplit = uploadUrl
    S3Bucket = ToSplit.split('/')[0]
    S3Key = ToSplit.split('/')[1]  
    try:
        S3.upload_file(uploadFile, S3Bucket, S3Key)
        return True 
    except:
        print("Upload Failed! : Verify Bucket Name and that you have set up credentials")
        sys.exit()
def main(argv):
    """Main functions of program, runs majority of code, gets arguments from command line"""
    inputFile = ''
    outputFile = 'VPCParse.json'
    s3url = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:u:",["ifile=","outputFile=","s3url="])
    except getopt.GetoptError:
        print ' 1 parse.py -i <inputfile> -o <Output File Name> -u <S3 Bucket Url>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'parse.py -i <Output File Name> -o <Output File Name> -u <S3 Bucket Url>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputFile = arg
        elif opt in ("-o", "--ofile"):
            outputFile = arg
        elif opt in ("-u", "--surl"):
            s3url = arg
            
    AllRejects = CheckLog(inputFile)
    OutputJson(AllRejects, outputFile)
    S3Upload(outputFile, s3url)

if __name__ == "__main__":
    main(sys.argv[1:])

# VPCLogs
Parse VPC Logs, find rejected entries and upload to an S3 Bucket.

Script assumes you have the AWS SDK installed (Boto3) and you have configured
your credentials for access to AWS, and are using python 2.7 (wrote and tested on a mac) 

Usage:
    
    VPCLogParse.py -i <logfile> -o <output json file> -u <S3 Url>
     -i (required) VPC Log File
     -o (option) Output log file name - for saving to your machine
     -u (required) S3 Url - must be in following format "VPCLogsS3Bucket\RejectedCounts"
         where bucket name is "VPCLogsS3Bucket" and Key is "RejectCounts"


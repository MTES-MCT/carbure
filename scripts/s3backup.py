import sys
import boto3
import datetime

def upload_db_dump(filename):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('carbure.database')
    today = datetime.date.today().strftime('%Y/%m/%d')
    object = s3.Object(bucket.name, today)
    with open(filename, 'rb') as data:
        object.upload_fileobj(data)

def main():
    filename = sys.argv[1]
    upload_db_dump(filename)
    
if __name__ == '__main__':
    main()


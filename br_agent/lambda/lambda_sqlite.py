import json
import boto3
import sqlite3

def lambda_handler(event, context):
    
    ## 1. load SQL Lite database from Amazon S3
    s3 = boto3.client('s3')
    ssm = boto3.client('ssm')
    
    # get info from parameter store
    bucket = ''
    db_name = ''
    local_db = '/tmp/' + db_name
    
    # create the db
    s3.download_file(bucket, db_name, local_db)
    conn = sqlite3.connect(local_db)    
    
    # 2. Query the database for information
    
    #read the event and format the query
    query = ''
    
    #query the db
    cursor = conn.cursor()
    cursor.execute(query)
    
    #3. format the return json
    
    
    
    #4. return
import json
import boto3
import sqlite3
import urllib

def setup_dynamodb(pets):
    
    dynamodb = boto3.client('dynamodb')
    ssm = boto3.client('ssm')
    
    dynamo_table = ssm.get_parameter(Name='/br_agent/dynamo_table')
    table = dynamodb.Table(dynamo_table)

    with table.batch_writer() as batch:
        for pet in pets:
            batch.put_item(Item=pet)
    return

def lambda_handler(event, context):
    
    s3 = boto3.client('s3')
    ssm = boto3.client('ssm')
    
    bucket_param = ssm.get_parameter(Name='/br_agent/bucket_name')
    bucket_name = bucket_param['Parameter']['Value']
    
    database_param = ssm.get_parameter(Name='/br_agent/sqlite_db_name')
    database_name = database_param['Parameter']['Value']

    db_file_path = "/tmp/pets.db"
    
    conn = sqlite3.connect(db_file_path)
    c = conn.cursor()
    
    c.execute("""CREATE TABLE IF NOT EXISTS pets (
               id INTEGER PRIMARY KEY, 
               name TEXT,
               status TEXT,
               category TEXT
               )""")

    url = 'https://petstore.swagger.io/v2/pet/findByStatus?status=available,sold,pending'
    response = urllib.request.urlopen(url)
    # Read response data as JSON
    pets = json.loads(response.read())

    for pet in pets:
        category_name = ""
        if "category" in pet:
            category_name = pet['category']['name']
        c.execute("INSERT INTO pets VALUES (?, ?, ?, ?)", 
                 (pet['id'], pet['name'], pet['status'], category_name))

    conn.commit()
    conn.close()

    s3.upload_file(db_file_path, bucket_name, database_name)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Created the data required'
    }
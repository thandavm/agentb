import json
import boto3
import sqlite3

def load_data():
    ## 1. load SQL Lite database from Amazon S3
    s3 = boto3.client('s3')
    ssm = boto3.client('ssm')
    
    # get info from parameter store
    bucket_param = ssm.get_parameter(Name='/br_agent/bucket_name')
    bucket = bucket_param['Parameter']['Value']
    
    database_param = ssm.get_parameter(Name='/br_agent/sqlite_db_name')
    db_name = database_param['Parameter']['Value']
    
    local_db = '/tmp/pets.db'
    
    # create the db
    s3.download_file(bucket, db_name, local_db)
    conn = sqlite3.connect(local_db)

    cursor = conn.cursor()
    return cursor

def list_pets(cursor):
    query = 'SELECT id, name, category, status FROM pets LIMIT 10'
    cursor.execute(query)
    return cursor.fetchall()
    
def total_pets(cursor):
    query = 'SELECT count(*) from pets'
    cursor.execute(query)
    for row in cursor.fetchall():
        count1 = row[0]
    print("in total_pets")
    print(count1)
    return count1    
    
    
def get_pet_name(cursor, id):
    print("in get_pet_name")
    print(id)
    query = 'SELECT name from pets where id = ' + str(id)
    cursor.execute(query)
    for row in cursor.fetchall():
        name = row[0]
    print("pet name found")
    print(name)
    return name   

def lambda_handler(event, context):
    responses = []
 
    cursor = load_data()
 
    for prediction in event['actionGroups']:
        action = prediction['actionGroup']
        api_path = prediction['apiPath']
        
        if api_path == '/total_pets':
            body = total_pets(cursor) 
            print("in prediction total_pets")
            print(body)
        elif api_path == '/pets/{petid}':
            parameters = prediction['parameters']
            id = 10
            for parameter in parameters:
                if parameter["name"] == "id":
                    id = parameter["value"]
            body = get_pet_name(cursor, id)
            print(body)
        elif api_path == '/pets':
            body = list_pets(cursor)
            print(body)
        else:
            body = {"{} is not a valid api, try another one.".format(api_path)}
 
        response_body = {
            'application/json': {
                'body': json.dumps(body)
            }
        }
        
        action_response = {
            'actionGroup': prediction['actionGroup'],
            'apiPath': prediction['apiPath'],
            'httpMethod': prediction['httpMethod'],
            'httpStatusCode': 200,
            'responseBody': response_body}

        responses.append(action_response)
 
    api_response = {'response': responses}
    print(api_response)
    return api_response
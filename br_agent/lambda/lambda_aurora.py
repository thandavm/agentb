import json
import boto3
import mysql.connector

def handler(event, context):
    print('request: {}'.format(json.dumps(event)))
    
    aurora_client = boto3.client('rds')
    response = aurora_client.describe_db_instances(DBInstanceIdentifier='my-aurora-instance')
    endpoint = response['DBInstances'][0]['Endpoint']['Address']
    
    # Connect to the database using the endpoint address, username, and password
    cnx = mysql.connector.connect(host=endpoint, user='myuser', password='mypassword', database='mydatabase')    

    # Execute an SQL query
    cursor = cnx.cursor()
    query = "SELECT * FROM mytable"
    cursor.execute(query)

    # Fetch the results of the query
    for row in cursor:
        print(row)

    #format the output
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Hello'
    }
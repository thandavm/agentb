import json
import boto3
import urllib
from boto3.dynamodb.conditions import Key
from datetime import datetime
    
def get_pets_online():
    
    ssm = boto3.client('ssm')
    petstore_online_url = ssm.get_parameter(Name='/br_agent/petstore_online_url') 
    petstore_url = petstore_online_url['Parameter']['Value']
    
    #petstore_url = 'https://petstore.swagger.io/v2/pet/findByStatus?status=available'
    response = urllib.request.urlopen(petstore_url)
    
    # Read response data as JSON
    pets = json.loads(response.read())
    pet_responses = []
    for pet in pets[:10]:
        id = ""
        name = ""
        category_name = ""
        status = ""
        if "id" in pet:
            id = pet['id']
        if "name" in pet:
            name = pet['name']
        if "category" in pet:
            if "name" in pet['category']:
                category_name = pet['category']['name']
        if "status" in pet:
            status = pet['status']

        available_pets = {
            'id': id,
            'name': name,
            'category': category_name,
            'status': status
            }

        pet_responses.append(available_pets)

    return pet_responses

def get_breed_info(breedname):
    
    ddb = boto3.resource('dynamodb')
    ssm = boto3.client('ssm')
    
    dynamo_param = ssm.get_parameter(Name='/br_agent/dynamo_table')
    dynamo_db_name = dynamo_param['Parameter']['Value']
    
    ddbTable = ddb.Table(dynamo_db_name)
    #ddbTable = ddb.Table('BreedInfoForPetStore') 
    responseDDBget = ddbTable.query(KeyConditionExpression=Key('breed').eq(breedname), ProjectionExpression = "demeanor_category, energy_level_category, temperament")
    
    return json.dumps(responseDDBget['Items'])

def lambda_handler(event, context):
    responses = []

    for prediction in event['actionGroups']:
        api_path = prediction['apiPath']

        if api_path == '/breed_info/{breedname}':
            parameters = prediction['parameters']
            bn = ''
            for parameter in parameters:
                if parameter["name"] == "breedname":
                    bn = parameter["value"]
            body = get_breed_info(bn)
        elif api_path == '/online_pet_store':
            body = list(get_pets_online())
        else:
            body = {"{} is not a valid api, try another one.".format(api_path)}
 
        response_body = {
            'application/json': {
                'body': body
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

    return api_response
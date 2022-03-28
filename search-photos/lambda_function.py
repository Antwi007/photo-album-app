import json
import boto3
import requests
from requests_aws4auth import AWS4Auth
import botocore

client = boto3.client('lex-runtime')

region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
auth = ('KeremNana', 'KeremNana1!')

host = 'https://search-photos2-uwqdo7dpete37eq6ebvw5p3hx4.us-east-1.es.amazonaws.com' # the OpenSearch Service domain, including https://
index = 'photos'
url = host + '/' + index + '/_search'

# print("hi")
# comment

def lambda_handler(event, context):
    user_id = '3957-1800-7070'
    
    user_message = event['queryStringParameters']['user_message']
    # user_message = "i want to see \"Kerem\""
    # print("user message", user_message)
    
    #http response object
    responseObject = {}
    responseObject["isBase64Encoded"] = False
    responseObject['statusCode'] = 200
    responseObject['headers'] = {}
    responseObject['headers']['Content-Type'] = 'application/json'
    responseObject['headers']["Access-Control-Allow-Headers"] = "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token"
    responseObject['headers']["Access-Control-Allow-Methods"] = "OPTIONS,GET"
    responseObject['headers']["Access-Control-Allow-Credentials"] = True
    responseObject['headers']["Access-Control-Allow-Origin"] = "*"
    responseObject['headers']['X-Requested-With'] = "*"
    
    responseObject['body']= json.dumps(
        {
          "type": "unstructured",
          "unstructured": {
            "id": "string",
            "text": "I didn't get that",
            "timestamp": "string"
          }
        }
    )
    
    if user_message is None:
        return responseObject
    
    # By default, treat the user request as coming from the America/New_York time zone.
    response = client.post_text(
        botName='ScottsBot',
        botAlias='one',
        userId=user_id,
        inputText=user_message,
    )
    
    try:
        queries = response['slots']
    except:
        return response
        
    queryOne = queries["queryOne"]
    queryTwo = None
    print(queryOne, queryTwo)
    try:
        queryTwo = queries["queryTwo"]
    except:
        pass
        
    query =  {
        "query": {
          "match": {
            "labels": queryOne
          }
        }
    }

    # Elasticsearch 6.x requires an explicit Content-Type header
    headers = { "Content-Type": "application/json" }

    # Make the signed HTTP request
    response = requests.get(url, auth=auth, headers=headers, data=json.dumps(query)).json()
    
    # print("res", response)
    photos = []
    try:
        res = response['hits']['hits']
        photos = res
    except:
        pass
    
    query =  {
        "query": {
          "match": {
            "labels": queryTwo
          }
        }
    }
    
    response = requests.get(url, auth=auth, headers=headers, data=json.dumps(query)).json()
    
    try:
        res = response['hits']['hits']
        photos += res
    except:
        pass
    
    responseObject['body']= json.dumps(
        {
          "type": "unstructured",
          "unstructured": {
            "id": "string",
            "photos": photos,
            "timestamp": "string"
          }
        }
    )
    
    return responseObject

import json
import urllib.parse
import boto3
from datetime import datetime
import requests
from requests_aws4auth import AWS4Auth

s3 = boto3.client('s3')
client=boto3.client('rekognition')

def lambda_handler(event, context):
    try:
        # Get bucket name and photo from S3 event trigger
        bucket = event['Records'][0]['s3']['bucket']['name']
        photo = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        # photo = "dog.jpeg"
        
        # Get labels of photo from Rekognition
        response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
            MaxLabels=10)
    
        labels = []
      
        for label in response['Labels']:
            labels.append(label['Name'])
    
        # Put object in Elastic Search
        
        region = 'us-east-1'
        service = 'es'
        credentials = boto3.Session().get_credentials()
        auth = ('KeremNana', 'KeremNana1!')
        
        host = 'https://search-photos-6hcrqwyptuxytg6vk2kalgxnny.us-east-1.es.amazonaws.com' # the OpenSearch Service domain, including https://
        index = 'photos'
        url = host + '/' + index + '/_create/'
    
        opensearch_object = {
            "objectKey": photo,
            "bucket": bucket,
            "createdTimeStamp": str(datetime.now()),
            "labels": labels
        }
    
        # Elasticsearch 6.x requires an explicit Content-Type header
        headers = { "Content-Type": "application/json" }
    
        # Make the signed HTTP request
        response = requests.post(url+photo, auth=auth, headers=headers, data=json.dumps(opensearch_object)).json()
        
        return response
    
    except Exception as e:
        print(e)
        return e
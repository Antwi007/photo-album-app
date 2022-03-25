import json
import urllib.parse
import boto3
from datetime import datetime
import requests
from requests_aws4auth import AWS4Auth

s3 = boto3.client('s3')
client = boto3.client('rekognition')


def lambda_handler(event, context):
    try:
        # Get bucket name and photo from S3 event trigger
        bucket = event['Records'][0]['s3']['bucket']['name']
        # bucket = "assignment2-kerem-nana-photos"
        photo = urllib.parse.unquote_plus(
            event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        # photo = "dogFINAL.jpeg"
        # comment to test codePipeline
        # Get labels of photo from Rekognition
        response = client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
                                        MaxLabels=10)

        labels = []

        for label in response['Labels']:
            labels.append(label['Name'])

        # Put object in Elastic Search Service

        region = 'us-east-1'
        service = 'es'
        credentials = boto3.Session().get_credentials()
        auth = ('KeremNana', 'KeremNana1!')

        # the OpenSearch Service domain, including https://
        host = 'https://search-photos2-uwqdo7dpete37eq6ebvw5p3hx4.us-east-1.es.amazonaws.com'
        index = 'photos'
        url = host + '/' + index + '/_create/'

        opensearch_object = {
            "objectKey": photo,
            "bucket": bucket,
            "createdTimeStamp": str(datetime.now()),
            "labels": labels
        }

        # Elasticsearch 6.x requires an explicit Content-Type header
        headers = {"Content-Type": "application/json"}

        # Make the signed HTTP request
        response = requests.post(
            url+photo, auth=auth, headers=headers, data=json.dumps(opensearch_object)).json()

        return response

    except Exception as e:
        print(e)
        return e

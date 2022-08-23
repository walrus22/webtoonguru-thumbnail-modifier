import json
import boto3
import base64
from PIL import Image
from io import BytesIO
import os

s3 = boto3.client('s3')
S3_BUCKET_NAME = 'webtoonguru-thumbnail-jjy'
# S3_KEY = 'https-::cds.myktoon.com:download?file=:img:webtoon:thumb:2020:03:24:1585010285518.jpg'

def hello(event, context):
    try : 
        response = s3.get_object(
            Bucket=S3_BUCKET_NAME,
            Key=S3_KEY, # decode 
        )
        img_body = response['Body'].read()
        img = Image.open(BytesIO(img_body))
        originalWidth, originalHeight = img.size
        
        query = event.get('queryStringParameters')
        S3_KEY = query.get('key')
        imgFormat = query.get('format', "webp")
        width = int(query.get('width', originalWidth))
        height = int(query.get('height', originalHeight))
        
        img = img.crop(((originalWidth-width)/2, (originalHeight-height)/2, (originalWidth+width)/2, (originalHeight+height)/2))
        buffer = BytesIO()
        img.save(buffer, imgFormat)
        # img.show()
        
        return {
            'headers': { "Content-Type": "image/" + imgFormat},
            'statusCode': 200,
            'body': base64.b64encode(buffer.getvalue()),
            'isBase64Encoded': True
        }
        
    except Exception as e:
        exception_type = e.__class__.__name__
        exception_message = str(e)
        api_exception_obj = {
            "isError": True,
            "type": exception_type,
            "message": exception_message,
            "query" : event.get('queryStringParameters'),
        }
        api_exception_json = json.dumps(api_exception_obj)
        return {
            "headers": {},
            "statusCode": 404,
            "body": api_exception_json,
        }
        
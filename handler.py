import json
import boto3
import base64
from PIL import Image
from io import BytesIO
import os
import re

def hello(event, context):
    try : 
        validURL='^https://.*\.webtoon.guru/.*'
        
        if True :
        # if event.get('headers').get('Referer') and re.search(validURL, event.get('headers').get('Referer')) :
            s3 = boto3.client('s3')
            query = event.get('queryStringParameters')
            S3_KEY = query.get('key')
            S3_BUCKET_NAME = 'webtoonguru-thumbnail-jjy'
            
            response = s3.get_object(
                Bucket=S3_BUCKET_NAME,
                Key=S3_KEY, # decode 
            )
            img_body = response['Body'].read()
            img = Image.open(BytesIO(img_body))
            originalWidth, originalHeight = img.size
            # print(img.size)
            # img.show()
            
                                    
            
            imgFormat = query.get('format', "webp")
            width = int(query.get('width', originalWidth))
            height = int(query.get('height', originalHeight))
            
            img = img.crop(((originalWidth-width)/2, (originalHeight-height)/2, (originalWidth+width)/2, (originalHeight+height)/2))
            buffer = BytesIO()
            img.save(buffer, imgFormat)
            return {
                'headers': { 
                    "Content-Type": "image/" + imgFormat,
                    "Access-Control-Allow-Origin" : "*",
                },
                'statusCode': 200,
                'body': base64.b64encode(buffer.getvalue()),
                'isBase64Encoded': True
            }
            
        else : 
            return {
                'headers': {
                    "Access-Control-Allow-Origin" : "*",
                },
                "statusCode": 403,
                'body' : json.dumps(event['headers']),            
            }
                
    except Exception as e:
        exception_type = e.__class__.__name__
        exception_message = str(e)
        api_exception_obj = {
            "isError": True,
            "type": exception_type,
            "message": exception_message,
            "query" : event.get('queryStringParameters'),
            # "options" : {"key": S3_KEY, "format" : format, "width" : width, "height" : height},
        }
        api_exception_json = json.dumps(api_exception_obj)
        return {
            "headers": {},
            "statusCode": 404,
            "body": api_exception_json,
        }
        
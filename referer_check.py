import json
import boto3
import base64
from PIL import Image
from io import BytesIO
import os
import re

def referer_check(event, context):
    try : 
        validURL='^https://.*\.webtoon.guru/.*'
        if event.get('headers').get('Referer') and re.search(validURL, event.get('headers').get('Referer')) :
            return {
                'headers': { 
                    "Access-Control-Allow-Origin" : "*",
                },
                'statusCode': 200,
                'body': json.dumps(event),
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
        
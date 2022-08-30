import json
import boto3
import base64
from PIL import Image
from io import BytesIO
import re
from collections import Counter

def is_meaningful_pix(pix, dominant_color):
    for i in range(len(pix)):
        diff = abs(pix[i] - dominant_color[i]) / 255
        if diff <= 30/255:
            continue
        else : 
            return True
    return False

def trim_side_background(img):
    dominant_color = Counter(list(img.getdata())).most_common(1)[0][0]
    pix = img.load()
    meaningful_zone_borders = []
    is_meaningful_zone = False

    for x in range(img.size[0]):
        for y in range(img.size[1]):
            
            # if pix[x,y] != dominant_color:
            if is_meaningful_pix(pix[x,y], dominant_color):
                if is_meaningful_zone == False: # zone start
                    is_meaningful_zone = True
                    meaningful_zone_borders.append(x) 
                break # if already in zone, skip
            elif y == img.size[1]-1: # all pix[x,y] == dominant column
                if is_meaningful_zone == True:
                    meaningful_zone_borders.append(x-1) 
                is_meaningful_zone = False
            
    if len(meaningful_zone_borders)%2 == 1: # last column 
        meaningful_zone_borders.append(img.size[1])

    max = 0
    for i in range(len(meaningful_zone_borders)):
        if i == len(meaningful_zone_borders)-1:
            break
        if max <= meaningful_zone_borders[i+1] - meaningful_zone_borders[i]:
            max = meaningful_zone_borders[i+1] - meaningful_zone_borders[i]
            meaningful_start = meaningful_zone_borders[i]
            meaningful_end = meaningful_zone_borders[i+1]
            
    img =  img.crop((meaningful_start, 0, meaningful_end, img.size[1]))
    return img

def thumbnail_modifier(event, context):
    try : 
        validURL='^https://.*\.webtoon.guru/.*'
        referer = event.get('headers').get('Referer')
        
        # if True :
        if referer and (re.search(validURL, referer) or re.search('https://webtoon.guru/.*', referer)):
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
            if query.get('trim') == 'true':
                img = trim_side_background(img)
                
            imgFormat = query.get('format', "webp")
            original_size = {'width' : img.size[0], 'height': img.size[1]}
            desire_size = {'width': int(query.get('width', original_size['width'])), 'height': int(query.get('height', original_size['height']))}
            
            long_aspect='width' if desire_size['width']/original_size['width'] > desire_size['height']/original_size['height'] else 'height'
            resize_ratio = desire_size[long_aspect] / original_size[long_aspect]
            img = img.resize((round(original_size['width'] * resize_ratio), round(original_size['height'] * resize_ratio)))
            img = img.crop(((img.size[0]-desire_size['width'])/2, (img.size[1]-desire_size['height'])/2, (img.size[0]+desire_size['width'])/2, (img.size[1]+desire_size['height'])/2)) 
            
            buffer = BytesIO()
            img.save(buffer, imgFormat)
            return {
                'headers': { 
                    "Content-Type": "image/" + imgFormat,
                    "Access-Control-Allow-Origin" : "*",
                    "Access-Control-Allow-Credentials" : True,
                },
                'statusCode': 200,
                'body': base64.b64encode(buffer.getvalue()),
                'isBase64Encoded': True
            }
            
        else : 
            return {
                'headers': {
                    "Access-Control-Allow-Origin" : "*",
                    "Access-Control-Allow-Credentials" : True,
                },
                "statusCode": 403,
                'body' : json.dumps(event),            
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
        
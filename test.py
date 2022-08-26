import json
import boto3
import base64
from PIL import Image
from io import BytesIO
import os
import re

s3 = boto3.client('s3')
S3_KEY = '630873c4eee3e6209904f84e'
S3_BUCKET_NAME = 'webtoonguru-thumbnail-jjy'

response = s3.get_object(
    Bucket=S3_BUCKET_NAME,
    Key=S3_KEY, # decode 
)
img_body = response['Body'].read()
img = Image.open(BytesIO(img_body))
originalWidth, originalHeight = img.size
print(img.size)
img.show()

imgFormat = 'webp'
width = 500
height = 500

"""
<썸네일 종류>
1. small card (home, genre, date)
2. list card (전체보기)
3. detail card (디테일 화면)
4. artist-other-work (아티스트 다른 작품)
5. special case



"""

# img = img.crop(((originalWidth-width)/2, (originalHeight-height)/2, (originalWidth+width)/2, (originalHeight+height)/2))
                        
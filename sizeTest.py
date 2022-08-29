import json
import boto3
import base64
from PIL import Image
from io import BytesIO
import os
import re
import cv2
from collections import Counter



def trim_side_background(img):
    dominant_color = Counter(list(img.getdata())).most_common(1)[0][0]
    pix = img.load()
    meaningful_zone_borders = []
    is_meaningful_zone = False

    for x in range(img.size[0]):
        for y in range(img.size[1]):
            if pix[x,y] != dominant_color:
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
    
    img =  img.crop((meaningful_start, 0, meaningful_start + meaningful_end, img.size[1]))
    return img

"""
# 썸네일 종류
1. small card (home, genre, date)
2. list card (전체보기)
3. detail card (디테일 화면)
4. artist-other-work (아티스트 다른 작품)
5. special case
    - 썸네일 치우처져 있는 경우

# resize
crop 이전에 잘리는 경우가 생기면 안됨
=> resize_ratio : original/desire이 큰 쪽으로 

# crop


# antialising
none: 114kb, LANCZOS: 120kb, BICUBIC: 114kb
셋다 체감 별로 없음.. 오히려 안하는게 더 나은 것 같기도

"""

s3 = boto3.client('s3')
# S3_KEY = '630874d3eee3e62099050604' ## 신마 [스크롤]
# S3_KEY = '630874f3eee3e62099050785' ## 어쩌다 생각나는 이야기
S3_KEY = '63087489eee3e620990502ae' 
S3_BUCKET_NAME = 'webtoonguru-thumbnail-jjy'

response = s3.get_object(
    Bucket=S3_BUCKET_NAME,
    Key=S3_KEY, # decode 
)
img_body = response['Body'].read()
    
img = Image.open(BytesIO(img_body))
img = trim_side_background(img)
img.show()

# img = Image.open('/Users/kss/Documents/GitHub/webtoonguru-thumbnail-modifier-jjy/imgTest/portrait_size.jpeg')
# img = Image.open('/Users/kss/Documents/GitHub/webtoonguru-thumbnail-modifier-jjy/imgTest/square.jpeg')
# img = Image.open('/Users/kss/Documents/GitHub/webtoonguru-thumbnail-modifier-jjy/imgTest/detail_original.jpg')
# original_size = {'width' : 1000, 'height': 600}

original_size = {'width' : img.size[0], 'height': img.size[1]}
desire_size = {'width': 80, 'height': 80}
long_aspect='width' if desire_size['width']/original_size['width'] > desire_size['height']/original_size['height'] else 'height'
resize_ratio = desire_size[long_aspect] / original_size[long_aspect]

img = img.resize((round(original_size['width'] * resize_ratio), round(original_size['height'] * resize_ratio)))
img.show()
img = img.crop(((img.size[0]-desire_size['width'])/2, (img.size[1]-desire_size['height'])/2, (img.size[0]+desire_size['width'])/2, (img.size[1]+desire_size['height'])/2)) # center crop
img.show()



# desireFormat = 'webp'



# img1.save('/Users/kss/Documents/GitHub/webtoonguru-thumbnail-modifier-jjy/imgTest/NONE.' + desireFormat, format=desireFormat)
# img2 = img.resize(desire_size, Image.LANCZOS)
# img2.save('/Users/kss/Documents/GitHub/webtoonguru-thumbnail-modifier-jjy/imgTest/LANCZOS.' + desireFormat, format=desireFormat)



# img.show()
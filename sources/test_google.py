import json
import traceback

from googleapiclient.discovery import build
import requests

headers = {'Content-Type': 'application/json'}
url = "https://customsearch.googleapis.com/customsearch/v1?cx=dc036f5cac32deb3d&imgSize=LARGE&num=10&q=friction&safe=active&key=AIzaSyAgTTei1O1_b1DTvrJWbEbM8tuyE_Fm1iA"


try:
    service = build("customsearch", "v1",
                    developerKey="AIzaSyAgTTei1O1_b1DTvrJWbEbM8tuyE_Fm1iA")
    res = service.cse().list(
        q='friction',
        cx='dc036f5cac32deb3d',
        num=10
    ).execute()

    for element in res['items']:
        print(element['pagemap']['cse_image'][0]['src'])
except:
    traceback.print_exc()
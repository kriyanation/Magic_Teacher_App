import traceback

from googleapiclient.discovery import build


class ImageUtils():


    def __init__(self):
        headers = {'Content-Type': 'application/json'}
        url = "https://customsearch.googleapis.com/customsearch/v1?cx=dc036f5cac32deb3d&imgSize=LARGE&num=10&q=friction&safe=active&key=AIzaSyAgTTei1O1_b1DTvrJWbEbM8tuyE_Fm1iA"
        self.imagelist = []
    def search_images(self,sq):
        try:
            service = build("customsearch", "v1",
                            developerKey="AIzaSyDCQTMmD3wJmtKv44wCLx_YT6xGg96Ml4o")
            res = service.cse().list(
                q=sq,
                cx='dc036f5cac32deb3d',
                num=10,

            ).execute()

            print(res)
            if 'items' in res.keys():
                for element in res['items']:
                    if 'pagemap' in element.keys():
                        if 'cse_image' in element['pagemap'].keys():
                            print(element['pagemap']['cse_image'][0]['src'])
                            self.imagelist.append(element['pagemap']['cse_image'][0]['src'])
            return self.imagelist
        except:
            traceback.print_exc()
            return self.imagelist




# gis.next_page()
# print("Next PAge......")
# for image in gis.results():
#     print(image.url)
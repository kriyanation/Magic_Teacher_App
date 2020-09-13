import traceback

from googleapiclient.discovery import build


class ImageUtils():


    def __init__(self):
        headers = {'Content-Type': 'application/json'}
        url = "https://customsearch.googleapis.com/customsearch/v1?cx=&imgSize=LARGE&num=10&q=friction&safe=active&key="
        self.imagelist = []
    def search_images(self,sq):
        try:
            service = build("customsearch", "v1",
                            developerKey="")
            res = service.cse().list(
                q='friction',
                cx='',
                num=10,






            ).execute()

            print(res)

            for element in res['items']:
                print(element['pagemap']['cse_image'][0]['src'])
                self.imagelist.append(element['pagemap']['cse_image'][0]['src'])
            return self.imagelist
        except:
            traceback.print_exc()




# gis.next_page()
# print("Next PAge......")
# for image in gis.results():
#     print(image.url)

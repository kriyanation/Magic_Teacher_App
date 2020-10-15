import traceback

from googleapiclient.discovery import build


class ImageUtils():




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
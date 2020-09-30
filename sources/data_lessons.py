
import os
import shutil
import traceback
from base64 import b64encode


import requests,json

import data_capture_lessons

file_root = os.path.abspath(os.path.join(os.getcwd(),".."))


def convert_base_64(imagefile):
    print(imagefile)
    try:
        with open(imagefile, 'rb') as open_file:
            byte_content = open_file.read()
        base64_bytes = b64encode(byte_content)
        base64_string = base64_bytes.decode("utf-8")
        return base64_string

    except Exception:
        traceback.print_exc()
        print("exception")
        return ""


def delete_lesson(lesson_id):
    try:
        delete_data = data_capture_lessons.delete_lesson(lesson_id)
        if delete_data == 0:
            shutil.rmtree("Lessons/Lesson"+lesson_id,True)
            return 0
    except:
        traceback.print_exc()
        print("Wondersky: Error Deleting Lessons")
        return 1

def prepare_lesson_share(lesson_id):
 class_id, User = data_capture_lessons.get_user_classid()
 rows = data_capture_lessons.get_lessons_for_share(lesson_id)
 imageroot = file_root+os.path.sep+"Lessons"+os.path.sep+"Lesson"+str(lesson_id)+os.path.sep+"images"+os.path.sep

 data = '''{
     "lesson_id": "''' +str(rows[0])+'''",
     "class_id": "''' +str(class_id)+'''",
     "user": "http://learning-room-285708.el.r.appspot.com/auth/users/'''+str(User)+'''/",
     "title": "''' +make_json_ready(rows[1])+'''",
     "title_image": "''' + convert_base_64(imageroot+rows[2]) + '''",
     "title_video": null,
     "title_description": "''' +make_json_ready(rows[4])+'''",
     "term1": "''' +make_json_ready(rows[5])+'''",
     "term1_description": "''' +make_json_ready(rows[6])+'''",
     "term1_image": "''' + convert_base_64(imageroot+rows[7]) + '''",
     "term2": "''' +make_json_ready(rows[8])+'''",
     "term2_description": "''' +make_json_ready(rows[9])+'''",
     "term2_image": "''' + convert_base_64(imageroot+rows[10]) + '''",
     "term3": "''' +make_json_ready(rows[11])+'''",
     "term3_description": "''' +make_json_ready(rows[12])+'''",
     "term3_image": "''' + convert_base_64(imageroot+rows[13]) + '''",
     "number_of_steps": "'''+str(rows[14])+'''",
     "step1_description": "'''+make_json_ready(rows[15])+'''",
     "step1_image": "''' + convert_base_64(imageroot+rows[23]) + '''",
     "step2_description": "'''+make_json_ready(rows[16])+'''",
     "step2_image": "''' + convert_base_64(imageroot+rows[24]) + '''",
     "step3_description": "'''+make_json_ready(rows[17])+'''",
     "step3_image": "''' + convert_base_64(imageroot+rows[25]) + '''",
     "step4_description": "'''+make_json_ready(rows[18])+'''",
     "step4_image": "''' + convert_base_64(imageroot+rows[26]) + '''",
     "step5_description": "'''+make_json_ready(rows[19])+'''",
     "step5_image": "''' + convert_base_64(imageroot+rows[27]) + '''",
     "step6_description": "'''+make_json_ready(rows[20])+'''",
     "step6_image": "''' + convert_base_64(imageroot+rows[28]) + '''",
     "step7_description": "'''+make_json_ready(rows[21])+'''",
     "step7_image": "''' + convert_base_64(imageroot+rows[29]) + '''",
     "step8_description": "'''+make_json_ready(rows[22])+'''",
     "step8_image": "''' + convert_base_64(imageroot+rows[30]) + '''",
     "questions": "'''+make_json_ready(rows[31])+'''",
     "lesson_language": "'''+rows[33]+'''",
     "whiteboard_image": "'''+convert_base_64(imageroot+rows[36])+'''",
     "application_video_link": "'''+rows[34]+'''",
     "application_video_running_notes": "'''+make_json_ready(rows[35])+'''"
 }'''
 return data

def make_json_ready(text):
    json_ready_string = text.replace("\n","~")
    json_ready_string = json_ready_string.replace("\"","|")
    return json_ready_string

def make_data_ready(text):
    data_ready_string = text.replace("~","\n")
    data_ready_string = data_ready_string.replace("|","\"")
    return data_ready_string

def get_token(username, password):

   url = 'https://thelearningroom.el.r.appspot.com/auth/token/login'
   json_string = '''{
                      "username":"'''+username+'''",
                      "password":"'''+password+'''"
                    }'''
   headers = {'Content-Type':'application/json'}
   response = requests.post(url,headers=headers,data=json_string)
   if response.status_code != 200:
       return "error"
   json_object = json.loads(response.content)
   return json_object["auth_token"]


def post_lesson(data, token,lesson_id):
    try:
        json_object = json.loads(data)
        class_id, User = data_capture_lessons.get_user_classid()
        headers = {'Content-Type': 'application/json', 'Authorization': 'Token '+token}
        url_root = "https://thelearningroom.el.r.appspot.com/"
        url = "https://thelearningroom.el.r.appspot.com/lesson/?username="+str(User)+"&lesson_id="+json_object['lesson_id']+"&class_id="+json_object['class_id']
        response_get =  requests.get(url,headers=headers)
        json_object_get = json.loads(response_get.content)
        if response_get.status_code==200 and len(json_object_get) > 0:
            global_lesson_id = json_object_get[0]["global_lesson_id"]
            url_put = url_root+"lesson/"+str(global_lesson_id)+"/?username="+str(User)+"&lesson_id="+str(json_object['lesson_id'])+"&class_id="+str(json_object['class_id'])
            response = requests.patch(url_put, headers=headers, data=data.encode('utf-8'))
        else:
            response = requests.post(url,headers=headers,data =data.encode('utf-8'))
            print(response.status_code)
            print(response.text)
        if response.status_code==201:
            data_capture_lessons.update_shared(lesson_id)
        url_logout= url_root+"auth/token/logout/"
        response_logout = requests.post(url_logout, headers=headers)
        print(response_logout.content)

    except Exception:
        print(traceback.print_exc())
        print("exception")


def import_new_lesson(user,classid,lessonid):

    url_root = "https://thelearningroom.el.r.appspot.com/"
    headers = {'Content-Type': 'application/json'}
    url = url_root+"lesson/?username=" + user + "&lesson_id=" + lessonid + "&class_id=" + classid
    response_get = requests.get(url, headers=headers)
    response_object_get = json.loads(response_get.content)
    if response_get.status_code == 200 and len(response_object_get) > 0:
       # messagebox.showinfo("Lesson Import","Import triggered\n The screen will close and refresh once import is completed",parent=lessonwindow)
        json_object = response_object_get[0]
        status = update_lesson_details(json_object)
        if status == "error":
            return "error"
    else:
        return "error"

def update_lesson_details(json_object):
    title_image_file = json_object["title_image"]
    title_filename, term1_filename, term2_filename,\
    term3_filename,step1_filename,step2_filename,step3_filename,step4_filename,step5_filename,\
    step6_filename,step7_filename,step8_filename,whiteboard_filename = "","","","","","","","","","","","",""

    if not os.path.exists("tmp"):
      os.mkdir("tmp")
    if title_image_file is not None:
        title_filename = constructfilename(title_image_file,"title")
    term1_image_file = json_object["term1_image"]
    if term1_image_file is not None:
        term1_filename = constructfilename(term1_image_file,"term1")
    term2_image_file = json_object["term2_image"]
    if term2_image_file is not None:
        term2_filename = constructfilename(term2_image_file,"term2")
    term3_image_file = json_object["term3_image"]
    if term3_image_file is not None:
        term3_filename = constructfilename(term3_image_file,"term3")
    step1_image_file = json_object["step1_image"]
    if step1_image_file is not None:
        step1_filename = constructfilename(step1_image_file,"step1")
    step2_image_file = json_object["step2_image"]
    if step2_image_file is not None:
        step2_filename = constructfilename(step2_image_file,"step2")
    step3_image_file = json_object["step3_image"]
    if step3_image_file is not None:
        step3_filename = constructfilename(step3_image_file,"step3")
    step4_image_file = json_object["step4_image"]
    if step4_image_file is not None:
        step4_filename = constructfilename(step4_image_file,"step4")
    step5_image_file = json_object["step5_image"]
    if step5_image_file is not None:
        step5_filename = constructfilename(step5_image_file,"step5")
    step6_image_file = json_object["step6_image"]
    if step6_image_file is not None:
        step6_filename = constructfilename(step6_image_file,"step6")
    step7_image_file = json_object["step7_image"]
    if step7_image_file is not None:
        step7_filename = constructfilename(step7_image_file,"step7")
    step8_image_file = json_object["step8_image"]
    if step8_image_file is not None:
        step8_filename = constructfilename(step8_image_file,"step8")
    whiteboard_image = json_object["whiteboard_image"]
    if whiteboard_image is not None:
        whiteboard_filename = constructfilename(whiteboard_image, "whiteboard")

    json_object["title_description"] = make_data_ready(json_object["title_description"])
    json_object["term1_description"] = make_data_ready(json_object["term1_description"])
    json_object["term2_description"] = make_data_ready(json_object["term2_description"])
    json_object["term3_description"] = make_data_ready(json_object["term3_description"])
    json_object["term1"] = make_data_ready(json_object["term1"])
    json_object["term2"] = make_data_ready(json_object["term2"])
    json_object["term3"] = make_data_ready(json_object["term3"])
    json_object["questions"] = make_data_ready(json_object["questions"])
    json_object["application_video_running_notes"] = make_data_ready(json_object["application_video_running_notes"])
    json_object["title"] = make_data_ready(json_object["title"])
    json_object["step1_description"] = make_data_ready(json_object["step1_description"])
    json_object["step2_description"] = make_data_ready(json_object["step2_description"])
    json_object["step3_description"] = make_data_ready(json_object["step3_description"])
    json_object["step4_description"] = make_data_ready(json_object["step4_description"])
    json_object["step5_description"] = make_data_ready(json_object["step5_description"])
    json_object["step6_description"] = make_data_ready(json_object["step6_description"])
    json_object["step7_description"] = make_data_ready(json_object["step7_description"])
    json_object["step8_description"] = make_data_ready(json_object["step8_description"])

    query_parameters = [json_object["title"],title_filename,json_object["title_video"],json_object["title_description"],
                        json_object["term1"],json_object["term1_description"],term1_filename,json_object["term2"],json_object["term2_description"],term2_filename,
                        json_object["term3"],json_object["term3_description"],term3_filename,json_object["number_of_steps"],json_object["step1_description"],step1_filename,json_object["step2_description"],step2_filename,
                        json_object["step3_description"],step3_filename,json_object["step4_description"],step4_filename,json_object["step5_description"],step5_filename,
                        json_object["step6_description"],step6_filename,json_object["step7_description"],step7_filename,json_object["step8_description"],step8_filename,
                        json_object["questions"],"",whiteboard_filename,json_object["application_video_running_notes"],json_object["application_video_link"],json_object["lesson_language"]]
    data_capture_lessons.insert_imported_record(query_parameters)
    new_id = data_capture_lessons.get_new_id()
    if not os.path.exists("../Lessons/Lesson"+str(new_id)):
        os.mkdir("../Lessons/Lesson"+str(new_id))
        os.mkdir("../Lessons/Lesson"+str(new_id)+"/images")
        src_files = os.listdir("tmp")
        for file_name in src_files:
            full_file_name = os.path.join("tmp", file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, "../Lessons/Lesson"+str(new_id)+"/images")
                os.remove(full_file_name)
        os.rmdir("tmp")
def constructfilename(fileurl,prefix):
    file_dl = fileurl.split("?", 2)
    extension = file_dl[0].split(".")[-1]
    status_dl = download_file(fileurl, "tmp/"+prefix+"."+ extension)
    title_filename = prefix+"."+extension
    return title_filename



def  download_file(fileurl,filename):
    try:
        response = requests.get(fileurl)
        if response.status_code != 200:
            return "error"
        file = open(filename, "wb")
        file.write(response.content)
        file.close()
    except:
        traceback.print_exc()



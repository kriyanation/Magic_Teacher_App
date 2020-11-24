
import os
import random
import sqlite3
import traceback


file_root = os.path.abspath(os.path.join(os.getcwd(),".."))
db = "MagicRoom.db"

def get_Lessons():
    print (db)
    connection = sqlite3.connect(db)
    cur = connection.cursor()
    sql = "select Lesson_ID, Lesson_Title, Title_Notes_Language from Magic_Science_Lessons"
    cur.execute(sql)
    rows = cur.fetchall()
    list_lessons = []
    for element in rows:
        list_lessons.append(element)
    connection.commit()
    connection.close()
    return list_lessons

def get_lesson_lanugage(lessonid):
    connection = sqlite3.connect(db)
    cur = connection.cursor()
    sql = "select Title_Notes_Language from Magic_Science_Lessons where Lesson_ID=?"
    cur.execute(sql, (lessonid,))
    rows = cur.fetchone()
    connection.commit()
    connection.close()
    return rows[0]


def get_lessons_for_share(lesson_id):
    connection = sqlite3.connect(db)
    cur = connection.cursor()
    sql = "select Lesson_ID, Lesson_Title, Title_Image,Title_Video,Title_Running_Notes,Factual_Term1,Factual_Term1_Description,Factual_Image1,Factual_Term2,Factual_Term2_Description,Factual_Image2,Factual_Term3,Factual_Term3_Description,Factual_Image3," \
          "Application_Steps_Number,Application_Step_Description_1,Application_Step_Description_2,Application_Step_Description_3,Application_Step_Description_4,Application_Step_Description_5,Application_Step_Description_6,Application_Step_Description_7," \
          "Application_Step_Description_8,Application_Steps_Widget_1,Application_Steps_Widget_2,Application_Steps_Widget_3,Application_Steps_Widget_4,Application_Steps_Widget_5,Application_Steps_Widget_6,Application_Steps_Widget_7," \
          "Application_Steps_Widget_8,IP_Questions,Apply_External_Link,Title_Notes_Language,Application_Video_Link,Application_Video_Running_Notes,Whiteboard_Image from Magic_Science_Lessons where Lesson_ID=?"
    cur.execute(sql,(lesson_id,))
    rows = cur.fetchall()
    connection.commit()
    connection.close()
    return rows[0]

def get_user_classid():
    connection = sqlite3.connect(db)
    cur = connection.cursor()
    sql = "select class_id, User from Magic_Teacher_Data where Class_No=?"
    cur.execute(sql,(1,))
    rows = cur.fetchall()[0]
    connection.commit()
    connection.close()
    return rows[0],rows[1]


def update_shared(lesson_id,userid):
    connection = sqlite3.connect(db)
    cur = connection.cursor()
    sql = "update Magic_Science_Lessons set Shared_Flag=1,UserID=? where Lesson_ID=?"
    cur.execute(sql, (userid,lesson_id))
    connection.commit()
    connection.close()

def is_shared(lesson_id):
    connection = sqlite3.connect(db)
    cur = connection.cursor()
    sql = "select Shared_Flag from Magic_Science_Lessons where Lesson_ID=?"
    cur.execute(sql, (lesson_id,))
    rows = cur.fetchone()
    connection.commit()
    connection.close()
    return rows[0]

def get_userid(lesson_id):
    connection = sqlite3.connect(db)
    cur = connection.cursor()
    sql = "select UserID from Magic_Science_Lessons where Lesson_ID=?"
    cur.execute(sql, (lesson_id,))
    rows = cur.fetchone()
    connection.commit()
    connection.close()
    return rows[0]


def insert_imported_record(query_parameters):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = ('insert into Magic_Science_Lessons (Lesson_Title,Title_Image,Title_Video,Title_Running_Notes,Factual_Term1,Factual_Term1_Description,Factual_Image1,Factual_Term2,Factual_Term2_Description,Factual_Image2,Factual_Term3,Factual_Term3_Description,'
                       'Factual_Image3,Application_Steps_Number,Application_Step_Description_1,Application_Steps_Widget_1,Application_Step_Description_2,Application_Steps_Widget_2,Application_Step_Description_3,Application_Steps_Widget_3,Application_Step_Description_4,Application_Steps_Widget_4,'
                       'Application_Step_Description_5,Application_Steps_Widget_5, Application_Step_Description_6,Application_Steps_Widget_6, Application_Step_Description_7, Application_Steps_Widget_7,Application_Step_Description_8,Application_Steps_Widget_8,'
                       'IP_Questions,Answer_Key,Whiteboard_Image,Application_Video_Running_Notes,Application_Video_Link,Title_Notes_Language) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)')
        cur.execute(sql, query_parameters)
        connection.commit()
        connection.close()
    except (Exception):
        traceback.print_exc()
def get_new_id():
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = "SELECT seq FROM sqlite_sequence where name = 'Magic_Science_Lessons'"
        cur.execute(sql)
        rows = cur.fetchone()
        new_id = rows[0]
        return new_id
    except sqlite3.OperationalError:
        traceback.print_exc()

def get_title_info(lesson_id):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = "SELECT Lesson_Title, Title_Image, Title_Running_Notes FROM Magic_Science_Lessons where Lesson_ID = ?"
        cur.execute(sql,(lesson_id,))
        rows = cur.fetchone()
        title = rows[0]
        title_image = rows[1]
        title_running_notes = rows[2]
        return title, title_image, title_running_notes
    except sqlite3.OperationalError:
        traceback.print_exc()


def get_fact_images(lessonid):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = "SELECT Factual_Image1, Factual_Image2,Factual_Image3 FROM Magic_Science_Lessons where Lesson_ID = ?"
        cur.execute(sql,(lessonid,))
        rows = cur.fetchone()
        return rows[0],rows[1],rows[2]
    except sqlite3.OperationalError:
        traceback.print_exc()

def get_fact_terms(lessonid):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = "SELECT Factual_Term1, Factual_Term2,Factual_Term3 FROM Magic_Science_Lessons where Lesson_ID = ?"
        cur.execute(sql,(lessonid,))
        rows = cur.fetchone()
        return rows[0],rows[1],rows[2]
    except sqlite3.OperationalError:
        traceback.print_exc()

def get_fact_descriptions(lessonid):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = "SELECT Factual_Term1_Description, Factual_Term2_Description,Factual_Term3_Description FROM Magic_Science_Lessons where Lesson_ID = ?"
        cur.execute(sql,(lessonid,))
        rows = cur.fetchone()
        return rows[0],rows[1],rows[2]
    except sqlite3.OperationalError:
        traceback.print_exc()


def get_number_of_steps(lessonid):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = "SELECT Application_Steps_Number FROM Magic_Science_Lessons where Lesson_ID = ?"
        cur.execute(sql,(lessonid,))
        rows = cur.fetchone()
        return rows[0]
    except sqlite3.OperationalError:
        traceback.print_exc()

def get_description_list(lessonid):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = ("SELECT Application_Step_Description_1,Application_Step_Description_2,Application_Step_Description_3,Application_Step_Description_4,"
              "Application_Step_Description_5,Application_Step_Description_6,Application_Step_Description_7,Application_Step_Description_8 " 
              "FROM Magic_Science_Lessons where Lesson_ID = ?")
        cur.execute(sql,(lessonid,))
        rows = cur.fetchone()
        return rows
    except sqlite3.OperationalError:
        traceback.print_exc()

def get_step_image_list(lessonid):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = ("SELECT Application_Steps_Widget_1,Application_Steps_Widget_2,Application_Steps_Widget_3," 
              "Application_Steps_Widget_4,Application_Steps_Widget_5,Application_Steps_Widget_6,Application_Steps_Widget_7," 
              "Application_Steps_Widget_8 FROM Magic_Science_Lessons where Lesson_ID = ?")
        cur.execute(sql,(lessonid,))
        rows = cur.fetchone()
        return rows
    except sqlite3.OperationalError:
        traceback.print_exc()


def get_questions_answer(lessonid):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = ("SELECT IP_Questions, Answer_Key FROM Magic_Science_Lessons where Lesson_ID = ?")
        cur.execute(sql,(lessonid,))
        rows = cur.fetchone()
        return rows[0], rows[1]
    except sqlite3.OperationalError:
        traceback.print_exc()

def set_answer(lessonid,answer_key):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = ("update Magic_Science_Lessons set Answer_Key = ? where Lesson_ID = ?")
        cur.execute(sql,(answer_key,lessonid))
        connection.commit()
        return 0
    except sqlite3.OperationalError:
        traceback.print_exc()
        return 1


def delete_lesson(lesson_id):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = ("delete from Magic_Science_Lessons where Lesson_ID = ?")
        cur.execute(sql, (lesson_id,))
        connection.commit()
        return 0
    except sqlite3.OperationalError:
        traceback.print_exc()
        return 1


def create_lesson(text_lesson_name,lang):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = ("insert into Magic_Science_Lessons (Lesson_Title,Title_Notes_Language) values (?,?)")
        cur.execute(sql, (text_lesson_name,lang))
        connection.commit()
        return 0

    except sqlite3.OperationalError:
        traceback.print_exc()
        return 1



def save_changes(lesson_id,text_image, text_label_1, text_label_2):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = ("update Magic_Science_Lessons set Title_Image=?,Lesson_Title=?,Title_Running_Notes=? where Lesson_ID = ?")
        cur.execute(sql, (text_image,text_label_1,text_label_2,lesson_id))
        connection.commit()
        return 0
    except sqlite3.OperationalError:
        traceback.print_exc()
        return 1


def update_term1(lessonid, text_image_display, text_term_description, text_term_display):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = ("update Magic_Science_Lessons set Factual_Term1=?,Factual_Term1_Description=?,Factual_Image1=? where Lesson_ID = ?")
        cur.execute(sql, (text_term_display,text_term_description,text_image_display,lessonid))
        connection.commit()
        return 0
    except sqlite3.OperationalError:
        traceback.print_exc()
        return 1

def update_term2(lessonid, text_image_display, text_term_description, text_term_display):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = ("update Magic_Science_Lessons set Factual_Term2=?,Factual_Term2_Description=?,Factual_Image2=? where Lesson_ID = ?")
        cur.execute(sql, (text_term_display,text_term_description,text_image_display,lessonid))
        connection.commit()
        return 0
    except sqlite3.OperationalError:
        traceback.print_exc()
        return 1

def update_term3(lessonid, text_image_display, text_term_description, text_term_display):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = ("update Magic_Science_Lessons set Factual_Term3=?,Factual_Term3_Description=?,Factual_Image3=? where Lesson_ID = ?")
        cur.execute(sql, (text_term_display,text_term_description,text_image_display,lessonid))
        connection.commit()
        return 0
    except sqlite3.OperationalError:
        traceback.print_exc()
        return 1


def save_step_texts(lessonid, text1, text2, text3, text4, text5, text6, text7, text8):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = ("update Magic_Science_Lessons set Application_Steps_Number=8,Application_Step_Description_1=?,Application_Step_Description_2=?,Application_Step_Description_3=?,"
               "Application_Step_Description_4=?,Application_Step_Description_5=?,Application_Step_Description_6=?,Application_Step_Description_7=?,"
               "Application_Step_Description_8=? where Lesson_ID = ?")
        cur.execute(sql, (text1,text2,text3,text4,text5,text6,text7,text8, lessonid))
        connection.commit()
        return 0
    except sqlite3.OperationalError:
        traceback.print_exc()
        return 1


def save_step_images(lessonid, step1, step2, step3, step4, step5, step6, step7, step8):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = ("update Magic_Science_Lessons set Application_Steps_Widget_1=?,Application_Steps_Widget_2=?,Application_Steps_Widget_3=?,"
               "Application_Steps_Widget_4=?,Application_Steps_Widget_5=?,Application_Steps_Widget_6=?,Application_Steps_Widget_7=?,"
               "Application_Steps_Widget_8=? where Lesson_ID = ?")
        cur.execute(sql, (step1,step2,step3,step4,step5,step6,step7,step8, lessonid))
        connection.commit()
        return 0
    except sqlite3.OperationalError:
        traceback.print_exc()
        return 1


def save_whiteboard_image(lessonid, filename):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = ("update Magic_Science_Lessons set Whiteboard_Image=? where Lesson_ID = ?")
        cur.execute(sql, (filename,lessonid))
        connection.commit()
        return 0
    except sqlite3.OperationalError:
        traceback.print_exc()
        return 1


def set_questions(lessonid, text_label_1):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = ("update Magic_Science_Lessons set IP_Questions = ? where Lesson_ID = ?")
        cur.execute(sql,(text_label_1,lessonid))
        connection.commit()
        return 0
    except sqlite3.OperationalError:
        traceback.print_exc()
        return 1

def save_notes(lessonid, text_label_1):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = ("update Magic_Science_Lessons set Application_Video_Running_Notes = ? where Lesson_ID = ?")
        cur.execute(sql,(text_label_1,lessonid))
        connection.commit()
        return 0
    except sqlite3.OperationalError:
        traceback.print_exc()
        return 1


def get_formlink(lessonid):

    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = ("SELECT Application_Video_Link FROM Magic_Science_Lessons where Lesson_ID = ?")
        cur.execute(sql, (lessonid,))
        rows = cur.fetchone()
        return rows[0]
    except sqlite3.OperationalError:
        traceback.print_exc()

def get_notes(lessonid):

    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = ("SELECT Application_Video_Running_Notes FROM Magic_Science_Lessons where Lesson_ID = ?")
        cur.execute(sql, (lessonid,))
        rows = cur.fetchone()
        return rows[0]
    except sqlite3.OperationalError:
        traceback.print_exc()


def set_form_link(lessonid, text_label_2):
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = ("update Magic_Science_Lessons set Application_Video_Link = ? where Lesson_ID = ?")
        cur.execute(sql,(text_label_2,lessonid))
        connection.commit()
        return 0
    except sqlite3.OperationalError:
        traceback.print_exc()
        return 1

def get_classid():
    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sqlsel = ("select class_id from Magic_Teacher_Data where Class_No=1")
        cur.execute(sqlsel)
        rows = cur.fetchone()
        connection.close()
        return rows[0]
    except sqlite3.OperationalError:
        traceback.print_exc()
        return 1

def set_classid():
    try:
        number = random.randint(10000, 99999)
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        sql = ("update Magic_Teacher_Data set class_id=? where Class_No=1")
        cur.execute(sql,(number,))
        connection.commit()
        connection.close()
        return 0
    except sqlite3.OperationalError:
        traceback.print_exc()
        return 1
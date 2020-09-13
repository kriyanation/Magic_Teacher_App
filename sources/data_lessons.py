import shutil
import traceback

import data_capture_lessons


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
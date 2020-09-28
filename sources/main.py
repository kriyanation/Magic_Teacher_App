import imghdr
import ntpath
import os
import shutil

import traceback
import random
from threading import Thread

from kivy.graphics import Color, Line
from kivy.metrics import Metrics

from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget


import requests
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock

from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage, Image
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window


import data_capture_lessons
import data_lessons
import image_utils
import certifi

# Here's all the magic !
os.environ['SSL_CERT_FILE'] = certifi.where()
Window.softinput_mode = 'below_target'

class LessonListScreen(Screen):


    def __init__(self, **kwargs):
        super(LessonListScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)

        print("Hello")
        Clock.schedule_once(self.add_buttons,1)

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'lessons':
                return False

    def add_buttons(self,dt):
        self.list_lessons = data_capture_lessons.get_Lessons()
        self.button_list = []
        self.ids.lesson_c.bind(minimum_height=self.ids.lesson_c.setter('height'))
        for element in self.list_lessons:
            button = Button(text=element[1], background_color=[0.76, 0.83, 0.86, 0.8], pos_hint={'top': 1},
                            size_hint_y=None, size_hint_x=1)
            button.on_release = lambda instance=button, a=element[0]: self.switch_to_title(instance, a)
            self.ids.lesson_c.add_widget(button)
            self.button_list.append(button)

    def launch_popup_import(self):
        show = ImportPop()
        self.popupWindow = Popup(title="Import Mini Lesson", content=show,
                            size_hint=(1, 0.4),auto_dismiss=False)
        show.set_popupw(self.popupWindow)
        show.set_screen_instance(self)
        # open popup window
        self.popupWindow.open()

    def switch_to_title(self, i, a):
        self.selected_lesson = a
        self.manager.current = "title"

    def launch_popup(self):
        show = CreatePop()
        self.popupWindow = Popup(title="Create Mini Lesson", content=show,
                                 size_hint=(1, 0.2), auto_dismiss=False)
        show.set_popupw(self.popupWindow)
        show.set_screen_instance(self)
        # open popup window
        self.popupWindow.open()

    def launch_del_popup(self):
        self.popup_delete = DeletePop()
        self.popup_delete.set_screen_instance(self)

        self.popup_delete.open()


class ImportPop(BoxLayout):
    text_userid = StringProperty()
    text_classid = StringProperty()
    text_lessonid = StringProperty()
    text_status = StringProperty()

    def __init__(self, **kwargs):

        super(ImportPop, self).__init__(**kwargs)
        self.lesson_import_flag = 0

    def import_lesson(self,button_sub):

        button_sub.state = "down"
        print(self.text_classid+self.text_userid+self.text_lessonid)
        response_code = 0
        if self.lesson_import_flag == 0:
             response_code, json_object = data_lessons.import_new_lesson(self.text_userid,self.text_classid,self.text_lessonid)

        if response_code == 1:
            self.text_status = "There was an error accessing the lesson. Check your access details."
            button_sub.disabled = False
            button_sub.state = "normal"
            self.lesson_import_flag = 0
        else:

            self.text_status = "Access details correct. Downloading the lesson..."
            self.call_update = Thread(target = data_lessons.update_lesson_details,args=(json_object,))
            self.call_update.start()
            self.progress_bar = ProgressBar()
            self.popup = Popup(
                title='Importing lesson',
                content=self.progress_bar,
                size_hint=(1, 0.3), auto_dismiss=False
            )
            self.popup.open()
            Clock.schedule_interval(self.next, 0.5)

    def next(self, dt):
        if self.call_update.is_alive():
            self.progress_bar.value += 5
        else:
            self.popup.dismiss()
            self.listscreen.container.clear_widgets()
            self.listscreen.add_buttons(1)
            self.lesson_import_flag = 0
            self.popw.dismiss()
            return False


    def close_pop(self):

        self.popw.dismiss()

    def set_popupw(self,pop):
        self.popw=pop

    def set_screen_instance(self,listscreen):
        self.listscreen =listscreen

class ScreenManagement(ScreenManager):
    lesson_dictionary = {}
    pass


class CreatePop(BoxLayout):
    text_lesson_name = StringProperty()

    def __init__(self, **kwargs):
        super(CreatePop, self).__init__(**kwargs)

    def create_lesson(self, *args):
        if hasattr("self","lang_lesson") == False:
            self.lang_lesson = "English"

        data_capture_lessons.create_lesson(self.text_lesson_name,self.lang_lesson)
        self.listscreen.ids.lesson_c.clear_widgets()
        self.listscreen.add_buttons(1)
        self.close_pop()
    def on_select_lang(self,text):
        self.lang_lesson = text
    def close_pop(self, *args):
        self.popw.dismiss()

    def set_screen_instance(self, listscreen):
        self.listscreen = listscreen

    def set_popupw(self, pop):
        self.popw = pop


class DeletePop(Popup):
    lesson_list = ListProperty()

    selected_lesson = StringProperty()
    status_label = StringProperty()

    def __init__(self, **kwargs):
        super(DeletePop, self).__init__(**kwargs)
        lessons = data_capture_lessons.get_Lessons()
        lessonlistdisplay = []
        for element in lessons:
            lesson_display = str(element[0]) + ":" + element[1]
            lessonlistdisplay.append(lesson_display)
        self.lesson_list = lessonlistdisplay

    def on_select_lesson(self, lesson):
        self.selected_lesson = lesson

    def on_delete(self):
        if self.selected_lesson != "Selected Lesson":
            lesson_id = self.selected_lesson.split(":")[0]
            deletion = data_lessons.delete_lesson(lesson_id)
            if deletion == 0:
                self.status_label = "You have deleted the selected lesson"
            else:
                self.status_label = "We could not delete the lesson, try again"
        self.listscreen.ids.lesson_c.clear_widgets()
        self.listscreen.add_buttons(1)

    def set_screen_instance(self, listscreen):
        self.listscreen = listscreen


class LessonTitleScreen(Screen):
    text_label_1 = StringProperty()
    text_label_2 = StringProperty()
    text_image = StringProperty()
    animation_count = NumericProperty()

    def __init__(self, **kwargs):
        super(LessonTitleScreen, self).__init__(**kwargs)
        self.speak_flag = 0
        Window.bind(on_keyboard=self.on_key)

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'title':
                self.manager.current = 'lessons'
                return True

    def read_intro(self, sb_button):
        pass

    def animate(self, dt):
        # create an animation object. This object could be stored
        # and reused each call or reused across different widgets.
        # += is a sequential step, while &= is in parallel
        self.animation_count += 1
        animation = Animation(center_x=self.width / 1.7, t='in_quad')
        animation += Animation(center_x=self.width / 2.3, t='in_quad')
        # animation += Animation(pos=(200, 100), t='out_bounce')
        # animation &= Animation(size=(500, 500))
        # animation += Animation(size=(100, 50))

        # apply the animation on the button, passed in the "instance" argument
        # Notice that default 'click' animation (changing the button
        # color while the mouse is down) is unchanged.
        if self.animation_count == 3:
            animation += Animation(center_x=self.width / 2, t='in_quad')
            animation.start(self.ids.tl_image)
            self.animation_count = 0
            return False

        animation.start(self.ids.tl_image)

    def reset_speak_flag(self, t):
        self.speak_flag = 0

    def on_enter(self):
        self.lessonid = self.manager.get_screen('lessons').selected_lesson
        title, title_image, title_running_notes = data_capture_lessons.get_title_info(self.lessonid)
        if title_running_notes is not None:
            self.text_label_1 = title_running_notes
        if title is not None:
            self.text_label_2 = title
        if title_image is not None:
            #imagepath = "Lessons/Lesson" + str(self.lessonid) + "/images/" + title_image
            imagepath = "Lessons/Lesson" +str(self.lessonid)+ "/images/" + title_image
            if os.path.exists(imagepath) and title_image != "":
                self.text_image = imagepath
            else:
                self.text_image = "placeholder.png"
        else:
            self.text_image = "placeholder.png"
        Clock.schedule_interval(self.animate, 2)


    def set_previous_screen(self):
        if self.manager.current == 'title':
            self.manager.transition.direction = 'right'
            self.manager.current = self.manager.previous()

    def set_next_screen(self):
        if self.manager.current == 'title':
            data_capture_lessons.save_changes(self.lessonid,ntpath.basename(self.text_image),self.text_label_1,self.text_label_2)
            self.manager.transition.direction = 'left'
            self.manager.current = self.manager.next()

    def launch_image_selector(self):
        self.popup_imageselect = ImageSelectPop(self)

        self.popup_imageselect.open()



class ImageSelectPop(Popup):
    search_query = StringProperty()
    def __init__(self,parentscreen,screenindex=100,**kwargs):
        super().__init__(**kwargs)
        self.parentscreen = parentscreen
        self.image_index =screenindex


    def showImages(self):
        print("button pressed" + self.search_query)
        img_util = image_utils.ImageUtils()
        image_urls = img_util.search_images(self.search_query)
        self.ids.imagelist.clear_widgets()
        for image in image_urls:
            box_layout = BoxLayout(orientation='vertical')
            async_image = AsyncImage(source=image, size=(200, 200))
            button_image = Button(text="view", size_hint=(0.4, 0.2), pos_hint={'center_x': .5, 'center_y': .5})
            button_image.on_release = lambda instance=button_image, a=image: self.load_image(instance, a)
            box_layout.add_widget(async_image)
            box_layout.add_widget(button_image)
            self.ids.imagelist.add_widget(box_layout)

    def load_image(self, source, src):
        img_pop = imgpopup()
        img_pop.set_text(src)
        img_pop.set_parentscreen(self.parentscreen,self.image_index, self)
        img_pop.open()
        print("image touched" + src)


    def file_pop(self):
        img_pop = imgurlpopup()

        img_pop.set_parentscreen(self.parentscreen, self.image_index, self)
        img_pop.open()



class imgurlpopup(Popup):
    text_image = StringProperty("placeholder.png")

    def set_parentscreen(self, parent,image_index, pop):
        self.parentscreen = parent
        self.pop = pop
        self.image_index = image_index
    def show_image(self,text):
        self.text_image = text
    def file_resize(self,imagefile):
        import PIL
        size = os.path.getsize(imagefile)
        img = PIL.Image.open(imagefile)

        if size <= 500000:
            return imagefile
        else:
            w, h = img.size
            img = img.resize(w/2,h/2,Image.ANTIALIAS)
            img.save("titletmp")
            self.file_resize("titletmp")

    def save_selected_image(self):
        print(self.text_image)

        if not os.path.exists("Lessons/Lesson" + str(self.parentscreen.lessonid)):
            os.mkdir("Lessons/Lesson" + str(self.parentscreen.lessonid))
            os.mkdir("Lessons/Lesson" + str(self.parentscreen.lessonid) + "/images")
        self.filename_pfix = "Lessons" + os.path.sep + "Lesson" + str(
            self.parentscreen.lessonid) + os.path.sep + "images" + os.path.sep
        filename = ""
        try:

            response = requests.get(self.text_image)
            if response.status_code == 400 or response.status_code==500:
                return "error"
            file = open("titletmp", "wb")
            file.write(response.content)
            file.close()
            file = self.file_resize("titletmp")
        except:
            traceback.print_exc()
            print("Wondersky: Error while downloading Images")
        filetype = imghdr.what("titletmp")
        fname_base = ""
        if self.parentscreen.manager.current == 'title':
            fname_base = "title"
        elif self.parentscreen.manager.current == 'factual':
            fname_base = "term"+str(self.image_index)
        elif self.parentscreen.manager.current == 'apply':
            fname_base = "step" + str(self.image_index)

        if filetype is not None:
            filename = self.filename_pfix + fname_base+"." + filetype
        else:
            filename = self.filename_pfix + fname_base
        shutil.copyfile("titletmp", filename)
        # os.remove("titletmp")

        if self.parentscreen.manager.current == "title":
            self.parentscreen.text_image = filename
            self.parentscreen.ids.tl_image.reload()
        elif self.parentscreen.manager.current =="factual":
            self.parentscreen.text_image_display = filename
            self.parentscreen.ids.display_image.reload()
        elif self.parentscreen.manager.current == "apply":

            if self.image_index == 0:
                self.parentscreen.step_image_0.source = filename
                self.parentscreen.step_image_0.reload()
            elif self.image_index == 1:
                self.parentscreen.step_image_1.source = filename
                self.parentscreen.step_image_1.reload()
            elif self.image_index == 2:
                self.parentscreen.step_image_2.source = filename
                self.parentscreen.step_image_2.reload()
            elif self.image_index == 3:
                self.parentscreen.step_image_3.source = filename
                self.parentscreen.step_image_3.reload()
            elif self.image_index == 4:
                self.parentscreen.step_image_4.source = filename
                self.parentscreen.step_image_4.reload()
            elif self.image_index == 5:
                self.parentscreen.step_image_5.source = filename
                self.parentscreen.step_image_5.reload()
            elif self.image_index == 6:
                self.parentscreen.step_image_6.source = filename
                self.parentscreen.step_image_6.reload()
            elif self.image_index == 7:
                self.parentscreen.step_image_7.source = filename
                self.parentscreen.step_image_7.reload()

        self.dismiss()
        self.pop.dismiss()



class imgpopup(Popup):
    text_image = StringProperty()

    def set_text(self, text_image):
        self.text_image = text_image

    def set_parentscreen(self, parent,image_index, pop):
        self.parentscreen = parent
        self.pop = pop
        self.image_index = image_index

    def file_resize(self, imagefile):
        import PIL
        size = os.path.getsize(imagefile)
        img = PIL.Image.open(imagefile)

        if size <= 500000:
            return imagefile
        else:
            w, h = img.size
            img = img.resize(w / 2, h / 2, Image.ANTIALIAS)
            img.save("titletmp")
            self.file_resize("titletmp")

    def save_selected_image(self):
        print(self.text_image)

        if not os.path.exists("Lessons/Lesson" + str(self.parentscreen.lessonid)):
            os.mkdir("Lessons/Lesson" + str(self.parentscreen.lessonid))
            os.mkdir("Lessons/Lesson" + str(self.parentscreen.lessonid) + "/images")
        self.filename_pfix = "Lessons" + os.path.sep + "Lesson" + str(
            self.parentscreen.lessonid) + os.path.sep + "images" + os.path.sep
        filename = ""
        try:

            response = requests.get(self.text_image)
            if response.status_code == 400 or response.status_code==500:
                return "error"
            file = open("titletmp", "wb")
            file.write(response.content)
            file.close()
            file = self.file_resize("titletmp")
        except:
            traceback.print_exc()
            print("Wondersky: Error while downloading Images")
        filetype = imghdr.what("titletmp")
        fname_base = ""
        if self.parentscreen.manager.current == 'title':
            fname_base = "title"
        elif self.parentscreen.manager.current == 'factual':
            fname_base = "term"+str(self.image_index)
        elif self.parentscreen.manager.current == 'apply':
            fname_base = "step" + str(self.image_index)

        if filetype is not None:
            filename = self.filename_pfix + fname_base+"." + filetype
        else:
            filename = self.filename_pfix + fname_base
        shutil.copyfile("titletmp", filename)
        # os.remove("titletmp")

        if self.parentscreen.manager.current == "title":
            self.parentscreen.text_image = filename
            self.parentscreen.ids.tl_image.reload()
        elif self.parentscreen.manager.current =="factual":
            self.parentscreen.text_image_display = filename
            self.parentscreen.ids.display_image.reload()
        elif self.parentscreen.manager.current == "apply":

            if self.image_index == 0:
                self.parentscreen.step_image_0.source = filename
                self.parentscreen.step_image_0.reload()
            elif self.image_index == 1:
                self.parentscreen.step_image_1.source = filename
                self.parentscreen.step_image_1.reload()
            elif self.image_index == 2:
                self.parentscreen.step_image_2.source = filename
                self.parentscreen.step_image_2.reload()
            elif self.image_index == 3:
                self.parentscreen.step_image_3.source = filename
                self.parentscreen.step_image_3.reload()
            elif self.image_index == 4:
                self.parentscreen.step_image_4.source = filename
                self.parentscreen.step_image_4.reload()
            elif self.image_index == 5:
                self.parentscreen.step_image_5.source = filename
                self.parentscreen.step_image_5.reload()
            elif self.image_index == 6:
                self.parentscreen.step_image_6.source = filename
                self.parentscreen.step_image_6.reload()
            elif self.image_index == 7:
                self.parentscreen.step_image_7.source = filename
                self.parentscreen.step_image_7.reload()

        self.dismiss()
        self.pop.dismiss()
        

class LessonFactualScreen(Screen):
    text_image_1 = StringProperty()
    text_image_2 = StringProperty()
    text_image_3 = StringProperty()
    text_image_display = StringProperty()

    text_term_description_1 = StringProperty()
    text_term_description_2 = StringProperty()
    text_term_description_3 = StringProperty()
    text_term_description = StringProperty()
    text_term_display = StringProperty()

    def __init__(self, **kwargs):
        super(LessonFactualScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)

    def on_enter(self):
        self.lessonid = self.manager.get_screen('lessons').selected_lesson
        self.display_index = 0
        self.draw_Screen()
        self.text_image_display = self.text_image_1
        self.text_term_description = self.text_term_description_1
        self.text_term_display = self.text_term_display_1
    def draw_Screen(self):
        self.textimage_1,  self.textimage_2,  self.textimage_3 = data_capture_lessons.get_fact_images(self.lessonid)
        self.text_term_1,  self.text_term_2,  self.text_term_3 = data_capture_lessons.get_fact_terms(self.lessonid)
        self.textterm_description_1,  self.textterm_description_2,  self.textterm_description_3 = data_capture_lessons.get_fact_descriptions(
            self.lessonid)
        imagepath = "Lessons/Lesson" + str(self.lessonid) + "/images/"
        if  self.textimage_1 is None:
            self.textimage_1 = ""
        if  self.textimage_2 is None:
            self.textimage_2 = ""
        if  self.textimage_3 is None:
            self.textimage_3 = ""
        text_image1 = imagepath +  self.textimage_1
        text_image2 = imagepath +  self.textimage_2
        text_image3 = imagepath +  self.textimage_3

        if  self.textterm_description_1 is not None:
            self.text_term_description_1 =  self.textterm_description_1
        else:
            self.text_term_description_1 = ""
        if  self.textterm_description_2 is not None:
            self.text_term_description_2 =  self.textterm_description_2
        else:
            self.text_term_description_2 = ""
        if  self.textterm_description_3 is not None:
            self.text_term_description_3 =  self.textterm_description_3
        else:
            self.text_term_description_3 = ""
        if  self.text_term_1 is not None:
            self.text_term_display_1 =  self.text_term_1
        else:
            self.text_term_display_1 = ""
        if  self.text_term_2 is not None:
            self.text_term_display_2 =  self.text_term_2
        else:
            self.text_term_display_2 = ""
        if  self.text_term_3 is not None:
            self.text_term_display_3 =  self.text_term_3
        else:
            self.text_term_display_3 = ""

        if not os.path.exists(text_image1) or  self.textimage_1 == "":
            self.text_image_1 = "placeholder.png"
        else:
            self.text_image_1 = text_image1
        if not os.path.exists(text_image2) or  self.textimage_2 == "":
            self.text_image_2 = "placeholder.png"
        else:
            self.text_image_2 = text_image2
        if not os.path.exists(text_image3) or  self.textimage_3 == "":
            self.text_image_3 = "placeholder.png"
        else:
            self.text_image_3 = text_image3



    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'factual':
                self.manager.current = 'title'
                return True



    def load_next(self):

        if self.display_index == 3:
            self.display_index = 0

        if self.display_index == 0:
            data_capture_lessons.update_term1(self.lessonid, os.path.basename(self.text_image_display),
                                              self.text_term_description, self.text_term_display)
            # self.text_image_display = self.text_image_1
            # self.text_term_description = self.text_term_description_1
            # self.text_term_display = self.text_term_display_1
            self.text_image_display = self.text_image_2
            self.text_term_description = self.text_term_description_2
            self.text_term_display = self.text_term_display_2

        elif self.display_index == 1:
            data_capture_lessons.update_term2(self.lessonid, os.path.basename(self.text_image_display),
                                              self.text_term_description,
                                              self.text_term_display)
            # self.text_image_display = self.text_image_2
            # self.text_term_description = self.text_term_description_2
            # self.text_term_display = self.text_term_display_2
            self.text_image_display = self.text_image_3
            self.text_term_description = self.text_term_description_3
            self.text_term_display = self.text_term_display_3

        else:
            data_capture_lessons.update_term3(self.lessonid, os.path.basename(self.text_image_display),
                                              self.text_term_description,
                                              self.text_term_display)
            # self.text_image_display = self.text_image_3
            # self.text_term_description = self.text_term_description_3
            # self.text_term_display = self.text_term_display_3
            self.text_image_display = self.text_image_1
            self.text_term_description = self.text_term_description_1
            self.text_term_display = self.text_term_display_1

        self.draw_Screen()
        self.display_index += 1
    def load_previous(self):

        self.display_index -= 1
        if self.display_index == -1:
            self.display_index = 2

        if self.display_index == 0:
            self.text_image_display = self.text_image_1
            self.text_term_description = self.text_term_description_1
            self.text_term_display = self.text_term_display_1
        elif self.display_index == 1:
            self.text_image_display = self.text_image_2
            self.text_term_description = self.text_term_description_2
            self.text_term_display = self.text_term_display_2
        else:
            self.text_image_display = self.text_image_3
            self.text_term_description = self.text_term_description_3
            self.text_term_display = self.text_term_display_3

    def set_previous_screen(self):
        if self.manager.current == 'factual':
            self.manager.transition.direction = 'right'
            self.manager.current = self.manager.previous()

    def set_next_screen(self):
        if self.manager.current == 'factual':
            self.manager.transition.direction = 'left'
            self.manager.current = self.manager.next()
    def launch_image_selector(self):
        self.popup_imageselect = ImageSelectPop(self,self.display_index)

        self.popup_imageselect.open()

class LessonApplyScreen(Screen):
    text_label_1 = StringProperty("Dynamic Text" + str(random.randint(1, 100)))
    text_label_2 = StringProperty("test.png")
    steps = ObjectProperty(None)
    text_image_0 = StringProperty()
    stepimage0 = ObjectProperty()

    def __init__(self, **kwargs):
        super(LessonApplyScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'apply':
                self.manager.current = 'factual'
                return True

    def on_enter(self):

        self.lessonid = self.manager.get_screen('lessons').selected_lesson
        self.number_of_steps = data_capture_lessons.get_number_of_steps(self.lessonid)
        self.step_list = data_capture_lessons.get_description_list(self.lessonid)
        self.image_list = data_capture_lessons.get_step_image_list(self.lessonid)
        if self.number_of_steps is None:
            self.number_of_steps = 1
        self.add_steps_buttons()

    def set_previous_screen(self):
        if self.manager.current == 'apply':
            self.manager.transition.direction = 'right'
            self.manager.current = self.manager.previous()
    def save_screen(self):
        data_capture_lessons.save_step_texts(self.lessonid,self.text_input_0.text,self.text_input_1.text,self.text_input_2.text,self.text_input_3.text,self.text_input_4.text,self.text_input_5.text,
                                             self.text_input_6.text,self.text_input_7.text)
        data_capture_lessons.save_step_images(self.lessonid,ntpath.basename(self.step_image_0.source),ntpath.basename(self.step_image_1.source),ntpath.basename(self.step_image_2.source),
                                             ntpath.basename(self.step_image_3.source),ntpath.basename(self.step_image_4.source),ntpath.basename(self.step_image_5.source),
                                             ntpath.basename(self.step_image_6.source), ntpath.basename(self.step_image_7.source))

    def set_next_screen(self):
        if self.manager.current == 'apply':
            self.save_screen()
            self.manager.transition.direction = 'left'
            self.manager.current = self.manager.next()

    def add_steps_buttons(self):
        self.steps.clear_widgets()
        self.ids.steps.bind(minimum_height=self.ids.steps.setter('height'))
        imagepath = "Lessons/Lesson" + str(self.lessonid) + "/images/"
        for i in range(8):
            text = self.step_list[i]
            if text is None:
                text = ""
            self.bx_layout = BoxLayout(spacing = [20,10])
            if i == 0:
                self.text_input_0 = TextInput(text=text, height="60sp", size_hint=(0.5, None)
                                       , text_size=(3.5 * Metrics.dpi, None),
                                       font_size='18sp',pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.text_input_0)
            elif i == 1:
                self.text_input_1 = TextInput(text=text, height="60sp", size_hint=(0.5, None)
                                       , text_size=(3.5 * Metrics.dpi, None),
                                       font_size='18sp',pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.text_input_1)
            elif i == 2:
                self.text_input_2 = TextInput(text=text, height="60sp", size_hint=(0.5, None)
                                       , text_size=(3.5 * Metrics.dpi, None),
                                       font_size='18sp',pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.text_input_2)
            elif i == 3:
                self.text_input_3 = TextInput(text=text, height="60sp", size_hint=(0.5, None)
                                       , text_size=(3.5 * Metrics.dpi, None),
                                       font_size='18sp',pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.text_input_3)
            elif i == 4:
                self.text_input_4 = TextInput(text=text, height="60sp", size_hint=(0.5, None)
                                       , text_size=(3.5 * Metrics.dpi, None),
                                       font_size='18sp',pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.text_input_4)
            elif i == 5:
                self.text_input_5 = TextInput(text=text, height="60sp", size_hint=(0.5, None)
                                       , text_size=(3.5 * Metrics.dpi, None),
                                       font_size='18sp',pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.text_input_5)
            elif i == 6:
                self.text_input_6 = TextInput(text=text, height="60sp", size_hint=(0.5, None)
                                       , text_size=(3.5 * Metrics.dpi, None),
                                       font_size='18sp',pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.text_input_6)
            elif i == 7:
                self.text_input_7 = TextInput(text=text, height="60sp", size_hint=(0.5, None)
                                       , text_size=(3.5 * Metrics.dpi, None),
                                       font_size='18sp',pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.text_input_7)

            image_button = Button(text="Image",size_hint = (0.1,0.2),pos_hint={'center_y':0.5})
            image_button.on_release=lambda instance = image_button,a=i:self.image_select(instance,a)


            self.bx_layout.add_widget(image_button)

            if i == 0 :
                if self.image_list[i] == "placeholder.png" or self.image_list[i] is None or self.image_list[i] == "":
                    self.text_image_0 = "placeholder.png"
                else:
                    self.text_image_0 = imagepath + self.image_list[i]
                self.step_image_0 = Image(source=self.text_image_0, size=(60, 60),size_hint=(0.2,None),pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.step_image_0)
            elif i == 1 :
                if self.image_list[i] == "placeholder.png" or self.image_list[i] is None or self.image_list[i] == "":
                    self.text_image_1 = "placeholder.png"
                else:
                    self.text_image_1 = imagepath + self.image_list[i]
                self.step_image_1 = Image(source=self.text_image_1,  size=(60, 60),size_hint=(0.2,None),pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.step_image_1)
            elif i == 2:
                if self.image_list[i] == "placeholder.png" or self.image_list[i] is None or self.image_list[i] == "":
                    self.text_image_2 = "placeholder.png"
                else:
                    self.text_image_2 = imagepath + self.image_list[i]
                self.step_image_2 = Image(source=self.text_image_2, size=(60, 60),size_hint=(0.2,None),pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.step_image_2)
            elif i == 3:
                if self.image_list[i] == "placeholder.png" or self.image_list[i] is None or self.image_list[i] == "":
                    self.text_image_3 = "placeholder.png"
                else:
                    self.text_image_3 = imagepath + self.image_list[i]
                self.step_image_3 = Image(source=self.text_image_3, size=(60, 60),size_hint=(0.2,None),pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.step_image_3)
            elif i == 4:
                if self.image_list[i] == "placeholder.png" or self.image_list[i] is None or self.image_list[i] == "":
                    self.text_image_4 = "placeholder.png"
                else:
                    self.text_image_4 = imagepath + self.image_list[i]
                self.step_image_4 = Image(source=self.text_image_4, size=(60, 60),size_hint=(0.2,None),pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.step_image_4)
            elif i == 5:
                if self.image_list[i] == "placeholder.png" or self.image_list[i] is None or self.image_list[i] == "":
                    self.text_image_5 = "placeholder.png"
                else:
                    self.text_image_5 = imagepath + self.image_list[i]
                self.step_image_5 = Image(source=self.text_image_5, size=(60, 60),size_hint=(0.2,None),pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.step_image_5)
            elif i == 6:
                if self.image_list[i] == "placeholder.png" or self.image_list[i] is None or self.image_list[i] == "":
                    self.text_image_6 = "placeholder.png"
                else:
                    self.text_image_6 = imagepath + self.image_list[i]
                self.step_image_6  = Image(source=self.text_image_6, size=(60, 60),size_hint=(0.2,None),pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.step_image_6)
            elif i == 7:
                if self.image_list[i] == "placeholder.png" or self.image_list[i] is None or self.image_list[i] == "":
                    self.text_image_7 = "placeholder.png"
                else:
                    self.text_image_7 = imagepath + self.image_list[i]
                self.step_image_7 = Image(source=self.text_image_7, size=(60, 60),size_hint=(0.2,None),pos_hint={'center_y':0.5})
                self.bx_layout.add_widget(self.step_image_7)


           # button.on_release = lambda instance=button, a=i: self.add_image(instance, a)
            self.steps.add_widget(self.bx_layout)

    def image_select(self,instance,display_index,*args):
        self.popup_imageselect = ImageSelectPop(self,display_index)
        self.popup_imageselect.open()



class CWidget(Widget):
    pencolor = ListProperty([0, 1, 1, 1])
    line_width = 3
    text_button = StringProperty()
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.text_button = "erase"
        self.start_flag = False

    def show_text(self,*args):
        self.tlabel = Label(text=self.input_text.text,pos=self.location,font_size='35sp',color=[1,0,0,0.9])
        self.add_widget(self.tlabel)

        self.popup.dismiss()
    def on_touch_down(self, touch):

        if touch.is_double_tap:
            print("double tap")
            self.location = (touch.x,touch.y)
            self.blayout = BoxLayout()
            self.input_text = TextInput()
            self.input_button = Button(text="Add Text",on_release=self.show_text)
            self.blayout.add_widget(self.input_text)
            self.blayout.add_widget(self.input_button)

            self.popup = Popup(
                title='Enter Text',
                content = self.blayout,
                size_hint=(1, 0.2), auto_dismiss=False
            )
            self.popup.open()
        with self.canvas:
            Color(rgba = self.pencolor)
            self.start_flag= True
            touch.ud['line'] = Line(points=(touch.x, touch.y),width=self.line_width)

            #d = 70
            #Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
    def erase(self):
        self.pencolor = [0,0,0,1]
        self.line_width = 15
    def pen(self):
        self.pencolor = [0,1,1,1]
        self.line_width = 3
    def clear(self):
        self.canvas.clear()
        print("clear")

    def on_touch_move(self, touch):
        if hasattr(touch, "ud") and self.start_flag:
            touch.ud['line'].points += [touch.x, touch.y]

class LessonWhiteboardScreen(Screen):
    def __init__(self,**kwargs):
        super(LessonWhiteboardScreen,self).__init__(**kwargs)


    def save_canvas(self,sv):
        self.lessonid = self.manager.get_screen('lessons').selected_lesson
        self.filename_pfix = "Lessons" + os.path.sep + "Lesson" + str(
                     self.lessonid) + os.path.sep + "images" + os.path.sep
        sv.export_to_png(self.filename_pfix+"whiteboard.png")
        data_capture_lessons.save_whiteboard_image(self.lessonid,"whiteboard.png")



    def set_next_screen(self):
        if self.manager.current == 'whiteboard':

            self.manager.transition.direction = 'left'
            self.manager.current = self.manager.next()

    def set_previous_screen(self):
        if self.manager.current == 'whiteboard':
            self.manager.transition.direction = 'right'
            self.manager.current = self.manager.previous()





class LessonNotesScreen(Screen):
    text_label_1 = StringProperty()


    def __init__(self, **kwargs):
        super(LessonNotesScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'notes':
                self.manager.current = 'apply'
                return True

    def on_enter(self):
        self.lessonid = self.manager.get_screen('lessons').selected_lesson
        txt_notes = data_capture_lessons.get_notes(self.lessonid)
        if (txt_notes is None):
            self.text_label_1 = ""
        else:
            self.text_label_1 = txt_notes

    def on_save(self):
        ret = data_capture_lessons.save_notes(self.lessonid, self.text_label_1)
        print(self.text_label_1)
        print(str(ret))
    def set_next_screen(self):
        self.on_save()
        if self.manager.current == 'notes':
            self.manager.transition.direction = 'left'
            self.manager.current = 'assess'

    def set_previous_screen(self):
        if self.manager.current == 'notes':
            self.manager.transition.direction = 'left'
            self.manager.current = 'whiteboard'

class PublishPop(Popup):
    text_status = StringProperty()
    text_user = StringProperty()
    text_pwd = StringProperty()

    def set_screen_instance(self, parentscreen):
        self.parentscreen = parentscreen
    def publish_lesson(self):
        self.logintoken = self.get_token(self.text_user, self.text_pwd)
        data = data_lessons.prepare_lesson_share(self.parentscreen.lessonid)
        data_lessons.post_lesson(data, self.logintoken, self.parentscreen.lessonid)
    def get_token(self, user, pwd):
        logintoken = data_lessons.get_token(user, pwd)
        return logintoken


class LessonAssessScreen(Screen):
    text_label_1 = StringProperty()
    text_label_2 = StringProperty()


    def __init__(self, **kwargs):
        super(LessonAssessScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'assess':
                self.manager.current = 'notes'
                return True

    def publish_lesson(self):
        self.on_save()
        self.popup_publish = PublishPop()
        self.popup_publish.set_screen_instance(self)

        self.popup_publish.open()




    def on_enter(self):
        self.lessonid = self.manager.get_screen('lessons').selected_lesson
        txt_questions, txt_answers = data_capture_lessons.get_questions_answer(self.lessonid)
        if (txt_questions is None):
            self.text_label_1 = ""
        else:
            self.text_label_1 = txt_questions
        txt_form = data_capture_lessons.get_formlink(self.lessonid)
        if (txt_form is None):
            self.text_label_2 = ""
        else:
            self.text_label_2 = txt_form

    def on_save(self):
        ret = data_capture_lessons.set_questions(self.lessonid, self.text_label_1)
        ret = data_capture_lessons.set_form_link(self.lessonid, self.text_label_2)
        print(self.text_label_1)
        print(str(ret))

    def set_next_screen(self):
        self.on_save()
        if self.manager.current == 'assess':
            self.manager.transition.direction = 'left'
            self.manager.current = 'lessons'

    def set_previous_screen(self):
        if self.manager.current == 'assess':
            self.manager.transition.direction = 'left'
            self.manager.current = 'notes'


class MagicTeacherApp(App):

    def build(self):
        # self.icon = 'lr_logo.png'
        return ScreenManagement()


MagicTeacherApp().run()

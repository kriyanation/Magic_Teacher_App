import imghdr
import ntpath
import os
import shutil

import traceback
import random

from kivy.metrics import Metrics
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from plyer import filechooser
from kivy.utils import platform

import requests
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage, Image
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen


import data_capture_lessons
import data_lessons
import image_utils
import certifi

# Here's all the magic !
os.environ['SSL_CERT_FILE'] = certifi.where()


class LessonListScreen(Screen):
    container = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LessonListScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)

        print("Hello")
        Clock.schedule_once(self.add_buttons, 1)

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'lessons':
                return False

    def add_buttons(self, dt):
        self.list_lessons = data_capture_lessons.get_Lessons()
        self.container.bind(minimum_height=self.container.setter('height'))
        for element in self.list_lessons:
            button = Button(text=element[1], background_color=[0.76, 0.83, 0.86, 0.8], pos_hint={'top': 1},
                            size_hint_y=None, size_hint_x=1)
            button.on_release = lambda instance=button, a=element[0]: self.switch_to_title(instance, a)
            self.container.add_widget(button)

    def switch_to_title(self, i, a):
        self.selected_lesson = a
        self.manager.current = "title"

    def launch_popup(self):
        show = CreatePop()
        self.popupWindow = Popup(title="Create Mini Lesson", content=show,
                                 size_hint=(1, 0.4), auto_dismiss=False)
        show.set_popupw(self.popupWindow)
        show.set_screen_instance(self)
        # open popup window
        self.popupWindow.open()

    def launch_del_popup(self):
        self.popup_delete = DeletePop()
        self.popup_delete.set_screen_instance(self)

        self.popup_delete.open()


class ScreenManagement(ScreenManager):
    lesson_dictionary = {}
    pass


class CreatePop(BoxLayout):
    text_lesson_name = StringProperty()

    def __init__(self, **kwargs):
        super(CreatePop, self).__init__(**kwargs)

    def create_lesson(self, *args):
        data_capture_lessons.create_lesson(self.text_lesson_name)
        self.listscreen.container.clear_widgets()
        self.listscreen.add_buttons(1)
        self.close_pop()

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
        self.listscreen.container.clear_widgets()
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
            imagepath = "Lessons/Lesson5" + "/images/" + "title.jpeg"
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

    def handle_selection(self,selection):
        print(selection)
        self.filename_pfix = "Lessons" + os.path.sep + "Lesson" + str(
                     self.parentscreen.lessonid) + os.path.sep + "images" + os.path.sep
        if len(selection) >0:
            split_filename = selection[0].split(".")
            extension = split_filename[-1]
            if ((extension is not None) and (extension.lower() == "png" or extension.lower() == "jpg" or extension.lower() =="gif")):
                shutil.copyfile(selection[0], self.filename_pfix + "title." + extension)
            elif extension is not None:
                print("Only Image files allowed")
                return
            else:
                extension = ""
                return
        else:
            return
        fname_base = ""
        if self.parentscreen.manager.current == 'title':
            fname_base = "title"
        elif self.parentscreen.manager.current == 'factual':
            fname_base = "term" + str(self.image_index)

        if self.parentscreen.manager.current == 'title':
                self.parentscreen.text_image = self.filename_pfix + fname_base+"."+extension
        elif self.parentscreen.manager.current == 'factual':
                self.parentscreen.text_image_display = self.filename_pfix + fname_base+"."+extension
        self.dismiss()



    def file_pop(self):
        filechooser.open_file(on_selection=self.handle_selection)


class imgpopup(Popup):
    text_image = StringProperty()

    def set_text(self, text_image):
        self.text_image = text_image

    def set_parentscreen(self, parent,image_index, pop):
        self.parentscreen = parent
        self.pop = pop
        self.image_index = image_index

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
        except:
            traceback.print_exc()
            print("Wondersky: Error while downloading Images")
        filetype = imghdr.what("titletmp")
        fname_base = ""
        if self.parentscreen.manager.current == 'title':
            fname_base = "title"
        elif self.parentscreen.manager.current == 'factual':
            fname_base = "term"+str(self.image_index)

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

    def set_next_screen(self):
        if self.manager.current == 'apply':
            self.manager.transition.direction = 'left'
            self.manager.current = self.manager.next()

    def add_steps_buttons(self):

        self.text_list = []
        self.steps.clear_widgets()
        #        self.images.clear_widgets()
        imagepath = "Lessons/Lesson" + str(self.lessonid) + "/images/"
        for i in range(8):
            text = self.step_list[i]
            if text is None:
                text = ""
            bx_layout = BoxLayout(spacing = [10,10])
            text_input = TextInput(text=text, height="70sp",size_hint = (0.8,None)
                            ,text_size=(3.5 * Metrics.dpi, None),
                            font_size='18sp')
            image_button = Button(text="Image",height="40sp",size_hint = (0.1,None))
            if self.image_list[i] is not None:
                text_image = imagepath + self.image_list[i]
            else:
                text_image = "placeholder.png"
            step_image = Image(source=text_image,size=(100,50),size_hint = (0.2,None))

            bx_layout.add_widget(text_input)
            bx_layout.add_widget(image_button)
            bx_layout.add_widget(step_image)

            self.text_list.append(text_input)
           # button.on_release = lambda instance=button, a=i: self.add_image(instance, a)
            self.steps.add_widget(bx_layout)



    def add_image(self, instance, a, *args):
        print(a)
        print(instance)
        if a < self.number_of_steps - 1:
            button = self.button_list[a + 1]
            button.disabled = False
        imagepath = "Lessons/Lesson" + str(self.lessonid) + "/images/"
        if (self.image_list[a] != None and self.image_list[a].strip() != ""):
            # image = Image(source=imagepath+self.image_list[a],size_hint_y=None,size=(400,400))
            # self.images.add_widget(image)

            self.text_image = imagepath + self.image_list[a]
            text_no_image = ""
        else:
            self.text_image = "trans.png"
            text_no_image = "No Image Associated with this step"
        img_pop = imgpopup()
        img_pop.set_text(self.text_image, self.step_list[a], text_no_image)
        img_pop.open()




class LessonWhiteboardScreen(Screen):
    pass


class LessonNotesScreen(Screen):
    pass


class LessonAssessScreen(Screen):
    pass


class MagicTeacherApp(App):

    def build(self):
        # self.icon = 'lr_logo.png'
        return ScreenManagement()


MagicTeacherApp().run()

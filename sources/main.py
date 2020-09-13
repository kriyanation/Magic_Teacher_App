import imghdr
import os
import shutil
import time
import traceback
from kivy.utils import platform

import requests
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
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
        Clock.schedule_interval(self.show_image_added, 10)
    def show_image_added(self,dt):
        print(self.text_image)
    def set_previous_screen(self):
        if self.manager.current == 'title':
            self.manager.transition.direction = 'right'
            self.manager.current = self.manager.previous()

    def set_next_screen(self):
        if self.manager.current == 'title':
            self.manager.transition.direction = 'left'
            self.manager.current = self.manager.next()

    def launch_image_selector(self):
        self.popup_imageselect = ImageSelectPop()
        self.popup_imageselect.set_screen_instance(self)
        self.popup_imageselect.open()



class ImageSelectPop(Popup):
    search_query = StringProperty()

    def showImages(self):
        print("button pressed" + self.search_query)
        img_util = image_utils.ImageUtils()
        image_urls = img_util.search_images(self.search_query)

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
        img_pop.set_parentscreen(self.titlescreen, self)
        img_pop.open()
        print("image touched" + src)

    def set_screen_instance(self, titlescreen):
        self.titlescreen = titlescreen

    def cam_pop(self):
        cam_pop = campopup()
        cam_pop.open()
        print("cam opened")

    def file_pop(self):
        file_pop = filepopup()
        file_pop.open()
        print("file opened")


class filepopup(Popup):
    def select(self, *args):
        print(args)
        if len(args[1]) > 0:
            print(args[1])
            self.dismiss()


class campopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._request_android_permissions()
    def capture(self):
        '''
        Function to capture the images and give them the names
        according to their captured time and date.
        '''
        camera = self.ids['camera']
        timestr = time.strftime("%Y%m%d_%H%M%S")
        camera.export_to_png("IMG_{}.png".format(timestr))
        print("Captured")

    @staticmethod
    def is_android():
        return platform == 'android'

    def _request_android_permissions(self):
        """
        Requests CAMERA permission on Android.
        """

        if not self.is_android():
            return
        from android.permissions import request_permission, Permission
        request_permission(Permission.CAMERA)


class imgpopup(Popup):
    text_image = StringProperty()

    def set_text(self, text_image):
        self.text_image = text_image

    def set_parentscreen(self, parent, pop):
        self.parentscreen = parent
        self.pop = pop

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
        if filetype is not None:
            filename = self.filename_pfix + "title." + filetype
        else:
            filename = self.filename_pfix + "title"
        shutil.copyfile("titletmp", filename)
        # os.remove("titletmp")
        if filetype is not None:
            self.parentscreen.manager.lesson_dictionary['title_image'] = "title." + filetype
        else:
            self.parentscreen.manager.lesson_dictionary['title_image'] = "title"

        self.parentscreen.text_image = self.filename_pfix + self.parentscreen.manager.lesson_dictionary['title_image']
        self.parentscreen.ids.tl_image.reload()
        self.dismiss()
        self.pop.dismiss()

class LessonFactualScreen(Screen):
    pass


class LessonApplyScreen(Screen):
    pass


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

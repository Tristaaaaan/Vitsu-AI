from kivy.metrics import dp
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy import platform
from os.path import dirname, join
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from docx import Document
from datetime import datetime
from kivy.clock import mainthread
from textwrap import fill
from kivy.uix.scrollview import ScrollView
from deep_translator import GoogleTranslator
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.dialog import MDDialog
from user_database import Database
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.snackbar import Snackbar
from kivy.core.window import Window

db = Database()

Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
Window.softinput_mode = "below_target"

if platform == "android":
    from speech_events import SpeechEvents
    from androidstorage4kivy import SharedStorage
    from jnius import autoclass
    from android.permissions import request_permissions, Permission

    # Define the required permissions
    request_permissions([
        Permission.RECORD_AUDIO,
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.READ_EXTERNAL_STORAGE,
        Permission.INTERNET
    ])

    # Environment
    Environment = autoclass('android.os.Environment')


class ClickableTextField(MDRelativeLayout):
    password = StringProperty()


class CreatePasswordClickableTextField(MDRelativeLayout):
    create_password = StringProperty()


class ConfirmPasswordClickableTextField(MDRelativeLayout):
    confirmpassword = StringProperty()


class FirstWindow(Screen):

    Builder.load_file('firstwindow.kv')

    def login(self):

        # If input(s) are incomplete
        if self.ids.username.text or self.ids.password.passw.text:
            # If username exists
            if db.locateUsername(self.ids.username.text) is True:
                # If password is correct
                if db.locateAcc(self.ids.username.text,
                                self.ids.password.passw.text) is True:
                    self.clear()
                    self.manager.current = "third"
                    self.manager.transition.direction = "left"
                else:
                    self.error_dialog(message="The password is incorrect.")
                    self.ids.password.passw.text = ''
            else:
                self.error_dialog(
                    message="Sorry, we couldn't find an account with that username.")
                self.ids.password.passw.text = ''
        else:
            self.error_dialog(
                message="Make sure that username and password are not empty.")

    def clear(self):
        self.ids.username.text = ''
        self.ids.password.passw.text = ''

    def error_dialog(self, message):

        close_button = MDFlatButton(
            text='CLOSE',
            text_color=[0, 0, 0, 1],
            on_release=self.close_dialog,
        )
        self.dialog = MDDialog(
            title='[color=#FF0000]Ooops![/color]',
            text=message,
            buttons=[close_button],
        )
        self.dialog.open()

    # Close Dialog
    def close_dialog(self, obj):
        self.dialog.dismiss()


class SecondWindow(Screen):

    Builder.load_file('secondwindow.kv')

    def signUp(self):
        username = self.ids.create_username.text
        create_password = self.ids.create_password.create_passw.text
        confirm_password = self.ids.confirm_password.confirm_passw.text

        # If input(s) are incomplete
        if (username or create_password or confirm_password) and (create_password or confirm_password) and username:
            # If username exists
            if db.locateUsername(username) is False:
                # If passwords matched
                if create_password == confirm_password:
                    db.storeAcc(username, create_password)
                    self.ids.create_username.text = ''
                    self.ids.create_password.create_passw.text = ''
                    self.ids.confirm_password.confirm_passw.text = ''
                    self.manager.current = "first"
                    self.manager.transition.direction = "right"
                else:
                    self.error_dialog(message="The password does not match.")
                    self.ids.create_password.create_passw.text = ''
                    self.ids.confirm_password.confirm_passw.text = ''
            else:
                self.error_dialog(
                    message="The username you entered is already in used.")
                self.ids.create_password.create_passw.text = ''
                self.ids.confirm_password.confirm_passw.text = ''
        else:
            self.error_dialog(
                message="Make sure to fill up all the required information to proceed.")

    def clear(self):
        self.ids.create_username.text = ''
        self.ids.create_password.create_passw.text = ''
        self.ids.confirm_password.confirm_passw.text = ''

    def error_dialog(self, message):

        close_button = MDFlatButton(
            text='CLOSE',
            text_color=[0, 0, 0, 1],
            on_release=self.close_dialog,
        )
        self.dialog = MDDialog(
            title='[color=#FF0000]Ooops![/color]',
            text=message,
            buttons=[close_button],
        )
        self.dialog.open()

    # Close Dialog
    def close_dialog(self, obj):
        self.dialog.dismiss()


class ThirdWindow(Screen):

    Builder.load_file('thirdwindow.kv')

    def start_recording(self):

        if self.ids.recording_status.text == 'Record':
            self.ids.recording_status.text = 'Stop Recording'
            self.ids.output.text = ''

            self.unwrapped = ''

            self.ids.output.text += "\nThe recording has started, you may speak now."

            self.speech_events = SpeechEvents()

            self.speech_events.create_recognizer(self.recognizer_event_handler)

            if self.speech_events:

                self.unwrapped = ''

                self.speech_events.start_listening()

        else:

            self.ids.output.text += "\n\nThe recording has stopped."

            self.ids.recording_status.text = 'Record'

            self.speech_events.stop_listening()

            recognized_text = self.unwrapped

            translate_text = GoogleTranslator(
                source='auto', target='en').translate(recognized_text)

            self.config_length(translate_text)

    def config_length(self, translated_output):
        self.task_list_dialog = MDDialog(
            title="Results",
            type="custom",
            size_hint_x=0.9,
            size_hint_y=None,
            auto_dismiss=False,
            content_cls=DialogContent(translated_output=translated_output),
        )

        self.task_list_dialog.open()

    def close_dialog(self, *args):
        self.task_list_dialog.dismiss()

    @mainthread
    def recognizer_event_handler(self, key, value):
        if key == 'onReadyForSpeech':
            self.ids.output.text += '\n\nStatus: Listening.'
        elif key == 'onBeginningOfSpeech':
            self.ids.output.text += '\n\nStatus: Speaker Detected.'
        elif key == 'onEndOfSpeech':
            self.ids.output.text += '\n\nStatus: Not Listening.'
        elif key == 'onError':
            self.ids.output.text += '\n\nStatus: ' + value + ' Not Listening.'
        elif key in ['onPartialResults', 'onResults']:
            self.unwrapped = str(value)
            # self.ids.output.text += fill(value, 40)
        elif key in ['onBufferReceived', 'onEvent', 'onRmsChanged']:
            pass


class DialogContent(MDBoxLayout):

    translated_output = StringProperty()

    """Customize dialog box for user to insert their expenses"""
    # Initiliaze date to the current date

    def cancel(self):

        #self.saved_successfully()

        MDApp.get_running_app().root.third.close_dialog()

        MDApp.get_running_app().root.third.ids.output.text = ''

    def save_to_word_document(self):

        # Generate a unique filename with timestamp
        current_datetime = datetime.now()
        timestamp = current_datetime.strftime(
            "%Y%m%d%H%M%S")  # YearMonthDayHourMinuteSecond

        ss = SharedStorage()

        document = Document()
        document.add_paragraph(self.ids.final_output.text)
        document_file = f"Vitsu-AI-{timestamp}.docx"
        document.save(document_file)

        # Get the path to the DCIM camera directory
        save_path = Environment.getExternalStoragePublicDirectory(
            Environment.DIRECTORY_DOCUMENTS).getAbsolutePath()

        ss.copy_to_shared(document_file, save_path)

        self.cancel()

        #MDApp.get_running_app().root.third.ids.output.text += f"\n\nFile '{document_file}' saved successfully!"

    def saved_successfully(self):
        snackbar = Snackbar(
            text="The text has been saved."
        )
        snackbar.open()


class WindowManager(ScreenManager):
    pass


class rawApp(MDApp):

    def build(self):

        return WindowManager()


if __name__ == '__main__':
    rawApp().run()

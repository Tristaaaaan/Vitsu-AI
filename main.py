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
from kivy.core.window import Window

import json

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

                    # Specify the JSON file path
                    json_file_path = 'login_cred.json'

                    # Load existing data from the JSON file
                    with open(json_file_path, 'r') as file:
                        data = json.load(file)

                    user = data['user']

                    user.update({
                        'username': self.ids.username.text})

                    # Save the updated data back to the JSON file
                    with open(json_file_path, 'w') as file:
                        json.dump(data, file, indent=2)

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
    translated_text = StringProperty()
    unwrapped = StringProperty()
    
    def remove_translated(self):
        self.translated_text = ''
        
    def back_to_main(self):
        self.manager.current = "first"
        self.manager.transition.direction = "right"

    def view_profile(self):

        # Specify the JSON file path
        json_file_path = 'login_cred.json'

        # Load existing data from the JSON file
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        # Access the "username" value directly
        username = data['user'].get('username')

        self.profile(username)

    def profile(self, current_user):
        self.profile_view = MDDialog(
            title="Profile",
            type="custom",
            size_hint_x=0.9,
            size_hint_y=None,
            auto_dismiss=False,
            content_cls=ProfileDialog(current_username=current_user),
        )

        self.profile_view.open()

    def close_profile_dialog(self, *args):
        self.profile_view.dismiss()

        
    def start_recording(self):

        
        if self.ids.recording_status.text == 'Record':
        
            self.ids.recording_status.text = 'Stop Recording'
            self.ids.output.text = ''


            self.ids.output.text += "\nThe recording has started, you may speak now."
            self.ids.recording_background.md_bg_color = [
                239/255, 153/255, 117/255, 1]

            self.ids.recording_status.text_color = 'white'
           
            self.speech_events = SpeechEvents()

            self.speech_events.create_recognizer(self.recognizer_event_handler)   
                     
            if self.speech_events:

                self.unwrapped = ''

                self.speech_events.start_listening()   
                
        else:
            self.speech_events.stop_listening()
            
            self.speech_events.destroy_recognizer()
            
            self.ids.output.text += "\n\nThe recording has stopped."

            self.ids.recording_status.text = 'Record'

            self.ids.recording_background.md_bg_color = 'white'

            self.ids.recording_status.text_color = 'black'


            recognized_text = self.unwrapped

            translate_text = GoogleTranslator(
                source='auto', target='en').translate(recognized_text)
                
            if translate_text == '':
                self.ids.output.text += f"\n\nThe system cannot understand what you are saying. Kindly try again."
            
            else:
                self.ids.output.text += f"\n\nTranslated Text:\n\n{translate_text}"
                
                self.translated_text = translate_text
                           
    @mainthread
    def recognizer_event_handler(self, key, value):
        if key == 'onReadyForSpeech':
            self.ids.output.text += '\n\nStatus: Listening.'
        elif key == 'onBeginningOfSpeech':
            self.ids.output.text += '\n\nStatus: Speaker Detected.'
        elif key == 'onEndOfSpeech':
            self.ids.output.text += '\n\nStatus: Not Listening.'
        elif key == 'onError':
            self.ids.output.text += '\n\nStatus: Currently, the Speech Recognizer is encountering an error kindly wait a little bit.'
            self.speech_events.stop_listening()
            self.speech_events.destroy_recognizer()
            self.ids.recording_status.text = 'Record'
            self.ids.recording_background.md_bg_color = 'white'
            self.ids.recording_status.text_color = 'black'
            self.start_recording()
            
        elif key in ['onPartialResults', 'onResults']:
            self.unwrapped = str(value)
        elif key in ['onBufferReceived', 'onEvent', 'onRmsChanged']:
            pass

    def view_dashboard(self):

        if self.translated_text == '':
            self.error_dialog(
                message="Sorry, we couldn't find any translated text.")
        else:
            self.dashboard_view = MDDialog(
                title="Results",
                type="custom",
                size_hint_x=0.9,
                size_hint_y=None,
                auto_dismiss=False,
                content_cls=DialogContent(
                    translated_output=self.translated_text),
            )

            self.dashboard_view.open()

    def close_dialog(self, *args):
        self.dashboard_view.dismiss()

    def error_dialog(self, message):

        close_button = MDFlatButton(
            text='CLOSE',
            text_color=[0, 0, 0, 1],
            on_release=self.close_error_ask_dialog,
        )
        self.error_ask = MDDialog(
            title='[color=#FF0000]Ooops![/color]',
            text=message,
            auto_dismiss=False,
            buttons=[close_button],
        )
        self.error_ask.open()

    # Close Dialog
    def close_error_ask_dialog(self, obj):
        self.error_ask.dismiss()



class DialogContent(MDBoxLayout):

    translated_output = StringProperty()

    """Customize dialog box for user to insert their expenses"""
    # Initiliaze date to the current date

    def cancel(self):

        MDApp.get_running_app().root.third.close_dialog()

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
        
        MDApp.get_running_app().root.third.ids.output.text += f"\n\nFile '{document_file}' saved successfully!"
        
    def refresh(self):
    
        MDApp.get_running_app().root.third.ids.output.text = ''
        
        self.ids.final_output.text = '' 
        
        # Clearing translated_text in ThirdWindow
        setattr(MDApp.get_running_app().root.third, 'translated_text', '')
        
        self.cancel()
        
class ProfileDialog(MDBoxLayout):

    current_username = StringProperty()

    """Customize dialog box for user to insert their expenses"""
    # Initiliaze date to the current date

    def cancel(self):


        MDApp.get_running_app().root.third.close_profile_dialog()


    def logout(self):

        MDApp.get_running_app().root.third.back_to_main()

        # Specify the JSON file path
        json_file_path = 'login_cred.json'

        # Load existing data from the JSON file
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        user = data['user']

        user.update({
            'username': ''})

        # Save the updated data back to the JSON file
        with open(json_file_path, 'w') as file:
            json.dump(data, file, indent=2)

        MDApp.get_running_app().root.third.ids.output.text = ''
        
        self.cancel()


class LoadingScreen(Screen):

    Builder.load_file('loadingscreen.kv')

    def on_enter(self, *args):

        Clock.schedule_once(self.switch_screen, 5)

    def switch_screen(self, dt):

        # Specify the JSON file path
        json_file_path = 'login_cred.json'

        # Load existing data from the JSON file
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        user = data['user']

        # Check if the username is an empty string
        if user.get('username', '') == '':
            # If the username is an empty string, update it

            self.manager.current = 'first'
        else:
            self.manager.current = 'third'


class WindowManager(ScreenManager):
    pass


class rawApp(MDApp):

    def build(self):

        return WindowManager()


if __name__ == '__main__':
    rawApp().run()

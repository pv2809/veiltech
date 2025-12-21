from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.clock import Clock
import os

class VeilTechApp(App):
    def build(self):
        self.secret_message = ""
        self.unlock_attempts = 0
        self.max_attempts = 5
        self.timer = None
        self.selected_file = None
        self.file_size_limit = 5 * 1024 * 1024  # 5 MB for demo

        main_layout = BoxLayout(orientation='horizontal', padding=20, spacing=20)

        # ------------------ Sender Section ------------------
        sender_layout = BoxLayout(orientation='vertical', spacing=10)
        sender_layout.add_widget(Label(text="Sender", font_size=24))

        # File chooser simulation
        self.filechooser = FileChooserListView(path=os.getcwd(), size_hint=(1, 0.4))
        self.filechooser.bind(selection=self.on_file_select)
        sender_layout.add_widget(self.filechooser)

        sender_layout.add_widget(Label(text="Enter Secret Message:"))
        self.sender_input = TextInput(multiline=True, size_hint=(1, 0.2))
        sender_layout.add_widget(self.sender_input)

        send_btn = Button(text="Send Message", size_hint=(1, 0.2))
        send_btn.bind(on_press=self.send_message)
        sender_layout.add_widget(send_btn)

        self.sender_status = Label(text="Status: Waiting to send")
        sender_layout.add_widget(self.sender_status)

        # ------------------ Receiver Section ------------------
        receiver_layout = BoxLayout(orientation='vertical', spacing=10)
        receiver_layout.add_widget(Label(text="Receiver", font_size=24))

        self.receiver_label = Label(text="Message will appear here", size_hint=(1, 0.4))
        self.receiver_label.text_size = (400, None)  # allow multi-line
        receiver_layout.add_widget(self.receiver_label)

        receiver_layout.add_widget(Label(text="Biometric Simulation (password '1234'):"))
        self.biometric_input = TextInput(password=True, multiline=False)
        receiver_layout.add_widget(self.biometric_input)

        unlock_btn = Button(text="Unlock Message", size_hint=(1, 0.2))
        unlock_btn.bind(on_press=self.unlock_message)
        receiver_layout.add_widget(unlock_btn)

        self.receiver_status = Label(text="Status: Waiting for message")
        receiver_layout.add_widget(self.receiver_status)

        main_layout.add_widget(sender_layout)
        main_layout.add_widget(receiver_layout)

        return main_layout

    # ------------------ File Selection ------------------
    def on_file_select(self, filechooser, selection):
        if selection:
            self.selected_file = selection[0]
            self.sender_status.text = f"Selected: {os.path.basename(self.selected_file)}"

    # ------------------ Message Sending ------------------
    def send_message(self, instance):
        msg = self.sender_input.text
        # Check for message or file
        if not msg and not self.selected_file:
            self.sender_status.text = "Status: Enter a message or select a file!"
            return

        # File size simulation
        if self.selected_file:
            size = os.path.getsize(self.selected_file)
            if size > self.file_size_limit:
                self.popup_alert("File too large! Limit 5MB")
                return

        # Animate "Encrypting..."
        self.sender_status.text = "Status: Encrypting..."
        Clock.schedule_once(lambda dt: self.finish_sending(msg), 1.5)  # 1.5 sec delay

    def finish_sending(self, msg):
        self.secret_message = msg if msg else f"File: {os.path.basename(self.selected_file)}"
        self.sender_status.text = "Status: Message Sent ✅"
        self.receiver_label.text = "Message received. Locked until unlock."
        self.unlock_attempts = 0
        self.popup_alert("Message sent successfully!")

        # Auto-delete after 10 mins
        if self.timer:
            self.timer.cancel()
        self.timer = Clock.schedule_once(self.expire_message, 600)

    # ------------------ Unlocking ------------------
    def unlock_message(self, instance):
        if not self.secret_message:
            self.receiver_status.text = "Status: No message available."
            return

        if self.biometric_input.text == "1234":
            self.receiver_label.text = f"Unlocked Message:\n{self.secret_message}"
            self.receiver_status.text = "Status: Success ✅"
            self.popup_alert("Message unlocked successfully!")
            if self.timer:
                self.timer.cancel()
        else:
            self.unlock_attempts += 1
            attempts_left = self.max_attempts - self.unlock_attempts
            if attempts_left <= 0:
                self.receiver_status.text = "Status: Too many failed attempts. Resend required."
                self.receiver_label.text = "Message lost"
                self.secret_message = ""
                self.popup_alert("Failed too many times. Sender must resend!")
            else:
                self.receiver_status.text = f"Status: Biometric failed ({attempts_left} attempts left)"
                self.popup_alert(f"Biometric failed! {attempts_left} attempts left.")

    # ------------------ Message Expiry ------------------
    def expire_message(self, dt):
        self.secret_message = ""
        self.sender_status.text = "Status: Message expired."
        self.receiver_status.text = "Status: Message expired."
        self.receiver_label.text = "Message lost"
        self.popup_alert("Message expired! Please resend.")

    # ------------------ Popup Alerts ------------------
    def popup_alert(self, message):
        popup = Popup(title="Notification",
                      content=Label(text=message),
                      size_hint=(0.6, 0.3))
        popup.open()

if __name__ == "__main__":
    VeilTechApp().run()

import sys
import requests
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QHBoxLayout, QScrollArea, QFileDialog, 
    QMenuBar, QMessageBox, QInputDialog, QTabWidget, QMenu
)
from PyQt6.QtCore import Qt, QSize, QMimeData
from PyQt6.QtGui import QFont, QPalette, QColor, QAction, QClipboard
import simpleaudio as sa

class ChatApplication(QWidget):
    def __init__(self):
        super().__init__()
        # Initialize conversation history
        self.conversation_history = {}
        self.api_key = ""
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('AI Chat Application')
        self.setGeometry(100, 100, 1000, 800)  # Bigger screen size

        # Set light theme colors
        self.setStyleSheet("background-color: white; color: black;")

        # Main Layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Menu Bar
        self.menu_bar = QMenuBar(self)
        main_layout.setMenuBar(self.menu_bar)

        # File Menu
        file_menu = self.menu_bar.addMenu('File')
        save_action = QAction('Save Chat', self)
        save_action.triggered.connect(self.save_chat)
        file_menu.addAction(save_action)

        # Settings Menu
        settings_menu = self.menu_bar.addMenu('Settings')
        settings_action = QAction('API Key', self)
        settings_action.triggered.connect(self.change_api_key)
        settings_menu.addAction(settings_action)

        # Chat Tabs
        self.chat_tabs = QTabWidget(self)
        main_layout.addWidget(self.chat_tabs)

        # Add new tab button
        new_tab_action = QAction('New Chat Tab', self)
        new_tab_action.triggered.connect(self.add_new_tab)
        self.menu_bar.addAction(new_tab_action)

        # Create initial tab without asking for a name
        self.add_new_tab(initial=True)

        # Apply font style to the entire app
        font = QFont("Arial", 10)
        self.setFont(font)

    def add_new_tab(self, initial=False):
        if initial:
            tab_name = "Default Chat"
        else:
            tab_name, ok = QInputDialog.getText(self, "Tab Name", "Enter a name for the new chat tab:")
            if not ok or not tab_name:
                return

        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        # Chat Area (Scrollable)
        chat_area = QScrollArea(tab)
        chat_area.setWidgetResizable(True)
        chat_content = QWidget()
        chat_layout = QVBoxLayout(chat_content)
        chat_area.setWidget(chat_content)
        tab_layout.addWidget(chat_area)

        # Input Area for New Messages
        input_layout = QHBoxLayout()

        # Text input for user
        input_text = QLineEdit(tab)
        input_text.setPlaceholderText('Type your message...')
        input_layout.addWidget(input_text)

        # File Upload Button
        upload_button = QPushButton('Upload File', tab)
        upload_button.setStyleSheet("background-color: #0078D7; color: white;")
        upload_button.clicked.connect(lambda: self.upload_file(input_text))
        input_layout.addWidget(upload_button)

        # Send Button
        send_button = QPushButton('Send', tab)
        send_button.setStyleSheet("background-color: #0078D7; color: white;")
        send_button.clicked.connect(lambda: self.send_message(input_text, chat_layout, tab_name))
        input_layout.addWidget(send_button)

        tab_layout.addLayout(input_layout)
        self.chat_tabs.addTab(tab, tab_name)

        # Initialize conversation history for this tab
        self.conversation_history[tab_name] = []

    def add_chat_bubble(self, text, is_user=True, chat_layout=None, tab_name=""):
        bubble_layout = QHBoxLayout()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Message Bubble
        bubble = QLabel(f"{text}\n\n{timestamp}", self)
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(450)
        bubble.setStyleSheet("padding: 10px; border-radius: 10px;")
        bubble.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        bubble.customContextMenuRequested.connect(lambda pos: self.show_context_menu(pos, bubble, text))

        if is_user:
            bubble.setStyleSheet("background-color: #DCF8C6; padding: 10px; border-radius: 10px;")
            bubble_layout.addWidget(bubble)
            bubble_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        else:
            bubble.setStyleSheet("background-color: #E0E0E0; padding: 10px; border-radius: 10px;")
            bubble_layout.addWidget(bubble)
            bubble_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        chat_layout.addLayout(bubble_layout)
        self.conversation_history[tab_name].append((text, timestamp, is_user))
        self.chat_tabs.currentWidget().findChild(QScrollArea).verticalScrollBar().setValue(self.chat_tabs.currentWidget().findChild(QScrollArea).verticalScrollBar().maximum())

        # Play sound notification
        self.play_sound()

    def show_context_menu(self, pos, bubble, text):
        context_menu = QMenu(self)
        copy_action = context_menu.addAction("Copy")
        copy_action.triggered.connect(lambda: self.copy_text_to_clipboard(text))
        context_menu.exec(bubble.mapToGlobal(pos))

    def copy_text_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        mime_data = QMimeData()
        mime_data.setText(text)
        clipboard.setMimeData(mime_data)

    def play_sound(self):
        try:
            wave_obj = sa.WaveObject.from_wave_file("message_sent.wav")
            wave_obj.play()
        except Exception as e:
            print(f"Sound error: {e}")

    def send_message(self, input_text, chat_layout, tab_name):
        user_text = input_text.text().strip()
        if not user_text:
            return

        self.add_chat_bubble(user_text, is_user=True, chat_layout=chat_layout, tab_name=tab_name)
        input_text.clear()

        if not self.api_key:
            QMessageBox.warning(self, "API Key Missing", "Please set your API key in the settings.")
            return

        # API URL
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={self.api_key}'
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": user_text}]}]
        }

        try:
            # Send request to API
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()

            # Process the response
            result = response.json()
            print(result)  # Debugging: Print the response to the console

            # Extract the generated content
            generated_content = result['candidates'][0]['content']['parts'][0]['text']
            if generated_content:
                self.add_chat_bubble(generated_content, is_user=False, chat_layout=chat_layout, tab_name=tab_name)
            else:
                self.add_chat_bubble("No content was generated. Please try again.", is_user=False, chat_layout=chat_layout, tab_name=tab_name)
        except requests.exceptions.HTTPError as http_err:
            self.add_chat_bubble(f"HTTP error occurred: {http_err}", is_user=False, chat_layout=chat_layout, tab_name=tab_name)
        except requests.exceptions.RequestException as req_err:
            self.add_chat_bubble(f"Request error occurred: {req_err}", is_user=False, chat_layout=chat_layout, tab_name=tab_name)
        except json.JSONDecodeError as json_err:
            self.add_chat_bubble(f"JSON decode error: {json_err}", is_user=False, chat_layout=chat_layout, tab_name=tab_name)
        except Exception as e:
            self.add_chat_bubble(f"An error occurred: {e}", is_user=False, chat_layout=chat_layout, tab_name=tab_name)

    def upload_file(self, input_text):
        file_dialog = QFileDialog()
        file_name, _ = file_dialog.getOpenFileName(self, "Open Text File", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    file_content = file.read()
                    input_text.setText(file_content)
            except Exception as e:
                QMessageBox.critical(self, "File Error", f"Could not read file: {e}")

    def save_chat(self):
        current_tab_name = self.chat_tabs.tabText(self.chat_tabs.currentIndex())
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Chat History", "", f"{current_tab_name} Chat History.txt", options=options)
        if file_name:
            try:
                with open(file_name, 'w') as file:
                    for message, timestamp, is_user in self.conversation_history[current_tab_name]:
                        role = "User" if is_user else "AI"
                        file.write(f"[{timestamp}] {role}: {message}\n\n")
                QMessageBox.information(self, "Chat Saved", "Chat history has been saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Could not save chat history: {e}")

    def change_api_key(self):
        text, ok = QInputDialog.getText(self, "API Key", "Enter new API key:")
        if ok and text:
            self.api_key = text

# Main application
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Set global palette for white and blue theme
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))  # White background
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))  # Black text
    palette.setColor(QPalette.ColorRole.Button, QColor(0, 120, 215))  # Blue buttons
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))  # White button text
    app.setPalette(palette)

    window = ChatApplication()
    window.show()
    sys.exit(app.exec())


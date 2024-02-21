import sys
import json
import subprocess
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

API_ENDPOINT = "https://api.ecosia.org/v2/chat/?sp=productivity"
USER_ID = "seed-torrents"
CONVERSATION_FILE = f"user_{USER_ID}_conversation.json"

class ChatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Angela Qt")
        self.setGeometry(100, 100, 400, 400)

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)

        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(50)
        self.input_field.setPlaceholderText("Type your message and press alt key to send")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        layout.addWidget(self.chat_history)
        layout.addWidget(self.input_field)
        central_widget.setLayout(layout)

        self.input_field.setFocus()

        if not os.path.exists(CONVERSATION_FILE):
            with open(CONVERSATION_FILE, "w") as file:
                json.dump({"messages": []}, file)

    def send_message(self):
        message = self.input_field.toPlainText().strip()
        if message:
            self.display_message("You: " + message)
            self.input_field.clear()
            self.get_response(message)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Alt:
           self.send_message()
        else:
            super().keyPressEvent(event)


    def get_response(self, message):
        with open(CONVERSATION_FILE, "r") as file:
            conversation = json.load(file)
            conversation["messages"].append({"content": message, "role": "user"})

        with open(CONVERSATION_FILE, "w") as file:
            json.dump(conversation, file)

        response_length = os.path.getsize(CONVERSATION_FILE)
        assistant_response = subprocess.run([
            "curl",
            "-s",
            "-k",
            "-X",
            "POST",
            "-H", "Host: api.ecosia.org",
            "-H", f"Content-Length: {response_length}",
            "-H", "Content-Type: application/json",
            "-H", "Accept: */*",
            "-H", "Origin: https://www.ecosia.org",
            "--data-binary", f"@{CONVERSATION_FILE}",
            API_ENDPOINT
        ], capture_output=True, text=True).stdout

        with open(CONVERSATION_FILE, "r") as file:
            conversation = json.load(file)
            conversation["messages"].append({"content": assistant_response, "role": "assistant"})

        with open(CONVERSATION_FILE, "w") as file:
            json.dump(conversation, file)

        self.display_message("Angela: " + assistant_response)

    def display_message(self, message):
        self.chat_history.append(message)
        self.chat_history.append("")

        cursor = self.chat_history.textCursor()
        cursor.movePosition(cursor.End)
        self.chat_history.setTextCursor(cursor)

    def closeEvent(self, event):
        if os.path.exists(CONVERSATION_FILE):
            os.remove(CONVERSATION_FILE)
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    chat_app = ChatApp()
    chat_app.show()
    sys.exit(app.exec_())

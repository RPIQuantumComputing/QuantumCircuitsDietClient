import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QHeaderView, QAbstractItemView, QLineEdit, QDialog, QTextEdit)

import hashlib
import requests
import os

example_assignment = []

# Global variable for user data
user_data = {'signed_in':False}

# Create session file if doesnt exist
try:
    with open("session/session","r") as infile:
        infile.seek(0, os.SEEK_END) 
        if infile.tell(): 
            infile.seek(0) 
            user_data["username"] = infile.read()
            user_data["session"] = infile.read()
            print(f"Signed in as {user_data['username']}")
            user_data["signed_in"] = True

    
            
except FileNotFoundError:
    with open("session/session","w") as outfile:
        pass


api = "http://127.0.0.1:5000/api"#"https://www.quantumcircut.com"

class SignInDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sign In")
        self.setGeometry(100, 100, 300, 200)
        layout = QVBoxLayout()

        self.username = QLineEdit(self)
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        signInButton = QPushButton("Sign In", self)
        signInButton.clicked.connect(self.signIn)

        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password)
        layout.addWidget(signInButton)

        self.setLayout(layout)

    def signIn(self):
        global user_data
        user_data['username'] = self.username.text()
        user_data['password'] = self.password.text()
        self.accept()

class MessagingDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 400, 300)
        layout = QVBoxLayout()

        self.messageArea = QTextEdit(self)
        self.messageArea.setReadOnly(True)
        self.inputField = QLineEdit(self)
        sendMessageButton = QPushButton("Send Message", self)
        sendMessageButton.clicked.connect(self.sendMessage)

        layout.addWidget(self.messageArea)
        layout.addWidget(self.inputField)
        layout.addWidget(sendMessageButton)

        self.setLayout(layout)

    def sendMessage(self):
        message = self.inputField.text()
        if message:  # Simple validation to ensure there's a message to send
            self.messageArea.append(message)
            self.inputField.clear()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Educational Interface")
        self.setGeometry(100, 100, 1000, 600)
        global example_assignment
        example_assignment = [
            ["Project 1", "2024-03-01", "Project", "A", "100/100", "Download", "Upload"],
            ["Homework 2", "2024-03-15", "Homework", "B+", "85/100", "Download", "Upload"],
        ]
        self.initUI()
    
    def initUI(self):
        # Main widget and layout
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        mainLayout = QHBoxLayout()
        
        # Table setup
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["Title", "Due Date", "Assignment Type", "Score", "Download", "Upload"])
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Populate table with example data and buttons
        self.populateTable()
        
        # Layout for table
        tableLayout = QVBoxLayout()
        tableLayout.addWidget(self.tableWidget)
        
        # Right side buttons setup
        classmateMessagingButton = QPushButton("Classmate Messaging")
        classmateMessagingButton.clicked.connect(self.openClassmateMessaging)
        lectureMessagingButton = QPushButton("Lecture Messaging")
        lectureMessagingButton.clicked.connect(self.openLectureMessaging)

        rightLayout = QVBoxLayout()
        rightLayout.addWidget(classmateMessagingButton)
        rightLayout.addWidget(lectureMessagingButton)
       
      
        if(user_data["signed_in"]):
            signOutButton = QPushButton("Sign Out")
            signOutButton.clicked.connect(self.signOutFunction)
            rightLayout.addWidget(signOutButton)
        else:
            signInButton = QPushButton("Sign In")
            signInButton.clicked.connect(self.openSignInDialog)
            rightLayout.addWidget(signInButton)
      
        # Add layouts to the main layout
        mainLayout.addLayout(tableLayout)
        mainLayout.addLayout(rightLayout)
        
        mainWidget.setLayout(mainLayout)
        
    def populateTable(self):
        global example_assignment
        
        for row_data in example_assignment:
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)
            for column, data in enumerate(row_data[1:-2]):  # Adjusted to skip buttons
                self.tableWidget.setItem(row, column, QTableWidgetItem(data))
            
            assignment_button = QPushButton(row_data[0])
            self.tableWidget.setCellWidget(row, 0, assignment_button)

            # Adding Download Button
            downloadBtn = QPushButton('Download')
            downloadBtn.clicked.connect(self.downloadClicked)
            self.tableWidget.setCellWidget(row, 4, downloadBtn)
            
            # Adding Upload Button
            uploadBtn = QPushButton('Upload')
            uploadBtn.clicked.connect(self.uploadClicked)
            self.tableWidget.setCellWidget(row, 5, uploadBtn)
            
    def downloadClicked(self):
        # Placeholder for download functionality
        header = {
            'session' : user_data['session']
        }
        
        param = {
            'file_owner': user_data['username'],
            'file_name' : "Test"
        }

        r = requests.get(f"{api}/download",headers=header,params=param)
        
        if(r.status_code == 200):
            print("Download Successful")
        else:
            print("Error Downloading")

        
    def uploadClicked(self):
        # Placeholder for upload functionality
        header = {
            'session' : user_data['session']
        }

        data = {
            'circuit_json' : None
        }
        
        r = requests.post(f"{api}/upload",headers=header,data=data)

        if(r.status_code == 200):
            print("Upload Successful")
        else:
            print("Error Uploading")


    def openSignInDialog(self):
        dialog = SignInDialog(self)
        if dialog.exec_():
            
            password_hash = hashlib.sha256(user_data['password'].encode(), usedforsecurity=True)
            
            user_data['password_hash'] = password_hash.hexdigest()
            
            data = {
                'username' : user_data['username'],
                'password' : password_hash.hexdigest()
            }
            
            # TEST
            class request:
                def json(self):
                    return {"session":"TEST123","success":True}
            
            r = requests.post(f"{api}/login",json=data)

            if(r.json()['success'] == True):
                print("Signed in as:", user_data['username'])
            else:
                print("Invalid Username or Password")
                return
            
            user_data['session'] = r.json()['session']
            
            # For automatic login
            with open("session/session","w") as outfile:
                outfile.write(user_data['username'] + "\n")
                outfile.write(user_data['session'])
        
            signOutButton = QPushButton("Sign Out")
            signOutButton.clicked.connect(self.signOutFunction)
            
            self = signOutButton
                
    def signOutFunction(self):    
        with open("session/session","w") as outfile:
            pass
            
    def openLectureMessaging(self):
        dialog = MessagingDialog("Lecture Messaging", self)
        dialog.exec_()

    def openClassmateMessaging(self):
        dialog = MessagingDialog("Classmate Messaging", self)
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

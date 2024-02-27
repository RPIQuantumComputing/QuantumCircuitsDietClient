import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QHeaderView, QAbstractItemView, QLineEdit, QDialog, QTextEdit)
import DesignerGUI

import hashlib

example_assignment = []

# Global variable for user data
user_data = {}

api = "https://www.quantumcircut.com"

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
        launchQuantumCircuitsButton = QPushButton("Launch Quantum Circuits")
        launchQuantumCircuitsButton.clicked.connect(self.launchQuantumCircuits)
        classmateMessagingButton = QPushButton("Classmate Messaging")
        classmateMessagingButton.clicked.connect(self.openClassmateMessaging)
        lectureMessagingButton = QPushButton("Lecture Messaging")
        lectureMessagingButton.clicked.connect(self.openLectureMessaging)
        signInButton = QPushButton("Sign In")
        signInButton.clicked.connect(self.openSignInDialog)

        # Add buttons to the right layout
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(launchQuantumCircuitsButton)
        rightLayout.addWidget(classmateMessagingButton)
        rightLayout.addWidget(lectureMessagingButton)
        rightLayout.addWidget(signInButton)
        
        # Add layouts to the main layout
        mainLayout.addLayout(tableLayout)
        mainLayout.addLayout(rightLayout)
        mainWidget.setLayout(mainLayout)
    
    def launchQuantumCircuits(self):
        quantumCircuit = DesignerGUI.MainWidget()
        quantumCircuit.show()
        
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
        
        r = requests.get(f"{api}/download",headers=header)
        
        print("Download button clicked")
        
    def uploadClicked(self):
        # Placeholder for upload functionality
        header = {
            'session' : user_data['session']
        }
        
        r = requests.post(f"{api}/upload",headers=header,file=None)
        print("Upload button clicked")

    def openSignInDialog(self):
        dialog = SignInDialog(self)
        if dialog.exec_():
            
            user_name_hash = hashlib.sha256(user_data['username'].encode(), usedforsecurity=True)
            password_hash = hashlib.sha256(user_data['password'].encode(), usedforsecurity=True)
            
            print(user_name_hash.digest(),password_hash.digest())
            
            user_data['username_hash'] = user_name_hash.digest()
            user_data['password_hash'] = password_hash.digest()
            
            data = {
                'username' : user_name_hash.digest(),
                'password' : password_hash.digest()
            }
            
            r = requests.post(f"{api}/signin",json=data)
            
            if(r.json()['success'] == True):
                print("Signed in as:", user_data['username'])
            else:
                print("Invalid Username or Password")
            
            user_data['session'] = r.json()['session']
            
            # For automatic login
            with open("session","w") outfile:
                outfile.write(r.json()['session'])
                

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

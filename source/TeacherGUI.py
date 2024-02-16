import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
                             QTableWidgetItem, QLabel, QHeaderView, QAbstractItemView, QLineEdit, QDialog, QTextEdit)

example_assignment = []

# Global variable for user data
user_data = {}

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

class AssignmentEditDialog(QDialog):
    def __init__(self, row, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Assignment")
        self.setGeometry(100, 100, 300, 200)
        layout = QVBoxLayout()

        self.titleField = QLineEdit(self)
        self.totalPointsField = QLineEdit(self)
        self.descriptionField = QTextEdit(self)
        updateButton = QPushButton("Update", self)
        updateButton.clicked.connect(lambda: self.updateAssignment(row))

        layout.addWidget(QLabel("Title:"))
        layout.addWidget(self.titleField)
        layout.addWidget(QLabel("Total Points:"))
        layout.addWidget(self.totalPointsField)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.descriptionField)
        layout.addWidget(updateButton)

        self.setLayout(layout)

    def updateAssignment(self, row):
        # Here, you would update the assignment in your data model
        print(f"Updated assignment at row {row} with title {self.titleField.text()}, total points {self.totalPointsField.text()}, and description {self.descriptionField.toPlainText()}")
        self.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Educational Interface")
        self.setGeometry(100, 100, 1000, 600)
        global example_assignment
        example_assignment = [
            ["Project 1", "2024-03-01", "Project", 100, "Description here"],
            ["Homework 2", "2024-03-15", "Homework", 85, "Description here"],
        ]
        self.initUI()

    def initUI(self):
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        mainLayout = QHBoxLayout()

        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(7)  # Adjusted column count
        self.tableWidget.setHorizontalHeaderLabels(["Edit", "Title", "Due Date", "Assignment Type", "Score", "Download", "Upload"])
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.populateTable()

        tableLayout = QVBoxLayout()
        tableLayout.addWidget(self.tableWidget)

        # Adding Share Screen Button
        shareScreenButton = QPushButton("Share Screen")
        shareScreenButton.clicked.connect(self.shareScreen)
        lectureMessagingButton = QPushButton("Lecture Messaging")
        lectureMessagingButton.clicked.connect(self.openLectureMessaging)
        signInButton = QPushButton("Sign In")
        signInButton.clicked.connect(self.openSignInDialog)

        rightLayout = QVBoxLayout()
        rightLayout.addWidget(lectureMessagingButton)
        rightLayout.addWidget(signInButton)
        rightLayout.addWidget(shareScreenButton)

        mainLayout.addLayout(tableLayout)
        mainLayout.addLayout(rightLayout)

        mainWidget.setLayout(mainLayout)

    def populateTable(self):
        global example_assignment
        
        for row, row_data in enumerate(example_assignment):
            self.tableWidget.insertRow(row)
            
            # Adding Edit Button
            editBtn = QPushButton('Edit')
            editBtn.clicked.connect(lambda _, r=row: self.openEditDialog(r))
            self.tableWidget.setCellWidget(row, 0, editBtn)

            for column, data in enumerate(row_data, 1):  # Adjust to include edit button
                if column < 5:  # Adjust for new column index
                    self.tableWidget.setItem(row, column, QTableWidgetItem(str(data)))

            # Adding Download and Upload Buttons
            downloadBtn = QPushButton('Download')
            downloadBtn.clicked.connect(self.downloadClicked)
            self.tableWidget.setCellWidget(row, 5, downloadBtn)
            
            uploadBtn = QPushButton('Upload')
            uploadBtn.clicked.connect(self.uploadClicked)
            self.tableWidget.setCellWidget(row, 6, uploadBtn)

    def openEditDialog(self, row):
        dialog = AssignmentEditDialog(row, self)
        dialog.exec_()

    def downloadClicked(self):
        print("Download button clicked")

    def uploadClicked(self):
        print("Upload button clicked")

    def shareScreen(self):
        # Placeholder for share screen functionality
        print("Share Screen button clicked")

    def openSignInDialog(self):
        dialog = SignInDialog(self)
        if dialog.exec_():
            print("Signed in as:", user_data['username'])

    def openLectureMessaging(self):
        dialog = MessagingDialog("Lecture Messaging", self)
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

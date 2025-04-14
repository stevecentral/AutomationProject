# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt6 UI code generator 6.8.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


import os
import subprocess
import time
import telnetlib3
import asyncio
from threading import Thread, Event
from queue import Queue
from PyQt6.QtWidgets import QFileDialog
from PyQt6 import QtCore, QtGui, QtWidgets
import socket
import select

import telnetlib3
import asyncio
from threading import Thread, Event
from queue import Queue
import time
from log_handler import LogHandler


class Ui_Dialog(object):
    def __init__(self):
        self.log_handler = None
        self.log_update_timer = None
        self.test_thread = None
        self.queue_files = {}  # Add this for queue functionality
        self.test_counter = 0


    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(900, 800)
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(64, 445, 161, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.commandsTextBox = QtWidgets.QPlainTextEdit(parent=Dialog)
        self.commandsTextBox.setGeometry(QtCore.QRect(70, 130, 530, 301))
        self.commandsTextBox.setObjectName("commandsTextBox")
        self.label = QtWidgets.QLabel(parent=Dialog)
        self.label.setGeometry(QtCore.QRect(70, 20, 91, 31))
        self.label.setObjectName("label")
        self.exportScriptButton = QtWidgets.QPushButton(parent=Dialog)
        self.exportScriptButton.setGeometry(QtCore.QRect(619, 445, 100, 23))
        self.exportScriptButton.setObjectName("exportScriptButton")
        self.label_2 = QtWidgets.QLabel(parent=Dialog)
        self.label_2.setGeometry(QtCore.QRect(70, 100, 171, 16))
        self.label_2.setObjectName("label_2")
        self.loadScriptButton = QtWidgets.QPushButton(parent=Dialog)
        self.loadScriptButton.setGeometry(QtCore.QRect(726, 445, 100, 23))
        self.loadScriptButton.setObjectName("loadScriptButton")
        self.addressTextBox = QtWidgets.QLineEdit(parent=Dialog)
        self.addressTextBox.setGeometry(QtCore.QRect(70, 60, 210, 23))
        self.addressTextBox.setObjectName("addressTextBox")
        self.elementNamesButton = QtWidgets.QPushButton(parent=Dialog)
        self.elementNamesButton.setGeometry(QtCore.QRect(501, 60, 100, 23))
        self.elementNamesButton.setObjectName("elementNamesButton")
        self.testQueue = QtWidgets.QListWidget(parent=Dialog)
        self.testQueue.setGeometry(QtCore.QRect(620, 130, 205, 301))
        self.testQueue.setObjectName("testQueue")
        self.instructionsButton = QtWidgets.QPushButton(parent=Dialog)
        self.instructionsButton.setGeometry(QtCore.QRect(394, 60, 100, 23))
        self.instructionsButton.setObjectName("instructionsButton")
        self.connectButton = QtWidgets.QPushButton(parent=Dialog)
        self.connectButton.setGeometry(QtCore.QRect(69, 709, 75, 23))
        self.connectButton.setObjectName("connectButton")
        self.clearButton = QtWidgets.QPushButton(parent=Dialog)
        self.clearButton.setGeometry(QtCore.QRect(151, 709, 75, 23))
        self.clearButton.setObjectName("clearButton")
        self.logViewer = QtWidgets.QTextBrowser(parent=Dialog)
        self.logViewer.setGeometry(QtCore.QRect(70, 490, 755, 201))
        font = QtGui.QFont()
        font.setFamily("Courier")
        self.logViewer.setFont(font)
        self.logViewer.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        self.logViewer.setObjectName("logViewer")

        # Functionality for buttons
        self.loadScriptButton.clicked.connect(self.open_file_dialog)
        self.exportScriptButton.clicked.connect(self.save_file_dialog)
        self.instructionsButton.clicked.connect(self.open_instructions)
        self.testQueue.itemClicked.connect(self.on_queue_item_clicked)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(self.run_script_generator)  # type: ignore
        self.buttonBox.rejected.connect(Dialog.reject)  # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.clearButton.clicked.connect(self.clear_logs)

        self.log_update_timer = QtCore.QTimer()
        self.log_update_timer.timeout.connect(self.update_logs)
        self.log_update_timer.setInterval(50)  # Update every 100ms

        # Connect button signal
        self.connectButton.clicked.connect(self.toggle_log_connection)

        self.test_count = 0

        Dialog.finished.connect(self.cleanup)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Enter IP Address"))
        self.exportScriptButton.setText(_translate("Dialog", "Export"))
        self.label_2.setText(_translate("Dialog", "Enter Commands Line By Line"))
        self.loadScriptButton.setText(_translate("Dialog", "Load Previous"))
        self.elementNamesButton.setText(_translate("Dialog", "Every Element"))
        self.instructionsButton.setText(_translate("Dialog", "Commands Help"))
        self.connectButton.setText(_translate("Dialog", "Connect"))
        self.clearButton.setText(_translate("Dialog", "Clear"))


    # ====== Test Execution Methods ======
    def run_script_generator(self):
        """Main entry point for test execution"""
        self.setup_logging()
        if not self.queue_files:
            self.run_single_test_thread()
        else:
            self.run_queue_tests_thread()

    def run_single_test_thread(self):
        """Execute a single test in a separate thread"""

        def run_test():
            try:
                address = self.addressTextBox.text()
                commands = self.commandsTextBox.toPlainText()
                self.run_single_test(address, commands, "single_test")
                QtCore.QMetaObject.invokeMethod(
                    self, "test_completed",
                    QtCore.Qt.ConnectionType.QueuedConnection
                )
            except Exception as e:
                QtCore.QMetaObject.invokeMethod(
                    self, "test_failed",
                    QtCore.Qt.ConnectionType.QueuedConnection,
                    QtCore.Q_ARG(str, str(e))
                )

        self.test_thread = Thread(target=run_test)
        self.test_thread.start()

    def run_queue_tests_thread(self):
        """Execute all queued tests in a separate thread"""

        def run_tests():
            try:
                address = self.addressTextBox.text()
                for file_name, file_info in self.queue_files.items():
                    try:
                        print(f"Running test: {file_name}")
                        self.run_single_test(address, file_info['content'], file_name)
                        QtCore.QMetaObject.invokeMethod(
                            self, "test_progress",
                            QtCore.Qt.ConnectionType.QueuedConnection,
                            QtCore.Q_ARG(str, file_name)
                        )
                    except Exception as e:
                        QtCore.QMetaObject.invokeMethod(
                            self, "test_failed",
                            QtCore.Qt.ConnectionType.QueuedConnection,
                            QtCore.Q_ARG(str, f"Error in {file_name}: {str(e)}")
                        )
                        return

                QtCore.QMetaObject.invokeMethod(
                    self, "queue_completed",
                    QtCore.Qt.ConnectionType.QueuedConnection
                )
            except Exception as e:
                QtCore.QMetaObject.invokeMethod(
                    self, "test_failed",
                    QtCore.Qt.ConnectionType.QueuedConnection,
                    QtCore.Q_ARG(str, str(e))
                )

        self.test_thread = Thread(target=run_tests)
        self.test_thread.start()

    def run_single_test(self, address, commands, test_name):
        """Execute a single test"""
        self.test_counter += 1
        with open('input.txt', 'w') as f:
            f.write(commands)

        os.environ['ADDRESS'] = address
        os.environ['TEST_NUM'] = str(self.test_counter)
        os.environ['TEST_NAME'] = test_name

        result = subprocess.run(
            ["python", "script_generator.py"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Test {test_name} output:", result.stdout)

    # ====== Queue Management Methods ======
    def add_to_queue(self, file_path):
        """Add a file to the test queue"""
        try:
            file_name = os.path.basename(file_path)
            item_widget = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout(item_widget)

            label = QtWidgets.QLabel(file_name)
            layout.addWidget(label)

            remove_button = QtWidgets.QPushButton("X")
            remove_button.setMaximumWidth(30)
            remove_button.clicked.connect(lambda: self.remove_from_queue(file_name))
            layout.addWidget(remove_button)

            item = QtWidgets.QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())

            self.testQueue.addItem(item)
            self.testQueue.setItemWidget(item, item_widget)

            with open(file_path, 'r') as f:
                content = f.read()

            self.queue_files[file_name] = {
                'path': file_path,
                'content': content,
                'item': item
            }
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Error", f"Failed to add file to queue: {str(e)}")

    def remove_from_queue(self, file_name):
        """Remove a file from the test queue"""
        if file_name in self.queue_files:
            item = self.queue_files[file_name]['item']
            self.testQueue.takeItem(self.testQueue.row(item))
            del self.queue_files[file_name]

    def on_queue_item_clicked(self, item):
        """Handle queue item selection"""
        widget = self.testQueue.itemWidget(item)
        file_name = widget.layout().itemAt(0).widget().text()
        if file_name in self.queue_files:
            self.commandsTextBox.setPlainText(self.queue_files[file_name]['content'])

    # ====== Logging Methods ======
    def setup_logging(self):
        """Initialize logging handler"""
        if not self.log_handler:
            address = self.addressTextBox.text()
            self.log_handler = LogHandler(address, callback=self.update_logs)
            if self.log_handler.connect():
                self.log_update_timer = QtCore.QTimer()
                self.log_update_timer.timeout.connect(self.update_logs)
                self.log_update_timer.start(100)

    def update_logs(self):
        """Update log viewer with new entries"""
        if self.log_handler and not self.log_handler.log_queue.empty():
            while not self.log_handler.log_queue.empty():
                log_entry = self.log_handler.log_queue.get()
                if log_entry:
                    # Ensure the log entry ends with a newline
                    if not log_entry.endswith('\n'):
                        log_entry += '\n'
                    self.logViewer.append(log_entry)
                    # Scroll to the bottom
                    self.logViewer.verticalScrollBar().setValue(
                        self.logViewer.verticalScrollBar().maximum()
                    )

    def toggle_log_connection(self):
        """Toggle log connection state"""
        if not self.log_handler or not self.log_handler.connected:
            self.connect_logs()
        else:
            self.disconnect_logs()

    def connect_logs(self):
        """Establish log connection"""
        ip_address = self.addressTextBox.text()
        if not ip_address:
            QtWidgets.QMessageBox.warning(None, "Warning", "Please enter an IP address")
            return

        self.log_handler = LogHandler(host=ip_address, port=23)

        if self.log_handler.connect():
            self.log_update_timer = QtCore.QTimer()
            self.log_update_timer.timeout.connect(self.update_logs)
            self.log_update_timer.start(100)  # Check every 100ms
            self.connectButton.setText("Disconnect")
            self.logViewer.append("Connected to device logs...")
        else:
            QtWidgets.QMessageBox.critical(None, "Error", "Failed to connect to device logs")

    def disconnect_logs(self):
        """Disconnect from logs"""
        if self.log_handler:
            self.log_handler.disconnect()
            self.log_update_timer.stop()
            self.connectButton.setText("Connect")
            self.logViewer.append("Disconnected from device logs.\n")
            self.log_handler = None

    # ====== File Operations ======
    def save_file_dialog(self):
        """Save current test to file"""
        try:
            content = self.commandsTextBox.toPlainText()
            if not content:
                QtWidgets.QMessageBox.warning(None, "Warning", "Nothing to save - text box is empty")
                return

            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.FileMode.AnyFile)
            dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            dialog.setNameFilter("Text Files (*.txt)")
            dialog.setDefaultSuffix("txt")

            if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                file_name = dialog.selectedFiles()[0]
                with open(file_name, 'w') as file:
                    file.write(content)
                QtWidgets.QMessageBox.information(None, "Success", f"File saved successfully to:\n{file_name}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Error", f"Failed to save file: {str(e)}")

    def open_file_dialog(self):
        try:
            filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(
                parent=None,
                caption="Open File",
                directory="",
                filter="Text Files (*.txt);;All Files (*.*)"
            )
            for filename in filenames:
                self.add_to_queue(filename)
        except Exception as e:
            print(f"Error opening file: {str(e)}")

    # ====== Utility Methods ======
    def clear_logs(self):
        self.logViewer.clear()

    def cleanup(self):
        if self.log_handler:
            self.log_handler.disconnect()
        if self.log_update_timer:
            self.log_update_timer.stop()

    # ====== Qt Slots ======
    @QtCore.pyqtSlot()
    def test_completed(self):
        """Handle test completion"""
        QtWidgets.QMessageBox.information(None, "Success", "Test execution completed successfully")

    @QtCore.pyqtSlot(str)
    def test_progress(self, file_name):
        """Handle test progress"""
        print(f"Completed test: {file_name}")

    @QtCore.pyqtSlot()
    def queue_completed(self):
        """Handle queue completion"""
        QtWidgets.QMessageBox.information(None, "Success", "All queued tests completed successfully")

    @QtCore.pyqtSlot(str)
    def test_failed(self, error_message):
        """Handle test failure"""
        QtWidgets.QMessageBox.critical(None, "Error", f"Script failed:\n{error_message}")


    def open_instructions(self):
        QtWidgets.QMessageBox.information(
            None,
            "Instructions",
            "login: login,\n"
            "logout: logout,\n"
            "power cycle: power_cycle,\n"
            "check: check_element,\n"
            "screenshot: screenshot,\n"
            "check_button: check_button,\n"
            "click: click,\n"
            "power: power_toggle,\n"
            "check_text: check_text,"
        )



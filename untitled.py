import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QInputDialog, QTabWidget, QTextEdit
from PyQt5.QtCore import Qt
from threading import Thread
import time

from log_handler import LogHandler


class LogViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Add your existing input and file loading widgets here
        # For example:
        # input_widget = YourInputWidget()
        # main_layout.addWidget(input_widget)

        # Add a button to add new log tabs
        self.add_tab_button = QPushButton("Add Log Tab")
        self.add_tab_button.clicked.connect(self.add_log_tab)
        main_layout.addWidget(self.add_tab_button)

        # Tab widget for logs
        self.log_tab_widget = QTabWidget()
        main_layout.addWidget(self.log_tab_widget)

        self.log_handlers = []

    def add_log_tab(self):
        # Prompt user for host information
        host, ok = QInputDialog.getText(self, "Enter Host", "Host:")
        if not ok or not host:
            return

        # Create a new tab with a QTextEdit for logs
        tab = QWidget()
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        layout.addWidget(text_edit)
        tab.setLayout(layout)

        self.log_tab_widget.addTab(tab, f"Log {self.log_tab_widget.count() + 1}")

        # Create a new LogHandler for this tab
        log_handler = LogHandler(host)  # Use the user-provided host
        self.log_handlers.append(log_handler)
        log_handler.connect()

        # Start a thread to update the text edit with logs
        def update_logs():
            while log_handler.connected:
                if not log_handler.log_queue.empty():
                    log = log_handler.log_queue.get()
                    text_edit.append(log)
                time.sleep(0.1)

        Thread(target=update_logs, daemon=True).start()

    def closeEvent(self, event):
        for handler in self.log_handlers:
            handler.disconnect()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = LogViewer()
    viewer.show()
    sys.exit(app.exec_())

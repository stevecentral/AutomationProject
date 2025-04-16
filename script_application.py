import sys
from PyQt6 import QtWidgets
from main_window import Ui_Dialog

class DialogWindow(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        # Initialize parent classes
        super().__init__()
        self.setupUi(self)

# Main entry point of the application
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = DialogWindow()
    dialog.show()
    sys.exit(app.exec())

import sys
from PyQt6 import QtWidgets
from main_window import Ui_Dialog

class DialogWindow(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = DialogWindow()
    dialog.show()
    sys.exit(app.exec())
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QMainWindow

from src.qt_material6 import apply_stylesheet


########################################################################
class RuntimeStylesheets(QMainWindow):
    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        super().__init__()
        self.main = QUiLoader().load("main_window.ui", self)
        self.main.pushButton_2.setProperty("class", "big_button")


if __name__ == "__main__":
    app = QApplication()

    # apply_stylesheet(app, theme='light_blue.xml')

    # stylesheet = app.styleSheet()
    # # app.setStyleSheet(stylesheet + "QPushButton{color: red; text-transform: none;}")
    # with open('custom.css') as file:
    # app.setStyleSheet(stylesheet + file.read().format(**os.environ))

    apply_stylesheet(app, theme="light_blue.xml", css_file="custom.css")

    frame = RuntimeStylesheets()
    frame.main.show()
    app.exec_()

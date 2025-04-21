from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QMainWindow

from src.qt_material.qt_style_tools import QtStyleTools


########################################################################
class RuntimeStylesheets(QMainWindow, QtStyleTools):
    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        super().__init__()
        self.main = QUiLoader().load("main_window.ui", self)

        self.apply_stylesheet(self.main, "light_red.xml")
        self.add_menu_theme(self.main, self.main.menuStyles)
        self.show_dock_theme(self.main)


if __name__ == "__main__":
    app = QApplication()
    frame = RuntimeStylesheets()
    frame.main.show()
    app.exec_()

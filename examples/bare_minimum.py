import sys

from PySide6 import QtWidgets

# from PySide2 import QtWidgets
# from PyQt5 import QtWidgets
# from PyQt6 import QtWidgets
from src.qt_material6 import apply_stylesheet

# create the app and the main window
app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()

# setup style sheet
apply_stylesheet(app, theme="dark_teal.xml")

# run
window.show()

if hasattr(app, "exec"):
    app.exec()
else:
    app.exec_()

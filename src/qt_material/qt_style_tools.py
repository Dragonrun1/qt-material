import os
import sys
from warnings import deprecated

if "PySide6" in sys.modules:
    from PySide6 import QtUiTools
elif "PyQt6" in sys.modules:
    from PyQt6 import uic

from ..qt_material import (
    _FEATURE,
    QtCore,
    QtGui,
    QtWidgets,
    apply_stylesheet,
    list_themes,
)


class QtStyleTools:
    """"""

    extra_values = {}

    @deprecated("set_extra")
    def set_extra_colors(self, extra):
        """"""
        self.extra_values = extra

    def set_extra(self, extra):
        """"""
        self.extra_values = extra

    def add_menu_theme(self, parent, menu):
        """"""
        self.menu_theme_ = menu
        action_group = QtGui.QActionGroup(menu)
        if _FEATURE:
            action_group.exclusive = True
        else:
            action_group.setExclusive(True)

        for i, theme in enumerate(["default"] + list_themes()):
            action = QtGui.QAction(parent)
            action.triggered.connect(lambda: self.update_theme_event(parent))
            if _FEATURE:
                action.text = theme
                action.checkable = True
                action.checked = not bool(i)
                action.action_group = action_group
                menu.add_action(action)
                action_group.add_action(action)
            else:
                action.setText(theme)
                action.setCheckable(True)
                action.setChecked(not bool(i))
                action.setActionGroup(action_group)
                menu.addAction(action)
                action_group.addAction(action)

    def add_menu_density(self, parent, menu):
        """"""
        self.menu_density_ = menu
        action_group = QtGui.QActionGroup(menu)

        if _FEATURE:
            action_group.exclusive = True
            for density in map(str, range(-3, 4)):
                action = QtGui.QAction(parent)
                action.triggered.connect(
                    lambda: self.update_theme_event(parent)
                )
                action.text = density
                action.checkable = True
                action.checked = density == "0"
                action.action_group = action_group
                menu.add_action(action)
                action_group.add_action(action)
        else:
            action_group.setExclusive(True)
            for density in map(str, range(-3, 4)):
                action = QtGui.QAction(parent)
                action.triggered.connect(
                    lambda: self.update_theme_event(parent)
                )
                action.setText(density)
                action.setCheckable(True)
                action.setChecked(density == "0")
                action.setActionGroup(action_group)
                menu.addAction(action)
                action_group.addAction(action)

    def apply_stylesheet(
        self, parent, theme, invert_secondary=False, extra=None, callable_=None
    ):
        """"""
        if theme == "default":
            if _FEATURE:
                parent.style_sheet = ""
            else:
                parent.setStyleSheet("")
            return

        if extra is None:
            extra = {}
        apply_stylesheet(
            parent,
            theme=theme,
            invert_secondary=invert_secondary,
            extra=extra,
        )

        if callable_:
            callable_()

    def update_theme_event(self, parent):
        """"""
        if _FEATURE:
            density = [
                action.text
                for action in self.menu_density_.actions()
                if action.checked
            ][0]
            theme = [
                action.text
                for action in self.menu_theme_.actions()
                if action.checked
            ][0]
        else:
            density = [
                action.text()
                for action in self.menu_density_.actions()
                if action.isChecked()
            ][0]
            theme = [
                action.text()
                for action in self.menu_theme_.actions()
                if action.isChecked()
            ][0]

        self.extra_values["density_scale"] = density

        self.apply_stylesheet(
            parent,
            theme=theme,
            invert_secondary=theme.startswith("light"),
            extra=self.extra_values,
            callable_=self.update_buttons,
        )

    def update_buttons(self):
        """"""
        if not hasattr(self, "colors"):
            return

        theme = {
            color_: os.environ[f"QTMATERIAL_{color_.upper()}"]
            for color_ in self.colors
        }

        if _FEATURE:
            if "light" in os.environ["QTMATERIAL_THEME"]:
                # noinspection PyUnresolvedReferences
                self.dock_theme.checkBox_light_theme.checked = True
            elif "dark" in os.environ["QTMATERIAL_THEME"]:
                # noinspection PyUnresolvedReferences
                self.dock_theme.checkBox_light_theme.checked = False
        else:
            if "light" in os.environ["QTMATERIAL_THEME"]:
                # noinspection PyUnresolvedReferences
                self.dock_theme.checkBox_light_theme.setChecked(True)
            elif "dark" in os.environ["QTMATERIAL_THEME"]:
                # noinspection PyUnresolvedReferences
                self.dock_theme.checkBox_light_theme.setChecked(False)

        if _FEATURE:
            # noinspection PyUnresolvedReferences
            if self.dock_theme.checkBox_light_theme.checked:
                (
                    theme["secondaryLightColor"],
                    theme["secondaryDarkColor"],
                ) = (
                    theme["secondaryDarkColor"],
                    theme["secondaryLightColor"],
                )
            else:
                # noinspection PyUnresolvedReferences
                if self.dock_theme.checkBox_light_theme.isChecked():
                    (
                        theme["secondaryLightColor"],
                        theme["secondaryDarkColor"],
                    ) = (
                        theme["secondaryDarkColor"],
                        theme["secondaryLightColor"],
                    )

        for color_ in self.colors:
            button = getattr(self.dock_theme, f"pushButton_{color_}")

            color = theme[color_]

            text_color = "#000000"
            # noinspection PyUnresolvedReferences
            if _FEATURE and self.get_color(color).get_hsv()[2] < 128:
                text_color = "#ffffff"
            elif not _FEATURE and self.get_color(color).getHsv()[2] < 128:
                text_color = "#ffffff"

            button.setStyleSheet(
                f"""
            *{{
            background-color: {color};
            color: {text_color};
            border: none;
            }}"""
            )

            self.custom_colors[color_] = color

    def get_color(self, color):
        """"""
        return QtGui.QColor(
            *[int(color[s : s + 2], 16) for s in range(1, 6, 2)]
        )

    def update_theme(self, parent):
        """"""
        with open("my_theme.xml", "w") as file:
            file.write(
                """
            <resources>
                <color name="primaryColor">{primaryColor}</color>
                <color name="primaryLightColor">{primaryLightColor}</color>
                <color name="secondaryColor">{secondaryColor}</color>
                <color name="secondaryLightColor">{secondaryLightColor}</color>
                <color name="secondaryDarkColor">{secondaryDarkColor}</color>
                <color name="primaryTextColor">{primaryTextColor}</color>
                <color name="secondaryTextColor">{secondaryTextColor}</color>
              </resources>
            """.format(**self.custom_colors)
            )
        if _FEATURE:
            # noinspection PyUnresolvedReferences
            light = self.dock_theme.checkBox_light_theme.checked
        else:
            # noinspection PyUnresolvedReferences
            light = self.dock_theme.checkBox_light_theme.isChecked()

        self.apply_stylesheet(
            parent,
            "my_theme.xml",
            invert_secondary=light,
            extra=self.extra_values,
            callable_=self.update_buttons,
        )

    def set_color(self, parent, button_):
        """"""

        def iner():
            initial = self.get_color(self.custom_colors[button_])
            color_dialog = QtWidgets.QColorDialog(parent=parent)
            if _FEATURE:
                color_dialog.current_color = initial
            else:
                color_dialog.setCurrentColor(initial)
            done = color_dialog.exec_()

            if _FEATURE:
                color_ = color_dialog.current_color
                if done and color_.is_valid():
                    rgb_255 = [color_.red(), color_.green(), color_.blue()]
                    color = "#" + "".join(
                        [hex(v)[2:].ljust(2, "0") for v in rgb_255]
                    )
                    self.custom_colors[button_] = color
                    self.update_theme(parent)
            else:
                color_ = color_dialog.currentColor()
                if done and color_.isValid():
                    rgb_255 = [color_.red(), color_.green(), color_.blue()]
                    color = "#" + "".join(
                        [hex(v)[2:].ljust(2, "0") for v in rgb_255]
                    )
                    self.custom_colors[button_] = color
                    self.update_theme(parent)

        return iner

    def show_dock_theme(self, parent):
        """"""
        self.colors = [
            "primaryColor",
            "primaryLightColor",
            "secondaryColor",
            "secondaryLightColor",
            "secondaryDarkColor",
            "primaryTextColor",
            "secondaryTextColor",
        ]

        self.custom_colors = {
            v: os.environ.get(f"QTMATERIAL_{v.upper()}", "")
            for v in self.colors
        }

        if "PySide6" in sys.modules:
            self.dock_theme = QtUiTools.QUiLoader().load(
                os.path.join(os.path.dirname(__file__), "dock_theme.ui")
            )
        elif "PyQt6" in sys.modules:
            self.dock_theme = uic.loadUi(
                os.path.join(os.path.dirname(__file__), "dock_theme.ui")
            )

        if _FEATURE:
            parent.add_dock_widget(
                QtGui.Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_theme
            )
            self.dock_theme.floating = True
        else:
            parent.addDockWidget(
                QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_theme
            )
            self.dock_theme.setFloating(True)

        self.update_buttons()
        self.dock_theme.checkBox_light_theme.clicked.connect(
            lambda: self.update_theme(self.main)
        )

        for color in self.colors:
            button = getattr(self.dock_theme, f"pushButton_{color}")
            button.clicked.connect(self.set_color(parent, color))

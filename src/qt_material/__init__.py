import logging
import os
import platform
import sys
from pathlib import Path
from xml.dom.minidom import parse

import jinja2
from resources import ResourseGenerator

GUI = True

if "PySide6" in sys.modules:
    from PySide6.QtCore import QDir
    from PySide6.QtGui import (
        QAction,
        QColor,
        QFontDatabase,
        QGuiApplication,
        QPalette,
    )

elif "PyQt6" in sys.modules:
    from PyQt6.QtCore import QDir
    from PyQt6.QtGui import (
        QAction,
        QColor,
        QFontDatabase,
        QGuiApplication,
        QPalette,
    )
else:
    GUI = False
    logging.warning("qt_material must be imported after PySide6 or PyQt6!")

__widget = QAction()
FEATURE = callable(getattr(__widget, "set_menu", None))
del __widget

TEMPLATE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "material.css.template"
)


def export_theme(
    theme="",
    qss=None,
    rcc=None,
    invert_secondary=False,
    extra=None,
    output="theme",
    prefix="icon:/",
):
    """"""
    if extra is None:
        extra = {}
    if not os.path.isabs(output) and not output.startswith("."):
        output = f".{output}"

    stylesheet = build_stylesheet(
        theme, invert_secondary, extra, output, export=True
    )

    if output.startswith("."):
        output = output[1:]

    with open(qss, "w") as file:
        file.writelines(stylesheet.replace("icon:/", prefix))

    if rcc:
        with open(rcc, "w") as file:
            file.write("<RCC>\n")
            file.write(f'  <qresource prefix="{prefix[:-2]}">\n')

            for subfolder in ["disabled", "primary"]:
                files = os.listdir(
                    os.path.join(os.path.abspath(output), subfolder)
                )
                files = filter(lambda s: s.endswith("svg"), files)
                for filename in files:
                    file.write(
                        f"    <file>{output}/{subfolder}/{filename}</file>\n"
                    )

            file.write("  </qresource>\n")

            file.write('  <qresource prefix="file">\n')
            if qss:
                file.write(f"    <file>{qss}</file>\n")
            file.write("  </qresource>\n")

            file.write("</RCC>\n")


def build_stylesheet(
    theme="",
    invert_secondary=False,
    extra=None,
    parent="theme",
    template=TEMPLATE_FILE,
    export=False,
):
    """"""

    if extra is None:
        extra = {}
    if not export:
        try:
            add_fonts()
        except Exception as e:
            logging.warning(e)

    theme = get_theme(theme, invert_secondary)
    if theme is None:
        return None

    set_icons_theme(theme, parent=parent)

    # Render custom template
    if os.path.exists(template):
        parent, template = os.path.split(template)
        loader = jinja2.FileSystemLoader(parent)
        env = jinja2.Environment(autoescape=True, loader=loader)
        env.filters["opacity"] = opacity
        env.filters["density"] = density
        stylesheet = env.get_template(template)
    else:
        logging.warning("Failed to find template!")
        return None

    theme.setdefault("icon", None)
    theme.setdefault("font_family", "Roboto")
    theme.setdefault("danger", "#dc3545")
    theme.setdefault("warning", "#ffc107")
    theme.setdefault("success", "#17a2b8")
    theme.setdefault("density_scale", "0")
    theme.setdefault("button_shape", "default")

    theme.update(extra)

    if GUI:
        default_palette = QGuiApplication.palette()
        color = QColor(
            *[int(theme["primaryColor"][i : i + 2], 16) for i in range(1, 6, 2)]
            + [92]
        )

        if FEATURE:
            default_palette.set_color(QPalette.ColorRole.Text, color)
            QGuiApplication.set_palette(default_palette)
            if hasattr(QPalette, "PlaceholderText"):  # pyside6
                default_palette.set_color(QPalette.PlaceholderText, color)
        else:
            default_palette.setColor(QPalette.ColorRole.Text, color)
            QGuiApplication.setPalette(default_palette)
            if hasattr(QPalette, "PlaceholderText"):  # pyside6
                default_palette.setColor(QPalette.PlaceholderText, color)

    environ = {
        "linux": platform.system() == "Linux",
        "windows": platform.system() == "Windows",
        "darwin": platform.system() == "Darwin",
        "pyqt6": "PyQt6" in sys.modules,
        "pyside6": "PySide6" in sys.modules,
    }

    environ.update(theme)
    return stylesheet.render(environ)


def get_theme(theme_name, invert_secondary=False):
    if theme_name in [
        "default_dark.xml",
        "default_dark",
    ]:
        theme = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "themes",
            "dark_teal.xml",
            # 'light_cyan_500.xml',
        )
    elif theme_name in [
        "default_light.xml",
        "default_light",
        "default.xml",
        "default",
    ]:
        invert_secondary = True
        theme = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "themes",
            "light_cyan_500.xml",
        )
    elif not os.path.exists(theme_name):
        theme = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "themes", theme_name
        )
    else:
        theme = theme_name

    if not os.path.exists(theme):
        logging.warning(f"{theme} does not exist!")
        return None

    document = parse(theme)
    theme = {
        child.getAttribute("name"): child.firstChild.nodeValue
        for child in document.getElementsByTagName("color")
    }

    for k in theme:
        os.environ[str(k)] = theme[k]

    if invert_secondary:
        (
            theme["secondaryColor"],
            theme["secondaryLightColor"],
            theme["secondaryDarkColor"],
        ) = (
            theme["secondaryColor"],
            theme["secondaryDarkColor"],
            theme["secondaryLightColor"],
        )

    for color in [
        "primaryColor",
        "primaryLightColor",
        "secondaryColor",
        "secondaryLightColor",
        "secondaryDarkColor",
        "primaryTextColor",
        "secondaryTextColor",
    ]:
        os.environ[f"QTMATERIAL_{color.upper()}"] = theme[color]
    os.environ["QTMATERIAL_THEME"] = theme_name

    return theme


def add_fonts():
    """"""
    fonts_path = os.path.join(os.path.dirname(__file__), "fonts")

    for font_dir in ["roboto"]:
        for font in filter(
            lambda s: s.endswith(".ttf"),
            os.listdir(os.path.join(fonts_path, font_dir)),
        ):
            if FEATURE:
                QFontDatabase.add_application_font(
                    os.path.join(fonts_path, font_dir, font)
                )
            else:
                QFontDatabase.addApplicationFont(
                    os.path.join(fonts_path, font_dir, font)
                )


def apply_stylesheet(
    app,
    theme="",
    style=None,
    save_as=None,
    invert_secondary=False,
    extra=None,
    parent="theme",
    css_file=None,
):
    """"""
    if extra is None:
        extra = {}
    if style:
        try:
            if FEATURE:
                app.style = style
            else:
                app.setStyle(style)
        except:
            logging.error(f"The style '{style}' does not exist.")
            pass

    if "QMenu" in extra:
        for k in extra["QMenu"]:
            extra[f"qmenu_{k}"] = extra["QMenu"][k]
        extra["QMenu"] = True

    stylesheet = build_stylesheet(theme, invert_secondary, extra, parent)
    if stylesheet is None:
        return

    if save_as:
        with open(save_as, "w") as file:
            file.writelines(stylesheet)

    if css_file and os.path.exists(css_file):
        with open(css_file) as file:
            stylesheet += file.read().format(**os.environ)

    if FEATURE:
        app.style_sheet = stylesheet
    else:
        app.setStyleSheet(stylesheet)


def opacity(theme, value=0.5):
    """"""
    r, g, b = theme[1:][0:2], theme[1:][2:4], theme[1:][4:]
    r, g, b = int(r, 16), int(g, 16), int(b, 16)

    return f"rgba({r}, {g}, {b}, {value})"


def density(
    value, density_scale, border=0, scale=1, density_interval=4, min_=4
):
    """"""
    # https://material.io/develop/web/supporting/density
    if isinstance(value, str) and value.startswith("@"):
        return value[1:] * scale

    if value == "unset":
        return "unset"

    if isinstance(value, str):
        value = float(value.replace("px", ""))

    density_ = (
        value + (density_interval * int(density_scale)) - (border * 2)
    ) * scale

    if density_ <= 0:
        density_ = min_
    return density_


def set_icons_theme(theme, parent="theme"):
    """"""
    source = os.path.join(os.path.dirname(__file__), "resources", "source")
    resources = ResourseGenerator(
        primary=theme["primaryColor"],
        secondary=theme["secondaryColor"],
        disabled=theme["secondaryLightColor"],
        source=source,
        parent=parent,
    )
    resources.generate()

    if GUI:
        if FEATURE:
            # noinspection PyUnresolvedReferences
            QDir.add_search_path("icon", resources.index)
            # noinspection PyUnresolvedReferences
            QDir.add_search_path(
                "qt_material",
                os.path.join(os.path.dirname(__file__), "resources"),
            )
        else:
            QDir.addSearchPath("icon", resources.index)
            QDir.addSearchPath(
                "qt_material",
                os.path.join(os.path.dirname(__file__), "resources"),
            )


def list_themes():
    """"""
    themes = os.listdir(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "themes")
    )
    themes = filter(lambda a: a.endswith("xml"), themes)
    return sorted(list(themes))


def get_hook_dirs():
    package_folder = Path(__file__).parent
    return [str(package_folder.absolute())]

with open("../README.md", "r") as file:
    content = file.read()
content = content.replace(
    "_images/",
    "https://github.com/Dragonrun1/qt-material6/tree/raw/main/docs/source/notebooks/_images",
)
with open("../README.md", "w") as file:
    file.write(content)

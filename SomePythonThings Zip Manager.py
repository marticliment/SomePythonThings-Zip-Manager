# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------- Required Modules ------------------------------------------------------------------------------ #
import os
import sys
import wget
import json
import time
import zipfile
import tempfile
import platform
import traceback
import darkdetect
import webbrowser
from ast import literal_eval
from sys import platform as _platform
from PySide2 import QtWidgets, QtGui, QtCore
from zipfile import ZipFile
from threading import Thread
from functools import partial
from urllib.request import urlopen
from qt_thread_updater import get_updater


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------- Global Classes ------------------------------------------------------------------------------- #
class Buttons():
    sel_file = None
    sel_folder = None
    create_zip = None
    clear_files = None
    remove_file = None
    select_zip = None
    extract_zip = None
    cancel_extract = None
    cancel_compress = None

class Labels():
    compression = None
    compress_level = None

class Sliders():
    compress_level = None

class CheckBoxes():
    create_subfolder = None


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------------------------------------- Globals ----------------------------------------------------------------------------------- #
debugging = False
actualVersion = 3.1

zip=""
font = ""
realpath="."
zip_files = ('Zip Files (*.zip);;All files (*.*)')

allDone = True
continueCreating = True
continueExtracting = True
compressionRunning = False
extractionRunning = False

files = []
compression_rate = [zipfile.ZIP_DEFLATED, zipfile.ZIP_BZIP2, zipfile.ZIP_LZMA, zipfile.ZIP_STORED]

lists = {}
labels = {}
fileLists = {}
progressbars = {}

compression_level = 5

lbls = Labels()
btns = Buttons()
sliders = Sliders()
chkbx = CheckBoxes()

tempDir = tempfile.TemporaryDirectory()

errorWhileCompressing = None
errorWhileExtracting = None


defaultSettings = {
    "default_algorithm": "Deflated",
    "default_level": 5,
    "create_subdir": True,
    "mode":'auto'
}
settings = defaultSettings.copy()

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------------------------------- Stylesheets related ----------------------------------------------------------------------------- #
lightModeStyleSheet = """
    *
    {{
        color: #000000;
        font-weight: normal;
        font-size:14px;
        font-family:{0};
    }}
    QPushButton
    {{
        border-image: none;
        background-color: #dddddd;
        /*border: 1px solid white;
        */width: 100px;
        height: 30px;
        border-radius: 3px;
    }}
    QPushButton::hover
    {{
        background-color: #bac7ff;

    }}
    QMessageBox 
    {{
        background-color: #eeeeee;
    }}
    QLineEdit 
    {{
        background-color: #ffffff;
    }}
    QInputDialog 
    {{
        background-color: #ffffff;
    }}
    QScrollBar 
    {{
        background-color: rgba(255, 255, 255, 0.0);
    }}
    QScrollBar::handle:vertical
    {{
        margin-top: 17px;
        margin-bottom: 17px;
        border: none;
        min-height: 30px;
        border-radius: 3px;
        border: 1px solid white;
        background-color: rgba(255, 255, 255, 0.6);
    }}
    QScrollBar::handle:horizontal
    {{
        margin-left: 17px;
        margin-right: 17px;
        border: none;
        min-width: 30px;
        border-radius: 3px;
        border: 1px solid white;
        background-color: rgba(255, 255, 255, 0.6);
    }}
    QScrollBar::add-line 
    {{
        border: none;
        border-radius: 3px;
        border: 1px solid white;
        background-color: rgba(255, 255, 255, 0.6);
    }}
    QScrollBar::sub-line 
    {{
        border: none;
        border-radius: 3px;
        border: 1px solid white;
        background-color: rgba(255, 255, 255, 0.6);
    }}
    QScrollBar::corner
    {{
        background-color: none;
    }}
    QLabel
    {{   
        border-image: none;
        padding: 3px;
        border-radius: 3px;   
    }}
    QComboBox
    {{   
        border-image: none;
        margin:0px;
        border: 1px solid white;
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 3px;
        border-top-left-radius: 0px;
        border-top-right-radius: 0px;
        border-top:0px;
        padding-left: 7px;
        selection-background-color: #bac7ff;
    }}
    QAbstractItemView
    {{
        background-color: #EEEEEE;
        margin: 0px;
        border-radius: 3px;
    }}
    QMenuBar
    {{
        background-color: #EEEEEE;
    }}
    QMenu
    {{
        background-color: #EEEEEE;
    }}
    QMenu::item 
    {{
        border: 5px solid #EEEEEE;
        border-right: 10px solid #EEEEEE;
    }}
    QMenu::item:selected 
    {{
        background-color: #bac7ff;
        border:5px solid  #bac7ff;
    }}
    QMenuBar::item
    {{
        background-color: #EEEEEE;
        border:5px solid  #EEEEEE;
    }}
    QMenuBar::item:selected
    {{
        background-color: #bac7ff;
        border:5px solid  #bac7ff;
    }}
    #halfTopLabel
    {{
        border-radius: 3px;
        font-family:{0};
        border-bottom-left-radius: 0px;
        border-bottom-right-radius: 0px;
        border: 1px solid white;
        background-color: rgba(255, 255, 255, 0.5);
        border-bottom-color: rgba(255, 255, 255, 0.5);
    }}
    #quarterWidget
    {{
        border-radius: 3px;
        font-family:{0};
        border: 1px solid white;
        background-color: rgba(255, 255, 255, 0.5);
        padding-left:5px;
    }}
    #quarterWidget::hover
    {{
        border-radius: 3px;
        font-family:{0};
        border: 1px solid white;
        background-color: rgba(255, 255, 255, 0.4);
        padding-left:5px;
    }}
    #normalbutton
    {{
        border-image: none;
        background-image: none;
        font-family:{0};
        border: 1px solid white;
        background-color: rgba(255, 255, 255, 0.6);
        font-size:14px;
        border-radius: 3px;
        color: #000000;
    }}
    #normalbutton::hover
    {{
        background-color: rgba(200, 200, 200, 0.3);
    }}
    #redbutton
    {{
        border-image: none;
        background-image: none;
        font-family:{0};
        border: 1px solid white;
        background-color: rgba(255, 255, 255, 0.5);
        font-size:14px;
        border-radius: 3px;
        color: #000000;
    }}
    #redbutton::hover
    {{
        border: 1px solid rgb(255, 0, 0);
        background-color: rgba(255, 50, 50, 0.5);
    }}
    #greenbutton
    {{
        border-image: none;
        background-image: none;
        font-family:{0};
        border: 1px solid white;
        background-color: rgba(255, 255, 255, 0.5);
        font-size:14px;
        border-radius: 3px;
        color: #000000;
    }}
    #greenbutton::hover
    {{
        border: 1px solid rgb(50, 200, 50);
        background-color: rgba(50, 200, 50, 0.7);
    }}
    #textinfos
    {{
        border-image: none;
        font-family:{0};
        background-image: none;
        border: 1px solid white;
        background-color: rgba(255, 255, 255, 0.5);
        font-size:15px;
        border-radius: 3px;
        color: #000000;
        padding: 5px;
    }}
    QProgressBar
    {{
        text-align: center;
        font-family:{0};
        border-image: none;
        background-image: none;
        border: 1px solid white;
        background-color: rgba(255, 255, 255, 0.5);
        font-size:15px;
        border-radius: 3px;
        color: #000000;
    }}
    QProgressBar::chunk
    {{
        border-radius: 3px;
        background-color: rgba(0, 255, 0, 0.5);
    }}
    QSizeGrip
    {{
        background-color: rgba(255, 255, 255, 0);
    }}
    QTableWidget
    {{
        show-decoration-selected: 0;
        background-color: transparent;
    }}
    QHeaderView::section
    {{
        show-decoration-selected: 0;
        background-color: transparent;
    }}
    QHeaderView
    {{
        show-decoration-selected: 0;
        background-color: transparent;
    }}
    QTableCornerButton::section
    {{
        show-decoration-selected: 0;
        background-color: transparent;
    }}
    QTreeWidget
    {{
        show-decoration-selected: 0;
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 3px;
        padding: 5px;
        padding-left: 5px;
        border: 1px solid rgb(255, 255, 255);
    }}
    QHeaderView::section
    {{
        background-color: rgba(255, 255, 255, 0.0);
        padding: 2px;
        height:20px;
        margin-bottom: 5px;
        border: 1px solid white;
        border-top:0px;
        border-left:0px;
        border-bottom:0x;
    }}
    QTreeWidget::item
    {{
        background-color: rgba(255, 255, 255, 0.0);
        padding-right: 5px;
        padding-left: 5px;
        height: 35px;
        margin-left: -5px;
        border: none;
        border-top: 1px solid rgb(255, 255, 255);
    }}
    QTreeWidget::item:hover
    {{
        background-color: rgba(255, 255, 255, 0.1);
        padding: 5px;
        padding-left: 5px;
        border: none;
        border-top: 1px solid rgb(255, 255, 255);
    }}
    QTreeWidget::item:selected
    {{
        background-color: rgba(255, 255, 255, 0.3);
        padding: 5px;
        color: black;
        padding-left: 5px;
        outline: none;
        border-top: 1px solid rgb(255, 255, 255);
    }}
    QTreeWidget::item:focus
    {{
        background-color: rgba(255, 255, 255, 0.3);
        padding: 5px;
        color: black;
        padding-left: 5px;
        outline: none;
        border-top: 1px solid rgb(255, 255, 255);
    }}
    #waiting 
    {{
        background-color: rgba(255, 255, 255, 255.5);
    }}
    #done 
    {{
        background-color: rgba(0, 255, 0, 0.5);
    }}
    #processing 
    {{
        background-color: rgba(0, 127, 127, 0.5);
    }}
    #halfBottomWidget
    {{   
        border-image: none;
        selection-background-color: rgb(255, 255, 255);
        margin:0px;
        border: 1px solid white;
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 3px;
        border-top-left-radius: 0px;
        border-top-right-radius: 0px;
        border-top:0px;
        position: absolute;
        height: 15px;
        padding-left: 10px;
    }}
    #scrollBarHalfBottom
    {{   
        border-image: none;
        selection-background-color: rgb(255, 255, 255);
        border: 1px solid white;
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 3px;
        border-top-left-radius: 0px;
        border-top-right-radius: 0px;
        border-top:0px;
    }}
    QSlider
    {{
        background-color: rgba(255, 255, 255, 0.0);
    }}
    QCheckBox
    {{
        border: 1px solid white;
        border-radius: 3px;
    }}
    QSlider::groove
    {{
        background: rgba(255, 255, 255, 0.0);
        height: 6px;
        border: 1px solid white;
        border-radius: 4px;
        left: 8px;
        right: 8px;
    }}
    QSlider::handle
    {{
        border-radius: 3px;
        background: rgba(255, 255, 255, 0.7);
        border: 1px solid white;
        height: 16px;
        margin: -5px 0;
        width: 15px;
    }}
    QSlider::add-page
    {{
        background-color: rgba(255, 255, 255, 0.3);
    }}
    QSlider::sub-page
    {{
        background-color: rgba(255, 255, 255, 0.3);
    }}
    QAbstractSlider QWidget
    {{
        background-color: transparent;
    }}
    QTableWidget
    {{
        background-color: rgba(255, 255, 255, 0.5);
        padding: 3px;
        border: 1px solid white;
        border-radius: 3px;
    }}
    QTableWidget:item
    {{
        border: none;
    }}
    QTableCornerButton::section
    {{
        background: rgba(255, 255, 255, 0);
        border: 0px outset red;
    }}
    QHeaderView::section
    {{
        border: none;
    }}
    #settingsBackground {{
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 0px;
        border-top-left-radius: 3px;
        border-bottom-left-radius: 3px;
        border: 1px solid rgb(255, 255, 255);
        border-right: none;
    }}
    #settingsCombo
    {{   
        border-image: none;
        margin:0px;
        border: 1px solid white;
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 3px;
        border-top-left-radius: 0px;
        border-bottom-left-radius: 0px;
        padding-left: 7px;
        selection-background-color: #bac7ff;
    }}
    #settingsFullWidth
    {{   
        border-image: none;
        margin:0px;
        border: 1px solid white;
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 3px;
        padding-left: 7px;
        selection-background-color: #111111;
    }}
    """

darkModeStyleSheet = """
    *
    {{
        color: #DDDDDD;
        font-weight:  nomal;;
        font-size: 14px;
        font-family:{0};
    }}
    QPushButton
    {{
        border-image: none;
        background-color: #222222;
        /*border: 1px solid black;
        */width: 100px;
        height: 30px;
        border-radius: 3px;
    }}
    QPushButton::hover
    {{
        background-color: #121212;

    }}
    QMessageBox 
    {{
        background-color: #333333;
    }}
    QLineEdit 
    {{
        background-color: #282828;
    }}
    QInputDialog 
    {{
        background-color: #282828;
    }}
    QScrollBar 
    {{
        background-color: rgba(0, 0, 0, 0.0);
    }}
    QScrollBar::handle:vertical
    {{
        margin-top: 17px;
        margin-bottom: 17px;
        border: none;
        min-height: 30px;
        border-radius: 3px;
        border: 1px solid black;
        background-color: rgba(0, 0, 0, 0.6);
    }}
    QScrollBar::handle:horizontal
    {{
        margin-left: 17px;
        margin-right: 17px;
        border: none;
        min-width: 30px;
        border-radius: 3px;
        border: 1px solid black;
        background-color: rgba(0, 0, 0, 0.6);
    }}
    QScrollBar::add-line 
    {{
        border: none;
        border-radius: 3px;
        border: 1px solid black;
        background-color: rgba(0, 0, 0, 0.6);
    }}
    QScrollBar::sub-line 
    {{
        border: none;
        border-radius: 3px;
        border: 1px solid black;
        background-color: rgba(0, 0, 0, 0.6);
    }}
    QScrollBar::corner
    {{
        background-color: none;
    }}
    QLabel
    {{   
        border-image: none;
        padding: 3px;
        border-radius: 3px;   
    }}
    QComboBox
    {{   
        border-image: none;
        selection-background-color: rgb(0, 0, 0);
        margin:0px;
        border: 1px solid black;
        background-color: rgba(0, 0, 0, 0.5);
        border-radius: 3px;
        border-top-left-radius: 0px;
        border-top-right-radius: 0px;
        border-top:0px;
        padding-left: 7px;
    }}
    QAbstractItemView
    {{
        background-color: rgb(41, 41, 41);
        margin: 0px;
        border-radius: 3px;
    }}
    QMenuBar
    {{
        background-color: #333333;
    }}
    QMenu
    {{
        background-color: #333333;
    }}
    QMenu::item 
    {{
        border: 5px solid #333333;
        border-right: 10px solid #333333;
    }}
    QMenu::item:selected 
    {{
        background-color: #000000;
        border:5px solid  #000000;
    }}
    QMenuBar::item
    {{
        background-color: #333333;
        border:5px solid  #333333;
    }}
    QMenuBar::item:selected
    {{
        background-color: #000000;
        border:5px solid  #000000;
    }}
    #halfTopLabel
    {{
        border-radius: 3px;
        font-family:{0};
        border-bottom-left-radius: 0px;
        border-bottom-right-radius: 0px;
        border: 1px solid black;
        background-color: rgba(0, 0, 0, 0.5);
        border-bottom-color: rgba(0, 0, 0, 0.5);
    }}
    #quarterWidget
    {{
        border-radius: 3px;
        font-family:{0};
        border: 1px solid black;
        background-color: rgba(0, 0, 0, 0.5);
        padding-left:5px;
    }}
    #quarterWidget::hover
    {{
        border-radius: 3px;
        font-family:{0};
        border: 1px solid black;
        background-color: rgba(0, 0, 0, 0.4);
        padding-left:5px;
    }}
    #normalbutton
    {{
        border-image: none;
        background-image: none;
        font-family:{0};
        border: 1px solid black;
        background-color: rgba(0, 0, 0, 0.5);
        font-size:14px;
        border-radius: 3px;
        color: #DDDDDD;
        font-weight:  nomal;;
    }}
    #normalbutton::hover
    {{
        background-color: rgba(0, 0, 0, 0.4);
    }}
    #redbutton
    {{
        border-image: none;
        background-image: none;
        font-family:{0};
        border: 1px solid black;
        background-color: rgba(0, 0, 0, 0.5);
        font-size:14px;
        border-radius: 3px;
        color: #DDDDDD;
        font-weight:  nomal;;
    }}
    #redbutton::hover
    {{
        border: 1px solid rgb(155, 0, 0);
        background-color: rgba(205, 0, 0, 0.7);
    }}
    #greenbutton
    {{
        border-image: none;
        background-image: none;
        font-family:{0};
        border: 1px solid black;
        background-color: rgba(0, 0, 0, 0.5);
        font-size:14px;
        border-radius: 3px;
        color: #DDDDDD;
        font-weight:  nomal;;
    }}
    #greenbutton::hover
    {{
        border: 1px solid rgb(0, 103, 1);
        background-color: rgba(0, 153, 51, 0.7);
    }}
    #textinfos
    {{
        border-image: none;
        font-family:{0};
        background-image: none;
        border: 1px solid black;
        background-color: rgba(0, 0, 0, 0.5);
        font-size:15px;
        border-radius: 3px;
        color: #DDDDDD;
        font-weight:  nomal;;
        padding: 5px;
    }}
    QProgressBar
    {{
        text-align: center;
        font-family:{0};
        border-image: none;
        background-image: none;
        border: 1px solid black;
        background-color: rgba(0, 0, 0, 0.5);
        font-size:15px;
        border-radius: 3px;
        color: #DDDDDD;
        font-weight:  nomal;;
    }}
    QProgressBar::chunk
    {{
        border-radius: 3px;
        background-color: rgba(0, 255, 0, 0.5);
    }}
    QSizeGrip
    {{
        background-color: rgba(0, 0, 0, 0);
    }}
    QTableWidget
    {{
        show-decoration-selected: 0;
        background-color: transparent;
    }}
    QHeaderView::section
    {{
        show-decoration-selected: 0;
        background-color: transparent;
    }}
    QHeaderView
    {{
        show-decoration-selected: 0;
        background-color: transparent;
    }}
    QTableCornerButton::section
    {{
        show-decoration-selected: 0;
        background-color: transparent;
    }}
    QTreeWidget
    {{
        show-decoration-selected: 0;
        background-color: rgba(0, 0, 0, 0.5);
        border-radius: 3px;
        padding: 5px;
        padding-left: 5px;
        border: 1px solid rgb(0, 0, 0);
    }}
    QHeaderView::section
    {{
        background-color: rgba(0, 0, 0, 0.0);
        padding: 2px;
        height:20px;
        margin-bottom: 5px;
        border: 1px solid black;
        border-top:0px;
        border-left:0px;
        border-bottom:0x;
    }}
    QTreeWidget::item
    {{
        background-color: rgba(0, 0, 0, 0.0);
        padding-right: 5px;
        padding-left: 5px;
        height: 35px;
        margin-left: -5px;
        border: none;
        border-top: 1px solid rgb(0, 0, 0);
    }}
    QTreeWidget::item:hover
    {{
        background-color: rgba(0, 0, 0, 0.1);
        padding: 5px;
        padding-left: 5px;
        border: none;
        border-top: 1px solid rgb(0, 0, 0);
    }}
    QTreeWidget::item:selected
    {{
        background-color: rgba(0, 0, 0, 0.3);
        padding: 5px;
        color: #dddddd;
        padding-left: 5px;
        outline: none;
        border-top: 1px solid rgb(0, 0, 0);
    }}
    #waiting 
    {{
        background-color: rgba(255, 0, 0, 0.5);
    }}
    #done 
    {{
        background-color: rgba(0, 255, 0, 0.5);
    }}
    #processing 
    {{
        background-color: rgba(0, 127, 127, 0.5);
    }}
    #halfBottomWidget
    {{   
        border-image: none;
        selection-background-color: rgb(0, 0, 0);
        margin:0px;
        border: 1px solid black;
        background-color: rgba(0, 0, 0, 0.5);
        border-radius: 3px;
        border-top-left-radius: 0px;
        border-top-right-radius: 0px;
        border-top:0px;
        position: absolute;
        height: 15px;
        padding-left: 10px;
    }}
    #scrollBarHalfBottom
    {{   
        border-image: none;
        selection-background-color: rgb(0, 0, 0);
        border: 1px solid black;
        background-color: rgba(0, 0, 0, 0.5);
        border-radius: 3px;
        border-top-left-radius: 0px;
        border-top-right-radius: 0px;
        border-top:0px;
    }}
    QSlider
    {{
        background-color: rgba(0, 0, 0, 0.0);
    }}
    QCheckBox
    {{
        border: 1px solid black;
        border-radius: 3px;
    }}
    QSlider::groove
    {{
        background: rgba(0, 0, 0, 0.0);
        height: 6px;
        border: 1px solid black;
        border-radius: 4px;
        left: 8px;
        right: 8px;
    }}
    QSlider::handle
    {{
        border-radius: 3px;
        background: rgba(0, 0, 0, 0.7);
        border: 1px solid black;
        height: 16px;
        margin: -5px 0;
        width: 15px;
    }}
    QSlider::add-page
    {{
        background-color: rgba(0, 0, 0, 0.3);
    }}
    QSlider::sub-page
    {{
        background-color: rgba(0, 0, 0, 0.3);
    }}
    QAbstractSlider QWidget
    {{
        background-color: transparent;
    }}
    QTableWidget
    {{
        background-color: rgba(0, 0, 0, 0.5);
        padding: 3px;
        border: 1px solid black;
        border-radius: 3px;
    }}
    QTableWidget:item
    {{
        border: none;
    }}
    QTableCornerButton::section {{
        background: rgba(0, 0, 0, 0);
        border: 0px outset red;
    }}
    QHeaderView::section
    {{
        border: none;
    }}
    #settingsBackground {{
        background-color: rgba(0, 0, 0, 0.5);
        border-radius: 0px;
        border-top-left-radius: 3px;
        border-bottom-left-radius: 3px;
        border: 1px solid rgb(0, 0, 0);
        border-right: none;
    }}
    #settingsCombo
    {{   
        border-image: none;
        margin:0px;
        border: 1px solid black;
        background-color: rgba(0, 0, 0, 0.5);
        border-radius: 3px;
        border-top-left-radius: 0px;
        border-bottom-left-radius: 0px;
        padding-left: 7px;
        selection-background-color: #111111;
    }}
    #settingsFullWidth
    {{   
        border-image: none;
        margin:0px;
        border: 1px solid black;
        background-color: rgba(0, 0, 0, 0.5);
        border-radius: 3px;
        padding-left: 7px;
        selection-background-color: #111111;
    }}
    """

def getTheme():
    if(platform.system()=="Windows"):
        import winreg
        if(int(platform.release())>=10):
            access_registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            access_key = winreg.OpenKey(access_registry, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize")
            readKeys = {}
            for n in range(20):
                try:
                    x = winreg.EnumValue(access_key, n)
                    readKeys[x[0]]=x[1]
                except:
                    pass
            try:
                return readKeys["AppsUseLightTheme"]
            except:
                return 1
        else:
            return 1
    elif(platform.system()=="Darwin"):
        return int(darkdetect.isLight())
    else:
        return 0

def getWindowStyleScheme():
    if(settings["mode"] == "dark"):
        theme = 0
    elif(settings["mode"] == "light"):
        theme = 1
    else:
        theme = getTheme()
    if(theme==1):
        return lightModeStyleSheet.format(font, realpath)
    else:
        return darkModeStyleSheet.format(font, realpath)

def checkModeThread():
    lastMode = getTheme()
    while True:
        if(lastMode!=getTheme()):
            if(settings["mode"] == "auto"):
                get_updater().call_in_main(zipManager.setStyleSheet, getWindowStyleScheme())
                lastMode = getTheme()
        time.sleep(1)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------------------------------- Essential Functions ----------------------------------------------------------------------------- #
def log(s):
    global debugging
    if(debugging or "WARN" in str(s) or "FAILED" in str(s)):
        print((time.strftime('[%H:%M:%S] ', time.gmtime(time.time())))+str(s))
    try:
        f = open(tempDir.name.replace('\\', '/')+'/log.txt', 'a+')
        f.write("\n"+time.strftime('[%H:%M:%S] ', time.gmtime(time.time()))+str(s))
        f.close()
    except:
        pass
    
def notify(title, body, icon='icon-zipmanager.png'):
    pass


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------ Update Functions ------------------------------------------------------------------------------- #
def checkUpdates_py(bypass="False"):
    global zipManager, actualVersion
    try:
        response = urlopen("http://www.somepythonthings.tk/versions/zip.ver")
        response = response.read().decode("utf8")
        if(bypass=="True"):
            get_updater().call_in_main(askUpdates, response)
        elif float(response.split("///")[0]) > actualVersion:
            get_updater().call_in_main(askUpdates, response)
        else:
            log("[   OK   ] No updates found")
            return 'No'
    except Exception as e:
        if debugging:
            raise e
        log("[  WARN  ] Unable to reach http://www.somepythonthings.tk/versions/zip.ver. Are you connected to the internet?")
        return 'Unable'

def askUpdates(response):
    notify("SomePythonThings Zip Manager Updater", "SomePythonThings Zip Manager has a new update!\nActual version: {0}\nNew version: {1}".format(actualVersion, response.split("///")[0]))
    if QtWidgets.QMessageBox.Yes == QtWidgets.QMessageBox.question(zipManager, 'SomePythonThings Zip Manager', "There are some updates available for SomePythonThings Zip Manager:\nYour version: "+str(actualVersion)+"\nNew version: "+str(response.split("///")[0])+"\nNew features: \n"+response.split("///")[1]+"\nDo you want to go download and install them?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes):

        #                'debian': debian link in posotion 2                  'win32' Windows 32bits link in position 3           'win64' Windows 64bits in position 4                   'macos' macOS 64bits INTEL in position 5
        downloadUpdates({'debian': response.split("///")[2].replace('\n', ''), 'win32': response.split("///")[3].replace('\n', ''), 'win64': response.split("///")[4].replace('\n', ''), 'macos':response.split("///")[5].replace('\n', '')})
    else:
        log("[  WARN  ] User aborted update!")

def download_win(url):
    try:
        #global texts
        os.system('cd %windir%\\..\\ & mkdir SomePythonThings')
        time.sleep(0.01)
        os.chdir("{0}/../SomePythonThings".format(os.environ['windir']))
        installationProgressBar('Downloading')
        filedata = urlopen(url)
        datatowrite = filedata.read()
        filename = ""
        with open("{0}/../SomePythonThings/SomePythonThings-Zip-Manager-Updater.exe".format(os.environ['windir']), 'wb') as f:
            f.write(datatowrite)
            filename = f.name
        installationProgressBar('Launching')
        log("[   OK   ] file downloaded to C:\\SomePythonThings\\{0}".format(filename))
        get_updater().call_in_main(launch_win, filename)
    except Exception as e:
        if debugging:
            raise e
        get_updater().call_in_main(throw_error, "SomePythonThings Zip Manager", "An error occurred while downloading the SomePythonTings Zip Manager installer. Please check your internet connection and try again later\n\nError Details:\n{0}".format(str(e)))

def launch_win(filename):
    try:
        installationProgressBar('Launching')
        throw_info("SomePythonThings Zip Manager Updater", "The update has been downloaded and is going to be installed.\nYou may be prompted for permissions, click YES.\nClick OK to start installation")
        os.system('start /B {0} /silent'.format(filename))
        get_updater().call_in_main(sys.exit)
        sys.exit()
    except Exception as e:
        if debugging:
            raise e
        throw_error("SomePythonThings Zip Manager Updater", "An error occurred while launching the SomePythonTings Zip Manager installer.\n\nError Details:\n{0}".format(str(e)))

def downloadUpdates(links):
    log('[   OK   ] Reached downloadUpdates. Download links are "{0}"'.format(links))
    if _platform == 'linux' or _platform == 'linux2':  # If the OS is linux
        log("[   OK   ] platform is linux, starting auto-update...")
        throw_info("SomePythonThings Updater", "The update is being downloaded. Please wait.")
        t = Thread(target=download_linux, args=(links,))
        t.daemon = True
        t.start()
    elif _platform == 'win32':  # if the OS is windows
        log('win32')
        url = ""
        if(platform.architecture()[0] == '64bit'):  # if OS is 64bits
            url = (links["win64"])
        else:  # is os is not 64bits
            url = (links['win32'])
        log(url)
        get_updater().call_in_main(throw_info, "SomePythonThings Update", "The update is being downloaded. Please wait.")
        t = Thread(target=download_win, args=(url,))
        t.daemon=True
        t.start()
    elif _platform == 'darwin':
        log("[   OK   ] platform is macOS, starting auto-update...")
        throw_info("SomePythonThings Updater", "The update is being downloaded. Please wait.")
        t = Thread(target=download_macOS, args=(links,))
        t.daemon=True
        t.start()
    else:  # If os is unknown
        webbrowser.open_new('https://www.somepythonthings.tk/programs/somepythonthings-zip-manager/')

def download_linux(links):
    get_updater().call_in_main(installationProgressBar, 'Downloading', 1, 4)
    p1 = os.system('cd; rm somepythonthings-zip-manager_update.deb; wget -O "somepythonthings-zip-manager_update.deb" {0}'.format(links['debian']))
    if(p1 == 0):  # If the download is done
        get_updater().call_in_main(install_linux_part1)
    else:  # If the download is falied
        get_updater().call_in_main(throw_error, "SomePythonThings", "An error occurred while downloading the update. Check your internet connection. If the problem persists, try to download and install the program manually.")
        webbrowser.open_new('https://www.somepythonthings.tk/programs/somepythonthings-zip-manager/')

def install_linux_part1(again=False):
    global zipManager
    installationProgressBar('Installing', 2, 4)
    time.sleep(0.2)
    if not again:
        passwd = str(QtWidgets.QInputDialog.getText(zipManager, "Autentication needed - SomePythonThings Zip Manager", "Please write your password to perform the update. \nThis password is NOT going to be stored anywhere in any way and it is going to be used ONLY for the update.\nIf you want, you can check that on the source code on github: \n(https://github.com/martinet101/SomePythonThings-Zip-Manager/)\n\nPassword:", QtWidgets.QLineEdit.Password, '')[0])
    else:
        passwd = str(QtWidgets.QInputDialog.getText(zipManager, "Autentication needed - SomePythonThings Zip Manager", "An error occurred while autenticating. Insert your password again (This attempt will be the last one)\n\nPassword:", QtWidgets.QLineEdit.Password, '')[0])
    t = Thread(target=install_linux_part2, args=(passwd, again))
    t.start()

def install_linux_part2(passwd, again=False):
    installationProgressBar('Installing', 3, 4)
    p1 = os.system('cd; echo "{0}" | sudo -S apt install ./"somepythonthings-zip-manager_update.deb"'.format(passwd))
    if(p1 == 0):  # If the installation is done
        p2 = os.system('cd; rm "./somepythonthings-zip-manager_update.deb"')
        if(p2 != 0):  # If the downloaded file cannot be removed
            log("[  WARN  ] Could not delete update file.")
        installationProgressBar('Installing', 4, 4)
        get_updater().call_in_main(throw_info,"SomePythonThings Manager Updater","The update has been applied succesfully. Please restart the application")
        get_updater().call_in_main(sys.exit)
        sys.exit()
    else:  # If the installation is falied on the 1st time
        if not again:
            get_updater().call_in_main(install_linux_part1, True)
        else:
            installationProgressBar('Stop')
            get_updater().call_in_main(throw_error, "SomePythonThings Zip Manager Updater", "Unable to apply the update. Please try again later.")

def download_macOS(links):
    try:
        installationProgressBar('Downloading')
        p1 = os.system('cd; rm somepythonthings-zip-manager_update.dmg')
        if(p1!=0):
            pass
        wget.download(links['macos'], out='{0}/somepythonthings-zipManager_update.dmg'.format(os.path.expanduser('~')))
        get_updater().call_in_main(install_macOS)
        log("[   OK   ] Download is done, starting launch process.")
    except Exception as e:
        if debugging:
            raise e
        get_updater().call_in_main(throw_error,"SomePythonThings Zip Manager Updater", "An error occurred while downloading the update. Check your internet connection. If the problem persists, try to download and install the program manually.\n\nError Details:\n"+str(e))
        webbrowser.open_new('https://www.somepythonthings.tk/programs/somepythonthings-zip-manager/')

def install_macOS():
    installationProgressBar('Launching')
    time.sleep(0.2)
    throw_info("SomePythonThings Zip Manager Updater", "The update file has been downloaded successfully. When you click OK, a folder will automatically be opened. Then drag the application on the folder to the applications folder link (also on the same folder).\nClick OK to continue")
    os.chdir(os.path.expanduser('~'))
    p2 = os.system('cd; open ./"somepythonthings-zip-manager_update.dmg"')
    log("[  INFO  ] macOS installation unix output code is \"{0}\"".format(p2))
    sys.exit()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------ Settings Functions ----------------------------------------------------------------------------- #
def saveSettings(silent=True, default_algorithm="Deflated", default_level=5, create_subdir=True, mode="auto"):
    global defaultSettings
    try:
        os.chdir(os.path.expanduser('~'))
        try:
            os.chdir('.SomePythonThings')
        except FileNotFoundError:
            log("[  WARN  ] Can't acces .SomePythonThings folder, creating .SomePythonThings...")
            os.mkdir(".SomePythonThings")
            os.chdir('.SomePythonThings')
        try:
            os.chdir('Zip Manager')
        except FileNotFoundError:
            log("[  WARN  ] Can't acces Zip Manager folder, creating Zip Manager...")
            os.mkdir("Zip Manager")
            os.chdir('Zip Manager')
        try:
            settingsFile = open('settings.conf', 'w')
            settingsFile.write(str({
                "default_algorithm": default_algorithm,
                "default_level":default_level,
                "create_subdir":create_subdir,
                "mode":mode,
                }))
            settingsFile.close()
            if(not(silent)):
                throw_info("SomePythonThings Zip Manager", "Settings saved successfuly")
            log("[   OK   ] Settings saved successfully")
            return True
        except Exception as e:
            throw_error('SomePythonThings Zip Manager', "An error occurred while loading the settings file. \n\nError details:\n"+str(e))
            log('[        ] Creating new settings.conf')
            saveSettings()
            if(debugging):
                raise e
            return False
    except Exception as e:
        if(not(silent)):
            throw_info("SomePythonThings Zip Manager", "Unable to save settings. \n\nError details:\n"+str(e))
        log("[ FAILED ] Unable to save settings")
        if(debugging):
            raise e
        return False

def openSettings():
    global defaultSettings
    os.chdir(os.path.expanduser('~'))
    try:
        os.chdir('.SomePythonThings')
        try:
            os.chdir('Zip Manager')
            try:
                settingsFile = open('settings.conf', 'r')
                settings = json.loads("\""+str(settingsFile.read().replace('\n', '').replace('\n\r', ''))+"\"")
                settingsFile.close()
                log('[        ] Loaded settings are: '+str(settings))
                return literal_eval(settings)
            except Exception as e:
                log('[        ] Creating new settings.conf')
                saveSettings()
                if(debugging):
                    raise e
                return defaultSettings
        except FileNotFoundError:
            log("[  WARN  ] Can't acces Zip Manager folder, creating settings...")
            saveSettings()
            return defaultSettings
    except FileNotFoundError:
        log("[  WARN  ] Can't acces .SomePythonThings folder, creating settings...")
        saveSettings()
        return defaultSettings

def openSettingsWindow():
    global zipManager, settings, settingsWindow
    settingsWindow = Window(zipManager)
    settingsWindow.setMinimumSize(500, 250)
    settingsWindow.setMaximumSize(500, 250)
    settingsWindow.setWindowTitle("SomePythonThings Zip Manager Settings")
    settingsWindow.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
    settingsWindow.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, False)
    settingsWindow.setWindowModality(QtCore.Qt.ApplicationModal)

    modeSelector = QtWidgets.QComboBox(settingsWindow)
    modeSelector.insertItem(0, 'Light')
    modeSelector.insertItem(1, 'Dark')
    if(_platform!='linux'):
        modeSelector.insertItem(2, 'Auto')
    modeSelector.resize(230, 30)
    modeSelector.move(250, 20)
    modeSelector.setObjectName("settingsCombo")
    modeSelectorLabel = QtWidgets.QLabel(settingsWindow)
    modeSelectorLabel.setText("Application mode: ")
    modeSelectorLabel.move(20, 20)
    modeSelectorLabel.setObjectName('settingsBackground')
    modeSelectorLabel.resize(230, 30)


    algorithmSelector = QtWidgets.QComboBox(settingsWindow)
    algorithmSelector.insertItem(0, 'Deflated')
    algorithmSelector.insertItem(1, 'BZIP2')
    algorithmSelector.insertItem(2, 'LZMA')
    algorithmSelector.insertItem(3, 'Without compression')
    algorithmSelector.resize(230, 30)
    algorithmSelector.setObjectName("settingsCombo")
    algorithmSelector.move(250, 60)
    algorithmSelectorLabel = QtWidgets.QLabel(settingsWindow)
    algorithmSelectorLabel.setText("Default compression algorithm: ")
    algorithmSelectorLabel.move(20, 60)
    algorithmSelectorLabel.setObjectName('settingsBackground')
    algorithmSelectorLabel.resize(230, 30)


    levelSelector = QtWidgets.QComboBox(settingsWindow)
    for i in range(1, 10):
        levelSelector.insertItem(i, str(i))
    levelSelector.resize(230, 30)
    levelSelector.setCurrentIndex(settings["default_level"]-1)
    levelSelector.setObjectName("settingsCombo")
    levelSelector.move(250, 100)
    levelSelectorLabel = QtWidgets.QLabel(settingsWindow)
    levelSelectorLabel.setText("Default compression level: ")
    levelSelectorLabel.move(20, 100)
    levelSelectorLabel.setObjectName('settingsBackground')
    levelSelectorLabel.resize(230, 30)

    create_subfolder = QtWidgets.QCheckBox(settingsWindow)
    create_subfolder.setChecked(settings["create_subdir"])
    create_subfolder.setText("Extract files and folders to a new directory")
    create_subfolder.setObjectName('settingsFullWidth')
    create_subfolder.move(20, 140)
    create_subfolder.resize(460, 30)

    saveButton = QtWidgets.QPushButton(settingsWindow)
    saveButton.setText("Save settings and close")
    saveButton.resize(460, 30)
    saveButton.move(20, 200)
    saveButton.setObjectName('normalbutton')
    saveButton.clicked.connect(partial(saveAndCloseSettings, modeSelector, algorithmSelector, settingsWindow, levelSelector, create_subfolder))

    try:
        if(settings['mode'].lower() == 'light'):
            modeSelector.setCurrentIndex(0)
        elif(settings['mode'].lower() == 'auto'):
            if(_platform!='linux'):
                modeSelector.setCurrentIndex(1)
            else:
                modeSelector.setCurrentIndex(0)
        elif(settings['mode'].lower() == 'dark'):
            modeSelector.setCurrentIndex(1)
        else:
            log("[  WARN  ] Could not detect mode!")
    except KeyError:
        log("[  WARN  ] Could not detect mode!")

    try:
        if(settings['default_algorithm'] == "Deflated"): #the "== False" is here to avoid eval of invalid values and crash of the program
            algorithmSelector.setCurrentIndex(0)
        elif(settings['default_algorithm'] == "BZIP2"):
            algorithmSelector.setCurrentIndex(1)
        elif(settings['default_algorithm'] == "LZMA"):
            algorithmSelector.setCurrentIndex(2)
        elif(settings['default_algorithm'] == "Without Compression"):
            algorithmSelector.setCurrentIndex(3)
        else:
            log("[  WARN  ] Could not set default algorithm!")
    except KeyError:
        log("[  WARN  ] Could not set default algorithm!")

    settingsWindow.show()

def saveAndCloseSettings(modeSelector, algorithmSelector, settingsWindow, levelSelector, create_subfolder):
    global settings, forceClose
    if(algorithmSelector.currentIndex() == 0):
        settings['default_algorithm'] = "Deflated"
    elif(algorithmSelector.currentIndex() == 1):
        settings['default_algorithm'] = "BZIP2"
    elif(algorithmSelector.currentIndex() == 2):
        settings['default_algorithm'] = "LZMA"
    else:
        settings['default_algorithm'] = "Without Compression"

    settings["create_subdir"] = create_subfolder.isChecked()

    if(modeSelector.currentIndex() == 0):
        settings['mode'] = 'light'
    elif(modeSelector.currentIndex() == 1):
        settings['mode'] = 'dark'
    else:
        settings['mode'] = 'auto'

    settings["default_level"] = levelSelector.currentIndex()+1

    forceClose = True
    settingsWindow.close()
    zipManager.setStyleSheet(getWindowStyleScheme())
    saveSettings(silent=False, create_subdir=settings['create_subdir'], default_level=settings['default_level'], default_algorithm=settings['default_algorithm'], mode=settings['mode'])

    if(settings['default_algorithm'] == "Deflated"):
        lists['compression'].setCurrentIndex(0)
    elif(settings['default_algorithm'] == "BZIP2"):
        lists['compression'].setCurrentIndex(1)
    elif(settings['default_algorithm'] == "LZMA"):
        lists['compression'].setCurrentIndex(2)
    else:
        lists['compression'].setCurrentIndex(3)

    sliders.compress_level.setValue(settings["default_level"])

    chkbx.create_subfolder.setChecked(settings["create_subdir"])


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------- Functions ---------------------------------------------------------------------------------- #
def extractFirstZip():
    log("[        ] Checking command line arguments")
    if zip != '':
        log('[   OK   ] Found one argument')
        try:
            if __name__ == "__main__":
                openZIP(zip.replace("\\", "/"))
        except Exception as e:
            if debugging:
                raise e
            throw_error("SomePythonThings Zip Manager",
                        "Unable to extract zip.\n\nReason:\n{0}".format(str(e)))

def getFileIcon(file):
    ext = getExtension(file).lower()
    if(ext in 'accdb;mdb;accde;mde;accdw;'.split(';')):
        return realpath+'/icons-zipmanager/access.ico'
    elif(ext in 'apk;'.split(';')):
        return realpath+'/icons-zipmanager/android.ico'
    elif(ext in 'bin;'.split(';')):
        return realpath+'/icons-zipmanager/bin.ico'
    elif(ext in 'java;jar;class;cpp;cc;cxx;h;hxx;hpp;js;project;ino;cs;'.split(';')):
        return realpath+'/icons-zipmanager/code.ico'
    elif(ext in 'conf;exe;deb;rpm;app;dat;dll;ini;log;sys:inf;cat;reg;'.split(';')):
        return realpath+'/icons-zipmanager/conf.ico'
    elif(ext in 'bmp;paint;gpaint;gdraw;'.split(';')):
        return realpath+'/icons-zipmanager/draw.ico'
    elif(ext in 'xl;xlsx;xlsm;xlsb;csv;gsheet;ods;xml;'.split(';')):
        return realpath+'/icons-zipmanager/excel.ico'
    elif(ext in 'swf;swt;swc;fla;wlv;'.split(';')):
        return realpath+'/icons-zipmanager/flash.ico'
    elif(ext in 'iso;img;cd;dvd;floppy;hdd;vdi;vmdk;disk;'.split(';')):
        return realpath+'/icons-zipmanager/iso.ico'
    elif(ext in 'md;'.split(';')):
        return realpath+'/icons-zipmanager/md.ico'
    elif(ext in 'mp3;wma;wav;ogg;flv;aiff;3gpp;m4a;mp2;'.split(';')):
        return realpath+'/icons-zipmanager/zipManager.ico'
    elif(ext in 'pdf;pdfa;'.split(';')):
        return realpath+'/icons-zipmanager/pdf.ico'
    elif(ext in 'png;jpg;jpeg;tiff;bmp;webp;svg;ico;gif;jfif;'.split(';')):
        return realpath+'/icons-zipmanager/picture.ico'
    elif(ext in 'pptx;ppt;pptm;odp;gslides;'.split(';')):
        return realpath+'/icons-zipmanager/powerpoint.ico'
    elif(ext in 'py;pyd;pyz;pym;'.split(';')):
        return realpath+'/icons-zipmanager/py.ico'
    elif(ext in 'sh;zsh;ash;bash;esh;'.split(';')):
        return realpath+'/icons-zipmanager/sh.ico'
    elif(ext in 'txt;rtf;'.split(';')):
        return realpath+'/icons-zipmanager/text.ico'
    elif(ext in 'torrent;'.split(';')):
        return realpath+'/icons-zipmanager/torrent.ico'
    elif(ext in 'mp4;wmv;mkv;avi;'.split(';')):
        return realpath+'/icons-zipmanager/video.ico'
    elif(ext in 'html;htm;php;mhtml;url;webp;web;webm;'.split(';')):
        return realpath+'/icons-zipmanager/web.ico'
    elif(ext in 'docx;doc;dotx;dotm;dot;odt;gdoc;'.split(';')):
        return realpath+'/icons-zipmanager/word.ico'
    elif(ext in 'psd;'.split(';')):
        return realpath+'/icons-zipmanager/photoshop.ico'
    elif(ext in 'zip;rar;7z;'.split(';')):
        return realpath+'/icons-zipmanager/zip.ico'
    else:
        return realpath+'/icons-zipmanager/unknown.ico'   

def getExtension(file):
    if(file.split('.')==1):
        return 'none'
    else:
        return (file.split('.'))[-1]

def clearZip():
    global zip
    zip = ''
    while(filesToExtract.topLevelItemCount()>0):
        filesToExtract.takeTopLevelItem(0)
    log('[   OK   ] files to extract from zip list cleared')

def clearFiles():
    global files
    files = []
    while(filesToCompress.topLevelItemCount()>0):
        filesToCompress.takeTopLevelItem(0)
    log('[   OK   ] File list cleared')

def clearSelectedFiles():
    global files
    selectedFiles = filesToCompress.selectedItems()
    actualFiles = []
    for file in files:
        actualFiles.append(file[0])
    for item in selectedFiles:
        files.remove(files[actualFiles.index(item.text(3)+"/"+item.text(0))])
        filesToCompress.takeTopLevelItem(filesToCompress.indexOfTopLevelItem(item))
        actualFiles = []
        for file in files:
            actualFiles.append(file[0])
    log('[   OK   ] Selected files removed from file list')

def refreshProgressbar(progressbar, actual, total):
    global progressbars, zipManager
    if(_platform=='win32'):
        global taskbprogress
        get_updater().call_in_main(taskbprogress.setRange, 0, int(total))
        get_updater().call_in_main(taskbprogress.setValue, int(actual))
        if(actual==0):
            get_updater().call_in_main(taskbprogress.hide)
            get_updater().call_in_main(taskbprogress.setRange, 0, 1)
            get_updater().call_in_main(taskbprogress.setValue, 0)
        else:
            get_updater().call_in_main(taskbprogress.show)
    if(progressbar=='extract'):
        get_updater().call_in_main(progressbars[progressbar].setFormat, "Extracted %v out of %m files (%p%)")
    else:
        get_updater().call_in_main(progressbars[progressbar].setFormat, "Compressed %v out of %m files (%p%)")
    get_updater().call_in_main(progressbars[progressbar].setMaximum, (int(total)))
    get_updater().call_in_main(progressbars[progressbar].setValue, (int(actual)))

def installationProgressBar(action = 'Downloading', actual = 1, total=2):
    global progressbars, zipManager
    if(_platform=="win32"):
        global taskbprogress
    if(action=="Stop"):
        if(_platform=='win32'):
            get_updater().call_in_main(taskbprogress.hide)
        get_updater().call_in_main(progressbars['extract'].setTextVisible, True)
        get_updater().call_in_main(progressbars['extract'].setFormat, "")
        get_updater().call_in_main(progressbars['extract'].setAlignment, QtCore.Qt.AlignCenter)
        get_updater().call_in_main(progressbars['extract'].setMaximum, 1)
        get_updater().call_in_main(progressbars['extract'].setMinimum, 0)
        get_updater().call_in_main(progressbars['extract'].setValue, 0)
        get_updater().call_in_main(progressbars['create'].setTextVisible, True)
        get_updater().call_in_main(progressbars['create'].setFormat, "")
        get_updater().call_in_main(progressbars['create'].setAlignment, QtCore.Qt.AlignCenter)
        get_updater().call_in_main(progressbars['create'].setMaximum, 1)
        get_updater().call_in_main(progressbars['create'].setMinimum, 0)
        get_updater().call_in_main(progressbars['create'].setValue, 0)
    else:
        if(_platform=='win32'):
            get_updater().call_in_main(taskbprogress.setRange, 0, 0)
            get_updater().call_in_main(taskbprogress.setValue, 0)
            get_updater().call_in_main(taskbprogress.show)
        get_updater().call_in_main(progressbars['extract'].setTextVisible, True)
        get_updater().call_in_main(progressbars['extract'].setFormat, str(action)+" the update...")
        get_updater().call_in_main(progressbars['extract'].setAlignment, QtCore.Qt.AlignCenter)
        get_updater().call_in_main(progressbars['extract'].setMaximum, 0)
        get_updater().call_in_main(progressbars['extract'].setMinimum, 0)
        get_updater().call_in_main(progressbars['extract'].setValue, 0)
        get_updater().call_in_main(progressbars['create'].setTextVisible, True)
        get_updater().call_in_main(progressbars['create'].setFormat, str(action)+" the update...")
        get_updater().call_in_main(progressbars['create'].setAlignment, QtCore.Qt.AlignCenter)
        get_updater().call_in_main(progressbars['create'].setMaximum, total)
        get_updater().call_in_main(progressbars['create'].setMinimum, 0)
        get_updater().call_in_main(progressbars['create'].setValue, actual)

def pureCompress(zipObj, a, b, compression_algorithm):
    global errorWhileCompressing, compression_level
    errorWhileCompressing = None
    try:
        zipObj.write(a, b, compression_algorithm, compression_level)
    except Exception as e:
        errorWhileCompressing = e

def heavy_createZip(zipfilename, files):
    global zipManager, continueCreating, allDone, progressbars, errorWhileCompressing
    try:
        zipObj = ZipFile(zipfilename, 'w')
        totalFiles = 0
        i = 0
        for path in files:
            item = filesToCompress.takeTopLevelItem(0)
            item.setIcon(0, QtGui.QIcon(realpath+"/icons-zipmanager/not.ico"))
            item.setText(2, "Queued")
            get_updater().call_in_main(filesToCompress.addTopLevelItem, item)
            log(path)
            if path[-1] == 'file':
                totalFiles += 1
                i += 1
            elif path[-1] == 'folder':
                if path[0] == '' or path[1] == '':
                    if path[0] == '':
                        files[i][0] = './'
                    if path[1] == '':
                        files[i][1] = './'
                    os.chdir(files[i][1])
                    i += 1
                    for folderName, subfolders, filenames in os.walk('./'):
                        for filename in filenames:
                            totalFiles += 1
                else:
                    os.chdir(path[1])
                    i += 1
                    for folderName, subfolders, filenames in os.walk('./'):
                        for filename in filenames:
                            totalFiles += 1
        log('[  INFO  ] Total number of files: '+str(totalFiles))
        progressbars['create'].setMaximum(totalFiles)
        actualFile = 0
        try:
            compression_type = compression_rate[lists['compression'].currentIndex()]
            log("[   OK   ] Selected compression algorithm is {0}".format(lists['compression'].currentIndex()))
            refreshProgressbar('create', 0, totalFiles)
        except Exception as e:
            if(debugging):
                raise e
            get_updater().call_in_main(throw_warning, "SomePythonThongs Zip Manager", "An error occurred while selecting your desired compression algorithm. Compression algorithm will be \"Deflated\". ")
            compression_type = zipfile.ZIP_DEFLATED
        continueCreating = True
        fileNumber=0
        errors = ""
        for path in files:
            if(fileNumber != 0):
                try:
                    item = filesToCompress.takeTopLevelItem(0)
                    item.setIcon(0, QtGui.QIcon(realpath+"/icons-zipmanager/done.ico"))
                    item.setText(2, "Done")
                    get_updater().call_in_main(filesToCompress.addTopLevelItem, item)
                    time.sleep(0.01)
                except AttributeError:
                    pass
            try:
                item = filesToCompress.takeTopLevelItem(0)
                item.setIcon(0, QtGui.QIcon(realpath+"/icons-zipmanager/loading.ico"))
                item.setText(2, "Compressing")
                get_updater().call_in_main(filesToCompress.insertTopLevelItem, 0, item)
            except AttributeError:
                pass
            fileNumber += 1
            if path[2] == 'file':
                try:
                    os.chdir(path[1])
                    if not zipfilename == path[0]:
                        t = KillableThread(target=pureCompress, args=(zipObj, path[0].split('/')[-1], path[0].split('/')[-1], compression_type,))
                        t.daemon = True
                        t.start()
                        while t.is_alive():
                            if not continueCreating:
                                log("[  WARN  ] User cancelled the zip creation!")
                                toggleCompressingState()
                                get_updater().call_in_main(progressbars['create'].setMaximum, 1)
                                get_updater().call_in_main(progressbars['create'].setValue, 0)
                                get_updater().call_in_main(progressbars['create'].setFormat, "")
                                get_updater().call_in_main(taskbprogress.hide)
                                t.shouldBeRuning=False
                                get_updater().call_in_main(throw_warning, "SomePythonThings Zip Manager", "User cancelled the zip creation")
                                time.sleep(0.5)
                                zipObj.close()
                                try: 
                                    os.remove(zipfilename)
                                except: 
                                    log("[  WARN  ] Unable to remove zip file")
                                files = []
                                sys.exit("User Killed zip creation process")
                            else:
                                time.sleep(0.01)
                        t.join()
                        if(errorWhileCompressing != None):
                            raise errorWhileCompressing
                        log('[   OK   ] File "'+str(path[0].split('/')[-1])+'" added successfully')
                    else:
                        log('[  WARN  ] File "'+str(path[0].split('/')[-1])+'" skipped because it is the output zip')
                except Exception as e:
                    allDone = False
                    log('[ FAILED ] Unable to add file "'+str(path)+'"')
                    errors += str(path)+"\n"
                finally:
                    actualFile += 1
                    refreshProgressbar('create', actualFile, totalFiles)
            elif path[2] == 'folder':
                try:
                    os.chdir(path[1])
                    for folderName, subfolders, filenames in os.walk('./'):
                        for filename in filenames:
                            try:
                                actualFile += 1
                                refreshProgressbar('create', actualFile, totalFiles)
                                if not(filename[0:2] == '._'):
                                    filePath = './' + path[0].split('/')[-1] + '/'+folderName+'/'+filename
                                    if not os.path.abspath(filename).replace('\\', '/') == zipfilename:
                                        t = KillableThread(target=pureCompress, args=(zipObj, folderName+'/'+filename, filePath, compression_type,))
                                        t.daemon = True
                                        t.start()
                                        while t.is_alive():
                                            if not continueCreating:
                                                log("[  WARN  ] User cancelled the zip creation!")
                                                toggleCompressingState()
                                                get_updater().call_in_main(progressbars['create'].setMaximum, 1)
                                                get_updater().call_in_main(progressbars['create'].setValue, 0)
                                                get_updater().call_in_main(progressbars['create'].setFormat, "")
                                                get_updater().call_in_main(taskbprogress.hide)
                                                t.shouldBeRuning=False
                                                get_updater().call_in_main(throw_warning, "SomePythonThings Zip Manager", "User cancelled the zip creation")
                                                time.sleep(0.5)
                                                zipObj.close()
                                                try: 
                                                    os.remove(zipfilename)
                                                except: 
                                                    log("[  WARN  ] Unable to remove zip file")
                                                sys.exit("User Killed zip creation process")
                                            else:
                                                time.sleep(0.01)

                                        t.join()
                                        if(errorWhileCompressing != None):
                                            raise errorWhileCompressing
                                        log(f'[   OK   ] File {filename} added successfully')
                                    else:
                                        log(f'[  WARN  ] File \"'+str(os.path.abspath(filename).replace("\\", "/"))+'" skipped because it is the output zip')
                            except Exception as e:
                                log('[ FAILED ] Unable to add file '+filename)
                                errors += str(filename)+"\n"
                                allDone = False
                except Exception as e:
                    allDone = False
                    log('[ FAILED ] Unable to add folder "'+str(path)+'"')
                    errors += str(path)+"\n"
        allWidgets = []
        for i in range(filesToCompress.topLevelItemCount()):
            allWidgets.append(filesToCompress.takeTopLevelItem(i))
        i = 0
        zipObj.close()
        refreshProgressbar('create', totalFiles, totalFiles)
        notify("File compression done!", "SomePythonThings Zip Manager has finished compressing the selected files and folders.")
        if allDone:
            get_updater().call_in_main(throw_info, "SomepythonThings Zip Manager", 'The Zip file was created sucessfully!')
            log('[   OK   ] zip file created sucessfully')
        else:
            get_updater().call_in_main(throw_warning, "SomePythonThings Zip Manager", 'The Zip file was created with some errors: \n'+str(errors))
            log('[  WARN  ] zip file created with errors:\n'+str(errors))
        openOnExplorer(zipfilename)
        clearFiles()
        files = []
        toggleCompressingState()
        return 1
    except Exception as e:
        toggleCompressingState()
        if(debugging):
            raise e
        log('[ FAILED ] Error occurred while creating zip File')
        try:
            get_updater().call_in_main(throw_error, "SomePythonThings Zip Manager", "Unable to create zip file "+zipfilename+".\n\nError reason:\n"+str(e))
        except:
            get_updater().call_in_main(throw_error, "SomePythonThings Zip Manager", "Unable to create zip file.\n\nError reason:\n"+str(e))
        return 0

def cancelZipCreation():
    global continueCreating, files
    continueCreating = False
    log("[  WARN  ] Sending cancel signal to compression thread")

def cancelZipExtraction():
    global continueExtracting, zip
    zip = ''
    continueExtracting = False
    log("[  WARN  ] Sending cancel signal to extraction thread")

def createZip():
    global files, zipManager
    global allDone
    allDone = True
    try:
        log('[        ] Preparing zip file')
        if(len(files) < 1):
            throw_warning("SomePythonThings Zip Manager",
                          "Please add at least one file or one folder to the zip!")
            return 0
        zipfilename = QtWidgets.QFileDialog.getSaveFileName( zipManager, 'Save the zip file', files[0][0]+".zip", zip_files)[0]
        if zipfilename == "":
            log("[  WARN  ] User aborted dialog")
            return 0
        toggleCompressingState()
        file = open(zipfilename, 'w')
        log('[   OK   ] zip file created succesfully')
        zipfilename = str(file.name)
        file.close()
        log('[        ] Creating zip file on '+str(zipfilename))
        t = Thread(target=heavy_createZip, args=(zipfilename, files))
        t.daemon = True
        t.start()
    except Exception as e:
        toggleCompressingState()
        throw_error("SomePythonThings Zip Manager", "An error occurred while creating the compressed file.\n\nError details:\n"+str(e))
        if debugging:
            raise e

def openFile(openFiles="None"):
    global files, zipManager
    filepaths = []
    try:
        if(openFiles=="None" or openFiles == False):
            log('[        ] Dialog in process')
            filepaths = QtWidgets.QFileDialog.getOpenFileNames(zipManager, "Select some files to compress them", '')
            log('[   OK   ] Dialog Completed')
            if(filepaths[0] == []):
                log("[  WARN  ] User aborted dialog")
                return 0
        else:
            log('[        ] Not showing dialog, files passed as an argument...')
            filesToAdd = []
            for file in openFiles.split('\n'):
                file=str(file)
                if not(file==""):
                    if(_platform=='win32' and file[0]=="/"):
                        file = file[1:]
                    filesToAdd.append(file)
            filepaths.append(filesToAdd)
        for filepath in filepaths[0]:
            if(os.path.isdir(filepath)):
                openFolder(folder=filepath)
            else:
                file = open(filepath, 'r')
                filename = file.name
                file.close()
                try:
                    if([filename, os.path.dirname(filename), 'file'] in files):
                        log("[  WARN  ] File already there!")
                        if(QtWidgets.QMessageBox.question(zipManager, "The file is already there!", f"The file {filename} is already selected to be compressed. Do tou want to add it anyway?",
                                                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes):
                            files.append([filename, os.path.dirname(filename), 'file'])
                            log("[   OK   ] File added anyway")
                            goAhead = True
                        else:
                            log("[   OK   ] File ommitted")
                            goAhead = False
                    else:
                        log("[        ] File not present in file list, adding it.")
                        files.append([filename, os.path.dirname(filename), 'file'])
                        goAhead=True
                    if(goAhead):
                        log('[   OK   ] File "'+str(filename)+'" processed')
                        item = QtWidgets.QTreeWidgetItem()
                        item.setText(0, filename.split('/')[-1])
                        item.setText(1, "{0:.3f} MB".format(os.path.getsize(filename)/1000000))
                        item.setText(2, "Pending")
                        item.setText(3, "/".join(filename.split('/')[0:-1]))
                        try:
                            item.setIcon(0, QtGui.QIcon(getFileIcon(filename)))
                        except:
                            pass
                        filesToCompress.addTopLevelItem(item)
                except Exception as e:
                    log('[ FAILED ] Unable to process file "'+filepath+'"')
                    if(debugging):
                        raise e
                    throw_error("Error processing file!","Unable to read file \""+filename+"\"")
                    try:
                        file.close()
                    except:
                        pass
    except Exception as e:
        if debugging:
            raise e
        throw_error("SomePythonThings Zip Manager", "An error occurred while adding one or more files. \n\nError detsils: "+str(e))
        log('[ FAILED ] Unable to open file. Returning value 0')

def reinstallZipManager():
    log('[        ] starting reinstall process...')
    Thread(target=checkUpdates_py, args=("True",), daemon=True).start()

def openFolder(folder=""):
    global files, zipManager
    log('[        ] Dialog in process')
    if(folder=="" or folder==False):
        folder = QtWidgets.QFileDialog.getExistingDirectory(zipManager, 'Select a folder to compress it')
        if folder == "":
            log("[  WARN  ] User aborted the dialog")
            return 0
    else:
        log("[  WARN  ] Folder was given as argument")
    log('[   OK   ] Dialog Completed')
    try:
        files.append([folder, folder, 'folder'])
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, folder.split('/')[-1])
        item.setText(1, "{0:.3f} MB".format(get_size(folder)))
        item.setText(2, "Pending")
        item.setText(3, "/".join(folder.split('/')[0:-1]))
        try:
            item.setIcon(0, QtGui.QIcon(realpath+"/icons-zipmanager/folder.ico"))
        except:
            pass
        filesToCompress.addTopLevelItem(item)
        log('[   OK   ] Folder selected. Returning value "'+str(files[-1])+'"')
        return str(folder)
    except Exception as e:
        if debugging:
            raise e
        log('[ FAILED ] openFolder() failed. Returning value 0')
        throw_error("Error processing folder!", "Unable to read folder \""+folder+"\"")

def get_size(start_path):
    total_size = 0
    for dirpath, _, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += int(os.path.getsize(fp)/1000000)

    return total_size

def openZIP(filepath=None):
    global zip
    try:
        if(filepath!=False and os.path.exists(filepath)):
            filepath = [filepath]
            log('[   OK   ] Zip file given by commandline')
        else:
            log('[        ] Dialog in process')
            filepath = QtWidgets.QFileDialog.getOpenFileName(zipManager, 'Select a zip file to extract it', '', zip_files)
            if(filepath[0] == ""):
                log("[  WARN  ] User aborted the dialog")
                return 0
        file = open(filepath[0], 'r')
        log('[   OK   ] Dialog Completed')
        supposedZip = str(file.name)
        log('[        ] Closing file')
        file.close()
        log('[   OK   ] File Closed.')
        if not zipfile.is_zipfile(supposedZip):
            throw_error("Error", f"The file {supposedZip} is not a valid zip file!")
            return
        else:
            clearZip()
            zip = supposedZip
            zipFile = zipfile.ZipFile(zip)
            zipInfoTable.setItem(0, 0, QtWidgets.QTableWidgetItem(str(zip.split('/')[-1]), 0))
            zipInfoTable.setItem(0, 1, QtWidgets.QTableWidgetItem(str('/'.join(zip.split('/')[0:-1])), 0))
            zipInfoTable.setItem(0, 2, QtWidgets.QTableWidgetItem("{0:.3f} MB".format(os.path.getsize(zip)/1000000), 0))
            for file in zipFile.namelist():
                fileInfo = zipFile.getinfo(file)
                item = QtWidgets.QTreeWidgetItem()
                item.setText(0, file.split('/')[-1])
                originalPath = file.split('/')
                originalPath[0] = zip.split('/')[-1]
                item.setText(1, "{0:.3f} MB".format(fileInfo.file_size/1000000))
                item.setText(2, "{0:.3f} MB".format(fileInfo.compress_size/1000000))
                item.setText(3, "/".join(originalPath))
                try:
                    item.setIcon(0, QtGui.QIcon(getFileIcon(file)))
                except:
                    pass
                filesToExtract.addTopLevelItem(item)
    except Exception as e:
        throw_error("SomePythonThings Zip Manager", "Unable to select zip file.\n\nReason:\n"+str(e))
        if(debugging):
            raise e

def pure_extract(zipObj, file, directory, passwd=""):
    global errorWhileExtracting
    errorWhileExtracting = None
    try:
        zipObj.extract(file, directory)
    except Exception as e:
        errorWhileExtracting = e

def extractZip():
    global zip
    if(zip == ''):
        throw_warning("SomePythonThings Zip Manager", "Please select one zip file to start the extraction.")
    else:
        try:
            zip = zip.replace("\\", "/")
            log('[        ] Dialog in proccess')
            directory = QtWidgets.QFileDialog.getExistingDirectory(zipManager, 'Select the destination folder where the zip is going to be extracted')
            if(directory == ''):
                log("[  WARN  ] User aborted the dialog")
                return 0
            log('[   OK   ] zip file selected successfully')
            directory = str(directory)
            if not(directory == ''):
                toggleExtractingState()
                print(directory)
                if(chkbx.create_subfolder.isChecked()):
                    log("[        ] Creating subdirectory...")
                    directory += "/"+zip.split('/')[-1]+"_extracted"
                log("[  INFO  ] Zip file will be extracted into "+directory)
                t = Thread(target=heavyExtract, args=(directory, zip))
                t.daemon = True
                t.start()
        except Exception as e:
            if debugging:
                raise e
            log('[ FAILED ] Error occurred while extracting zip File')
            throw_error("SomePythonThings Zip Manager",
                        'Unable to extract the zip\n\nReason:\n'+str(e))

def heavyExtract(directory, zip, password=""):
    try:
        global continueExtracting, errorWhileExtracting
        continueExtracting=True
        error = False
        log('[        ] Extracting zip file on '+str(directory))
        totalFiles = 0
        archive = ZipFile(zip)
        for file in archive.namelist():
            totalFiles += 1
        actualFile = 0
        if(password!=""):
            archive.setpassword(bytes(password, 'utf-8'))
        for file in archive.namelist():
            try:
                refreshProgressbar('extract', actualFile, totalFiles)
                t = KillableThread(target=pure_extract, args=( archive, file, directory, password))
                t.daemon = True
                t.start()
                while t.is_alive():
                    if not continueExtracting:
                        log("[  WARN  ] User cancelled the zip extraction!")
                        toggleExtractingState()
                        get_updater().call_in_main(progressbars['extract'].setMaximum, 1)
                        get_updater().call_in_main(progressbars['extract'].setValue, 0)
                        get_updater().call_in_main(progressbars['extract'].setFormat, "")
                        get_updater().call_in_main(taskbprogress.hide)
                        t.shouldBeRuning=False
                        get_updater().call_in_main(throw_warning, "SomePythonThings Zip Manager", "User cancelled the zip extraction")
                        archive.close()
                        sys.exit("User killed zip creation process")
                    else:
                        time.sleep(0.01)
                t.join()
                if(errorWhileExtracting!=None):
                    raise errorWhileExtracting
                log('[   OK   ] File '+file.split('/')[-1]+' extracted successfully')
            except Exception as e:
                log('[  WARN  ] Unable to extract file ' +file.split('/')[-1])
                get_updater().call_in_main(throw_warning,"SomePythonThings Zip Manager", 'Unable to extract file '+file.split('/')[-1]+"\n\nReason:\n"+str(e))
                error = True
            finally:
                actualFile += 1
        refreshProgressbar('extract', totalFiles, totalFiles)
        zip = ''
        time.sleep(0.1)
        notify("File extraction done!", "SomePythonThings Zip Manager has finished extracting the selected files and folders.")
        toggleExtractingState()
        if error:
            log('[  WARN  ] Zip file extracted with some errors')
            get_updater().call_in_main(throw_warning,"SomePythonThings Zip Manager", 'Zip file extracted with some errors')
        else:
            log('[   OK   ] Zip file extracted sucessfully')
            get_updater().call_in_main(throw_info,"SomePythonThings Zip Manager", 'Zip file extracted sucessfully')
        openOnExplorer(directory, force=True)
    except Exception as e:
        if debugging:
            raise e
        toggleExtractingState()
        log('[ FAILED ] Error occurred while extracting zip File')
        get_updater().call_in_main(throw_error, "SomePythonThings Zip Manager", 'Unable to extract the zip\n\nReason:\n'+str(e))

def throw_info(title, body, icon="zip_ok.ico"):
    if(icon==False):
        icon='zip_ok.ico'
    log("[  INFO  ] "+body)
    msg = QtWidgets.QMessageBox(zipManager)
    if(os.path.exists(str(realpath)+"/icons-zipmanager/"+str(icon))):
        msg.setIconPixmap(QtGui.QPixmap(str(realpath)+"/icons-zipmanager/"+str(icon)).scaledToHeight(96, QtCore.Qt.SmoothTransformation))
    else:
        msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText(body)
    msg.setWindowTitle(title)
    msg.exec_()

def throw_warning(title, body, warning=None, icon="zip_warn.ico"):
    global zipManager
    log("[  WARN  ] "+body)
    if(warning != None ):
        log("\t Warning reason: "+warning)
    msg = QtWidgets.QMessageBox(zipManager)
    if(os.path.exists(str(realpath)+"/icons-zipmanager/"+str(icon))):
        msg.setIconPixmap(QtGui.QPixmap(str(realpath)+"/icons-zipmanager/"+str(icon)).scaledToHeight(96, QtCore.Qt.SmoothTransformation))
    else:
        msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setText(body)
    msg.setWindowTitle(title)
    msg.exec_()

def throw_error(title, body, error="Not Specified", icon="zip_error.ico"):
    global zipManager
    log("[ FAILED ] "+body+"\n\tError reason: "+error)
    msg = QtWidgets.QMessageBox(zipManager)
    if(os.path.exists(str(realpath)+"/icons-zipmanager/"+str(icon))):
        msg.setIconPixmap(QtGui.QPixmap(str(realpath)+"/icons-zipmanager/"+str(icon)).scaledToHeight(96, QtCore.Qt.SmoothTransformation))
    else:
        msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setText(body)
    msg.setWindowTitle(title)
    msg.exec_()

def updates_thread():
    log("[        ] Starting check for updates thread...")
    checkUpdates_py()

def quitZipManager():
    log("[  INFO  ] Quitting application...")
    global zipManager
    zipManager.close()
    sys.exit()

def checkDirectUpdates():
    global actualVersion
    result = checkUpdates_py()
    if(result=='No'):
        throw_info("SomePythonThings Zip Manager Updater", "There aren't updates available at this time. \n(actual version is {0})".format(actualVersion))
    elif(result=="Unable"):
        throw_warning("SomePythonThings Zip Manager Updater", "Can't reach SomePythonThings Servers!\n  - Are you connected to the internet?\n  - Is your antivirus or firewall blocking SomePythonThings Zip Manager?\nIf none of these solved the problem, please check back later.")

def openHelp():
    webbrowser.open_new("http://www.somepythonthings.tk/programs/somepythonthings-zip-manager/help/")

def openOnExplorer(file, force=False):
    if    (_platform == 'win32'):
        try:
            os.system('start explorer /select,"{0}"'.format(file.replace("/", "\\")))
        except:
            log("[  WARN  ] Unable to show file {0} on file explorer.".format(file))
    elif (_platform == 'darwin'):
        if(force):
            try:
                os.system("open "+file)
            except:
                log("[  WARN  ] Unable to show file {0} on finder.".format(file))
        else:
            try:
                os.system("open "+("/".join(str(file).split("/")[:-1])))
            except:
                log("[  WARN  ] Unable to show file {0} on finder.".format(file))

    elif (_platform == 'linux' or _platform == 'linux2'):
        try:
            t = Thread(target=os.system, args=("xdg-open "+file,))
            t.daemon=True
            t.start()
        except:
            log("[  WARN  ] Unable to show file {0} on default file explorer.".format(file))

def changeCompressionRate():
    global compression_level
    compression_level = sliders.compress_level.value()
    lbls.compress_level.setText("Select compression rate (1-9): {}".format(compression_level))

def openLog():
    log("[        ] Opening log...")
    openOnExplorer(tempDir.name.replace('\\', '/')+'/log.txt', force=True)

def toggleCompressingState():
    global compressionRunning
    if(compressionRunning):
        compressionRunning = False
        get_updater().call_in_main(btns.cancel_compress.hide)
        get_updater().call_in_main(btns.create_zip.show)
    else:
        get_updater().call_in_main(btns.cancel_compress.show)
        get_updater().call_in_main(btns.create_zip.hide)
        compressionRunning = True

def toggleExtractingState():
    global extractionRunning
    if(extractionRunning):
        extractionRunning = False
        get_updater().call_in_main(btns.cancel_extract.hide)
        get_updater().call_in_main(btns.extract_zip.show)
    else:
        get_updater().call_in_main(btns.cancel_extract.show)
        get_updater().call_in_main(btns.extract_zip.hide)
        extractionRunning = True

def resizeWidgets():
    global zipManager, progressbars, font

    separation20=20
    separation10=10

    btn_full_width = int((zipManager.width()/2)-40)-10
    btn_half_width = int((((zipManager.width()/2)-40)/2)-10)
    # btn_full_height = int(((zipManager.height())-25)/5)+10 # This is saved for possible future use
    btn_half_height = 70#int(((zipManager.height())-25)/10)
    btn_quarter_height = 30#int(((zipManager.height())-25)/20)-5
    if(_platform == 'darwin'):
        btn_1st_row = separation20+25
    else:
        btn_1st_row = separation20+25
    btn_2nd_row = btn_1st_row+btn_quarter_height+separation10
    btn_3rd_row = btn_2nd_row+btn_quarter_height+separation10
    btn_4th_row = btn_3rd_row+btn_quarter_height+separation10
    btn_1st_column = 20
    btn_2nd_column = btn_1st_column+btn_half_width+10
    btn_3rd_column = int(zipManager.width()/2)+btn_1st_column
    btn_4th_column = int(zipManager.width()/2)+btn_2nd_column

    text_1st_row = int(btn_4th_row+btn_quarter_height+separation20)
    text_1st_column = btn_1st_column
    text_2nd_column = btn_3rd_column
    text_width = btn_full_width
    text_height = int((zipManager.height())-25)-text_1st_row - (30+10+70+20)

    pgsbar_1st_column = text_1st_column
    pgsbar_2nd_column = text_2nd_column
    pgsbar_1st_row = text_1st_row+text_height+separation20
    pgsbar_width = text_width
    pgsbar_height = 30

    btn_cancel_1st_row = pgsbar_1st_row+pgsbar_height+separation20

    btns.sel_file.resize(btn_half_width, btn_quarter_height)
    btns.sel_file.move(btn_1st_column, btn_1st_row)
    btns.sel_folder.resize(btn_half_width, btn_quarter_height)
    btns.sel_folder.move(btn_1st_column, btn_2nd_row)
    btns.create_zip.move(btn_1st_column, btn_cancel_1st_row)
    btns.create_zip.resize(btn_full_width, btn_half_height)
    btns.clear_files.move(btn_1st_column, btn_3rd_row)
    btns.clear_files.resize(btn_half_width, btn_quarter_height)
    btns.remove_file.move(btn_1st_column, btn_4th_row)
    btns.remove_file.resize(btn_half_width, btn_quarter_height)
    btns.select_zip.move(btn_3rd_column, btn_1st_row)
    btns.select_zip.resize(btn_half_width, btn_quarter_height)
    btns.extract_zip.move(btn_3rd_column, btn_cancel_1st_row)
    btns.extract_zip.resize(btn_full_width, btn_half_height)
    btns.cancel_compress.move(btn_1st_column, btn_cancel_1st_row)
    btns.cancel_compress.resize(btn_full_width, btn_half_height)
    btns.cancel_extract.move(btn_3rd_column, btn_cancel_1st_row)
    btns.cancel_extract.resize(btn_full_width, btn_half_height)
    
    chkbx.create_subfolder.resize(btn_half_width , btn_quarter_height)
    chkbx.create_subfolder.move(btn_4th_column, btn_1st_row)

    zipInfoTable.resize(btn_full_width, btn_half_height+btn_quarter_height+separation10)
    zipInfoTable.move(btn_3rd_column, btn_2nd_row)

    filesToCompress.move(btn_1st_column, text_1st_row)
    filesToCompress.resize(text_width, text_height)
    
    filesToExtract.move(btn_3rd_column, text_1st_row)
    filesToExtract.resize(text_width, text_height)
    
    progressbars["create"].setGeometry(pgsbar_1st_column, pgsbar_1st_row, pgsbar_width, pgsbar_height)
    progressbars["extract"].setGeometry( pgsbar_2nd_column, pgsbar_1st_row, pgsbar_width, pgsbar_height)

    lists['compression'].move(btn_2nd_column, int(btn_1st_row+btn_quarter_height+separation10/2))
    lists['compression'].resize(btn_half_width, int(btn_quarter_height+separation10/2))

    lbls.compression.move(btn_2nd_column, btn_1st_row)
    lbls.compression.resize(btn_half_width, int(btn_quarter_height+separation10/2))

    lbls.compress_level.move(btn_2nd_column, btn_3rd_row)
    lbls.compress_level.resize(btn_half_width, int(btn_quarter_height+separation10/2))

    sliders.compress_level.move(btn_2nd_column, int(btn_3rd_row+btn_quarter_height+separation10/2))
    sliders.compress_level.resize(btn_half_width, int(btn_quarter_height+separation10/2))
    

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------- Main Code ---------------------------------------------------------------------------------- #
if __name__ == "__main__":
    try:

        if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
            QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

        if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
            QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
        
        os.chdir(os.path.expanduser("~"))


        tempFile = tempfile.TemporaryFile()
        if(len(sys.argv)>1):
            zip = sys.argv[1]
            if('debug' in zip):
                debugging=True
        else:
            zip=''

        log("[        ] Actual directory is {0}".format(os.getcwd()))

        if _platform == "linux" or _platform == "linux2":
            log("[   OK   ] OS detected is linux")
            realpath="/bin"
            font = "Ubuntu"

        elif _platform == "darwin":
            log("[   OK   ] OS detected is macOS")
            font = "Lucida Grande"
            realpath = "/Applications/SomePythonThings Zip Manager.app/Contents/Resources"

        elif _platform == "win32":
            if int(platform.release()) >= 10: #Font check: os is windows 10
                font = "Segoe UI"#Cascadia Mono
                log("[   OK   ] OS detected is win32 release 10 ")
            else:# os is windows 7/8
                font="Segoe UI"
                log("[   OK   ] OS detected is win32 release 8 or less ")
            if(os.path.exists("\\Program Files\\SomePythonThingsZipManager")):
                realpath = "/Program Files/SomePythonThingsZipManager"
                log("[   OK   ] Directory set to /Program Files/SomePythonThingsZipManager/")
            else:
                realpath = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
                log("[  WARN  ] Directory /Program Files/SomePythonThingsZipManager/ not found, getting working directory...")
        else:
            log("[  WARN  ] Unable to detect OS")

        log("[   OK   ] Platform is {0}, font is {1} and real path is {2}".format(_platform, font, realpath))



        background_picture_path='{0}/background-zipmanager.png'.format(realpath.replace('c:', 'C:'))
        black_picture_path='{0}/black-zipmanager.png'.format(realpath.replace('c:', 'C:'))

        class TreeWidget(QtWidgets.QTreeWidget):

            def __init__(self, parent):
                super().__init__(parent)
                self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
                self.setDropIndicatorShown(True)
                self.setAcceptDrops(True)
                self.setSupportedDropActions = QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

            def dragEnterEvent(self, e):
                e.accept()

            def dragMoveEvent(self, e):
                e.accept()

            def dropEvent(self, e):
                openFile(str(e.mimeData().text().replace("file://", "")))

        class Ui_MainWindow(object):
            def setupUi(self, MainWindow):
                global background_picture_path
                self.centralwidget = QtWidgets.QWidget(MainWindow)
                self.centralwidget.setObjectName("centralwidget")
                self.centralwidget.setStyleSheet("""border-image: url(\""""+background_picture_path+"""\") 0 0 0 0 stretch stretch;""")
                log("[        ] Background picture real path is "+background_picture_path)
                MainWindow.setCentralWidget(self.centralwidget)
                QtCore.QMetaObject.connectSlotsByName(MainWindow)

        class Window(QtWidgets.QMainWindow):
            resized = QtCore.Signal()
            keyRelease = QtCore.Signal(int)

            def __init__(self, parent=None):
                super(Window, self).__init__(parent=parent)
                ui = Ui_MainWindow()
                ui.setupUi(self)
                self.resized.connect(resizeWidgets)

            def resizeEvent(self, event):
                self.resized.emit()
                return super(Window, self).resizeEvent(event)

            def closeEvent(self, event):
                if(compressionRunning):
                    log("[  WARN  ] Compresion running!")
                    if(QtWidgets.QMessageBox.question(self, "Warning", "A compression is running! Do you want to quit anyway?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes):
                        log("[   OK   ] Quitting anyway...")
                        event.accept()
                    else:
                        log("[   OK   ] Not quitting")
                        event.ignore()
                elif(extractionRunning):
                    log("[  WARN  ] Extraction running!")
                    if(QtWidgets.QMessageBox.question(self, "Warning", "An extraction is running! Do you want to quit anyway?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes):
                        log("[   OK   ] Quitting anyway...")
                        event.accept()
                    else:
                        log("[   OK   ] Not quitting")
                        event.ignore()
                else:
                    event.accept()

        class KillableThread(Thread): 
            def __init__(self, *args, **keywords): 
                Thread.__init__(self, *args, **keywords) 
                self.shouldBeRuning = True

            def start(self): 
                self._run = self.run 
                self.run = self.settrace_and_run
                Thread.start(self) 

            def settrace_and_run(self): 
                sys.settrace(self.globaltrace) 
                self._run()

            def globaltrace(self, frame, event, arg): 
                return self.localtrace if event == 'call' else None
                
            def localtrace(self, frame, event, arg): 
                if not(self.shouldBeRuning) and event == 'line': 
                    raise SystemExit() 
                return self.localtrace 

        QtWidgets.QApplication.setStyle('fusion')
        app = QtWidgets.QApplication(sys.argv)
        QtWidgets.QApplication.setStyle('fusion')
        zipManager = Window()

        try:
            readSettings = openSettings()
            i = 0
            for key in readSettings.keys():
                settings[key] = readSettings[key]
                i +=1
            log("[   OK   ] Settings loaded (settings={0})".format(str(settings)))
        except Exception as e:
            log("[ FAILED ] Unable to read settings! ({0})".format(str(e)))
            if(debugging):
                raise e

        zipManager.resize(1200, 700)
        zipManager.setWindowTitle('SomePythonThings Zip Manager') 
        zipManager.setStyleSheet(getWindowStyleScheme())
        try:
            zipManager.setWindowIcon(QtGui.QIcon("{0}/icon-zipmanager.png".format(realpath)))
        except:
            pass

        zipManager.setMinimumSize(600, 450)
        btns.sel_file = QtWidgets.QPushButton(zipManager)
        btns.sel_file.setText("Add file(s)")
        btns.sel_file.clicked.connect(openFile)
        btns.sel_file.setObjectName('normalbutton')
        btns.sel_folder = QtWidgets.QPushButton(zipManager)
        btns.sel_folder.setText("Add folder")
        btns.sel_folder.setObjectName('normalbutton')
        btns.sel_folder.clicked.connect(openFolder)
        btns.create_zip = QtWidgets.QPushButton(zipManager)
        btns.create_zip.setText("Create Zip")
        btns.create_zip.setObjectName('greenbutton')
        btns.create_zip.clicked.connect(createZip)
        btns.clear_files = QtWidgets.QPushButton(zipManager)
        btns.clear_files.setText("Clear file list")
        btns.clear_files.setObjectName('redbutton')
        btns.clear_files.clicked.connect(clearFiles)
        btns.remove_file = QtWidgets.QPushButton(zipManager)
        btns.remove_file.setText("Remove selected file(s)")
        btns.remove_file.setObjectName('redbutton')
        btns.remove_file.clicked.connect(clearSelectedFiles)
        btns.select_zip = QtWidgets.QPushButton(zipManager)
        btns.select_zip.setText("Select zip")
        btns.select_zip.setObjectName('normalbutton')
        btns.select_zip.clicked.connect(openZIP)
        btns.extract_zip = QtWidgets.QPushButton(zipManager)
        btns.extract_zip.setText("Extract Zip")
        btns.extract_zip.setObjectName('greenbutton')
        btns.extract_zip.clicked.connect(extractZip)
        btns.cancel_extract = QtWidgets.QPushButton(zipManager)
        btns.cancel_extract.setText("Cancel Extraction")
        btns.cancel_extract.setObjectName('redbutton')
        btns.cancel_extract.clicked.connect(cancelZipExtraction)
        btns.cancel_extract.hide()
        btns.cancel_compress = QtWidgets.QPushButton(zipManager)
        btns.cancel_compress.setText("Cancel Creation")
        btns.cancel_compress.setObjectName('redbutton')
        btns.cancel_compress.clicked.connect(cancelZipCreation)
        btns.cancel_compress.hide()

        progressbars["create"] = QtWidgets.QProgressBar(zipManager)
        progressbars["create"].setFormat("Compressed %v out of %m files (%p%)")
        progressbars["extract"] = QtWidgets.QProgressBar(zipManager)
        progressbars["extract"].setFormat("Extracted %v out of %m files (%p%)")

        zipInfoTable = QtWidgets.QTableWidget(zipManager)
        zipInfoTable.setRowCount(3)
        zipInfoTable.setColumnCount(1)
        zipInfoTable.setSelectionMode(QtWidgets.QTableWidget.NoSelection)
        zipInfoTable.setFocusPolicy(QtCore.Qt.NoFocus)
        zipInfoTable.setShowGrid(False)
        zipInfoTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        zipInfoTable.setColumnWidth(0, 100)
        zipInfoTable.setRowHeight(0, 24)
        zipInfoTable.setRowHeight(1, 24)
        zipInfoTable.setRowHeight(2, 24)
        zipInfoTable.horizontalHeader().setStretchLastSection(True)
        zipInfoTable.setVerticalScrollMode(QtWidgets.QTreeWidget.ScrollPerPixel)
        zipInfoTable.setHorizontalScrollMode(QtWidgets.QTreeWidget.ScrollPerPixel)
        zipInfoTable.setHorizontalHeaderLabels([" Zip File Information "])
        zipInfoTable.setVerticalHeaderLabels([" Name: ", " Location:", " Size: "])

        lbls.compression = QtWidgets.QLabel(zipManager)
        lbls.compression.setText('Select compression algorithm:')
        lbls.compression.setObjectName("halfTopLabel")

        lists['compression'] = QtWidgets.QComboBox(zipManager)
        i = 0
        for compression_type in ['Deflated', 'BZIP2', 'LZMA', 'Without Compression']:
            lists['compression'].insertItem(i, compression_type)
            i += 1

        if(settings['default_algorithm'] == "Deflated"):
            lists['compression'].setCurrentIndex(0)
        elif(settings['default_algorithm'] == "BZIP2"):
            lists['compression'].setCurrentIndex(1)
        elif(settings['default_algorithm'] == "LZMA"):
            lists['compression'].setCurrentIndex(2)
        else:
            lists['compression'].setCurrentIndex(3)

        lbls.compress_level = QtWidgets.QLabel(zipManager)
        lbls.compress_level.setText("Select compression rate (1-9): 5")
        lbls.compress_level.setObjectName("halfTopLabel")

        sliders.compress_level = QtWidgets.QSlider(zipManager)
        sliders.compress_level.setOrientation(QtCore.Qt.Horizontal)
        sliders.compress_level.setObjectName("scrollBarHalfBottom")
        sliders.compress_level.setMinimum(1)
        sliders.compress_level.setMaximum(9)
        sliders.compress_level.setValue(5)
        sliders.compress_level.setSingleStep(1)
        sliders.compress_level.setPageStep(1)
        sliders.compress_level.valueChanged.connect(changeCompressionRate)
        sliders.compress_level.setValue(settings["default_level"])

        chkbx.create_subfolder = QtWidgets.QCheckBox(zipManager)
        chkbx.create_subfolder.setChecked(True)
        chkbx.create_subfolder.setText("Create subfolder")
        chkbx.create_subfolder.setObjectName('quarterWidget')
        chkbx.create_subfolder.setChecked(settings["create_subdir"])

        filesToCompress = TreeWidget(zipManager)
        filesToCompress.setVerticalScrollMode(QtWidgets.QTreeWidget.ScrollPerPixel)
        filesToCompress.setHorizontalScrollMode(QtWidgets.QTreeWidget.ScrollPerPixel)
        filesToCompress.setColumnCount(3)
        filesToCompress.setHeaderLabels(["   Files to compress", "Size", "Status", "Location"])
        filesToCompress.setColumnHidden(0, False)
        filesToCompress.setColumnHidden(1, False)
        filesToCompress.setColumnWidth(0, 350)
        filesToCompress.setColumnWidth(1, 100)
        filesToCompress.setColumnWidth(2, 100)
        filesToCompress.setFocusPolicy(QtCore.Qt.NoFocus)
        filesToCompress.setIconSize(QtCore.QSize(24, 24))
        filesToCompress.setColumnWidth(3, 400)
        filesToCompress.setColumnHidden(2, False)

        filesToExtract = TreeWidget(zipManager)
        filesToExtract.setVerticalScrollMode(QtWidgets.QTreeWidget.ScrollPerPixel)
        filesToExtract.setHorizontalScrollMode(QtWidgets.QTreeWidget.ScrollPerPixel)
        filesToExtract.setColumnCount(3)
        filesToExtract.setHeaderLabels(["   Files to extract", "Real Size", "Compressed Size", "Location inside the zip file"])
        filesToExtract.setColumnHidden(0, False)
        filesToExtract.setColumnHidden(1, False)
        filesToExtract.setColumnWidth(0, 250)
        filesToExtract.setColumnWidth(1, 150)
        filesToExtract.setIconSize(QtCore.QSize(24, 24))
        filesToExtract.setColumnWidth(2, 150)
        filesToExtract.setColumnWidth(3, 300)
        filesToExtract.setColumnHidden(2, False)

        menuBar = zipManager.menuBar()
        menuBar.setNativeMenuBar(False)
        fileMenu = menuBar.addMenu("File")
        settingsMenu = menuBar.addMenu("Settings")
        helpMenu = menuBar.addMenu("Help")



        quitAction = QtWidgets.QAction(" Quit", zipManager)
        quitAction.triggered.connect(quitZipManager)
        fileMenu.addAction(quitAction)
        
        openSettingsAction = QtWidgets.QAction(" Settings    ", zipManager)
        openSettingsAction.triggered.connect(openSettingsWindow)
        settingsMenu.addAction(openSettingsAction)
        
        logAction = QtWidgets.QAction(" Open Log", zipManager)
        logAction.triggered.connect(openLog)
        settingsMenu.addAction(logAction)
        
        reinstallAction = QtWidgets.QAction(" Re-install SomePythonThings Zip Manager", zipManager)
        reinstallAction.triggered.connect(reinstallZipManager)
        settingsMenu.addAction(reinstallAction)
        
        openHelpAction = QtWidgets.QAction(" Online manual", zipManager)
        openHelpAction.triggered.connect(openHelp)
        helpMenu.addAction(openHelpAction)
        
        updatesAction = QtWidgets.QAction(" Check for updates", zipManager)
        updatesAction.triggered.connect(checkDirectUpdates)
        helpMenu.addAction(updatesAction)
        
        aboutAction = QtWidgets.QAction(" About SomePythonThings Zip Manager", zipManager)
        aboutAction.triggered.connect(partial(throw_info, "About SomePythonThings Zip Manager", "SomePythonThings Zip Manager\nVersion "+str(actualVersion)+"\n\nThe SomePythonThings Project\n\n © 2021 Martí Climent, SomePythonThings\nhttps://www.somepythonthings.tk\n\n\nThe iconset has a CC Non-Commercial Atribution 4.0 License"))
        helpMenu.addAction(aboutAction)

        if(_platform=='darwin'):
            openSettingsAction = QtWidgets.QAction("Settings...    ", zipManager)
            openSettingsAction.triggered.connect(openSettingsWindow)
            settingsMenu.addAction(openSettingsAction)
        
        if(_platform == "win32"):
            from PySide2 import QtWinExtras
            loadbutton = QtWinExtras.QWinTaskbarButton()
            loadbutton.setWindow(zipManager.windowHandle())
            taskbprogress = loadbutton.progress()
            taskbprogress.setRange(0, 100)
            taskbprogress.setValue(0)
            taskbprogress.show()

        try:
            if(os.path.isfile(zip)):
                extractFirstZip()
        except:
            zip = ''

        Thread(target=updates_thread, daemon=True).start()
        Thread(target=checkModeThread, daemon=True).start()

        log("[        ] Program loaded, starting UI...")
        zipManager.show()
        log("[   OK   ] UI Loaded")

        app.exec_()

        

    except Exception as e:
        log("[ FAILED ] A FATAL ERROR OCCURRED. PROGRAM WILL BE TERMINATED AFTER ERROR REPORT")
        try:
            throw_error('SomePythonThings Zip Manager', "SomePythonThings Zip Manager crashed because of a fatal error.\n\nAn Error Report will be generated and opened automatically\n\nSending the report would be very appreciated. Sorry for any inconveniences")
        except:
            pass
        os_info = f"" + \
        f"                        OS: {platform.system()}\n"+\
        f"                   Release: {platform.release()}\n"+\
        f"           OS Architecture: {platform.machine()}\n"+\
        f"          APP Architecture: {platform.architecture()[0]}\n"+\
        f"                   Program: SomePythonThings Zip Manager Version {actualVersion}"+\
        "\n\n-----------------------------------------------------------------------------------------"
        traceback_info = "Traceback (most recent call last):\n"
        try:
            for line in traceback.extract_tb(e.__traceback__).format():
                traceback_info += line
            traceback_info += f"\n{type(e).__name__}: {str(e)}"
        except:
            traceback_info += "\nUnable to get traceback"
            if(debugging):
                raise e
        f = open(tempDir.name.replace('\\', '/')+'/log.txt', 'r')
        webbrowser.open("https://www.somepythonthings.tk/error-report/?appName=SomePythonThings Zip Manager&errorBody="+os_info.replace('\n', '{newline}').replace(' ', '{space}')+"{newline}{newline}{newline}{newline}SomePythonThings Zip Manager Log:{newline}"+str(f.read()+"\n\n\n\n"+traceback_info).replace('\n', '{newline}').replace(' ', '{space}'))
        f.close()
        if(debugging):
            raise e
else:
    log("[ FAILED ] __name__ is not __main__, not running program!")
log('[  EXIT  ] Reached end of the script')

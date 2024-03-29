debugging = False
version = 4.3


import time, tempfile, os, json, sys, darkdetect, webbrowser, subprocess
from threading import Thread
from sys import platform as _platform
from PySide2 import QtWidgets, QtCore, QtGui
from ast import literal_eval
import winreg

if(len(sys.argv)>1):
    zip = sys.argv[1]
    if('debug' in zip):
        debugging=True

realpath = ""
dataToLog = []
app = None
tempDir = tempfile.TemporaryDirectory()

defaultSettings = {
    "default_algorithm": "Deflated",
    "default_level": 5,
    "create_subdir": True,
    "mode": "auto",
    "autoCheckForUpdates": True,
    "plainAppearance": False
}
settings = defaultSettings.copy()


if hasattr(sys, 'frozen'):
    realpath = sys._MEIPASS
else:
    realpath = '/'.join(sys.argv[0].replace("\\", "/").split("/")[:-1])


def getPath(file):
    return os.path.join(os.path.join(realpath, "res"), file).replace("\\", "/")

baseStyleSheet = """
QLabel QPushButton QTreeView{font-size: 11px;}
"""

def readRegedit(aKey, sKey, default, storage=winreg.HKEY_CURRENT_USER):
    registry = winreg.ConnectRegistry(None, storage)
    reg_keypath = aKey
    try:
        reg_key = winreg.OpenKey(registry, reg_keypath)
    except FileNotFoundError as e:
        return default
    except Exception as e:
        print(e)
        return default

    for i in range(1024):
        try:
            value_name, value, _ = winreg.EnumValue(reg_key, i)
            if value_name == sKey:
                return value
        except OSError as e:
            return default
        except Exception as e:
            print(e)
            return default

def setMainApp(newApp: QtWidgets.QApplication):
    global app
    app = newApp

def getColors() -> list:
    colors = ['215,226,228', '160,174,183', '101,116,134', '81,92,107', '69,78,94', '41,47,64', '15,18,36', '239,105,80']
    string = readRegedit(r"Software\Microsoft\Windows\CurrentVersion\Explorer\Accent", "AccentPalette", b'\xe9\xd8\xf1\x00\xcb\xb7\xde\x00\x96}\xbd\x00\x82g\xb0\x00gN\x97\x00H4s\x00#\x13K\x00\x88\x17\x98\x00')
    i = 0
    j = 0
    while (i+2)<len(string):
        colors[j] = f"{string[i]},{string[i+1]},{string[i+2]}"
        j += 1
        i += 4
    return colors

def log(s: str, force: bool = False) -> None:
    global debugging
    timePrefix = time.strftime('[%H:%M:%S] ', time.gmtime(time.time()))
    dataToLog.append(timePrefix+str(s))

log(f"[   OK   ] REALPATH set to \"{realpath}\"")

def logToFileWorker() -> None:
    print(f"[##:##:##] [   OK   ] File thread started on temp folder {tempDir.name}")
    while True:
        if len(dataToLog)>0:
            try:
                with open(tempDir.name.replace('\\', '/')+'/log.txt', "a+", errors="ignore") as log:
                    try:
                        if(debugging or "WARN" in str(dataToLog[0]) or "FAILED" in str(dataToLog[0])):
                            print(dataToLog[0])
                        log.write(dataToLog[0]+"\n")
                    except Exception as e:
                        log.write(f"!--- An error occurred while saving line, missing log line ---!   ({e})\n")
                del dataToLog[0]
            except NotADirectoryError:
                pass
        else:
            time.sleep(0.01)

def openLog() -> None:
    log("[        ] Opening log...")
    os.startfile(tempDir.name.replace('\\', '/')+'/log.txt')

def openOnExplorer(file: str, force: bool = True) -> None:
    if    (_platform == 'win32'):
        try:
            subprocess.run('start explorer /select,"{0}"'.format(file.replace("/", "\\")), shell=True)
        except:
            log("[  WARN  ] Unable to show file {0} on file explorer.".format(file))

class CheckModeThread(QtCore.QThread):
    refreshTheme = QtCore.Signal()
    shouldBeRunning = True

    def __init__(self):
        super().__init__()
        self.setTerminationEnabled(True)

    def run(self) -> None:
        log("[  INFO  ] New theme check thread spawned")
        lastModeWasLight = darkdetect.isLight()
        while self.shouldBeRunning:
            if(lastModeWasLight!=darkdetect.isLight()):
                log("[   OK   ] Theme changed, emitting signal...")
                self.refreshTheme.emit()
                lastModeWasLight = darkdetect.isLight()
            time.sleep(0.01)

def saveSettings(silent=True, default_algorithm="Deflated", default_level=5, create_subdir=True, mode="auto", plainAppearance=None, autoCheckForUpdates=True) -> bool:
    if plainAppearance == None:
        plainAppearance = settings["plainAppearance"]
    
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
                "autoCheckForUpdates": autoCheckForUpdates,
                "plainAppearance": plainAppearance,
                }))
            settingsFile.close()
            log("[   OK   ] Settings saved successfully")
            return True
        except Exception as e:
            log('[        ] Creating new settings.conf')
            saveSettings()
            if(debugging):
                raise e
            return False
    except Exception as e:
        log("[ FAILED ] Unable to save settings")
        if(debugging):
            raise e
        return False

def openSettings() -> dict:
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

try:
    readSettings = openSettings()
    i = 0
    for key in readSettings.keys():
        settings[key] = readSettings[key]
        i +=1
    log("[   OK   ] Settings loaded (settings={0})".format(str(settings)))
except Exception as e:
    log("[ FAILED ] Unable to read settings! ({0})".format(str(e)))

def winIsLight() -> bool:
        mode = darkdetect.isLight()
        if(mode!=None):
            return mode
        else:
            return True

def openSettingsWindow(parent: QtWidgets.QMainWindow):
    global settings
    from FramelessWindow import QFramelessWindow
    settingsWindow = QFramelessWindow(parent)   
    settingsWindow.setFixedSize(400, 420)
    w = settingsWindow.width()
    h = settingsWindow.height()
    settingsWindow.move(
        parent.window().x()+(parent.window().width()-w)//2,
        parent.window().y()+(parent.window().height()-h)//2
    )
    settingsWindow.setWindowTitle("SomePythonThings Zip Manager Settings")
    settingsWindow.setObjectName("darkbackground")
    settingsWindow.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, False)
    settingsWindow.setWindowModality(QtCore.Qt.ApplicationModal)
    
    layout = QtWidgets.QVBoxLayout()

    settingsWindow.setCentralWidget(QtWidgets.QWidget())
    settingsWindow.centralWidget().setLayout(layout)


    themeSettings = QtWidgets.QGroupBox()
    themeSettings.setObjectName("lightbackground")
    themeSettings.setTitle("General")

    l = QtWidgets.QFormLayout()

    themeSettings.setLayout(l)

    modeSelector = QtWidgets.QComboBox()

    plainAppearance = CheckBoxAction()
    plainAppearance.setChecked(settings["plainAppearance"])
    plainAppearance.setText("")
    
    
    autoUpdate = CheckBoxAction()
    autoUpdate.setChecked(settings["autoCheckForUpdates"])
    autoUpdate.setText("")

    modeSelector.insertItem(0, 'Light')
    modeSelector.insertItem(1, 'Dark')
    modeSelector.insertItem(2, 'Auto')
    l.addRow("Check for updates at startup: ", autoUpdate)
    l.addRow("Follow system appearance: ", plainAppearance)
    l.addRow("Application theme: ", modeSelector)


    layout.addWidget(themeSettings)
    
    compressionSettings = QtWidgets.QGroupBox()
    compressionSettings.setObjectName("lightbackground")
    compressionSettings.setTitle("Compression Settings")
    l = QtWidgets.QFormLayout()
    compressionSettings.setLayout(l)

    algorithmSelector = QtWidgets.QComboBox()
    algorithmSelector.insertItem(0, 'Deflated')
    algorithmSelector.insertItem(1, 'BZIP2')
    algorithmSelector.insertItem(2, 'LZMA')
    algorithmSelector.insertItem(3, 'Without compression')
    l.addRow("Default compression algorithm: ", algorithmSelector)



    levelSelector = QtWidgets.QComboBox()
    for i in range(1, 10):
        levelSelector.insertItem(i, str(i))
    levelSelector.setCurrentIndex(settings["default_level"]-1)
    l.addRow("Default compression level: ", levelSelector)

    layout.addWidget(compressionSettings)

    extractionSettings = QtWidgets.QGroupBox()
    extractionSettings.setObjectName("lightbackground")
    extractionSettings.setTitle("Extraction Settings")
    l = QtWidgets.QFormLayout()
    extractionSettings.setLayout(l)


    create_subfolder = CheckBoxAction()
    create_subfolder.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    create_subfolder.setChecked(settings["create_subdir"])
    create_subfolder.setText("Enable/Disable")
    l.addRow("Extract files on new folder: ", create_subfolder)

    layout.addWidget(extractionSettings)
    layout.addStretch()

    saveButton = QtWidgets.QPushButton()
    saveButton.setText("Save settings and close")
    saveButton.setObjectName("AccentButton")
    saveButton.clicked.connect(lambda: saveAndCloseSettings(modeSelector, plainAppearance, algorithmSelector, settingsWindow, levelSelector, create_subfolder, parent, autoUpdate))
    layout.addWidget(saveButton)

    try:
        if(settings['mode'].lower() == 'light'):
            modeSelector.setCurrentIndex(0)
        elif(settings['mode'].lower() == 'auto'):
            modeSelector.setCurrentIndex(2)
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

    

def saveAndCloseSettings(modeSelector: QtWidgets.QComboBox, plainAppearance: QtWidgets.QCheckBox, algorithmSelector: QtWidgets.QComboBox, settingsWindow, levelSelector: QtWidgets.QComboBox, create_subfolder: QtWidgets.QCheckBox, parent, autoUpdate: QtWidgets.QCheckBox):
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

    settings["plainAppearance"] = plainAppearance.isChecked()
    
    settings["autoCheckForUpdates"] = autoUpdate.isChecked()
    
    parent.loadStyleSheet()

    settings["default_level"] = levelSelector.currentIndex()+1

    forceClose = True
    settingsWindow.close()
    saveSettings(silent=True, create_subdir=settings['create_subdir'], default_level=settings['default_level'], default_algorithm=settings['default_algorithm'], mode=settings['mode'], autoCheckForUpdates=settings["autoCheckForUpdates"])

def openHelp() -> None:
    webbrowser.open_new("https://github.com/martinet101/SomePythonThings-Zip-Manager/wiki")

def getExtension(file) -> str:
    if(file.split('.')==1):
        return 'none'
    else:
        return (file.split('.'))[-1]

fileIconProvider = QtWidgets.QFileIconProvider()
cachedIcons = {}

def getFileIcon(file: str, skipCacheOnExe: bool = False) -> QtGui.QIcon:
    ext = getExtension(file).lower()
    if(ext[-1]=="/"):
        ext = "folder"
    if ext in cachedIcons and (ext!="exe" or skipCacheOnExe):
        return cachedIcons[ext]
    else:
        fileInfo = QtCore.QFileInfo(file)
        icon = fileIconProvider.icon(fileInfo)
        if icon.isNull():
            icon = QtGui.QIcon(fileIconProvider.icon(fileInfo).pixmap(48, 48).scaledToHeight(24, QtCore.Qt.SmoothTransformation))
        cachedIcons[ext] = icon
        return icon

def showWindow(window: QtWidgets.QMainWindow) -> None:
    window.show()
    window.raise_()
    window.activateWindow()
    if not(window.isMaximized() or window.isFullScreen()):
        window.showNormal()

def notify(title: str, text: str, window: QtWidgets.QMainWindow = None) -> None:
    if(window):
        app.trayIcon.messageClicked.connect(lambda: showWindow(window))
        app.trayIcon.activated.connect(lambda: showWindow(window))
    try:
        app.trayIcon.showMessage(title, text)
    except AttributeError:
        log(f"[ FAILED ] Unable to show notification!!!\n\tTitle: {title}\n\t Body: {text} ")

def throwInfo(*args) -> None:
    app.w.throwInfo(*args)

def throwWarning(*args) -> None:
    app.w.throwInfo(*args)

def throwError(*args) -> None:
    app.w.throwInfo(*args)

def confirm(*args) -> QtWidgets.QAbstractButton:
    return app.w.throwInfo(*args)

class CheckBoxAction(QtWidgets.QWidget):
    def __init__(self, parent=None, text: str = "", checked: bool = False):
        super().__init__(parent=parent)
        self.setLayout(QtWidgets.QHBoxLayout(self))
        if not(settings["plainAppearance"]):
            if(settings["mode"] == "dark"):
                isLight = False
            elif(settings["mode"] == "light"):
                isLight = True
            else:
                isLight = winIsLight()
            if(isLight):
                self.setStyleSheet(f"""
                    QCheckBox::indicator {{width: 12px;height: 12px;}}
                    QCheckBox::indicator:checked{{background-color: #058fff;border-radius: 3px;image: url({getPath("checkCheckedBlack.png")});}}
                    QCheckBox::indicator:indeterminate{{background-color: #058fff;border-radius: 3px;image: url({getPath("checkUnknowndBlack.png")});}}
                    QCheckBox::indicator:unchecked{{background-color: transparent;border-radius: 3px;image: url({getPath("checkUncheckedBlack.png")});}}""")
            else:
                self.setStyleSheet(f"""
                    QCheckBox::indicator {{width: 12px;height: 12px;}}
                    QCheckBox::indicator:checked{{background-color: #058fff;border-radius: 3px;image: url({getPath("checkCheckedWhite.png")});}}
                    QCheckBox::indicator:indeterminate{{background-color: #058fff;border-radius: 3px;image: url({getPath("checkUnknowndWhite.png")});}}
                    QCheckBox::indicator:unchecked{{background-color: transparent;border-radius: 3px;image: url({getPath("checkUncheckedWhite.png")});}}""")
        self.label = QtWidgets.QLabel(text)
        self.layout().addWidget(self.label)
        self.layout().setMargin(1)
        self.check = QtWidgets.QCheckBox(self)
        self.layout().addWidget(self.check)
        self.check.setChecked(checked)
        self.check.stateChanged.connect(self.changeText)
        self.changeText()
    
    def setText(self, text: str) -> None:
        self.label.setText(text)
        
    def setEnabled(self, enabled: bool) -> None:
        self.check.setEnabled(enabled)
        self.changeText()
    
    def isChecked(self) -> bool:
        return self.check.isChecked()
    
    def changeText(self) -> None:
        if(self.check.isChecked()):
            self.check.setText("Enabled")
        else:
            self.check.setText("Disabled")
            
    def setChecked(self, value: bool) -> None:
        return self.check.setChecked(value)
    
    def setTristate(self, value: bool) -> None:
        return self.check.setTristate(value)



if(__name__ == "__main__"):
    import __init__

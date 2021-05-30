<<<<<<< Updated upstream
from PySide2 import QtWidgets, QtGui, QtCore
from Tools import *
#from Tools import log, openLog, openHelp, openSettingsWindow, getPath, CheckModeThread, baseStyleSheet, settings, version, realpath
import darkdetect, qtmodern.styles, sys, os
import qtmodern.styles
from sys import platform as _platform
from Compressor import Compressor
from Extractor import Extractor
from Welcome import Welcome
from Updater import checkForUpdates


class Window(QtWidgets.QMainWindow):
    resized = QtCore.Signal()
    keyRelease = QtCore.Signal(int)

    def __init__(self, app: QtWidgets.QApplication, parent=None):
        log("[        ] Creating a new window...")

        super(Window, self).__init__(parent=parent)

        self.setUnifiedTitleAndToolBarOnMac(True)


        self.app = app
        self.isCompressing = False
        self.isExtracting = False
        self.version = version
        self.setWindowIcon(QtGui.QIcon(getPath("zip.ico")))
        self.menuBarAlreadyCreated = False

        self.themeThread = CheckModeThread()
        self.themeThread.start()
        self.themeThread.refreshTheme.connect(self.loadStyleSheet)
        self.themeThread

        self.setWindowTitle("SomePythonThings Zip Manager")
        self.loadStyleSheet()
        self.setStyleSheet(baseStyleSheet)
        self.resize(1200, 700)
        self.setMinimumSize(600, 450)
        self.show()
        self.loadMenuBar()
        self.loadWidgets()
        self.installEventFilter(self)
        log("[   OK   ] Window loaded successfully")
        log("[        ] Calling updates thread...")
        checkForUpdates(self)

        if(_platform == "win32"):
                    from PySide2 import QtWinExtras
                    self.loadbutton = QtWinExtras.QWinTaskbarButton(self)
                    self.loadbutton.setWindow(self.windowHandle())
                    self.taskbprogress = self.loadbutton.progress()
                    self.taskbprogress.setRange(0, 100)
                    self.taskbprogress.setValue(0)
                    self.taskbprogress.hide()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.themeThread.shouldBeRunning = False
        self.themeThread.quit()
        self.themeThread.wait()
        import time
        time.sleep(1)
        return event.accept()
        
        

    def loadStyleSheet(self) -> None:
        if not(settings["plainAppearance"]):
            if(settings["mode"] == "dark"):
                isLight = False
            elif(settings["mode"] == "light"):
                isLight = True
            else:
                isLight = self.isLight()
            if(isLight):
                qtmodern.styles.light(self.app)
            else:
                qtmodern.styles.dark(self.app)
        else:
            self.app.setPalette(self.app.style().standardPalette())
            self.app.setStyleSheet("")
            if(_platform=="win32"):
                self.app.setStyle("windowsvista")
            elif(_platform=="darwin"):
                self.app.setStyle("macintosh")
            elif(_platform=="linux"):
                pass
                self.app.setStyle("gtk2")


                
    
    def isLight(self) -> bool:
        mode = darkdetect.isLight()
        if(mode!=None):
            return mode
        else:
            return True
    
    def addTab(self, widget: QtWidgets.QWidget, icon: QtGui.QIcon, title: str, closable: bool = True) -> int:
        button = QtWidgets.QPushButton(self)
        button.resize(QtCore.QSize(20, 20))
        button.setIconSize(QtCore.QSize(12, 12))
        button.setStyleSheet("""QPushButton{border: none}QPushButton::hover{border: 1px solid grey;border-radius:3px;}""")
        button.setIcon(QtGui.QIcon(getPath("not.ico")))
        i = self.tabWidget.addTab(widget, icon, title)
        if(closable):
            button.clicked.connect(lambda: self.tabWidget.removeTab(i))
            self.tabWidget.tabBar().setTabButton(i, QtWidgets.QTabBar.RightSide,  button)
            self.tabWidget.tabBar().setTabButton(i, QtWidgets.QTabBar.LeftSide,  None)

        return i

    def loadWidgets(self) -> None:
        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tabWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.tabWidget.setTabsClosable(False)
        self.setCentralWidget(self.tabWidget)
        
        self.addTab(Welcome(self), QtGui.QIcon(getPath("zip.ico")), "Home Page", closable=False)

    def addCompressTab(self) -> None:
        t = self.addTab(Compressor(self), QtGui.QIcon(getPath("compressFiles.ico")), "Compress Files")
        self.tabWidget.setCurrentIndex(t)

    def addExtractTab(self, zipFile: str = "") -> None:
        tabName = "Extract Files"
        if(zipFile != ""):
            tabName = zipFile.replace("\\", "/").split("/")[-1]
        t = self.addTab(Extractor(self, zipFile), QtGui.QIcon(getPath("extractFiles.ico")), tabName)
        self.tabWidget.setCurrentIndex(t)

    def createMenuBar(self, native: bool = False, macOS: bool = False) -> QtWidgets.QMenuBar:
        if not(self.menuBarAlreadyCreated):
            menuBar = self.menuBar()
            self.menuBarAlreadyCreated = True
        else:
            menuBar = QtWidgets.QMenuBar(self)
        menuBar.setNativeMenuBar(native)
        fileMenu = menuBar.addMenu("File")
        settingsMenu = menuBar.addMenu("Settings")
        helpMenu = menuBar.addMenu("Help")

        newAction = QtWidgets.QAction(" New window", self)
        newAction.triggered.connect(lambda: self.createNewWindow())
        newAction.setShortcut("Ctrl+N")
        fileMenu.addAction(newAction)

        compressAction = QtWidgets.QAction(" Compress files", self)
        compressAction.triggered.connect(lambda: self.addCompressTab())
        compressAction.setShortcut("")
        fileMenu.addAction(compressAction)

        extractAction = QtWidgets.QAction(" Extract files", self)
        extractAction.triggered.connect(lambda: self.addExtractTab())
        extractAction.setShortcut("")
        fileMenu.addAction(extractAction)

        closeAction = QtWidgets.QAction(" Close Window", self)
        closeAction.triggered.connect(lambda: self.close())
        closeAction.setShortcut("Ctrl+W")
        fileMenu.addAction(closeAction)

        quitAction = QtWidgets.QAction(" Quit", self)
        quitAction.triggered.connect(lambda: sys.exit(0))
        quitAction.setShortcut("Ctrl+Q")
        fileMenu.addAction(quitAction)

        openSettingsAction = QtWidgets.QAction(" Settings    ", self)
        openSettingsAction.triggered.connect(lambda: openSettingsWindow(self))
        settingsMenu.addAction(openSettingsAction)
        
        logAction = QtWidgets.QAction(" Open Log", self)
        logAction.triggered.connect(openLog)
        settingsMenu.addAction(logAction)
        
        reinstallAction = QtWidgets.QAction(" Re-install SomePythonThings Zip Manager", self)
        reinstallAction.triggered.connect(lambda: checkForUpdates(parent=self, force=True))
        settingsMenu.addAction(reinstallAction)
        
        openHelpAction = QtWidgets.QAction(" Online manual", self)
        openHelpAction.triggered.connect(lambda: openHelp())
        helpMenu.addAction(openHelpAction)
        
        updatesAction = QtWidgets.QAction(" Check for updates", self)
        updatesAction.triggered.connect(lambda: checkForUpdates(parent=self, verbose=True))
        helpMenu.addAction(updatesAction)
        
        aboutQtAction = QtWidgets.QAction(" About Qt framework   ", self)
        aboutQtAction.triggered.connect(lambda: QtWidgets.QMessageBox.aboutQt(self, "About the Qt framework - SomePythonThings Zip Manager"))
        helpMenu.addAction(aboutQtAction)
        
        aboutAction = QtWidgets.QAction(" About SomePythonThings Zip Manager", self)
        aboutAction.triggered.connect(lambda: self.throwInfo("About SomePythonThings Zip Manager", "SomePythonThings Zip Manager\nVersion "+str(self.version)+"\n\nThe SomePythonThings Project\n\n © 2021 Martí Climent, SomePythonThings\nhttps://www.somepythonthings.tk\n\n\nThe iconset has a CC Non-Commercial Atribution 4.0 License"))
        helpMenu.addAction(aboutAction)

        if(macOS):
            legacyAboutAction = QtWidgets.QAction("About", self)
            legacyAboutAction.triggered.connect(lambda: self.throwInfo("About SomePythonThings Zip Manager", "SomePythonThings Zip Manager\nVersion "+str(self.version)+"\n\nThe SomePythonThings Project\n\n © 2021 Martí Climent, SomePythonThings\nhttps://www.somepythonthings.tk\n\n\nThe iconset has a CC Non-Commercial Atribution 4.0 License"))
            helpMenu.addAction(legacyAboutAction)

            
            legacyOpenSettingsAction = QtWidgets.QAction("Settings", self)
            legacyOpenSettingsAction.triggered.connect(lambda: openSettingsWindow(self))
            settingsMenu.addAction(legacyOpenSettingsAction)


        return menuBar

    def loadMenuBar(self) -> None:
        if(_platform=="darwin"):
            self.createMenuBar(native=False) # Create non native menubar on macOS
        self.createMenuBar(native=True, macOS=_platform=="darwin") # Create native menubar

    def throwInfo(self, title: str, body: str) -> None:
        global music
        log("[  INFO  ] "+body)
        msg = QtWidgets.QMessageBox(self)
        if(os.path.exists(getPath("zip_ok.ico"))):
            msg.setIconPixmap(QtGui.QPixmap(str(getPath("zip_ok.ico"))).scaledToHeight(96, QtCore.Qt.SmoothTransformation))
        else:
            msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(body)
        if(_platform == 'darwin'):
            msg.setAutoFillBackground(True)
            msg.setWindowModality(QtCore.Qt.WindowModal)
            msg.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            msg.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
            msg.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
            msg.setModal(True)
            msg.setSizeGripEnabled(False)
        msg.setWindowTitle(title)
        msg.exec_()

    def throwWarning(self, title: str, body: str) -> None:
        log("[  WARN  ] "+body)
        msg = QtWidgets.QMessageBox(self)
        if(os.path.exists(getPath("zip_ok.ico"))):
            msg.setIconPixmap(QtGui.QPixmap(str(getPath("zip_warn.ico"))).scaledToHeight(96, QtCore.Qt.SmoothTransformation))
        else:
            msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(body)
        if(_platform == 'darwin'):
            msg.setAutoFillBackground(True)
            msg.setWindowModality(QtCore.Qt.WindowModal)
            msg.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            msg.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
            msg.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
            msg.setModal(True)
            msg.setSizeGripEnabled(False)
        msg.setWindowTitle(title)
        msg.exec_()



    def throwError(self, title: str, body: str) -> None:
        log("[ FAILED ] "+body)
        msg = QtWidgets.QMessageBox(self)
        if(os.path.exists(getPath("zip_ok.ico"))):
            msg.setIconPixmap(QtGui.QPixmap(str(getPath("zip_error.ico"))).scaledToHeight(96, QtCore.Qt.SmoothTransformation))
        else:
            msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(body)
        if(_platform == 'darwin'):
            msg.setAutoFillBackground(True)
            msg.setWindowModality(QtCore.Qt.WindowModal)
            msg.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            msg.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
            msg.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
            msg.setModal(True)
            msg.setSizeGripEnabled(False)
        msg.setWindowTitle(title)
        msg.exec_()

    def confirm(self, title: str, body: str, firstButton: QtWidgets.QAbstractButton, secondButton: QtWidgets.QAbstractButton, defaultButton: QtWidgets.QAbstractButton) -> QtWidgets.QAbstractButton:
        msg = QtWidgets.QMessageBox(self)
        log("[  WARN  ] "+body)
        if(os.path.exists(str(realpath)+"/icons-sptmusic/ok.png")):
            msg.setIconPixmap(QtGui.QPixmap(str(realpath)+"/icons-sptmusic/ok.png").scaledToHeight(96, QtCore.Qt.SmoothTransformation))
        else:
            msg.setIcon(QtWidgets.QMessageBox.Warning)
        
        if(_platform == 'darwin'):
            msg.setAutoFillBackground(True)
            msg.setWindowModality(QtCore.Qt.WindowModal)
            msg.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            msg.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
            msg.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
            msg.setModal(True)
            msg.setSizeGripEnabled(False)
        msg.setWindowTitle(title)
        msg.setText(body)
        msg.addButton(firstButton)
        msg.addButton(secondButton)
        msg.setDefaultButton(defaultButton)
        msg.exec_()
        return msg.standardButton(msg.clickedButton())




    def resizeEvent(self, event: QtCore.QEvent):
        self.resized.emit()
        return super(Window, self).resizeEvent(event)

    def closeEvent(self, event: QtCore.QEvent) -> None:
        self.themeThread.terminate()
        if(self.isCompressing):
            log("[  WARN  ] Compresion running!")
            if(QtWidgets.QMessageBox.question(self, "Warning", "A compression is running! Do you want to quit anyway?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes):
                log("[   OK   ] Quitting anyway...")
                event.accept()
            else:
                log("[   OK   ] Not quitting")
                event.ignore()
        elif(self.isExtracting):
            log("[  WARN  ] Extraction running!")
            if(QtWidgets.QMessageBox.question(self, "Warning", "An extraction is running! Do you want to quit anyway?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes):
                log("[   OK   ] Quitting anyway...")
                event.accept()
            else:
                log("[   OK   ] Not quitting")
                event.ignore()
        else:
            event.accept()

    def createNewWindow(self) -> None:
        Window(self.app)

if(__name__ == "__main__"):
=======
<<<<<<< HEAD
from PySide2 import QtWidgets, QtGui, QtCore
from Tools import *
#from Tools import log, openLog, openHelp, openSettingsWindow, getPath, CheckModeThread, baseStyleSheet, settings, version, realpath
import darkdetect, qtmodern.styles, sys, os
import qtmodern.styles
from sys import platform as _platform
from Compressor import Compressor
from Extractor import Extractor
from Welcome import Welcome
from Updater import checkForUpdates


class Window(QtWidgets.QMainWindow):
    resized = QtCore.Signal()
    keyRelease = QtCore.Signal(int)

    def __init__(self, app: QtWidgets.QApplication, parent=None):
        log("[        ] Creating a new window...")

        super(Window, self).__init__(parent=parent)

        self.setUnifiedTitleAndToolBarOnMac(True)


        self.app = app
        self.isCompressing = False
        self.isExtracting = False
        self.version = version
        self.setWindowIcon(QtGui.QIcon(getPath("zip.ico")))
        self.menuBarAlreadyCreated = False

        self.themeThread = CheckModeThread()
        self.themeThread.start()
        self.themeThread.refreshTheme.connect(self.loadStyleSheet)
        self.themeThread

        self.setWindowTitle("SomePythonThings Zip Manager")
        self.loadStyleSheet()
        self.setStyleSheet(baseStyleSheet)
        self.resize(1200, 700)
        self.setMinimumSize(600, 450)
        self.show()
        self.loadMenuBar()
        self.loadWidgets()
        self.installEventFilter(self)
        log("[   OK   ] Window loaded successfully")
        log("[        ] Calling updates thread...")
        checkForUpdates(self)

        if(_platform == "win32"):
                    from PySide2 import QtWinExtras
                    self.loadbutton = QtWinExtras.QWinTaskbarButton(self)
                    self.loadbutton.setWindow(self.windowHandle())
                    self.taskbprogress = self.loadbutton.progress()
                    self.taskbprogress.setRange(0, 100)
                    self.taskbprogress.setValue(0)
                    self.taskbprogress.hide()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.themeThread.shouldBeRunning = False
        self.themeThread.quit()
        self.themeThread.wait()
        import time
        time.sleep(1)
        return event.accept()
        
        

    def loadStyleSheet(self) -> None:
        if not(settings["plainAppearance"]):
            if(settings["mode"] == "dark"):
                isLight = False
            elif(settings["mode"] == "light"):
                isLight = True
            else:
                isLight = self.isLight()
            if(isLight):
                qtmodern.styles.light(self.app)
            else:
                qtmodern.styles.dark(self.app)
        else:
            self.app.setPalette(self.app.style().standardPalette())
            self.app.setStyleSheet("")
            if(_platform=="win32"):
                self.app.setStyle("windowsvista")
            elif(_platform=="darwin"):
                self.app.setStyle("macintosh")
            elif(_platform=="linux"):
                pass
                self.app.setStyle("gtk2")


                
    
    def isLight(self) -> bool:
        mode = darkdetect.isLight()
        if(mode!=None):
            return mode
        else:
            return True
    
    def addTab(self, widget: QtWidgets.QWidget, icon: QtGui.QIcon, title: str, closable: bool = True) -> int:
        button = QtWidgets.QPushButton(self)
        button.resize(QtCore.QSize(20, 20))
        button.setIconSize(QtCore.QSize(12, 12))
        button.setStyleSheet("""QPushButton{border: none}QPushButton::hover{border: 1px solid grey;border-radius:3px;}""")
        button.setIcon(QtGui.QIcon(getPath("not.ico")))
        i = self.tabWidget.addTab(widget, icon, title)
        if(closable):
            button.clicked.connect(lambda: self.tabWidget.removeTab(i))
            self.tabWidget.tabBar().setTabButton(i, QtWidgets.QTabBar.RightSide,  button)
            self.tabWidget.tabBar().setTabButton(i, QtWidgets.QTabBar.LeftSide,  None)

        return i

    def loadWidgets(self) -> None:
        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tabWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.tabWidget.setTabsClosable(False)
        self.setCentralWidget(self.tabWidget)
        
        self.addTab(Welcome(self), QtGui.QIcon(getPath("zip.ico")), "Home Page", closable=False)

    def addCompressTab(self) -> None:
        t = self.addTab(Compressor(self), QtGui.QIcon(getPath("compressFiles.ico")), "Compress Files")
        self.tabWidget.setCurrentIndex(t)

    def addExtractTab(self, zipFile: str = "") -> None:
        tabName = "Extract Files"
        if(zipFile != ""):
            tabName = zipFile.replace("\\", "/").split("/")[-1]
        t = self.addTab(Extractor(self, zipFile), QtGui.QIcon(getPath("extractFiles.ico")), tabName)
        self.tabWidget.setCurrentIndex(t)

    def createMenuBar(self, native: bool = False, macOS: bool = False) -> QtWidgets.QMenuBar:
        if not(self.menuBarAlreadyCreated):
            menuBar = self.menuBar()
            self.menuBarAlreadyCreated = True
        else:
            menuBar = QtWidgets.QMenuBar(self)
        menuBar.setNativeMenuBar(native)
        fileMenu = menuBar.addMenu("File")
        settingsMenu = menuBar.addMenu("Settings")
        helpMenu = menuBar.addMenu("Help")

        newAction = QtWidgets.QAction(" New window", self)
        newAction.triggered.connect(lambda: self.createNewWindow())
        newAction.setShortcut("Ctrl+N")
        fileMenu.addAction(newAction)

        compressAction = QtWidgets.QAction(" Compress files", self)
        compressAction.triggered.connect(lambda: self.addCompressTab())
        compressAction.setShortcut("")
        fileMenu.addAction(compressAction)

        extractAction = QtWidgets.QAction(" Extract files", self)
        extractAction.triggered.connect(lambda: self.addExtractTab())
        extractAction.setShortcut("")
        fileMenu.addAction(extractAction)

        closeAction = QtWidgets.QAction(" Close Window", self)
        closeAction.triggered.connect(lambda: self.close())
        closeAction.setShortcut("Ctrl+W")
        fileMenu.addAction(closeAction)

        quitAction = QtWidgets.QAction(" Quit", self)
        quitAction.triggered.connect(lambda: sys.exit(0))
        quitAction.setShortcut("Ctrl+Q")
        fileMenu.addAction(quitAction)

        openSettingsAction = QtWidgets.QAction(" Settings    ", self)
        openSettingsAction.triggered.connect(lambda: openSettingsWindow(self))
        settingsMenu.addAction(openSettingsAction)
        
        logAction = QtWidgets.QAction(" Open Log", self)
        logAction.triggered.connect(openLog)
        settingsMenu.addAction(logAction)
        
        reinstallAction = QtWidgets.QAction(" Re-install SomePythonThings Zip Manager", self)
        reinstallAction.triggered.connect(lambda: checkForUpdates(parent=self, force=True))
        settingsMenu.addAction(reinstallAction)
        
        openHelpAction = QtWidgets.QAction(" Online manual", self)
        openHelpAction.triggered.connect(lambda: openHelp())
        helpMenu.addAction(openHelpAction)
        
        updatesAction = QtWidgets.QAction(" Check for updates", self)
        updatesAction.triggered.connect(lambda: checkForUpdates(parent=self, verbose=True))
        helpMenu.addAction(updatesAction)
        
        aboutQtAction = QtWidgets.QAction(" About Qt framework   ", self)
        aboutQtAction.triggered.connect(lambda: QtWidgets.QMessageBox.aboutQt(self, "About the Qt framework - SomePythonThings Zip Manager"))
        helpMenu.addAction(aboutQtAction)
        
        aboutAction = QtWidgets.QAction(" About SomePythonThings Zip Manager", self)
        aboutAction.triggered.connect(lambda: self.throwInfo("About SomePythonThings Zip Manager", "SomePythonThings Zip Manager\nVersion "+str(self.version)+"\n\nThe SomePythonThings Project\n\n © 2021 Martí Climent, SomePythonThings\nhttps://www.somepythonthings.tk\n\n\nThe iconset has a CC Non-Commercial Atribution 4.0 License"))
        helpMenu.addAction(aboutAction)

        if(macOS):
            legacyAboutAction = QtWidgets.QAction("About", self)
            legacyAboutAction.triggered.connect(lambda: self.throwInfo("About SomePythonThings Zip Manager", "SomePythonThings Zip Manager\nVersion "+str(self.version)+"\n\nThe SomePythonThings Project\n\n © 2021 Martí Climent, SomePythonThings\nhttps://www.somepythonthings.tk\n\n\nThe iconset has a CC Non-Commercial Atribution 4.0 License"))
            helpMenu.addAction(legacyAboutAction)

            
            legacyOpenSettingsAction = QtWidgets.QAction("Settings", self)
            legacyOpenSettingsAction.triggered.connect(lambda: openSettingsWindow(self))
            settingsMenu.addAction(legacyOpenSettingsAction)


        return menuBar

    def loadMenuBar(self) -> None:
        if(_platform=="darwin"):
            self.createMenuBar(native=False) # Create non native menubar on macOS
        self.createMenuBar(native=True, macOS=_platform=="darwin") # Create native menubar

    def throwInfo(self, title: str, body: str) -> None:
        global music
        log("[  INFO  ] "+body)
        msg = QtWidgets.QMessageBox(self)
        if(os.path.exists(getPath("zip_ok.ico"))):
            msg.setIconPixmap(QtGui.QPixmap(str(getPath("zip_ok.ico"))).scaledToHeight(96, QtCore.Qt.SmoothTransformation))
        else:
            msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(body)
        if(_platform == 'darwin'):
            msg.setAutoFillBackground(True)
            msg.setWindowModality(QtCore.Qt.WindowModal)
            msg.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            msg.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
            msg.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
            msg.setModal(True)
            msg.setSizeGripEnabled(False)
        msg.setWindowTitle(title)
        msg.exec_()

    def throwWarning(self, title: str, body: str) -> None:
        log("[  WARN  ] "+body)
        msg = QtWidgets.QMessageBox(self)
        if(os.path.exists(getPath("zip_ok.ico"))):
            msg.setIconPixmap(QtGui.QPixmap(str(getPath("zip_warn.ico"))).scaledToHeight(96, QtCore.Qt.SmoothTransformation))
        else:
            msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(body)
        if(_platform == 'darwin'):
            msg.setAutoFillBackground(True)
            msg.setWindowModality(QtCore.Qt.WindowModal)
            msg.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            msg.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
            msg.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
            msg.setModal(True)
            msg.setSizeGripEnabled(False)
        msg.setWindowTitle(title)
        msg.exec_()



    def throwError(self, title: str, body: str) -> None:
        log("[ FAILED ] "+body)
        msg = QtWidgets.QMessageBox(self)
        if(os.path.exists(getPath("zip_ok.ico"))):
            msg.setIconPixmap(QtGui.QPixmap(str(getPath("zip_error.ico"))).scaledToHeight(96, QtCore.Qt.SmoothTransformation))
        else:
            msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(body)
        if(_platform == 'darwin'):
            msg.setAutoFillBackground(True)
            msg.setWindowModality(QtCore.Qt.WindowModal)
            msg.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            msg.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
            msg.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
            msg.setModal(True)
            msg.setSizeGripEnabled(False)
        msg.setWindowTitle(title)
        msg.exec_()

    def confirm(self, title: str, body: str, firstButton: QtWidgets.QAbstractButton, secondButton: QtWidgets.QAbstractButton, defaultButton: QtWidgets.QAbstractButton) -> QtWidgets.QAbstractButton:
        msg = QtWidgets.QMessageBox(self)
        log("[  WARN  ] "+body)
        if(os.path.exists(str(realpath)+"/icons-sptmusic/ok.png")):
            msg.setIconPixmap(QtGui.QPixmap(str(realpath)+"/icons-sptmusic/ok.png").scaledToHeight(96, QtCore.Qt.SmoothTransformation))
        else:
            msg.setIcon(QtWidgets.QMessageBox.Warning)
        
        if(_platform == 'darwin'):
            msg.setAutoFillBackground(True)
            msg.setWindowModality(QtCore.Qt.WindowModal)
            msg.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            msg.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
            msg.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
            msg.setModal(True)
            msg.setSizeGripEnabled(False)
        msg.setWindowTitle(title)
        msg.setText(body)
        msg.addButton(firstButton)
        msg.addButton(secondButton)
        msg.setDefaultButton(defaultButton)
        msg.exec_()
        return msg.standardButton(msg.clickedButton())




    def resizeEvent(self, event: QtCore.QEvent):
        self.resized.emit()
        return super(Window, self).resizeEvent(event)

    def closeEvent(self, event: QtCore.QEvent) -> None:
        self.themeThread.terminate()
        if(self.isCompressing):
            log("[  WARN  ] Compresion running!")
            if(QtWidgets.QMessageBox.question(self, "Warning", "A compression is running! Do you want to quit anyway?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes):
                log("[   OK   ] Quitting anyway...")
                event.accept()
            else:
                log("[   OK   ] Not quitting")
                event.ignore()
        elif(self.isExtracting):
            log("[  WARN  ] Extraction running!")
            if(QtWidgets.QMessageBox.question(self, "Warning", "An extraction is running! Do you want to quit anyway?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes):
                log("[   OK   ] Quitting anyway...")
                event.accept()
            else:
                log("[   OK   ] Not quitting")
                event.ignore()
        else:
            event.accept()

    def createNewWindow(self) -> None:
        Window(self.app)

if(__name__ == "__main__"):
=======
from PySide2 import QtWidgets, QtGui, QtCore
from Tools import *
#from Tools import log, openLog, openHelp, openSettingsWindow, getPath, CheckModeThread, baseStyleSheet, settings, version, realpath
import darkdetect, qtmodern.styles, sys, os
import qtmodern.styles
from sys import platform as _platform
from Compressor import Compressor
from Extractor import Extractor
from Welcome import Welcome
from Updater import checkForUpdates


class Window(QtWidgets.QMainWindow):
    resized = QtCore.Signal()
    keyRelease = QtCore.Signal(int)

    def __init__(self, app: QtWidgets.QApplication, parent=None):
        log("[        ] Creating a new window...")

        super(Window, self).__init__(parent=parent)

        self.setUnifiedTitleAndToolBarOnMac(True)


        self.app = app
        self.isCompressing = False
        self.isExtracting = False
        self.version = version
        self.setWindowIcon(QtGui.QIcon(getPath("zip.ico")))
        self.menuBarAlreadyCreated = False

        self.themeThread = CheckModeThread()
        self.themeThread.start()
        self.themeThread.refreshTheme.connect(self.loadStyleSheet)
        self.themeThread

        self.setWindowTitle("SomePythonThings Zip Manager")
        self.loadStyleSheet()
        self.setStyleSheet(baseStyleSheet)
        self.resize(1200, 700)
        self.setMinimumSize(600, 450)
        self.show()
        self.loadMenuBar()
        self.loadWidgets()
        self.installEventFilter(self)
        log("[   OK   ] Window loaded successfully")
        log("[        ] Calling updates thread...")
        checkForUpdates(self)

        if(_platform == "win32"):
                    from PySide2 import QtWinExtras
                    self.loadbutton = QtWinExtras.QWinTaskbarButton(self)
                    self.loadbutton.setWindow(self.windowHandle())
                    self.taskbprogress = self.loadbutton.progress()
                    self.taskbprogress.setRange(0, 100)
                    self.taskbprogress.setValue(0)
                    self.taskbprogress.hide()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.themeThread.shouldBeRunning = False
        self.themeThread.quit()
        self.themeThread.wait()
        import time
        time.sleep(1)
        return event.accept()
        
        

    def loadStyleSheet(self) -> None:
        if not(settings["plainAppearance"]):
            if(settings["mode"] == "dark"):
                isLight = False
            elif(settings["mode"] == "light"):
                isLight = True
            else:
                isLight = self.isLight()
            if(isLight):
                qtmodern.styles.light(self.app)
            else:
                qtmodern.styles.dark(self.app)
        else:
            self.app.setPalette(self.app.style().standardPalette())
            self.app.setStyleSheet("")
            if(_platform=="win32"):
                self.app.setStyle("windowsvista")
            elif(_platform=="darwin"):
                self.app.setStyle("macintosh")
            elif(_platform=="linux"):
                pass
                self.app.setStyle("gtk2")


                
    
    def isLight(self) -> bool:
        mode = darkdetect.isLight()
        if(mode!=None):
            return mode
        else:
            return True
    
    def addTab(self, widget: QtWidgets.QWidget, icon: QtGui.QIcon, title: str, closable: bool = True) -> int:
        button = QtWidgets.QPushButton(self)
        button.resize(QtCore.QSize(20, 20))
        button.setIconSize(QtCore.QSize(12, 12))
        button.setStyleSheet("""QPushButton{border: none}QPushButton::hover{border: 1px solid grey;border-radius:3px;}""")
        button.setIcon(QtGui.QIcon(getPath("not.ico")))
        i = self.tabWidget.addTab(widget, icon, title)
        if(closable):
            button.clicked.connect(lambda: self.tabWidget.removeTab(i))
            self.tabWidget.tabBar().setTabButton(i, QtWidgets.QTabBar.RightSide,  button)
            self.tabWidget.tabBar().setTabButton(i, QtWidgets.QTabBar.LeftSide,  None)

        return i

    def loadWidgets(self) -> None:
        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tabWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.tabWidget.setTabsClosable(False)
        self.setCentralWidget(self.tabWidget)
        
        self.addTab(Welcome(self), QtGui.QIcon(getPath("zip.ico")), "Home Page", closable=False)

    def addCompressTab(self) -> None:
        t = self.addTab(Compressor(self), QtGui.QIcon(getPath("compressFiles.ico")), "Compress Files")
        self.tabWidget.setCurrentIndex(t)

    def addExtractTab(self, zipFile: str = "") -> None:
        tabName = "Extract Files"
        if(zipFile != ""):
            tabName = zipFile.replace("\\", "/").split("/")[-1]
        t = self.addTab(Extractor(self, zipFile), QtGui.QIcon(getPath("extractFiles.ico")), tabName)
        self.tabWidget.setCurrentIndex(t)

    def createMenuBar(self, native: bool = False, macOS: bool = False) -> QtWidgets.QMenuBar:
        if not(self.menuBarAlreadyCreated):
            menuBar = self.menuBar()
            self.menuBarAlreadyCreated = True
        else:
            menuBar = QtWidgets.QMenuBar(self)
        menuBar.setNativeMenuBar(native)
        fileMenu = menuBar.addMenu("File")
        settingsMenu = menuBar.addMenu("Settings")
        helpMenu = menuBar.addMenu("Help")

        newAction = QtWidgets.QAction(" New window", self)
        newAction.triggered.connect(lambda: self.createNewWindow())
        newAction.setShortcut("Ctrl+N")
        fileMenu.addAction(newAction)

        compressAction = QtWidgets.QAction(" Compress files", self)
        compressAction.triggered.connect(lambda: self.addCompressTab())
        compressAction.setShortcut("")
        fileMenu.addAction(compressAction)

        extractAction = QtWidgets.QAction(" Extract files", self)
        extractAction.triggered.connect(lambda: self.addExtractTab())
        extractAction.setShortcut("")
        fileMenu.addAction(extractAction)

        closeAction = QtWidgets.QAction(" Close Window", self)
        closeAction.triggered.connect(lambda: self.close())
        closeAction.setShortcut("Ctrl+W")
        fileMenu.addAction(closeAction)

        quitAction = QtWidgets.QAction(" Quit", self)
        quitAction.triggered.connect(lambda: sys.exit(0))
        quitAction.setShortcut("Ctrl+Q")
        fileMenu.addAction(quitAction)

        openSettingsAction = QtWidgets.QAction(" Settings    ", self)
        openSettingsAction.triggered.connect(lambda: openSettingsWindow(self))
        settingsMenu.addAction(openSettingsAction)
        
        logAction = QtWidgets.QAction(" Open Log", self)
        logAction.triggered.connect(openLog)
        settingsMenu.addAction(logAction)
        
        reinstallAction = QtWidgets.QAction(" Re-install SomePythonThings Zip Manager", self)
        reinstallAction.triggered.connect(lambda: checkForUpdates(parent=self, force=True))
        settingsMenu.addAction(reinstallAction)
        
        openHelpAction = QtWidgets.QAction(" Online manual", self)
        openHelpAction.triggered.connect(lambda: openHelp())
        helpMenu.addAction(openHelpAction)
        
        updatesAction = QtWidgets.QAction(" Check for updates", self)
        updatesAction.triggered.connect(lambda: checkForUpdates(parent=self, verbose=True))
        helpMenu.addAction(updatesAction)
        
        aboutQtAction = QtWidgets.QAction(" About Qt framework   ", self)
        aboutQtAction.triggered.connect(lambda: QtWidgets.QMessageBox.aboutQt(self, "About the Qt framework - SomePythonThings Zip Manager"))
        helpMenu.addAction(aboutQtAction)
        
        aboutAction = QtWidgets.QAction(" About SomePythonThings Zip Manager", self)
        aboutAction.triggered.connect(lambda: self.throwInfo("About SomePythonThings Zip Manager", "SomePythonThings Zip Manager\nVersion "+str(self.version)+"\n\nThe SomePythonThings Project\n\n © 2021 Martí Climent, SomePythonThings\nhttps://www.somepythonthings.tk\n\n\nThe iconset has a CC Non-Commercial Atribution 4.0 License"))
        helpMenu.addAction(aboutAction)

        if(macOS):
            legacyAboutAction = QtWidgets.QAction("About", self)
            legacyAboutAction.triggered.connect(lambda: self.throwInfo("About SomePythonThings Zip Manager", "SomePythonThings Zip Manager\nVersion "+str(self.version)+"\n\nThe SomePythonThings Project\n\n © 2021 Martí Climent, SomePythonThings\nhttps://www.somepythonthings.tk\n\n\nThe iconset has a CC Non-Commercial Atribution 4.0 License"))
            helpMenu.addAction(legacyAboutAction)

            
            legacyOpenSettingsAction = QtWidgets.QAction("Settings", self)
            legacyOpenSettingsAction.triggered.connect(lambda: openSettingsWindow(self))
            settingsMenu.addAction(legacyOpenSettingsAction)


        return menuBar

    def loadMenuBar(self) -> None:
        if(_platform=="darwin"):
            self.createMenuBar(native=False) # Create non native menubar on macOS
        self.createMenuBar(native=True, macOS=_platform=="darwin") # Create native menubar

    def throwInfo(self, title: str, body: str) -> None:
        global music
        log("[  INFO  ] "+body)
        msg = QtWidgets.QMessageBox(self)
        if(os.path.exists(getPath("zip_ok.ico"))):
            msg.setIconPixmap(QtGui.QPixmap(str(getPath("zip_ok.ico"))).scaledToHeight(96, QtCore.Qt.SmoothTransformation))
        else:
            msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(body)
        if(_platform == 'darwin'):
            msg.setAutoFillBackground(True)
            msg.setWindowModality(QtCore.Qt.WindowModal)
            msg.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            msg.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
            msg.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
            msg.setModal(True)
            msg.setSizeGripEnabled(False)
        msg.setWindowTitle(title)
        msg.exec_()

    def throwWarning(self, title: str, body: str) -> None:
        log("[  WARN  ] "+body)
        msg = QtWidgets.QMessageBox(self)
        if(os.path.exists(getPath("zip_ok.ico"))):
            msg.setIconPixmap(QtGui.QPixmap(str(getPath("zip_warn.ico"))).scaledToHeight(96, QtCore.Qt.SmoothTransformation))
        else:
            msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(body)
        if(_platform == 'darwin'):
            msg.setAutoFillBackground(True)
            msg.setWindowModality(QtCore.Qt.WindowModal)
            msg.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            msg.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
            msg.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
            msg.setModal(True)
            msg.setSizeGripEnabled(False)
        msg.setWindowTitle(title)
        msg.exec_()



    def throwError(self, title: str, body: str) -> None:
        log("[ FAILED ] "+body)
        msg = QtWidgets.QMessageBox(self)
        if(os.path.exists(getPath("zip_ok.ico"))):
            msg.setIconPixmap(QtGui.QPixmap(str(getPath("zip_error.ico"))).scaledToHeight(96, QtCore.Qt.SmoothTransformation))
        else:
            msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(body)
        if(_platform == 'darwin'):
            msg.setAutoFillBackground(True)
            msg.setWindowModality(QtCore.Qt.WindowModal)
            msg.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            msg.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
            msg.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
            msg.setModal(True)
            msg.setSizeGripEnabled(False)
        msg.setWindowTitle(title)
        msg.exec_()

    def confirm(self, title: str, body: str, firstButton: QtWidgets.QAbstractButton, secondButton: QtWidgets.QAbstractButton, defaultButton: QtWidgets.QAbstractButton) -> QtWidgets.QAbstractButton:
        msg = QtWidgets.QMessageBox(self)
        log("[  WARN  ] "+body)
        if(os.path.exists(str(realpath)+"/icons-sptmusic/ok.png")):
            msg.setIconPixmap(QtGui.QPixmap(str(realpath)+"/icons-sptmusic/ok.png").scaledToHeight(96, QtCore.Qt.SmoothTransformation))
        else:
            msg.setIcon(QtWidgets.QMessageBox.Warning)
        
        if(_platform == 'darwin'):
            msg.setAutoFillBackground(True)
            msg.setWindowModality(QtCore.Qt.WindowModal)
            msg.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            msg.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
            msg.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
            msg.setModal(True)
            msg.setSizeGripEnabled(False)
        msg.setWindowTitle(title)
        msg.setText(body)
        msg.addButton(firstButton)
        msg.addButton(secondButton)
        msg.setDefaultButton(defaultButton)
        msg.exec_()
        return msg.standardButton(msg.clickedButton())




    def resizeEvent(self, event: QtCore.QEvent):
        self.resized.emit()
        return super(Window, self).resizeEvent(event)

    def closeEvent(self, event: QtCore.QEvent) -> None:
        self.themeThread.terminate()
        if(self.isCompressing):
            log("[  WARN  ] Compresion running!")
            if(QtWidgets.QMessageBox.question(self, "Warning", "A compression is running! Do you want to quit anyway?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes):
                log("[   OK   ] Quitting anyway...")
                event.accept()
            else:
                log("[   OK   ] Not quitting")
                event.ignore()
        elif(self.isExtracting):
            log("[  WARN  ] Extraction running!")
            if(QtWidgets.QMessageBox.question(self, "Warning", "An extraction is running! Do you want to quit anyway?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes):
                log("[   OK   ] Quitting anyway...")
                event.accept()
            else:
                log("[   OK   ] Not quitting")
                event.ignore()
        else:
            event.accept()

    def createNewWindow(self) -> None:
        Window(self.app)

if(__name__ == "__main__"):
>>>>>>> d2c6635dea116061bc2ba7114a5b2453fd18553a
>>>>>>> Stashed changes
    import __init__
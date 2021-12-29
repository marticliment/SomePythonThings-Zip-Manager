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
from FramelessWindow import QFramelessDialog
        
class Window(QtWidgets.QMainWindow):
    resized = QtCore.Signal()
    keyRelease = QtCore.Signal(int)

    def __init__(self, app: QtWidgets.QApplication, parent=None):
        log("[        ] Creating a new window...")

        super(Window, self).__init__(parent=parent)

        self.setUnifiedTitleAndToolBarOnMac(True)

        self.setObjectName("background")

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
        if(settings["autoCheckForUpdates"]):
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
        
    def getPx(self, i: int):
        return i
        

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
                colors = getColors()
                self.app.setStyleSheet(f"""
                                * {{
                                    background-color: #262626;
                                    font-family: "Segoe UI Variable Display Semib";
                                }}
                                QGroupBox {{
                                    border: none;
                                    padding: 3px;
                                    background-color: #303030;
                                    border-radius: 5px;
                                }}
                                QLabel,QWidget {{
                                    background-color: transparent;
                                }}
                                #background {{
                                    background-color: #262626;
                                }}
                                #darkbackground {{
                                    background-color: #212121;
                                }}
                                #lightbackground {{
                                    background-color: #303030;
                                    border: {self.getPx(1)}px solid #262626;
                                    height: {self.getPx(25)}px;
                                    border-top: {self.getPx(1)}px solid #262626;
                                }}
                                QToolTip {{
                                    border: {self.getPx(1)}px solid #222222;
                                    padding: {self.getPx(4)}px;
                                    border-radius: {self.getPx(6)}px;
                                    background-color: #262626;
                                }}
                                QMenuBar {{
                                    border: none;
                                    padding: {self.getPx(2)}px;
                                    outline: 0px;
                                    color: white;
                                    background: transparent;
                                    border-radius: {self.getPx(8)}px;
                                }}
                                QMenuBar::separator {{
                                    margin: {self.getPx(2)}px;
                                    height: {self.getPx(1)}px;
                                    background: rgb(60, 60, 60);
                                }}
                                QMenuBar::icon{{
                                    padding-left: {self.getPx(10)}px;
                                }}
                                QMenuBar::item{{
                                    height: {self.getPx(30)}px;
                                    border: none;
                                    background: transparent;
                                    padding-right: {self.getPx(10)}px;
                                    padding-left: {self.getPx(10)}px;
                                    border-radius: {self.getPx(4)}px;
                                    margin: {self.getPx(2)}px;
                                }}
                                QMenuBar::item:selected{{
                                    background: rgba(255, 255, 255, 10%);
                                    height: {self.getPx(30)}px;
                                    outline: none;
                                    border: none;
                                    padding: 5px;
                                    padding-right: {self.getPx(10)}px;
                                    padding-left: {self.getPx(10)}px;
                                    border-radius: {self.getPx(4)}px;
                                }}  
                                QMenuBar::item:selected:disabled{{
                                    background: transparent;
                                    height: {self.getPx(30)}px;
                                    outline: none;
                                    border: none;
                                    padding-right: {self.getPx(10)}px;
                                    padding-left: {self.getPx(10)}px;
                                    border-radius: {self.getPx(4)}px;
                                }}
                                QMenu {{
                                    border: {self.getPx(1)}px solid rgb(60, 60, 60);
                                    padding: {self.getPx(2)}px;
                                    outline: 0px;
                                    color: white;
                                    background: #262626;
                                    border-radius: {self.getPx(8)}px;
                                }}
                                QMenu::separator {{
                                    margin: {self.getPx(2)}px;
                                    height: {self.getPx(1)}px;
                                    background: rgb(60, 60, 60);
                                }}
                                QMenu::icon{{
                                    padding-left: {self.getPx(10)}px;
                                }}
                                QMenu::item{{
                                    height: {self.getPx(30)}px;
                                    border: none;
                                    background: transparent;
                                    padding-right: {self.getPx(10)}px;
                                    padding-left: {self.getPx(10)}px;
                                    border-radius: {self.getPx(4)}px;
                                    margin: {self.getPx(2)}px;
                                }}
                                QMenu::item:selected{{
                                    background: rgba(255, 255, 255, 10%);
                                    height: {self.getPx(30)}px;
                                    outline: none;
                                    border: none;
                                    padding-right: {self.getPx(10)}px;
                                    padding-left: {self.getPx(10)}px;
                                    border-radius: {self.getPx(4)}px;
                                }}  
                                QMenu::item:selected:disabled{{
                                    background: transparent;
                                    height: {self.getPx(30)}px;
                                    outline: none;
                                    border: none;
                                    padding-right: {self.getPx(10)}px;
                                    padding-left: {self.getPx(10)}px;
                                    border-radius: {self.getPx(4)}px;
                                }}
                                QColorDialog {{
                                    background-color: transparent;
                                    border: none;
                                }}
                                QLineEdit {{
                                    background-color: #1d1d1d;
                                    padding: 5px;
                                    border-radius: {self.getPx(6)}px;
                                    border: 1px solid #262626;
                                }}
                                QScrollArea {{
                                   color: white;
                                   padding-left: 5px;
                                   border-radius: 5px;
                                   background-color: #212121;
                                }}
                                QLabel {{
                                    font-family: "Segoe UI Variable Display Semib";
                                    font-weight: medium;
                                }}
                                * {{
                                   color: #dddddd;
                                   font-size: 8pt;
                                }}
                                QPlainTextEdit{{
                                    font-family: "Cascadia Mono";
                                    background-color: #212121;
                                    selection-background-color: rgb({colors[4]});
                                    border: none;
                                }}
                                QSpinBox {{
                                   background-color: #363636;
                                   border-radius: {self.getPx(6)}px;
                                   border: {self.getPx(1)}px solid #393939;
                                   height: {self.getPx(25)}px;
                                   border-top: {self.getPx(1)}px solid #404040;
                                }}
                                QPushButton {{
                                   width: 100px;
                                   background-color: #363636;
                                   border-radius: {self.getPx(6)}px;
                                   border: {self.getPx(1)}px solid #393939;
                                   height: {self.getPx(25)}px;
                                   border-top: {self.getPx(1)}px solid #404040;
                                }}
                                QPushButton:hover {{
                                   background-color: #393939;
                                   border-radius: {self.getPx(6)}px;
                                   border: {self.getPx(1)}px solid #414141;
                                   height: {self.getPx(25)}px;
                                   border-top: {self.getPx(1)}px solid #454545;
                                }}
                                QSCrollArea, QVBoxLayout{{
                                    border: none;
                                    margin: none;
                                    padding: none;
                                    outline: none;
                                }}
                                QScrollBar:vertical {{
                                    background: #303030;
                                    margin: {self.getPx(4)}px;
                                    width: {self.getPx(20)}px;
                                    border: none;
                                    border-radius: {self.getPx(5)}px;
                                }}
                                QScrollBar:horizontal {{
                                    background: #303030;
                                    margin: {self.getPx(4)}px;
                                    height: {self.getPx(20)}px;
                                    border: none;
                                    border-radius: {self.getPx(5)}px;
                                }}
                                QScrollBar::handle {{
                                    margin: {self.getPx(3)}px;
                                    min-height: 20px;
                                    min-width: 20px;
                                    border-radius: {self.getPx(3)}px;
                                    background: #505050;
                                }}
                                QScrollBar::handle:hover {{
                                    margin: {self.getPx(3)}px;
                                    border-radius: {self.getPx(3)}px;
                                    background: #808080;
                                }}
                                QScrollBar::add-line {{
                                    height: 0;
                                    subcontrol-position: bottom;
                                    subcontrol-origin: margin;
                                }}
                                QScrollBar::sub-line {{
                                    height: 0;
                                    subcontrol-position: top;
                                    subcontrol-origin: margin;
                                }}
                                QScrollBar::up-arrow, QScrollBar::down-arrow {{
                                    background: none;
                                }}
                                QScrollBar::add-page, QScrollBar::sub-page {{
                                    background: none;
                                }}
                                #AccentButton{{
                                    background-color: rgb({colors[3]});
                                    border-color: rgb({colors[4]});
                                    border-top-color: rgb({colors[5]});
                                }}
                                #AccentButton:hover{{
                                    background-color: rgb({colors[2]});
                                    border-color: rgb({colors[3]});
                                    border-top-color: rgb({colors[4]});
                                }}
                                QTabWidget::pane {{
                                    margin: 5px;
                                    padding: 3px;
                                    margin-top: 0px;
                                    background-color: #2e2e2e;
                                    border-radius: {self.getPx(6)}px;
                                    border: {self.getPx(1)}px solid #393939;
                                    border-top: {self.getPx(1)}px solid #404040;
                                }}
                                QTabBar::tab {{
                                    margin: 5px;
                                    margin-right: 0px;
                                    padding: 3px;
                                    width: 200px;
                                    background-color: #363636;
                                    border-radius: {self.getPx(6)}px;
                                    border: {self.getPx(1)}px solid #393939;
                                    height: {self.getPx(25)}px;
                                    border-top: {self.getPx(1)}px solid #404040;
                                }}
                                QTabBar::tab:hover {{
                                    background-color: #393939;
                                    border-radius: {self.getPx(6)}px;
                                    border: {self.getPx(1)}px solid #414141;
                                    height: {self.getPx(25)}px;
                                    border-top: {self.getPx(1)}px solid #454545;
                                }}
                                QTabBar::tab:selected {{
                                    margin: 5px;
                                    padding: 3px;
                                    background-color: rgb({colors[3]});
                                    border-color: rgb({colors[4]});
                                    border-top-color: rgb({colors[5]});
                                }}
                                QTabBar::tab:selected:hover {{ 
                                    background-color: rgb({colors[2]});
                                    border-color: rgb({colors[3]});
                                    border-top-color: rgb({colors[4]});
                                }}
                                QTreeWidget,QTreeView {{
                                    show-decoration-selected: 0;
                                    border: {self.getPx(1)}px solid #393939;
                                    border-bottom: {self.getPx(1)}px solid #454545;
                                    background-color: #212121;
                                    border-radius: 5px;
                                    outline: none;
                                }}
                                QTreeView::item:selected:active{{
                                    color: white;
                                    background: rgb({colors[3]});
                                    outline: none;
                                    border: none;
                                }}
                                QHeaderView::section{{
                                    border: none;
                                    padding: 5px;
                                    background-color: #212121;
                                    border-radius: 5px;  
                                }}
                                QGroupBox {{
                                    padding-top: 30px;
                                    border: none;
                                }}
                                QGroupBox::title{{
                                    border: none;
                                    font-size: 15pt;
                                    margin-top: 10px;
                                    margin-left: 10px;
                                    subcontrol-position: top left;
                                }}
                                QProgressBar:horizontal {{
                                    border: {self.getPx(1)}px solid #393939;
                                    border-bottom: {self.getPx(1)}px solid #454545;
                                    background-color: #212121;
                                    border-radius: 5px;
                                    height: 20px;
                                }}
                                QProgressBar::chunk:horizontal {{
                                    background-color: rgb({colors[2]});
                                    border-radius: 5px;
                                }}
                                #CloseTabButton {{
                                    background-color: transparent;
                                    margin-right: 5px;
                                    border: none;
                                    width: 20px;
                                    height: 20px;
                                }}
                                #CloseTabButton:hover {{
                                    background-color: #303030;
                                    border-radius: 6px;
                                }}
                                QToolButton:hover {{
                                   background-color: #3b3b3b;
                                   border-radius: {self.getPx(6)}px;
                                   border: {self.getPx(1)}px solid #414141;
                                   height: {self.getPx(25)}px;
                                   border-top: {self.getPx(1)}px solid #454545;
                                }}
                                QToolButton:pressed {{
                                   background-color: #2b2b2b;
                                   border-radius: {self.getPx(6)}px;
                                   border: {self.getPx(1)}px solid #393939;
                                   height: {self.getPx(25)}px;
                                   border-top: {self.getPx(1)}px solid #393939;
                                }}
                                #bgDialog {{
                                    background-color: #303030;
                                    font-size: 13pt;
                                }}
                                #dialogButtonWidget {{
                                    background-color: #212121;
                                }}
                                QComboBox {{
                                    margin: 0px;
                                    padding: 6px;
                                    height: 20px;
                                    background-color: #3b3b3b;
                                    border-radius: {self.getPx(6)}px;
                                    border: {self.getPx(1)}px solid #414141;
                                    border-top: {self.getPx(1)}px solid #454545;
                                }}
                                QAbstractItemView {{
                                    padding: 0px;
                                    border-radius: 4px;
                                }}
                                QComboBox QAbstractItemView {{
                                    border: {self.getPx(1)}px solid rgb(60, 60, 60);
                                    outline: 0px;
                                    color: white;
                                    background: #262626;
                                    border-radius: {self.getPx(8)}px;
                                    padding: 3px;
                                    margin: 0px;
                                }}
                                QComboBox::drop-down {{
                                    subcontrol-origin: margin;
                                    subcontrol-position: top right;
                                    width: 15px;
                                    margin: 4px;
                                    padding: 3px;
                                    background-color: #2b2b2b;
                                    border-radius: {self.getPx(4)}px;
                                    border: {self.getPx(1)}px solid #303030;
                                    border-top: {self.getPx(1)}px solid #363636;
                                    
                                }}
                                QAbstractScrollArea::cornerWidget {{
                                    border: none;
                                    background: transparent;
                                }}
                                
                                       """)
        else:
            self.app.setPalette(self.app.style().standardPalette())
            self.app.setStyleSheet("")
            self.app.setStyle("windowsvista")
            self.app.setStyle(QtWidgets.QStyleFactory.create("windowsvista"))


                
    
    def isLight(self) -> bool:
        mode = darkdetect.isLight()
        if(mode!=None):
            return mode
        else:
            return True
    
    def addTab(self, widget: QtWidgets.QWidget, icon: QtGui.QIcon, title: str, closable: bool = True) -> int:
        button = QtWidgets.QPushButton(self)
        button.setFixedSize(QtCore.QSize(25, 20))
        button.setIconSize(QtCore.QSize(12, 12))
        button.setObjectName("CloseTabButton")
        #button.setStyleSheet("""QPushButton{background-color: transparent; margin-right: 10px;border: none;width: 20px; height: 20px;}QPushButton::hover{background-color: rgba(255, 96, 96, 100%); border-radius: 3px;}""")
        button.setIcon(QtGui.QIcon(getPath("not.ico")))
        i = self.tabWidget.addTab(widget, icon, title)
        if(closable):
            button.clicked.connect(lambda: self.tabWidget.removeTab(self.tabWidget.indexOf(widget)))
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
        aboutAction.triggered.connect(lambda: self.throwInfo("About SomePythonThings Zip Manager", "SomePythonThings Zip Manager\nVersion "+str(self.version)+"\n\nThe SomePythonThings Project\n\n © 2021 Martí Climent, SomePythonThings\nhttps://www.somepythonthings.tk\n\n\nThe Blue Folder Logo has a CC Non-Commercial Atribution 4.0 License\nIcons by Icons8  (https://icons8.com)"))
        helpMenu.addAction(aboutAction)

        if(macOS):
            legacyAboutAction = QtWidgets.QAction("About", self)
            legacyAboutAction.triggered.connect(lambda: self.throwInfo("About SomePythonThings Zip Manager", "SomePythonThings Zip Manager\nVersion "+str(self.version)+"\n\nThe SomePythonThings Project\n\n © 2021 Martí Climent, SomePythonThings\nhttps://www.somepythonthings.tk\n\n\nThe Blue Folder Logo has a CC Non-Commercial Atribution 4.0 License\nIcons by Icons8  (https://icons8.com)"))
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
        log("[  INFO  ] "+body)
        msg = QFramelessDialog(self)
        msg.setAutoFillBackground(True)
        msg.setStyleSheet(self.styleSheet())
        msg.setAttribute(QtCore.Qt.WA_StyledBackground)
        msg.setObjectName("QMessageBox")
        msg.setTitle("Information")
        msg.setText(body)
        msg.addButton("Ok", QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        msg.setDefaultButtonRole(QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole, self.styleSheet())
        msg.setWindowTitle(title)
        msg.show()

    def throwWarning(self, title: str, body: str) -> None:
        log("[  WARN  ] "+body)
        msg = QFramelessDialog(self)
        msg.setAutoFillBackground(True)
        msg.setStyleSheet(self.styleSheet())
        msg.setAttribute(QtCore.Qt.WA_StyledBackground)
        msg.setObjectName("QMessageBox")
        msg.setTitle("Warning!")
        msg.setText(body)
        msg.addButton("Ok", QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        msg.setDefaultButtonRole(QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole, self.styleSheet())
        msg.setWindowTitle(title)
        msg.show()

    def throwError(self, title: str, body: str) -> None:
        log("[ FAILED ] "+body)
        msg = QFramelessDialog(self)
        msg.setAutoFillBackground(True)
        msg.setStyleSheet(self.styleSheet())
        msg.setAttribute(QtCore.Qt.WA_StyledBackground)
        msg.setObjectName("QMessageBox")
        msg.setTitle("Unhandled error!")
        msg.setText(body)
        msg.addButton("Ok", QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        msg.setDefaultButtonRole(QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole, self.styleSheet())
        msg.setWindowTitle(title)
        msg.show()

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
    import __init__
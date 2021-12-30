from PySide2 import QtWidgets, QtCore, QtGui
import PySide2
from Updater import checkForUpdates
from urllib.request import urlopen
from threading import Thread

from Tools import *
#from Tools import log, debugging, _platform, getFileIcon, getPath, openOnExplorer, notify, settings, version, openSettingsWindow

class Welcome(QtWidgets.QWidget):

    loadPixmapSignal = QtCore.Signal(bytes)


    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.compressButton = QtWidgets.QPushButton(self)
        self.compressButton.clicked.connect(lambda: self.window().addCompressTab())
        self.compressButton.resize(128, 128)
        self.compressButton.setIcon(QtGui.QIcon(getPath("compressFiles.ico")))
        self.compressButton.setIconSize(QtCore.QSize(96, 96))
        self.extractButton = QtWidgets.QPushButton(self)
        self.extractButton.clicked.connect(lambda: self.window().addExtractTab())
        self.extractButton.setIcon(QtGui.QIcon(getPath("extractFiles.ico")))
        self.extractButton.resize(128, 128)
        self.extractButton.setIconSize(QtCore.QSize(96, 96))
 
        self.infoLabel = QtWidgets.QLabel(self)
        self.infoLabel.setText(f"SomePythonThings Zip Manager v{version}  © 2022 The SomePythonThings Project")

        self.checkForUpdatesButton = QtWidgets.QPushButton(self)
        self.checkForUpdatesButton.setText("Check for updates...")
        self.checkForUpdatesButton.setFixedWidth(150)
        self.checkForUpdatesButton.setFixedHeight(25)
        self.checkForUpdatesButton.clicked.connect(lambda: checkForUpdates(self.window(), verbose=True))

        self.settingsButton = QtWidgets.QPushButton(self)
        self.settingsButton.setText("Settings...")
        self.settingsButton.clicked.connect(lambda: openSettingsWindow(self.window()))
        self.settingsButton.setFixedHeight(25)
        self.settingsButton.setFixedWidth(100)

        self.compressLabel = QtWidgets.QLabel(self)
        self.compressLabel.setText("Compress Files")
        self.compressLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.compressLabel.resize(128, 25)
        
        self.extractLabel = QtWidgets.QLabel(self)
        self.extractLabel.setText("Extract Files")
        self.extractLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.extractLabel.resize(128, 25)

        self.bannerLabel = QtWidgets.QLabel()
        #self.bannerLabel.resize(700, 200)
        self.bannerLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.bannerLabel.setText("Welcome to SomePythonThings Zip Manager! We are now loading internet info...")

        self.scrollLayout = QtWidgets.QGridLayout(self)
        self.scrollLayout.addWidget(self.bannerLabel)

        self.scrollabreArea = QtWidgets.QScrollArea(self)
        self.scrollabreArea.setWidgetResizable(True)
        self.scrollabreArea.setWidget(self.bannerLabel)
        self.bannerLabel.resize(1000, 1000)
        self.pixmap = QtGui.QPixmap()
        self.resizeEvent()

        self.loadPixmapSignal.connect(self.showPic)

        Thread(target=self.loadPicThread, daemon=True).start()

    def showPic(self, data) -> None:
        log("[   OK   ] Showing banner...")
        self.pixmap.loadFromData(data)
        self.resizeEvent()
        
    def loadPicThread(self) -> None:
        log("[        ] Downloading banner...")
        url = 'https://raw.githubusercontent.com/martinet101/SomePythonThings-Zip-Manager/master/media/live_banner.png'    
        data = urlopen(url).read()
        self.loadPixmapSignal.emit(data)
    
    def loadEvent(self, ok: bool) -> None:
        if(ok):
            self.banner.show()
        else:
            self.bannerLabel.setText("Unable to load news page :(\n\n Please check your internet connection and try again")
    
    def resizeEvent(self, event: QtGui.QResizeEvent = None) -> None:
        if(event):
            super().resizeEvent(event)

        w = self.width()
        h = self.height()

        self.compressButton.move(w//2-133, h//2-14)
        self.extractButton.move(w//2+5, h//2-14)

        self.infoLabel.move(10, h-25)
        self.infoLabel.resize(1500, 24)

        #self.banner.move(50, 50)
        #self.banner.resize(w-100, h//2-64-50)
        self.bannerLabel.setPixmap(self.pixmap.scaledToWidth(self.scrollabreArea.width()-20, QtCore.Qt.SmoothTransformation))
        self.bannerLabel.setFixedHeight(self.pixmap.scaledToWidth(self.scrollabreArea.width()).height())

        self.scrollabreArea.move(50, 50)
        self.scrollabreArea.resize(w-100, h//2-64-50)

        self.settingsButton.move(w-105, 5)
        self.checkForUpdatesButton.move(w-155, h-30)

        self.extractLabel.move(w//2+5, h//2+124)
        self.compressLabel.move(w//2-133, h//2+124)


if(__name__=="__main__"):
    import __init__
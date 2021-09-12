from PySide2.QtWidgets import QCheckBox, QComboBox, QSpinBox, QTreeWidget, QWidget, QLabel, QProgressBar, QHBoxLayout
from PySide2 import QtCore, QtGui, QtWidgets

from Tools import *
#from Tools import getPath, log, debugging
from sys import platform as _platform
from threading import Thread
import sys, typing


class TreeWidget(QTreeWidget):
    def __init__(self, parent=None, emptyText="Hint"):
        super().__init__(parent=parent)
        self.backgroundLabel = QLabel(self)
        self.backgroundLabel.show()
        self.openFileAction = self.doNothing
        self.backgroundLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.backgroundLabel.setText(emptyText)
        self.backgroundLabel.resize(250, 70)
        self.setColumnCount(5)
        self.setIconSize(QtCore.QSize(32, 32))
        self.setAutoScroll(True)
        self.setVerticalScrollMode(QtWidgets.QTreeWidget.ScrollPerPixel)
        self.setHorizontalScrollMode(QtWidgets.QTreeWidget.ScrollPerPixel)
        self.setColumnWidth(0, 300)
        self.setSelectionMode(QtWidgets.QTreeView.SelectionMode.ContiguousSelection)
        self.setColumnWidth(3, 200)
        self.setHeaderLabels(["File name", "Size", "Status", "File location", "Relative path"])
        self.setDropIndicatorShown(True)
        self.setAcceptDrops(True)
        self.setSupportedDropActions = QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

    def dragEnterEvent(self, e):
        e.accept()

    def dragMoveEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        self.openFileAction(str(e.mimeData().text().replace("file://", "")))
    
    def resizeEvent(self, event) -> None:
        eventResult = super().resizeEvent(event)
        w, h = self.width(), self.height()
        diffW = w-self.backgroundLabel.width()
        diffH = h-self.backgroundLabel.height()
        self.backgroundLabel.move(diffW//2, diffH//2)
        return eventResult
    
    def setEmptyText(self, text: str) -> None:
        self.backgroundLabel.setText(text)

    def connectFileDragEvent(self, func) -> None:
        self.openFileAction = func
    
    def doNothing(self, f: str) -> None:
        log("[  WARN  ] File {f} dragged, but no actoin was defined for this event")
    
    def showHideLabel(self) -> None:
        if(self.topLevelItemCount()>0):
            self.backgroundLabel.hide()
        else:
            self.backgroundLabel.show()
    
    def addTopLevelItem(self, item: QtWidgets.QTreeWidgetItem) -> None:
        super().addTopLevelItem(item)
        self.showHideLabel()
    
    def addTopLevelItems(self, items: typing.Sequence) -> None:
        super().addTopLevelItems(items)
        self.showHideLabel()

    def clear(self) -> None:
        super().clear()
        self.showHideLabel()
    
    def takeTopLevelItem(self, index: int) -> QtWidgets.QTreeWidgetItem:
        w = super().takeTopLevelItem(index)
        self.showHideLabel()
        return w
    
    def insertTopLevelItem(self, index: int, item: QtWidgets.QTreeWidgetItem) -> None:
        super().insertTopLevelItem(index, item)
        self.showHideLabel()

    def insertTopLevelItems(self, index: int, items: typing.Sequence) -> None:
        super().insertTopLevelItems(index, items)
        self.showHideLabel()

class ProgressUpdater(QWidget):
    def __init__(self, parent: QtCore.QObject = None, window: QtWidgets.QMainWindow = None, processingText: str = "Compressing...", clickToStartText: str = "Click compress to start.") -> None:
        super().__init__(parent=parent)
        self.parentWindow: QtWidgets.QMainWindow = window
        self.processingText = processingText
        self.clickToStartText = clickToStartText
        self.isLoading = True
        self.setFixedHeight(25)
        self.setUpWidgets()
        
    def setUpWidgets(self) -> None:
        self.wheelLabel = QLabel(self)
        self.progressBar = QProgressBar(self)
        self.infoLabel = QLabel(self)
        self.infoLabel.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

        self.mainLayout = QHBoxLayout()
        self.mainLayout.addWidget(self.wheelLabel)
        self.mainLayout.addWidget(self.progressBar)
        self.mainLayout.addWidget(self.infoLabel, stretch=1)

        self.wheelMovie = QtGui.QMovie(self)
        self.wheelMovie.setFileName(getPath("load.gif"))
        self.wheelMovie.setScaledSize(QtCore.QSize(20, 20))
        self.wheelMovie.start()

        self.wheelLabel.setMovie(self.wheelMovie)
        self.wheelLabel.hide()
        self.progressBar.setRange(0, 100)
        self.progressBar.setFixedHeight(25)
        if(_platform=="win32"): self.parentWindow.taskbprogress.setRange(0, 100)
        self.progressBar.setValue(0)
        if(_platform=="win32"): self.parentWindow.taskbprogress.setValue(0)
        self.progressBar.setFixedSize(400, 20)
        self.progressBar.setFormat("Ready")
        self.infoLabel.setText(self.clickToStartText)

        self.mainLayout.setMargin(0)

        self.setLayout(self.mainLayout)

    def startLoading(self) -> None:
        self.isLoading = True
        if(_platform=="win32"): self.parentWindow.taskbprogress.show()
        if(_platform=="win32"): self.parentWindow.taskbprogress.setValue(0)
        self.progressBar.setValue(0)
        if(_platform=="win32"): self.parentWindow.taskbprogress.setRange(0, 0)
        self.progressBar.setRange(0, 0)
        self.infoLabel.setText(self.processingText)
        self.progressBar.setFormat("%p%")
        self.wheelLabel.show()

    def stopLoading(self) -> None:
        self.isLoading = False
        self.wheelLabel.hide()
        if(_platform=="win32"): self.parentWindow.taskbprogress.hide()
        if(_platform=="win32"): self.parentWindow.taskbprogress.setRange(0, 100)
        self.progressBar.setRange(0, 100)
        if(_platform=="win32"): self.parentWindow.taskbprogress.setValue(0)
        self.progressBar.setValue(0)
        self.progressBar.setFormat("Ready")
        self.infoLabel.setText(self.clickToStartText)
    
    def setText(self, text: str) -> None:
        self.infoLabel.setText(text)
        self.infoLabel.setToolTip(text)

    def setRange(self, min: int, max: int) -> None:
        self.progressBar.setRange(min, max)
        if(_platform=="win32"): self.parentWindow.taskbprogress.setRange(min, max)
    
    def setValue(self, value: int) -> None:
        self.progressBar.setValue(value)
        if(_platform=="win32"): self.parentWindow.taskbprogress.setValue(value)


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


class ComboBoxAction(QWidget):
    def __init__(self, parent=None, text: str = "", items: list = []):
        super().__init__(parent=parent)
        self.setLayout(QtWidgets.QHBoxLayout(self))
        self.label = QLabel(text)
        self.layout().addWidget(self.label)
        self.layout().setMargin(1)
        self.combo = QComboBox(self)
        self.layout().addWidget(self.combo)
        self.setItems(items)
    
    def setText(self, text: str) -> None:
        self.label.setText(text)
    
    def setItems(self, items: list) -> None:
        for item in items:
            self.combo.addItem(item)
        
    def setIndex(self, index: int) -> None:
        self.combo.setCurrentIndex(index)
    
    def getSelectedItem(self) -> str:
        return self.combo.currentText()

class CheckBoxAction(QWidget):
    def __init__(self, parent=None, text: str = "", checked: bool = False, onState: str = "Enabled", offState: str = "Disabled"):
        super().__init__(parent=parent)
        self.onState = onState
        self.offState = offState
        self.setLayout(QtWidgets.QHBoxLayout(self))
        self.avoidInternalChecking = False
        if not(settings["plainAppearance"]):
            if(settings["mode"] == "dark"):
                isLight = False
            elif(settings["mode"] == "light"):
                isLight = True
            else:
                isLight = self.window().isLight()
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
        self.label = QLabel(text)
        self.layout().addWidget(self.label)
        self.layout().setMargin(1)
        self.check = QCheckBox(self)
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
    
    def setCheckedWithoutInternalChecking(self, value: bool) -> None:
        self.avoidInternalChecking = True
        return self.check.setChecked(value)
    
    def setChecked(self, value: bool) -> None:
        return self.check.setChecked(value)
    
    def changeText(self) -> None:
        if(self.check.isChecked()):
            self.check.setText(self.onState)
        else:
            self.check.setText(self.offState)


class SpinBoxAction(QWidget):
    def __init__(self, parent=None, text: str = "", min: int = 0, max: int = 10, val: int = 5):
        super().__init__(parent=parent)
        self.setLayout(QtWidgets.QHBoxLayout(self))
        self.label = QLabel(text)
        self.layout().addWidget(self.label)
        self.layout().setMargin(1)
        self.combo = QSpinBox(self)
        self.layout().addWidget(self.combo)
        self.setRange(min, max)
        self.combo.setValue(val)
    
    def setText(self, text: str) -> None:
        self.label.setText(text)
    
    def setRange(self, min: int, max: int) -> None:
        self.combo.setMinimum(min)
        self.combo.setMaximum(max)
    
    def getSelectedItem(self) -> int:
        return self.combo.value()







        
if(__name__ == "__main__"):
    import __init__
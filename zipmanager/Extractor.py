
from PySide2 import QtWidgets, QtGui, QtCore
from functools import partial
from Tools import *
from CustomWidgets import TreeWidget, ProgressUpdater, KillableThread, CheckBoxActionForTreeWidget, SpinBoxAction, CheckBoxAction
#from Tools import log, debugging, _platform, getFileIcon, getPath, openOnExplorer, notify, settings, tempDir
import os, zipfile, time, sys
from sys import platform as _platform
from threading import Thread
import subprocess
from qt_thread_updater import get_updater


class Extractor(QtWidgets.QWidget):
    throwInfoSignal = QtCore.Signal(str, str)
    throwWarningSignal = QtCore.Signal(str, str)
    throwErrorSignal = QtCore.Signal(str, str)
    showFileSignal = QtCore.Signal(str)
    
    updateProgressBar = QtCore.Signal([int, int], [int, int, str])
    
    changeItemIcon = QtCore.Signal(object, int, str)
    changeItemText = QtCore.Signal(object, int, str)

    stopLoadingSignal = QtCore.Signal()
    
    
    callInMain = QtCore.Signal(object)


    def __init__(self, parent=None, startFile: str = ""):
        super().__init__(parent=parent)
        self.window = parent
        self.isExtracting = False
        self.errorWhileCompressing = None
        self.compression_level = 5
        self.files = []
        self.zip = ""
        self.setUpToolBar()
        self.setUpWidgets()
        self.throwInfoSignal.connect(self.throwInfo)
        self.throwWarningSignal.connect(self.throwWarning)
        self.throwErrorSignal.connect(self.throwError)
        self.showFileSignal.connect(self.showFile)
        self.callInMain.connect(lambda f: f())
        
        self.changeItemIcon.connect(lambda a, b, c: self.changeItemIconFun(a, b, c))
        self.changeItemText.connect(lambda a, b, c: self.changeItemTextFun(a, b, c))

        self.updateProgressBar[int, int].connect(self.updateProgressBarValue)
        self.updateProgressBar[int, int, str].connect(self.updateProgressBarValue)

        self.stopLoadingSignal.connect(self.stopLoading)

        if(startFile != ""):
            self.openZip(startFile)
            
        self.cachedIcons = {}
        
        
        if not(settings["plainAppearance"]):
            if(settings["mode"] == "dark"):
                isLight = False
            elif(settings["mode"] == "light"):
                isLight = True
            else:
                isLight = darkdetect.isLight() if darkdetect.isLight()!=None else True
            if(isLight):
                self.setStyleSheet(f"""
                    #QCheckBoxAction::indicator {{width: 12px;height: 12px;}}
                    #QCheckBoxAction::indicator:checked{{background-color: #058fff;border-radius: 3px;image: url({getPath("checkCheckedBlack.png")});}}
                    #QCheckBoxAction::indicator:indeterminate{{background-color: #058fff;border-radius: 3px;image: url({getPath("checkUnknowndBlack.png")});}}
                    #QCheckBoxAction::indicator:unchecked{{background-color: transparent;border-radius: 3px;image: url({getPath("checkUncheckedBlack.png")});}}
                    """)
            else:
                self.setStyleSheet(f"""
                    #QCheckBoxAction::indicator {{width: 12px;height: 12px;}}
                    #QCheckBoxAction::indicator:checked{{background-color: #058fff;border-radius: 3px;image: url({getPath("checkCheckedWhite.png")});}}
                    #QCheckBoxAction::indicator:indeterminate{{background-color: #058fff;border-radius: 3px;image: url({getPath("checkUnknowndWhite.png")});}}
                    #QCheckBoxAction::indicator:unchecked{{background-color: transparent;border-radius: 3px;image: url({getPath("checkUncheckedWhite.png")});}}
                    """)
            
    def changeItemIconFun(self, item: QtWidgets.QTreeWidgetItem, index: int, icon: str):
        if icon in self.cachedIcons:
            item.setIcon(index, self.cachedIcons[icon])
        else:
            icn = QtGui.QIcon(QtGui.QPixmap(icon).scaledToHeight(16, QtCore.Qt.SmoothTransformation))
            self.cachedIcons[icon] = icn
            item.setIcon(index, icn)
            
    def changeItemTextFun(self, item: QtWidgets.QTreeWidgetItem, index: int, text: str):
        item.setText(index, text)
        if(text=="Extracting"):
            self.treeWidget.scrollToItem(item)
        item.setToolTip(index, text)
    
    def throwInfo(self, title: str, body: str) -> None:
        try:
            self.window.throwInfo(title, body)
        except AttributeError:
            log(f"[ FAILED ] Unable to show info message!!!\n\n[                   ] Info: {body}")
    
    def throwError(self, title: str, body: str) -> None:
        try:
            self.window.throwError(title, body)
        except AttributeError as e:
            log(f"[ FAILED ] Unable to show error message!!!\n\n[                   ] Info: {body}")
            if(debugging):
                raise e

    def throwWarning(self, title: str, body: str) -> None:
        try:
            self.window.throwWarning(title, body)
        except AttributeError:
            log(f"[ FAILED ] Unable to show warning message!!!\n\n[                   ] Info: {body}")

    def setUpToolBar(self) -> None:
        self.toolBar = QtWidgets.QToolBar(self)
        self.toolBar.setIconSize(QtCore.QSize(24, 24))
        self.toolBar.setContentsMargins(0, 0, 0, 0)

        self.addFileAction = QtWidgets.QAction("Open zip file", self)
        self.addFileAction.setToolTip("Open zip file")
        self.addFileAction.setIcon(QtGui.QIcon(getPath("openzip.ico")))
        self.addFileAction.triggered.connect(lambda: self.openZip())
        self.toolBar.addAction(self.addFileAction)

        self.toolBar.addSeparator()

        self.subdircheck = CheckBoxAction(self, "Extract on a new folder: ", settings["create_subdir"])
        self.toolBar.addWidget(self.subdircheck)

        self.toolBar.addSeparator()

        self.selectNoneAction = QtWidgets.QAction("Select none", self)
        self.selectNoneAction.setToolTip("Select none")
        self.selectNoneAction.setIcon(QtGui.QIcon(getPath("selectnone.png")))
        self.selectNoneAction.triggered.connect(self.selectNone)
        self.toolBar.addAction(self.selectNoneAction)
        
        self.selectAllAction = QtWidgets.QAction("Select all", self)
        self.selectAllAction.setToolTip("Select all")
        self.selectAllAction.setIcon(QtGui.QIcon(getPath("selectall.png")))
        self.selectAllAction.triggered.connect(self.selectAll)
        self.toolBar.addAction(self.selectAllAction)
        
        self.invertSelectionAction = QtWidgets.QAction("Invert selection", self)
        self.invertSelectionAction.setToolTip("Invert selection")
        self.invertSelectionAction.setIcon(QtGui.QIcon(getPath("invertselect.png")))
        self.invertSelectionAction.triggered.connect(self.invertSelection)
        self.toolBar.addAction(self.invertSelectionAction)
        
        self.toolBar.addSeparator()

        self.openFilesAction = QtWidgets.QAction("Open file without extracting", self)
        self.openFilesAction.setToolTip("Open file without extracting")
        self.openFilesAction.setIcon(QtGui.QIcon(getPath("window.ico")))
        self.openFilesAction.triggered.connect(self.openItemFile)
        self.toolBar.addAction(self.openFilesAction)
        
        self.toolBar.addSeparator()
        
        self.magicAction = QtWidgets.QAction("Compress", self)
        self.magicAction.setToolTip("Compress")
        self.magicAction.setIcon(QtGui.QIcon(getPath("extractFiles.ico")))
        self.magicAction.triggered.connect(self.magicButtonAction)
        self.toolBar.addAction(self.magicAction)
            
    def selectAll(self) -> None:
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            if(item.text(1) == ""):
                self.treeWidget.itemWidget(item, 2).setCheckedWithoutInternalChecking(True)
                self.selectAllSubChild(item)
            else:
                self.treeWidget.itemWidget(item, 2).setCheckedWithoutInternalChecking(True)
                
    def selectAllSubChild(self, child: QtWidgets.QTreeWidgetItem) -> None:
        for i in range(child.childCount()):
            item = child.child(i)
            if(item.text(1) == ""):
                self.treeWidget.itemWidget(item, 2).setCheckedWithoutInternalChecking(True)
                self.selectAllSubChild(item)
            else:
                self.treeWidget.itemWidget(item, 2).setCheckedWithoutInternalChecking(True)
    
    def selectNone(self) -> None:
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            if(item.text(1) == ""):
                self.treeWidget.itemWidget(item, 2).setCheckedWithoutInternalChecking(False)
                self.selectNoneSubChild(item)
            else:
                self.treeWidget.itemWidget(item, 2).setCheckedWithoutInternalChecking(False)
                
    def selectNoneSubChild(self, child: QtWidgets.QTreeWidgetItem) -> None:
        for i in range(child.childCount()):
            item = child.child(i)
            if(item.text(1) == ""):
                self.treeWidget.itemWidget(item, 2).setCheckedWithoutInternalChecking(False)
                self.selectNoneSubChild(item)
            else:
                self.treeWidget.itemWidget(item, 2).setCheckedWithoutInternalChecking(False) 
    
    def invertSelection(self) -> None:
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            if(item.text(1) == ""):
                self.treeWidget.itemWidget(item, 2).setCheckedWithoutInternalChecking(not(self.treeWidget.itemWidget(item, 2).isChecked()))
                self.invertSelectionSubChild(item)
            else:
                self.treeWidget.itemWidget(item, 2).setChecked(not(self.treeWidget.itemWidget(item, 2).isChecked()))
                
    def invertSelectionSubChild(self, child: QtWidgets.QTreeWidgetItem) -> None:
        for i in range(child.childCount()):
            item = child.child(i)
            if(item.text(1) == ""):
                self.treeWidget.itemWidget(item, 2).setCheckedWithoutInternalChecking(not(self.treeWidget.itemWidget(item, 2).isChecked()))
                self.invertSelectionSubChild(item)
            else:
                self.treeWidget.itemWidget(item, 2).setChecked(not(self.treeWidget.itemWidget(item, 2).isChecked()))

    def setUpWidgets(self) -> None:

        log("[        ] Now loading widgets...")

        self.treeWidget = TreeWidget(self)
        self.treeWidget.setSortingEnabled(True)
        self.treeWidget.setEmptyText("Select a zip file to start")
        self.treeWidget.connectFileDragEvent(self.openZip)
        self.treeWidget.setHeaderLabels(["Name", "Empty Slot", "Extract or skip", "Real size", "Compressed size", "Status", "Location inside the zip"])
        self.treeWidget.setColumnWidth(5, 100)
        self.treeWidget.setColumnWidth(3, 100)
        self.treeWidget.setColumnWidth(4, 110)
        self.treeWidget.setColumnWidth(6, 150)
        self.treeWidget.setColumnHidden(1, True)
        self.treeWidget.itemDoubleClicked.connect(self.openItemFile)
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)  
        self.treeWidget.customContextMenuRequested.connect(self.showRightClickMenu)

        self.magicButton = QtWidgets.QPushButton(self)
        self.magicButton.setFixedHeight(25)
        self.magicButton.setText("Extract")
        self.magicButton.clicked.connect(self.magicButtonAction)

        self.currentStatusBar = ProgressUpdater(self, self.window, "Extracting...", "Click extract to start")
        
        self.horLayout1 = QtWidgets.QHBoxLayout()

        verLayout1 = QtWidgets.QVBoxLayout()
        verLayout2 = QtWidgets.QVBoxLayout()


        self.zipFileInfo = QtWidgets.QGroupBox()
        self.zipFileInfo.setTitle("Zip file information")
        self.infoLayout = QtWidgets.QFormLayout()
        self.zipFileInfo.setLayout(self.infoLayout)
        self.zipFileInfo.setFixedWidth(256)


        self.zipName = QtWidgets.QLineEdit()
        self.zipName.setFocusPolicy(QtCore.Qt.NoFocus)
        self.infoLayout.addRow("Zip name:", self.zipName)

        self.zipPath = QtWidgets.QLineEdit()
        self.zipPath.setFocusPolicy(QtCore.Qt.NoFocus)
        self.infoLayout.addRow("Zip location:", self.zipPath)
        
        self.zipSize = QtWidgets.QLineEdit()
        self.zipSize.setFocusPolicy(QtCore.Qt.NoFocus)
        self.infoLayout.addRow("Compressed size:", self.zipSize)
        
        self.zipRealSize = QtWidgets.QLineEdit()
        self.zipRealSize.setFocusPolicy(QtCore.Qt.NoFocus)
        self.infoLayout.addRow("Real size:", self.zipRealSize)
        
        self.zipRate = QtWidgets.QLineEdit()
        self.zipRate.setFocusPolicy(QtCore.Qt.NoFocus)
        self.infoLayout.addRow("Compression rate:", self.zipRate)
        
        self.zipAlgorithm = QtWidgets.QLineEdit()
        self.zipAlgorithm.setFocusPolicy(QtCore.Qt.NoFocus)
        self.infoLayout.addRow("Used algoritms: ", self.zipAlgorithm)




        verLayout1.addWidget(self.zipFileInfo)
        verLayout1.addWidget(self.magicButton)
        verLayout2.addWidget(self.treeWidget)
        verLayout2.addWidget(self.currentStatusBar)

        self.horLayout1.addLayout(verLayout1)
        self.horLayout1.addLayout(verLayout2, strech=1)

        self.mainVerLayout = QtWidgets.QVBoxLayout(self)
        self.mainVerLayout.addWidget(self.toolBar)
        self.mainVerLayout.addLayout(self.horLayout1)

        self.setLayout(self.mainVerLayout)

    def magicButtonAction(self) -> None:
        if not(self.isExtracting):
            self.startLoading()
        else:
            self.stopLoading()
    
    def startLoading(self) -> None:
        self.magicButton.setText("Cancel extraction")
        self.isExtracting = True
        self.treeWidget.expandAll()
        self.currentStatusBar.startLoading()
        self.addFileAction.setEnabled(False)
        self.subdircheck.setEnabled(False)
        self.magicAction.setText("Cancel Extraction")
        self.magicAction.setToolTip("Cancel Extraction")
        self.magicAction.setIcon(QtGui.QIcon(getPath("cancelCompress.ico")))
        self.extractZip()
    
    def stopLoading(self) -> None:
        self.magicButton.setText("Extract")
        self.isExtracting = False
        self.treeWidget.setEnabled(True)
        self.addFileAction.setEnabled(True)
        self.subdircheck.setEnabled(True)
        self.magicAction.setText("Extract")
        self.magicAction.setToolTip("Extract")
        self.magicAction.setIcon(QtGui.QIcon(getPath("extractFiles.ico")))
        self.currentStatusBar.stopLoading()
    
    def openItemFile(self) -> None:
        item = self.treeWidget.currentItem()
        if(item.text(4)!=""):
            log("[        ] Opening file with default app...")
            archive = zipfile.ZipFile(self.zip)
            self.currentStatusBar.setRange(0, 0)
            self.currentStatusBar.setText(f"Reading {item.text(0)}...")
            self.currentStatusBar.startLoading()
            Thread(target=self.extractOnlyOneFile, args=(archive, item)).start()
    
    def extractOnlyOneFile(self, archive: zipfile.ZipFile, item: QtWidgets.QTreeWidgetItem) -> None:
        path = archive.extract(item.text(6), tempDir.name)
        archive.close()
        
        self.showFileSignal.emit(path)
        
    def showFile(self, path: str) -> None:
        self.openOSFileDirectly(path)
        self.currentStatusBar.stopLoading()
    
    def updateProgressBarValue(self, actual: int, total: int, actualFile=""):
        if(actualFile!=""):
            try:
                size = os.path.getsize(actualFile)
                size = size/1000
                if(size<1000):
                    fsize = f"{size:.2f} KB"
                else:
                    fsize = f"{size/1000:.2f} MB"

            except FileNotFoundError:
                fsize = "0 B"
            self.currentStatusBar.infoLabel.setText(f"Extracting file \"{actualFile}\" ({fsize}, {actual} out of {total})")
            if(actual!=total):
                self.setWindowTitle(f"SomePythonThings Zip Manager - Extracting {actual} out of {total}")
            else:
                self.setWindowTitle(f"SomePythonThings Zip Manager")
        else:
            self.currentStatusBar.infoLabel.setText("Extracting...")
        self.currentStatusBar.setRange(0, total)
        self.currentStatusBar.setValue(actual)

    def showRightClickMenu(self, pos: QtCore.QPoint) -> None:
        x = 0
        x = 0
        x += self.treeWidget.pos().x()
        x += self.window.pos().x()
        x += pos.x()
        y = 0
        y += 90 # Tab widget + menubar
        y += self.treeWidget.pos().y()
        y += self.window.pos().y()
        y += pos.y()
        log(f"[        ] Showing menu at {x}x{y}")
        menu = QtWidgets.QMenu(self)
        menu.move(x, y)

        menu.addAction(self.addFileAction)
        
        menu.addSeparator()

        menu.addAction(self.openFilesAction)

        menu.addSeparator()
        
        menu.addAction(self.selectNoneAction)
        menu.addAction(self.selectAllAction)
        menu.addAction(self.invertSelectionAction)
        
        menu.addSeparator()

        menu.addAction(self.magicAction)

        menu.exec_()
    
    def openOSFileDirectly(self, file: str) -> None:
        log(f"[        ] Spawining process to open file {file}")
        if(_platform=="win32"):
            os.startfile(file)
            c = 0
            #c = os.system(f"start \"\" \"{file}\"")#, shell=False, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        elif(_platform=="darwin"):
            c = os.system(f"open \"{file}\"")
            #c = subprocess.run(f"open \"{file}\"", shell=False, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            c = os.system(f"xdg-open \"{file}\"")
            #c = subprocess.run(f"xdg-open \"{file}\"", shell=False, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if(c != 0):
            self.throwError("Error opening file", f"Unable to open file \"{file}\"\n\nOutput code: \"{c.returncode}\"\n\nError Details: \n\"{str(c.stdout)}\"")
        else:
            log("[   OK   ] File opened succesfully (exit code is 0)")

    def openZip(self, filepath: str = "") -> None:
        try:
            if(filepath != ""):
                if(_platform=="win32" and filepath[0]=="/"):
                    filepath = filepath[1:]
                filepath = [filepath]
                log('[   OK   ] Zip file given by commandline')
            else:
                log('[        ] Dialog in process')
                filepath = QtWidgets.QFileDialog.getOpenFileName(self.parent(), "Select a zip file to extract it", "", "Zip Files (*.zip);;All files (*.*)")
                if(filepath[0] == ""):
                    log("[  WARN  ] User aborted the dialog")
                    return
            file = open(filepath[0], 'r')
            log('[   OK   ] Dialog Completed')
            supposedZip = str(file.name)
            log('[        ] Closing file')
            file.close()
            log('[   OK   ] File Closed.')
            
            if not zipfile.is_zipfile(supposedZip):
                self.throwError("Error", f"The file {supposedZip} is not a valid zip file!")
                return
            else:
                self.loadZipAsync(supposedZip)
        except Exception as e:
            if debugging:
                raise e
                
    def loadZipAsync(self, supposedZip):
        try:
            callInMain = self.callInMain
            
            callInMain.emit(lambda: self.startLoading())
            callInMain.emit(lambda: self.treeWidget.clear())
            zip = supposedZip.replace("\\", "/")
            self.zip = zip
            zipFile = zipfile.ZipFile(zip)

            size = 0
            compSize = 0

            deflate, lzma, bzip2, stored = False, False, False, False
            
            files = []
            folders: dict = {}
            infos = []

            for element in zipFile.namelist():
                if(element[-1] == "/"): # if isdir
                    pass
                else:
                    files.append(element.split('/'))
                    infoelement = zipFile.getinfo(element)
                    infos.append(infoelement)
                    
                    compSize += infoelement.compress_size
                    size += infoelement.file_size
                    if not(deflate):
                        if(infoelement.compress_type == zipfile.ZIP_DEFLATED):
                            deflate = True
                    if not(lzma):
                        if(infoelement.compress_type == zipfile.ZIP_LZMA):
                            lzma = True
                    if not(bzip2):
                        if(infoelement.compress_type == zipfile.ZIP_BZIP2):
                            bzip2 = True
                    if not(stored):
                        if(infoelement.compress_type == zipfile.ZIP_STORED):
                            stored = True

            zipAlgorithms = ""
            if(deflate):
                zipAlgorithms += "Deflated; "
            if(lzma):
                zipAlgorithms += "LZMA; "
            if(bzip2):
                zipAlgorithms += "BZIP2; "
            if(stored):
                zipAlgorithms += "Stored; "

            callInMain.emit(lambda: self.zipName.setText(zip.split("/")[-1]))
            callInMain.emit(lambda: self.zipPath.setText('/'.join(zip.split("/")[:-1])))
            callInMain.emit(lambda: self.zipSize.setText(f"{compSize/1000000:.2f} MB"))
            callInMain.emit(lambda: self.zipRealSize.setText(f"{size/1000000:.2f} MB"))
            try:
                callInMain.emit(lambda: self.zipRate.setText(f"{compSize/size*100:.1f} %"))
            except ZeroDivisionError:
                callInMain.emit(lambda: self.zipRate.setText("100%"))
            callInMain.emit(lambda: self.zipAlgorithm.setText(zipAlgorithms))

            
            
            infoindex = 0
            itemsToProcess = []
            folderIcon = QtGui.QIcon(getFileIcon(os.path.expanduser("~")))
            
            def newItem(path, info, dirLevel, file):
                item =  QtWidgets.QTreeWidgetItem()
                item.setText(0, path)
                item.setText(6, "/".join(info.filename.split("/")[:dirLevel+1]))
                if(dirLevel+1<len(file)):
                    item.setText(3, "")
                    item.setText(7, "folder")
                    try:
                        item.setIcon(0, folderIcon)
                    except:
                        pass
                else:
                    item.setText(3, f"{info.file_size/1000000:.3f} MB")
                    item.setText(4, f"{info.compress_size/1000000:.3f} MB")
                    item.setText(7, "file")
                    try:
                        item.setIcon(0, QtGui.QIcon(getFileIcon(path)))
                    except:
                        pass
                folders[idpath] = item
                itemsToProcess.append(item)
                
            for file in files:
                try:
                    info: zipfile.ZipInfo = infos[infoindex]
                    dirLevel = 0
                    parentWidgets = []
                    while dirLevel<len(file):
                        path = file[dirLevel]
                        idpath = path+f"_lvl{file[:dirLevel]}"
                        if(idpath in folders):
                            parentWidgets.append(folders[idpath])
                            dirLevel += 1
                        else:
                            log(f"[        ] Adding item {path}")
                            
                            callInMain.emit(lambda: newItem(path, info, dirLevel, file))
                        

                    dirLevel = 0
                    while dirLevel<(len(parentWidgets)-1):
                        parentWidgets[dirLevel].addChild(parentWidgets[dirLevel+1])
                        dirLevel += 1
                    
                except Exception as e:
                    callInMain.emit(lambda: self.throwError("SomePythonThings Zip Manager", f"Unable to load file {file}\n\nError Details:\n{str(e)}"))
                    if(debugging):
                        raise e
                infoindex += 1

            for folder in folders.values():
                callInMain.emit(lambda: self.treeWidget.addTopLevelItem(folder))
            callInMain.emit(lambda: self.treeWidget.expandAll())
            
            def changeState(checkbox: CheckBoxAction, item: QtWidgets.QTreeWidgetItem):
                if(checkbox.avoidInternalChecking):
                    checkbox.avoidInternalChecking = False
                    item.setDisabled(not(checkbox.isChecked()))
                else:
                    item.setDisabled(not(checkbox.isChecked()))
                    for i in range(item.childCount()):
                        subitem = item.child(i)
                        subcheckbox = subitem.treeWidget().itemWidget(subitem, 2)
                        if(subcheckbox):
                            subitem.setDisabled(not(subcheckbox.isChecked()))
                            subcheckbox.setChecked(checkbox.isChecked())
                        else:
                            log("[  WARN  ] Unable to disable/enable other checkboxes")
                        
                        
                        
            def addCheckbox(item):
                checkbox = CheckBoxActionForTreeWidget(checked=True, onState="Extract", offState="Skip")
                checkbox.check.stateChanged.connect(lambda: changeState(checkbox, item))
                item.treeWidget().setItemWidget(item, 2, checkbox)     
                        
            for item in itemsToProcess:
                callInMain.emit(lambda: addCheckbox(item))
                
            if(self.treeWidget.topLevelItemCount() == 1):
                callInMain.emit(lambda: self.subdircheck.setChecked(False))
                callInMain.emit(lambda: self.subdircheck.setText("Extract on a new folder (This zip file has a root folder already!): "))
            else:
                callInMain.emit(lambda: self.subdircheck.setChecked(settings["create_subdir"]))
                callInMain.emit(lambda: self.subdircheck.setText("Extract on a new folder: "))
            callInMain.emit(lambda: self.stopLoading())
        except Exception as e:
            callInMain.emit(lambda: self.stopLoading())
            callInMain.emit(lambda: self.throwError("SomePythonThings Zip Manager", "Unable to select zip file.\n\nReason:\n"+str(e)))
            if(debugging):
                raise e
            

    def extractZip(self):
        zip = self.zip
        if(self.zip == ''):
            self.window.throwWarning("SomePythonThings Zip Manager", "Please select one zip file to start the extraction.")
            self.stopLoading()
        else:
            try:
                zip = zip.replace("\\", "/")
                log('[        ] Dialog in proccess')
                directory = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select the destination folder where the zip is going to be extracted', os.path.expanduser("~"))
                if(directory == ''):
                    log("[  WARN  ] User aborted the dialog")
                    self.stopLoading()
                    return 0
                log('[   OK   ] zip file selected successfully')
                directory = str(directory)
                if not(directory == ''):
                    if(self.subdircheck.isChecked()):
                        log("[        ] Creating subdirectory...")
                        directory += "/"+zip.split('/')[-1]+" - Extracted files"
                    log("[  INFO  ] Zip file will be extracted into "+directory)

                    def analyzeFileList(files: list, item: QtWidgets.QTreeWidgetItem):
                            if(item.childCount()>0):
                                for i in range(item.childCount()):
                                    files = analyzeFileList(files, item.child(i))
                            else:
                                files.append(item)
                            return files

                    files = []
                    for i in range(self.treeWidget.topLevelItemCount()):
                        files = analyzeFileList(files, self.treeWidget.topLevelItem(i))

                    Thread(target=self.heavyExtract, args=(directory, zip, files), daemon=True).start()
            except Exception as e:
                if debugging:
                    raise e
                log('[ FAILED ] Error occurred while extracting zip File')
                self.window.throwError("SomePythonThings Zip Manager", 'Unable to extract the zip\n\nReason:\n'+str(e))

    def pure_extract(self, zipObj, file, directory, passwd=""):
        self.errorWhileExtracting = None
        try:
            zipObj.extract(file, directory)
        except Exception as e:
            self.errorWhileExtracting = e

    def heavyExtract(self, directory, zip, files):
        try:
            error = False
            log('[        ] Extracting zip file on '+str(directory))
            archive = zipfile.ZipFile(zip)
            totalFiles = 0
            for file in files:
                if(file.treeWidget().itemWidget(file, 2).isChecked()):
                    self.changeItemIcon.emit(file, 5, getPath("not.ico"))
                    self.changeItemText.emit(file, 5, "Queued")
                    totalFiles += 1
                else:
                    pass
                    self.changeItemIcon.emit(file, 5, getPath("skipped.png"))
                    self.changeItemText.emit(file, 5, "Not selected")
            actualFile = 0
            self.errorWhileExtracting = None
            #if(password!=""):
            #    archive.setpassword(bytes(password, 'utf-8'))
            for item in files:
                if(item.treeWidget().itemWidget(item, 2).isChecked()):
                    file = item.text(6)
                    try:
                        self.changeItemIcon.emit(item, 5, getPath("loading.ico"))
                        self.changeItemText.emit(item, 5, "Extracting")
                        self.updateProgressBar[int, int, str].emit(actualFile, totalFiles, file)
                        t = KillableThread(target=self.pure_extract, args=( archive, file, directory))
                        t.start()
                        while t.is_alive():
                            if not(self.isExtracting):
                                log("[  WARN  ] User canceled the zip extraction!")
                                self.stopLoadingSignal.emit()
                                t.shouldBeRuning=False
                                for item in files:
                                    self.changeItemIcon.emit(item, 5, getPath("warn.ico"))
                                    self.changeItemText.emit(item, 5, "Canceled")
                                self.throwWarningSignal.emit("SomePythonThings Zip Manager", "User cancelled the zip extraction")
                                archive.close()
                                sys.exit("User killed zip creation process")
                            else:
                                time.sleep(0.01)
                        t.join()
                        if(self.errorWhileExtracting!=None):
                            raise self.errorWhileExtracting
                        log('[   OK   ] File '+file.split('/')[-1]+' extracted successfully')
                        self.changeItemIcon.emit(item, 5, getPath("ok.ico"))
                        self.changeItemText.emit(item, 5, "Done")
                    except Exception as e:
                        self.changeItemIcon.emit(item, 5, getPath("warn.ico"))
                        self.changeItemText.emit(item, 5, str(e))
                        log('[  WARN  ] Unable to extract file ' +file.split('/')[-1])
                        self.throwWarningSignal.emit("SomePythonThings Zip Manager", 'Unable to extract file '+file.split('/')[-1]+"\n\nReason:\n"+str(e))
                        error = True
                    finally:
                        actualFile += 1
                else:
                    log(f"[   OK   ] Skipping file {item.text(0)}")
            self.updateProgressBar[int, int].emit(totalFiles, totalFiles)
            notify("Extraction Done!", "SomePythonThings Zip Manager has finished extracting the selected files and folders.", self.window)
            self.stopLoadingSignal.emit()
            if error:
                log('[  WARN  ] Zip file extracted with some errors')
                self.throwWarningSignal.emit("SomePythonThings Zip Manager", 'Zip file extracted with some errors')
            else:
                log('[   OK   ] Zip file extracted sucessfully')
                self.throwInfoSignal.emit("SomePythonThings Zip Manager", 'Zip file extracted sucessfully')
            openOnExplorer(directory, force=True)
        except Exception as e:
            if debugging:
                raise e
            self.stopLoadingSignal.emit()
            log('[ FAILED ] Error occurred while extracting zip File')
            self.throwErrorSignal.emit("SomePythonThings Zip Manager", 'Unable to extract the zip\n\nReason:\n'+str(e))



if(__name__=="__main__"):
    import __init__
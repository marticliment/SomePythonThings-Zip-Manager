
from PySide2 import QtWidgets, QtGui, QtCore
from CustomWidgets import TreeWidget, ProgressUpdater, KillableThread, ComboBoxAction, SpinBoxAction

from Tools import *
#from Tools import log, debugging, _platform, getFileIcon, getPath, openOnExplorer, notify, settings
import os, zipfile, time, sys
from threading import Thread
from sys import platform as _platform
import subprocess
from qt_thread_updater import get_updater

class Compressor(QtWidgets.QWidget):

    setIconSignal = QtCore.Signal(QtWidgets.QTreeWidgetItem, QtGui.QIcon)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mainWindow = parent
        self.isCompressing = False
        self.errorWhileCompressing = None
        self.compression_level = 5
        self.files = [] 
        self.setUpToolBar()
        self.setUpWidgets()
    
    def throwInfo(self, title: str, body: str) -> None:
        try:
            self.mainWindow.throwInfo(title, body)
        except AttributeError:
            log(f"[ FAILED ] Unable to show info message!!!\n\n[                   ] Info: {body}")
    
    def throwError(self, title: str, body: str) -> None:
        try:
            self.mainWindow.throwError(title, body)
        except AttributeError:
            log(f"[ FAILED ] Unable to show error message!!!\n\n[                   ] Info: {body}")

    def throwWarning(self, title: str, body: str) -> None:
        try:
            self.mainWindow.throwWarning(title, body)
        except AttributeError:
            log(f"[ FAILED ] Unable to show warning message!!!\n\n[                   ] Info: {body}")

    def setUpToolBar(self) -> None:
        self.toolBar = QtWidgets.QToolBar(self)
        self.toolBar.setIconSize(QtCore.QSize(24, 24))
        self.toolBar.setContentsMargins(0, 0, 0, 0)

        self.addFileAction = QtWidgets.QAction("Add File", self)
        self.addFileAction.setToolTip("Add one or more files")
        self.addFileAction.setIcon(QtGui.QIcon(getPath("addfile.ico")))
        self.addFileAction.triggered.connect(self.openFile)
        self.toolBar.addAction(self.addFileAction)

        self.addFolderAction = QtWidgets.QAction("Add folder", self)
        self.addFolderAction.setToolTip("Add a folder")
        self.addFolderAction.setIcon(QtGui.QIcon(getPath("addfolder.ico")))
        self.addFolderAction.triggered.connect(self.openFolder)
        self.toolBar.addAction(self.addFolderAction)

        self.toolBar.addSeparator()

        self.removeFileAction = QtWidgets.QAction("Remove selected file(s) from the list", self)
        self.removeFileAction.setToolTip("Remove selected file(s) from the list")
        self.removeFileAction.setIcon(QtGui.QIcon(getPath("deleteFile.ico")))
        self.removeFileAction.triggered.connect(self.removeSelectedFiles)
        self.toolBar.addAction(self.removeFileAction)

        self.removeFilesAction = QtWidgets.QAction("Remove all files from the list", self)
        self.removeFilesAction.setToolTip("Remove all files from the list")
        self.removeFilesAction.setIcon(QtGui.QIcon(getPath("not.ico")))
        self.removeFilesAction.triggered.connect(self.removeFiles)
        self.toolBar.addAction(self.removeFilesAction)

        self.toolBar.addSeparator()

        self.setIconSignal.connect(lambda item, icon: item.setIcon(0, icon))


        self.algorithm = ComboBoxAction(self, "Compression Algorithm: ", ["Deflated", "None", "BZIP2", "LZMA"])
        self.toolBar.addWidget(self.algorithm)

        if(settings["default_algorithm"] == "Deflated"):
            self.algorithm.setIndex(0)
        elif(settings["default_algorithm"] == "LZMA"):
            self.algorithm.setIndex(3)
        elif(settings["default_algorithm"] == "BZIP2"):
            self.algorithm.setIndex(2)
        elif(settings["default_algorithm"] == "Without Compression"):
            self.algorithm.setIndex(1)

        self.toolBar.addSeparator()

        self.rate = SpinBoxAction(self, "Compression rate:", 1, 9, settings["default_level"])
        self.toolBar.addWidget(self.rate)

        self.toolBar.addSeparator()

        self.openFilesAction = QtWidgets.QAction("Open with system application", self)
        self.openFilesAction.setToolTip("Open with system application")
        self.openFilesAction.setIcon(QtGui.QIcon(getPath("window.ico")))
        self.openFilesAction.triggered.connect(self.openItemFile)
        self.toolBar.addAction(self.openFilesAction)
        
        self.toolBar.addSeparator()

        self.magicAction = QtWidgets.QAction("Compress", self)
        self.magicAction.setToolTip("Compress")
        self.magicAction.setIcon(QtGui.QIcon(getPath("compressFiles.ico")))
        self.magicAction.triggered.connect(self.magicButtonAction)
        self.toolBar.addAction(self.magicAction)

    def setUpWidgets(self) -> None:

        log("[        ] Now loading widgets...")

        self.model = QtWidgets.QFileSystemModel(self)
        self.model.setRootPath(os.path.expanduser("~"))
        self.model.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Files)
        self.model.setNameFilterDisables(False)


        self.fileExplorerTreeWidget = QtWidgets.QTreeView(self)
        self.fileExplorerTreeWidget.setSelectionMode(QtWidgets.QTreeView.SelectionMode.ContiguousSelection)
        self.fileExplorerTreeWidget.setDragEnabled(True)
        self.fileExplorerTreeWidget.setModel(self.model)
        self.fileExplorerTreeWidget.setColumnWidth(0, 400)
        self.fileExplorerTreeWidget.setColumnHidden(2, True)
        self.fileExplorerTreeWidget.setRootIndex(self.model.index(os.path.expanduser(os.path.expanduser("~"))))

        self.treeWidget = TreeWidget(self)
        self.treeWidget.setSortingEnabled(True)
        self.treeWidget.setEmptyText("Add some files or folders to start compressing\n\nThen, click \"Compress\" to save them in a zip file")
        self.treeWidget.connectFileDragEvent(self.openFile)
        self.treeWidget.itemDoubleClicked.connect(self.openItemFile)
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)  
        self.treeWidget.customContextMenuRequested.connect(self.showRightClickMenu)

        self.magicButton = QtWidgets.QPushButton(self)
        self.magicButton.setFixedHeight(25)
        self.magicButton.setText("Compress")
        self.magicButton.clicked.connect(self.magicButtonAction)

        self.currentStatusBar = ProgressUpdater(self, self.mainWindow, "Compressing...", "Click compress to start")
        
        self.horLayout1 = QtWidgets.QHBoxLayout()

        verLayout1 = QtWidgets.QVBoxLayout()
        verLayout2 = QtWidgets.QVBoxLayout()

        verLayout1.addWidget(self.fileExplorerTreeWidget)
        verLayout2.addWidget(self.treeWidget)
        verLayout1.addWidget(self.magicButton)
        verLayout2.addWidget(self.currentStatusBar)

        self.horLayout1.addLayout(verLayout1)
        self.horLayout1.addLayout(verLayout2, stretch=1)

        self.mainVerLayout = QtWidgets.QVBoxLayout(self)
        self.mainVerLayout.addWidget(self.toolBar)
        self.mainVerLayout.addLayout(self.horLayout1)

        self.setLayout(self.mainVerLayout)

    def magicButtonAction(self) -> None:
        if not(self.isCompressing):
            self.startLoading()
        else:
            self.stopLoading()
    
    def startLoading(self) -> None:
        self.magicButton.setText("Cancel compression")
        self.isCompressing = True
        self.treeWidget.expandAll()
        self.fileExplorerTreeWidget.setEnabled(False)
        self.currentStatusBar.startLoading()
        self.addFileAction.setEnabled(False)
        self.addFolderAction.setEnabled(False)
        self.removeFileAction.setEnabled(False)
        self.removeFilesAction.setEnabled(False)
        self.algorithm.setEnabled(False)
        self.rate.setEnabled(False)
        self.magicAction.setText("Cancel Compression")
        self.magicAction.setToolTip("Cancel Compression")
        self.magicAction.setIcon(QtGui.QIcon(getPath("cancelCompress.ico")))
        self.createZip()
    
    def stopLoading(self) -> None:
        self.magicButton.setText("Compress")
        self.isCompressing = False
        self.fileExplorerTreeWidget.setEnabled(True)
        self.treeWidget.setEnabled(True)
        self.addFileAction.setEnabled(True)
        self.addFolderAction.setEnabled(True)
        self.removeFileAction.setEnabled(True)
        self.removeFilesAction.setEnabled(True)
        self.algorithm.setEnabled(True)
        self.rate.setEnabled(True)
        self.magicAction.setText("Compress")
        self.magicAction.setToolTip("Compress")
        self.magicAction.setIcon(QtGui.QIcon(getPath("compressFiles.ico")))
        self.currentStatusBar.stopLoading()
    
    def openItemFile(self) -> None:
        item = self.treeWidget.currentItem()
        if(item.text(2)!=""):
            log("[        ] Opening file with default app...")
            self.openOSFileDirectly(item.text(3))
    
    def showRightClickMenu(self, pos: QtCore.QPoint) -> None:
        x = 0
        x += self.treeWidget.pos().x()
        x += self.window().pos().x()
        x += pos.x()
        y = 0
        y += 90 # Tab widget + menubar
        y += self.treeWidget.pos().y()
        y += self.window().pos().y()
        y += pos.y()
        log(f"[        ] Showing menu at {x}x{y}")
        menu = QtWidgets.QMenu(self)
        menu.move(x, y)

        menu.addAction(self.addFileAction)
        menu.addAction(self.addFolderAction)

        menu.addSeparator()

        menu.addAction(self.removeFileAction)
        menu.addAction(self.removeFilesAction)

        menu.addSeparator()

        menu.addAction(self.openFilesAction)
        
        menu.addSeparator()

        menu.addAction(self.magicAction)

        menu.exec_()
    
    def openOSFileDirectly(self, file: str) -> None:
        log(f"[        ] Spawining process to open file {file}")
        if(_platform=="win32"):
            c = os.system(f"start \"\" \"{file}\"")#, shell=False, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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

    def removeFiles(self) -> None:
        self.files = []
        while(self.treeWidget.topLevelItemCount()>0):
            self.treeWidget.takeTopLevelItem(0)
        log('[   OK   ] File list cleared')

    def removeSelectedFiles(self) -> None:
        selectedFiles = self.treeWidget.selectedItems()
        for item in selectedFiles:
            if(item.parent()):
                i = item.parent().takeChild(item.parent().indexOfChild(item))
            else:
                i = self.treeWidget.takeTopLevelItem(self.treeWidget.indexOfTopLevelItem(item))
            del i
        log('[   OK   ] Selected files removed from file list')

    def openFile(self, openFiles="None"):
        filepaths = []
        try:
            if(openFiles=="None" or openFiles == False):
                log('[        ] Dialog in process')
                filepaths = QtWidgets.QFileDialog.getOpenFileNames(self, "Select some files to compress them", '')
                log('[   OK   ] Dialog Completed')
                if(filepaths[0] == []):
                    log("[  WARN  ] User aborted dialog")
                    return 0
            else:
                log('[        ] Not showing dialog, files passed as an argument...')
                filesToAdd = []
                for file in openFiles.split('\n'):
                    file=str(file).replace("\\", "/")
                    if not(file==""):
                        if(_platform=='win32' and file[0]=="/"):
                            file = file[1:]
                        filesToAdd.append(file)
                filepaths.append(filesToAdd)
            for filepath in filepaths[0]:
                if(os.path.isdir(filepath)):
                    self.openFolder(folder=filepath)
                else:
                    file = open(filepath, 'r')
                    filename = file.name.replace("\\", "/")
                    file.close()
                    try:
                        if([filename, os.path.dirname(filename), 'file'] in self.files):
                            log("[  WARN  ] File already there!")
                            if(QtWidgets.QMessageBox.question(self, "The file is already there!", f"The file {filename} is already selected to be compressed. Do tou want to add it anyway?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes):
                                self.files.append([filename, os.path.dirname(filename), 'file'])
                                log("[   OK   ] File added anyway")
                                goAhead = True
                            else:
                                log("[   OK   ] File ommitted")
                                goAhead = False
                        else:
                            log("[        ] File not present in file list, adding it.")
                            self.files.append([filename, os.path.dirname(filename), 'file'])
                            goAhead=True
                        if(goAhead):
                            log('[   OK   ] File "'+str(filename)+'" processed')
                            item = QtWidgets.QTreeWidgetItem()
                            item.setText(0, filename.split('/')[-1])
                            item.setText(1, "{0:.3f} MB".format(os.path.getsize(filename)/1000000))
                            item.setText(2, "Pending")
                            item.setText(3, filename)
                            item.setText(4, "/")
                            try:
                                item.setIcon(0, QtGui.QIcon(getFileIcon(filename)))
                            except:
                                pass
                            self.treeWidget.addTopLevelItem(item)
                    except Exception as e:
                        log('[ FAILED ] Unable to process file "'+filepath+'"')
                        if(debugging):
                            raise e
                        self.throwError("Error processing file!","Unable to read file \""+filename+"\"")
                        try:
                            file.close()
                        except:
                            pass
        except Exception as e:
            if debugging:
                raise e
            self.throwError("SomePythonThings Zip Manager", "An error occurred while adding one or more files. \n\nError detsils: "+str(e))
            log('[ FAILED ] Unable to open file. Returning value 0')
    
    def getChildFolderName(self, baseDir: str, longerDir: str) -> str:
        return longerDir.replace(baseDir, "")
    
    def setIcon(self, item: QtWidgets.QTreeWidgetItem, filename: str) -> None:
        icon = QtGui.QIcon(getFileIcon(filename))
        try:
            log("[   OK   ] Icon loaded successfully")
            self.setIconSignal.emit(item, icon)
        except:
            pass

    def addChildFolder(self, folderItem: QtWidgets.QTreeWidgetItem, folderpath: str, rootFolder: str):
        log(f"[   OK   ] Processing {folderpath} child files...")
        len_root = len(folderpath.replace("\\", "/").split("/"))
        for root, folders, files in os.walk(folderpath):
            root = root.replace("\\", "/")
            for file in files:
                file = file.replace("\\", "/")
                filename = root.replace("\\", "/")+"/"+file
                if(len(root.split('/'))==len_root):
                    log("[   OK   ] Adding child file "+root+"__"+file)
                    item = QtWidgets.QTreeWidgetItem()
                    item.setText(0, filename.split('/')[-1])
                    item.setText(1, "{0:.3f} MB".format(os.path.getsize(filename)/1000000))
                    item.setText(2, "Pending")
                    item.setText(3, filename)
                    item.setText(4, self.getChildFolderName(rootFolder, folderpath))
                    Thread(target=self.setIcon, args=(item, filename)).start()
                    folderItem.addChild(item)
            for folder in folders:
                folder = folder.replace("\\", "/")
                foldername = root.replace("\\", "/")+"/"+folder.replace("\\", "/")
                if(len(root.split('/'))==len_root):
                    log("[   OK   ] Adding child folder "+root+folder)
                    item = QtWidgets.QTreeWidgetItem()
                    item.setText(0, foldername.split('/')[-1])
                    item.setText(1, "{0:.3f} MB".format(os.path.getsize(foldername)/1000000))
                    item.setText(2, "")
                    item.setText(3, "/".join(foldername.split('/')[0:-1]))
                    try:
                        item.setIcon(0, QtGui.QIcon(QtGui.QPixmap(getPath("folder.ico")).scaledToWidth(24, QtCore.Qt.SmoothTransformation)))
                    except:
                        pass
                    folderItem.addChild(item)
                    self.addChildFolder(item, foldername, rootFolder)

    def openFolder(self, folder=""):
        log('[        ] Dialog in process')
        if(folder=="" or folder==False):
            folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select a folder to compress it')
            if folder == "":
                log("[  WARN  ] User aborted dialog")
                self.stopLoading()
        else:
            log("[  WARN  ] Folder was given as argument")
        log('[   OK   ] Dialog Completed')
        try:
            self.files.append([folder, folder, 'folder'])
            folderItem = QtWidgets.QTreeWidgetItem()
            folderItem.setText(0, folder.split('/')[-1])
            folderItem.setText(1, "{0:.3f} MB".format(self.get_size(folder)))
            folderItem.setText(2, "")
            folderItem.setText(3, "/".join(folder.split('/')[0:-1]))
            try:
                folderItem.setIcon(0, QtGui.QIcon(QtGui.QPixmap(getPath("folder.ico")).scaledToWidth(24, QtCore.Qt.SmoothTransformation)))
            except:
                pass
            self.treeWidget.addTopLevelItem(folderItem)
            print(folder, '/'.join(folder.split('/')[:-1]))
            self.addChildFolder(folderItem, folder, '/'.join(folder.split('/')[:-1]))
            log('[   OK   ] Folder selected successfully.')
        except Exception as e:
            if debugging:
                raise e
            self.throwError("Error processing folder!", "Unable to read folder \""+folder+"\"")

    def get_size(self, start_path):
        total_size = 0
        for dirpath, _, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += int(os.path.getsize(fp)/1000000)
        return total_size

    def updateProgressBar(self, actual: int, total: int, actualFile=""):
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
            self.currentStatusBar.infoLabel.setText(f"Compressing file \"{actualFile}\" ({fsize}, {actual} out of {total})")
        else:
            self.currentStatusBar.infoLabel.setText("Compressing...")
        self.currentStatusBar.setRange(0, total)
        self.currentStatusBar.setValue(actual)

    class CreateZipThread(QtCore.QThread):
        
        throwInfo = QtCore.Signal(str, str)
        throwWarning = QtCore.Signal(str, str)
        throwError = QtCore.Signal(str, str)
        
        updateProgressBar = QtCore.Signal([int, int], [int, int, str])
        
        changeItemIcon = QtCore.Signal(QtWidgets.QTreeWidgetItem, int, str)
        changeItemText = QtCore.Signal(QtWidgets.QTreeWidgetItem, int, str)

        def __init__(self, zipfilename: str, files: list, parent):
            super().__init__()
            self.parent: Compressor = parent
            self.zipfilename = zipfilename
            self.files = files
    
        def pureCompress(self, zipObj: zipfile.ZipFile, a, b, compression_algorithm):
            self.errorWhileCompressing = None
            try:
                zipObj.write(a, b, compression_algorithm, self.parent.compression_level)
            except Exception as e:
                self.errorWhileCompressing = e 

        def run(self):
            log("[        ] Starting compression thread...")
            try:
                zipObj = zipfile.ZipFile(self.zipfilename, 'w')
                totalFiles = 0
                for item in self.files:
                    self.changeItemIcon.emit(item, 2, getPath("not.ico"))
                    self.changeItemText.emit(item, 2, "Queued")
                    totalFiles += 1

                log('[  INFO  ] Total number of files: '+str(totalFiles))
                actualFile = 0
                try:
                    algorithm = self.parent.algorithm.getSelectedItem()
                    if(algorithm == "None"):
                        log("[   OK   ] Selected compression algorithm is none: {0}".format(algorithm))
                        compression_type = zipfile.ZIP_STORED
                    elif(algorithm == "LZMA"):
                        log("[   OK   ] Selected compression algorithm is lzma: {0}".format(algorithm))
                        compression_type = zipfile.ZIP_LZMA
                    elif(algorithm == "BZIP2"):
                        log("[   OK   ] Selected compression algorithm is bzip2: {0}".format(algorithm))
                        compression_type = zipfile.ZIP_BZIP2
                    else:
                        log("[   OK   ] Selected compression algorithm is deflated: {0}".format(algorithm))
                        compression_type = zipfile.ZIP_DEFLATED
     
                    self.updateProgressBar[int, int].emit(0, totalFiles)
                except Exception as e:
                    if(debugging):
                        raise e
                    self.throwWarning.emit("SomePythonThongs Zip Manager", "An error occurred while selecting your desired compression algorithm. Compression algorithm will be \"Deflated\". ")
                    compression_type = zipfile.ZIP_DEFLATED

                try:
                    self.parent.compression_level = self.parent.rate.getSelectedItem()
                except Exception as e:
                    if(debugging):
                        raise e
                log(f"[   OK   ] Compress rate set to {self.parent.compression_level}")

                errors = ""
                allDone = True
                for item in self.files:
                    item: QtWidgets.QTreeWidgetItem
                    self.changeItemIcon.emit(item, 2, getPath("loading.ico"))
                    self.changeItemText.emit(item, 2, "Compressing")
                    subdir = item.text(4)
                    path = (item.text(3), '/'.join(item.text(3).split('/')[:-1]), subdir)
                    try:
                        self.updateProgressBar[int, int, str].emit(actualFile, totalFiles, path[0])
                        os.chdir(path[1])
                        if not self.zipfilename == path[0]:
                            t = KillableThread(target=self.pureCompress, args=(zipObj, path[0].split('/')[-1], os.path.join(subdir, path[0].split('/')[-1]), compression_type), daemon=True)
                            t.start()
                            while t.is_alive():
                                if not(self.parent.isCompressing):
                                    log("[  WARN  ] User cancelled the zip creation!")
                                    t.shouldBeRuning=False
                                    for item in self.files:
                                        self.changeItemIcon.emit(item, 2, getPath("warn.ico"))
                                        self.changeItemText.emit(item, 2, "Canceled")
                                    self.throwWarning.emit("SomePythonThings Zip Manager", "User cancelled the zip creation")
                                    time.sleep(0.5)
                                    zipObj.close()
                                    try: 
                                        os.remove(self.zipfilename)
                                    except: 
                                        log("[  WARN  ] Unable to remove zip file")
                                    self.parent.files = []
                                    break
                                else:
                                    time.sleep(0.01)
                            t.join()
                            if(self.errorWhileCompressing != None):
                                raise self.errorWhileCompressing
                            log('[   OK   ] File "'+str(path[0].split('/')[-1])+f'" added successfully on relative directory {subdir}')
                        else:
                            log('[  WARN  ] File "'+str(path[0].split('/')[-1])+'" skipped because it is the output zip')
                        self.changeItemIcon.emit(item, 2, getPath("ok.ico"))
                        self.changeItemText.emit(item, 2, "Done")
                    except Exception as e:
                        allDone = False
                        self.changeItemIcon.emit(item, 2, getPath("warn.ico"))
                        self.changeItemText.emit(item, 2, str(e))
                        log(f'[ FAILED ] Unable to add file "{str(path)}": {e}')
                        errors += " - "+str(path[0])+"\n"
                    finally:
                        actualFile += 1
                    if not(self.parent.isCompressing):
                        break
                zipObj.close()
                if(self.parent.isCompressing):
                    get_updater().call_in_main(self.parent.stopLoading)
                    notify("Compression Done!", "SomePythonThings Zip Manager has finished compressing the selected files and folders.", self.parent.window)
                    if allDone:
                        self.throwInfo.emit("SomepythonThings Zip Manager", 'The Zip file was created sucessfully!')
                        log('[   OK   ] zip file created sucessfully')
                    else:
                        self.throwWarning.emit("SomePythonThings Zip Manager", 'The Zip file was created with some errors: \n'+str(errors))
                        log('[  WARN  ] zip file created with errors:\n'+str(errors))
                    get_updater().call_in_main(openOnExplorer, self.zipfilename, force=False)
            except Exception as e:
                get_updater().call_in_main(self.parent.stopLoading)
                if(debugging):
                    raise e
                log('[ FAILED ] Error occurred while creating zip File')
                try:
                    self.throwError.emit("SomePythonThings Zip Manager", "Unable to create zip file "+self.zipfilename+".\n\nError reason:\n"+str(e))
                except:
                    self.throwError.emit("SomePythonThings Zip Manager", "Unable to create zip file.\n\nError reason:\n"+str(e))
    
    def cancelZipCreation(self):
        self.isCompressing = False
        log("[  WARN  ] Sending cancel signal to compression thread")

    def createZip(self):

        def analyzeFileList( files: list, item: QtWidgets.QTreeWidgetItem):
            if(item.childCount()>0):
                for i in range(item.childCount()):
                    files = analyzeFileList(files, item.child(i))
            else:
                files.append(item)
            return files

        def changeItemIcon(item: QtWidgets.QTreeWidgetItem, index: int, icon: str):
            item.setIcon(index, QtGui.QIcon(QtGui.QPixmap(icon).scaledToHeight(16, QtCore.Qt.SmoothTransformation)))
            
        def changeItemText(item: QtWidgets.QTreeWidgetItem, index: int, text: str):
            item.setText(index, text)
            if(text=="Compressing"):
                self.treeWidget.scrollToItem(item)
            item.setToolTip(index, text)

        try:
            files = []
            for i in range(self.treeWidget.topLevelItemCount()):
                files = analyzeFileList(files, self.treeWidget.topLevelItem(i))
            log('[        ] Preparing zip file')
            if(len(files) < 1):
                self.throwWarning("SomePythonThings Zip Manager","Please add at least one file or one folder to the zip!")
                self.stopLoading()
                return
            try:
                filename = self.files[0][0]
            except:
                filename = files[0].text(0)
            zipfilename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save the zip file', filename+".zip", ("Compressed File;;(.zip)"))[0]
            if zipfilename == "":
                log("[  WARN  ] User aborted dialog")
                self.stopLoading()
                return 
            file = open(zipfilename, 'w')
            log('[   OK   ] zip file created succesfully')
            zipfilename = str(file.name)
            file.close()
            log('[        ] Creating zip file on '+str(zipfilename))
        
            log("[        ] Initializing thread...")
            self.t = self.CreateZipThread(zipfilename, files, self)
            self.t.throwInfo.connect(self.throwInfo)
            self.t.throwWarning.connect(self.throwWarning)
            self.t.throwError.connect(self.throwError)
            self.t.changeItemIcon.connect(changeItemIcon)
            self.t.changeItemText.connect(changeItemText)
            self.t.updateProgressBar[int, int].connect(self.updateProgressBar)
            self.t.updateProgressBar[int, int, str].connect(self.updateProgressBar)
            log("[   OK   ] Thread initialized!")

            self.t.start()
        
        except Exception as e:
            self.throwError("SomePythonThings Zip Manager", "An error occurred while creating the compressed file.\n\nError details:\n"+str(e))
            self.stopLoading()
            if debugging:
                raise e


if(__name__ == "__main__"):
    import __init__

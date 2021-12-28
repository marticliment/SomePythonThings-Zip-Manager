from PySide2 import QtWidgets, QtCore, QtGui
from urllib.request import urlopen
from sys import platform as _platform
from threading import Thread
import platform, os, sys, webbrowser, wget, subprocess

from Tools import *
#from Tools import version, debugging, notify, log, getPath, tempDir
from qt_thread_updater import get_updater



class checkForUpdates(QtWidgets.QProgressDialog):

    throwInfoSignal = QtCore.Signal(str, str)
    throwErrorSignal = QtCore.Signal(str, str)
    dialogSignal = QtCore.Signal(str)
    sysExitSignal = QtCore.Signal()
    askUpdatesSignal = QtCore.Signal(dict)

    closeDialogSignal = QtCore.Signal()
    hideDialogSignal = QtCore.Signal()

    continueSignal = QtCore.Signal(dict)
    
    callInMain = QtCore.Signal(object)

    def __init__(self, parent: QtWidgets.QMainWindow = None, force: bool = False, verbose: bool = False) -> str:
        super().__init__(parent)
        self.force = force
        self.verbose = verbose
        self.callInMain.connect(lambda fun: fun())
        self.setParent(parent)
        self.setAutoFillBackground(True)
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, True)
        self.setModal(True)
        self.setVisible(False)
        self.setCancelButton(None)
        self.setSizeGripEnabled(False)
        self.setWindowTitle('Updater')
        self.setFixedWidth(300)
        self.setFixedHeight(90)
        self.setLabelText(f'Please wait...')
        pgsbar = QtWidgets.QProgressBar()
        pgsbar.setTextVisible(False)
        self.setBar(pgsbar)
        self.setRange(0, 0)
        self.throwInfoSignal.connect(self.throwInfo)
        self.throwErrorSignal.connect(self.throwError)
        self.dialogSignal.connect(self.setLabelText)
        self.sysExitSignal.connect(lambda: self.parent().app.closeAllWindows())
        self.askUpdatesSignal.connect(self.askUpdates)
        self.closeDialogSignal.connect(self.close)
        self.hideDialogSignal.connect(self.hide)
        self.continueSignal.connect(self.checkIfUpdates)
        self.setMinimumDuration(0)
        self.setAutoClose(True)
        if(_platform == 'darwin'):
            self.setAutoFillBackground(True)
            self.setWindowModality(QtCore.Qt.WindowModal)
            self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
            self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
            self.setModal(True)
            self.setSizeGripEnabled(False)
        if(self.verbose):
            self.show()
        else:
            self.hide()
        log("[   OK   ] Starting repo list download thread...")
        Thread(target=self.downloadReleaseFile, daemon=True).start()

    def downloadReleaseFile(self):
        try:
            if(not(self.verbose)):
                self.callInMain.emit(self.close)
            response = urlopen("http://www.somepythonthings.tk/versions/zip.ver")
            response = response.read().decode("utf8")
            self.continueSignal.emit(response)
        except Exception as e:
            if(self.verbose):
                self.throwErrorSignal.emit("Zip Manager Updater", f"Unable to check for updates. Are you connected to the internet?\n\n{str(e)}")
            self.closeDialogSignal.emit()
            if(debugging):
                raise e

    def checkIfUpdates(self, response: bool):
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        try:
            if float(response.split("///")[0]) > version:
                if(_platform=="win32" and int(platform.release())<10):
                    self.closeDialogSignal.emit()
                else:
                    self.show()
                    self.askUpdatesSignal.emit(response)
            elif(self.force):
                if(_platform=="win32" and int(platform.release())<10):
                    self.throwErrorSignal.emit("Outdated Operating System", "Windows 7, 8 and 8.1 won't be supported on next SomePythonThings Zip Manager versions. Please upgrade Windows 10 to recieve new updates.")
                    self.closeDialogSignal.emit()
                else:
                    self.show()
                    self.askUpdatesSignal.emit(response)
            else:
                if(self.verbose):
                    self.show()
                    self.throwInfo("SomePythonThings Zip Manager Updater", f"No updates found!\n\nInstalled version is {version}")
                self.close()
                log("[   OK   ] No updates found")
        except Exception as e:
            if(self.verbose):
                self.throwWarning("SomePythonThings Zip Manager Updater", "Unable to reach SomePythonThings Servers. Are you connected to the internet?")
            self.close()
            log("[  WARN  ] Unable to reach http://www.somepythonthings.tk/versions/zip.ver. Are you connected to the internet?")
            if debugging:
                raise e    

    def askUpdates(self, response: str) -> None:
        notify("SomePythonThings Zip Manager Updater", "SomePythonThings Zip Manager has a new update!\nActual version: {0}\nNew version: {1}".format(version, response.split("///")[0]))
        if QtWidgets.QMessageBox.Yes == self.confirm('SomePythonThings Zip Manager', "There are some updates available for SomePythonThings Zip Manager:\nYour version: "+str(version)+"\nNew version: "+str(response.split("///")[0])+"\nNew features: \n"+response.split("///")[1]+"\nDo you want to download and install them?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes):

            #                'debian': debian link in posotion 2                  'win32' Windows 32bits link in position 3           'win64' Windows 64bits in position 4                   'macos' macOS 64bits INTEL in position 5
            self.show()
            self.downloadUpdates({'debian': response.split("///")[2].replace('\n', ''), 'win32': response.split("///")[3].replace('\n', ''), 'win64': response.split("///")[4].replace('\n', ''), 'macos':response.split("///")[5].replace('\n', '')})
        else:
            self.closeDialogSignal.emit()
            log("[  WARN  ] User aborted update!")


    def downloadUpdates(self, links: dict) -> None:
        log('[   OK   ] Reached downloadUpdates. Download links are "{0}"'.format(links))
        if _platform == 'linux' or _platform == 'linux2':  # If the OS is linux
            raise NotImplementedError("Linux is not supported anymore")
        elif _platform == 'win32':  # if the OS is windows
            if(int(platform.release())<10):
                self.throwErrorSignal.emit("Outdated Operating System", "Windows 7, 8 and 8.1 won't be supported on next SomePythonThings Zip Manager versions. Please upgrade to Windows 10 to recieve new updates")
                self.closeDialogSignal.emit()
            else:
                url = ""
                if(platform.architecture()[0] == '64bit'):  # if OS is 64bits
                    url = (links["win64"])
                else:  # is os is not 64bits
                    url = (links['win32'])
                t = Thread(target=self.download_win, args=(url,))
                t.daemon=True
                t.start()
        elif _platform == 'darwin':
            raise NotImplementedError("Linux is not supported anymore")
        else:  # If os is unknown
            webbrowser.open_new('https://www.somepythonthings.tk/programs/somepythonthings-zip-manager/')

    def download_win(self, url: str) -> None:
        try:
            self.dialogSignal.emit('Downloading the update. Please wait...')
            filedata = urlopen(url)
            datatowrite = filedata.read()
            filename = ""
            with open(os.path.join(os.path.join(tempDir.name, ".."), "SomePythonThings-Zip Manager-Updater.exe"), 'wb') as f:
                f.write(datatowrite)
                filename = f.name
            self.dialogSignal.emit('Launching the updater. Please wait')
            log(f"[   OK   ] file downloaded to {filename}".format(filename))
            get_updater().call_in_main(self.launch_win, filename)
        except Exception as e:
            if debugging:
                raise e
            self.throwErrorSignal.emit("SomePythonThings Zip Manager", "An error occurred while downloading the SomePythonTings Zip Manager installer. Please check your internet connection and try again later\n\nError Details:\n{0}".format(str(e)))
            self.closeDialogSignal.emit()

    def launch_win(self, filename: str) -> None:
        try:
            self.dialogSignal.emit('Launching the updater. Please wait')
            subprocess.run('start /B "" "{0}" /silent'.format(filename), shell=True)
            self.sysExitSignal.emit()
        except Exception as e:
            if debugging:
                raise e
            self.throwError("SomePythonThings Zip Manager Updater", "An error occurred while launching the SomePythonTings Zip Manager installer.\n\nError Details:\n{0}".format(str(e)))
            self.closeDialogSignal.emit()

    def updateProgressBar(self, mode: str) -> None:
        self.dialogSignal.emit(mode)
    

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
        if(os.path.exists(getPath("zip_warn.ico"))):
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
        if(os.path.exists(getPath("zip_error.ico"))):
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
        if(os.path.exists(getPath('zip.ico'))):
            msg.setIconPixmap(QtGui.QPixmap(getPath("zip.ico")).scaledToHeight(96, QtCore.Qt.SmoothTransformation))
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




if __name__ == "__main__":
    import __init__

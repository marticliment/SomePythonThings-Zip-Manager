#Modules
import zipfile
import os
import webbrowser
import urllib.request
import sys
import time
import platform
from sys import platform as _platform
from PyQt5 import QtWidgets, QtGui, QtCore
from zipfile import ZipFile
from threading import Thread
from urllib.request import urlopen
from qt_thread_updater import get_updater
from functools import partial

#Globals
debugging = False
actualVersion = 2.3
zip=""
font = ""
realpath="."
allDone = True
zip_files = ('Zip Files (*.zip);;All files (*.*)')
compression_rate = [zipfile.ZIP_DEFLATED, zipfile.ZIP_BZIP2, zipfile.ZIP_LZMA, zipfile.ZIP_STORED]
files = []
continueExtracting = True
continueCreating = True
buttons = {}
texts = {}
progressbars = {}
lists = {}
labels = {}

#Functions
def log(s):
    global debugging
    if(debugging or "WARN" in str(s) or "FAILED" in str(s)):
        print(str(s))

def notify(title, body, icon='icon-zipmanager.png'):
    global realpath
    notify=False
    if _platform == 'win32':
        if int(platform.release()) >= 10:
            notify=True
    elif _platform == 'darwin':
        notify=True
        print('notify')
    elif _platform == 'linux' or _platform=='linux2':
        notify=True
    if(notify):
        try:
            from notifypy import Notify
            notification = Notify()
            notification.title = str(title)
            notification.message = str(body)
            try:
                notification.icon = realpath+'/'+icon
            except:
                pass
            notification.send(block=True)
        except Exception as e:
            log("[FAILED] Unable to show notification: "+str(e))

def extractFirstZip():
    log("[      ] Checking command line arguments")
    if zip != '':
        log('[  OK  ] Found one argument')
        try:
            if __name__ == "__main__":
                extractZip()
        except Exception as e:
            throw_error("SomePythonThings Zip Manager",
                        "Unable to extract zip.\n\nReason:\n{0}".format(str(e)))


def checkUpdates_py():
    global zipManager, actualVersion
    try:
        response = urllib.request.urlopen(
            "http://www.somepythonthings.tk/versions/zip.ver")
        response = response.read().decode("utf8")
    except:
        log("[ WARN ] Unacble to reach http://www.somepythonthings.tk/versions/zip.ver. Are you connected to the internet?")
        return 'Unable'
    if float(response.split("///")[0]) > actualVersion:
        notify("SomePythonThings Zip Manager Updater", "SomePythonThings Zip Manager has a new update!\nActual version: {0}\nNew version: {1}".format(actualVersion, response.split("///")[0]))
        if QtWidgets.QMessageBox.Yes == QtWidgets.QMessageBox.question(zipManager, 'SomePythonThings Zip Manager', "There are some updates available for SomePythonThings Zip Manager:\nYour version: "+str(actualVersion)+"\nNew version: "+str(response.split("///")[0])+"\nNew features: \n"+response.split("///")[1]+"\nDo you want to go download and install them?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes):

            #                'debian': debian link in posotion 2                  'win32' Windows 32bits link in position 3           'win64' Windows 64bits in position 4                   'macos' macOS 64bits INTEL in position 5
            downloadUpdates({'debian': response.split("///")[2].replace('\n', ''), 'win32': response.split("///")[3].replace('\n', ''), 'win64': response.split("///")[4].replace('\n', ''), 'macos':response.split("///")[5].replace('\n', '')})
            return True
        else:
            log("[ WARN ] User aborted update!")
            return False
    else:
        log("[  OK  ] No updates found")
        return 'No'


def download_win(url):
    try:
        global texts
        os.system('cd %windir%\\..\\ & mkdir SomePythonThings')
        time.sleep(0.01)
        os.chdir("{0}/../SomePythonThings".format(os.environ['windir']))
        installationProgressBar('Downloading')
        get_updater().call_in_main(texts["create"].setPlainText, "The installer is being downloaded. Please wait until the download process finishes. This shouldn't take more than a couple of minutes.\n\nPlease DO NOT close the application")
        get_updater().call_in_main(texts["extract"].setPlainText, "The installer is being downloaded. Please wait until the download process finishes. This shouldn't take more than a couple of minutes.\n\nPlease DO NOT close the application")

        filedata = urlopen(url)
        datatowrite = filedata.read()
        filename = ""
        with open("{0}/../SomePythonThings/SomePythonThings-Zip-Manager-Updater.exe".format(os.environ['windir']), 'wb') as f:
            f.write(datatowrite)
            filename = f.name
        installationProgressBar('Launching')
        get_updater().call_in_main(texts["create"].setPlainText, "Please follow on-screen instructions to continue")
        get_updater().call_in_main(texts["extract"].setPlainText, "Please follow on-screen instructions to continue")
        log(
            "[  OK  ] file downloaded to C:\\SomePythonThings\\{0}".format(filename))
        get_updater().call_in_main(launch_win, filename)
    except Exception as e:
        get_updater().call_in_main(throw_error, "SomePythonThings Zip Manager", "An error occurred while downloading the SomePythonTings Zip Manager installer. Please check your internet connection and try again later\n\nError Details:\n{0}".format(str(e)))


def launch_win(filename):
    try:
        installationProgressBar('Launching')
        throw_info("SomePythonThings Zip Manager Updater", "The file has been downloaded successfully and the setup will start now. When clicking OK, the application will close and a User Account Control window will appear. Click Yes on the User Account Control Pop-up asking for permissions to launch SomePythonThings-Zip-Manager-Updater.exe. Then follow the on-screen instructions.")
        os.system('start /B start /B {0}'.format(filename))
        get_updater().call_in_main(sys.exit)
        sys.exit()
    except Exception as e:
        throw_error("SomePythonThings Zip Manager Updater", "An error occurred while launching the SomePythonTings Zip Manager installer.\n\nError Details:\n{0}".format(str(e)))


def downloadUpdates(links):
    log('[  OK  ] Reached downloadUpdates. Download links are "{0}"'.format(links))
    if _platform == 'linux' or _platform == 'linux2':  # If the OS is linux
        log("[  OK  ] platform is linux, starting auto-update...")
        throw_info("SomePythonThings Updater", "The new version is going to be downloaded and installed automatically. \nThe installation time may vary depending on your internet connection and your computer's performance, but it shouldn't exceed a few minutes.\nPlease DO NOT kill the program until the update is done, because it may corrupt the executable files.\nClick OK to start downloading.")
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
        get_updater().call_in_main(throw_info, "SomePythonThings Update", "The new version is going to be downloaded and prepared for the installation. \nThe download time may vary depending on your internet connection and your computer's performance, but it shouldn't exceed a few minutes.\nClick OK to continue.")
        t = Thread(target=download_win, args=(url,))
        t.daemon=True
        t.start()
    elif _platform == 'darwin':
        log("[  OK  ] platform is macOS, starting auto-update...")
        throw_info("SomePythonThings Updater", "The new version is going to be downloaded and installed automatically. \nThe installation time may vary depending on your internet connection and your computer's performance, but it shouldn't exceed a few minutes.\nPlease DO NOT kill the program until the update is done, because it may corrupt the executable files.\nClick OK to start downloading.")
        t = Thread(target=download_macOS, args=(links,))
        t.daemon=True
        t.start()
    else:  # If os is unknown
        webbrowser.open_new('https://www.somepythonthings.tk/programs/somepythonthings-zip-manager/')

def download_linux(links):
    get_updater().call_in_main(installationProgressBar, 'Downloading', 1, 4)
    get_updater().call_in_main(texts["create"].setPlainText, "The installer is being downloaded. Please wait until the download process finishes. This shouldn't take more than a couple of minutes.\n\nPlease DO NOT close the application")
    get_updater().call_in_main(texts["extract"].setPlainText, "The installer is being downloaded. Please wait until the download process finishes. This shouldn't take more than a couple of minutes.\n\nPlease DO NOT close the application")
    p1 = os.system(
        'cd; rm somepythonthings-zip-manager_update.deb; wget -O "somepythonthings-zip-manager_update.deb" {0}'.format(links['debian']))
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
    get_updater().call_in_main(texts["create"].setPlainText, "The program is being installed. Please wait until the installation process finishes. This shouldn't take more than a couple of minutes.\n\nPlease DO NOT close the application")
    get_updater().call_in_main(texts["extract"].setPlainText, "The program is being installed. Please wait until the installation process finishes. This shouldn't take more than a couple of minutes.\n\nPlease DO NOT close the application")
    p1 = os.system('cd; echo "{0}" | sudo -S apt install ./"somepythonthings-zip-manager_update.deb"'.format(passwd))
    if(p1 == 0):  # If the installation is done
        p2 = os.system('cd; rm "./somepythonthings-zip-manager_update.deb"')
        if(p2 != 0):  # If the downloaded file cannot be removed
            log("[ WARN ] Could not delete update file.")
        installationProgressBar('Installing', 4, 4)
        get_updater().call_in_main(throw_info,"SomePythonThings Manager Updater","The update has been applied succesfully. Please reopen the application")
        get_updater().call_in_main(sys.exit)
        sys.exit()
    else:  # If the installation is falied on the 1st time
        if not again:
            get_updater().call_in_main(install_linux_part1, True)
        else:
            installationProgressBar('Stop')
            get_updater().call_in_main(throw_error, "SomePythonThings Zip Manager Updater", "Unable to apply the update. Please try again later.")

def download_macOS(links):
    installationProgressBar('Downloading')
    get_updater().call_in_main(texts["create"].setPlainText, "The installer is being downloaded. Please wait until the download process finishes. This shouldn't take more than a couple of minutes.\n\nPlease DO NOT close the application")
    get_updater().call_in_main(texts["extract"].setPlainText, "The installer is being downloaded. Please wait until the download process finishes. This shouldn't take more than a couple of minutes.\n\nPlease DO NOT close the application")
    p1 = os.system('cd; rm somepythonthings-zip-manager_update.dmg')
    filedata = urlopen(links['macos'])
    datatowrite = filedata.read()
    os.chdir(os.path.expanduser("~"))
    try:
        with open("somepythonthings-zip-manager_update.dmg", 'wb') as f:
            f.write(datatowrite)
    except:
        p1=1
    if(p1 == 0):  # If the download is done
        get_updater().call_in_main(install_macOS)
    else:  # If the download is falied
        get_updater().call_in_main(throw_error,"SomePythonThings Zip Manager Updater", "An error occurred while downloading the update. Check your internet connection. If the problem persists, try to download and install the program manually.")
        webbrowser.open_new(
            'https://www.somepythonthings.tk/programs/somepythonthings-zip-manager/')

def install_macOS():
    installationProgressBar('Launching')
    time.sleep(0.2)
    get_updater().call_in_main(texts["create"].setPlainText, "Please follow on-screen instructions to continue")
    get_updater().call_in_main(texts["extract"].setPlainText, "Please follow on-screen instructions to continue")
    throw_info("SomePythonThings Zip Manager Updater", "The update file has been downloaded successfully. When you click OK, SomePythonThings Zip Manager is going to be closed and a DMG file will automatically be opened. Then, you'll need to drag the application on the DMG to the applications folder (also on the DMG). Click OK to continue")
    p2 = os.system('cd; open ./"somepythonthings-zip-manager_update.dmg"')
    log("[ INFO ] macOS installation unix output code is \"{0}\"".format(p2))
    sys.exit()

def clearZip():
    global zip, texts
    zip = ''
    log('[  OK  ] Zip file cleared')
    texts["extract"].setPlainText("Extract files and folders from a zip\n\nZip file to be extracted:")


def clearFiles():
    global files, texts
    files = []
    log('[  OK  ] Files list cleared')
    texts["create"].setPlainText("Compress files and folders into a zip\n\nFiles to be compressed:")


def refreshProgressbar(progressbar, actual, total, filename, size):
    global progressbars, texts, zipManager
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
    if not size == 0:
        get_updater().call_in_main(texts[progressbar].appendPlainText, (" - Processing {0} ({1:.2f} MB)".format(filename, size/1000000)))
    else:
        get_updater().call_in_main(texts[progressbar].appendPlainText, ( " - Processing {0}".format(filename)))
    get_updater().call_in_main(texts[progressbar].moveCursor, QtGui.QTextCursor.End)

def installationProgressBar(action = 'Downloading', actual = 1, total=2):
    global progressbars, texts, zipManager
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

def scrollBottom():
    get_updater().call_in_main(texts['create'].moveCursor, QtGui.QTextCursor.End)
    get_updater().call_in_main(texts['extract'].moveCursor, QtGui.QTextCursor.End)


def pureCompress(zipObj, a, b, c):
    zipObj.write(a, b, c)


def heavy_createZip(zipfilename, files):
    global zipManager, continueCreating, allDone, texts, progressbars
    try:
        zipObj = ZipFile(zipfilename, 'w')
        totalFiles = 0
        i = 0
        for path in files:
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
        log('[ INFO ] Total number of files: '+str(totalFiles))
        progressbars['create'].setMaximum(totalFiles)
        actualFile = 0
        try:
            compression_type = compression_rate[lists['compression'].currentIndex()]
            log("[  OK  ] Selected compression algorithm is {0}".format(lists['compression'].currentIndex()))
        except Exception as e:
            if(debugging):
                raise e
            get_updater().call_in_main(throw_warning, "SomePythonThongs Zip Manager", "An error occurred while selecting your desired compression algorithm. Compression algorithm will be \"Deflated\". ")
            compression_type = zipfile.ZIP_DEFLATED
        continueCreating = True
        for path in files:
            if path[2] == 'file':
                try:
                    os.chdir(path[1])
                    if not zipfilename == path[0]:
                        t = KillableThread(target=pureCompress, args=(zipObj, path[0].split('/')[-1], path[0].split('/')[-1], compression_type,))
                        t.daemon = True
                        t.start()
                        while t.is_alive():
                            if not continueCreating:
                                log("[ WARN ] User cancelled the zip creation!")
                                get_updater().call_in_main(progressbars['create'].setMaximum, 1)
                                get_updater().call_in_main(progressbars['create'].setValue, 0)
                                get_updater().call_in_main(progressbars['create'].setFormat, "")
                                get_updater().call_in_main(taskbprogress.hide)
                                t.shouldBeRuning=False
                                files = []
                                get_updater().call_in_main(throw_warning, "SomePythonThings Zip Manager", "User cancelled the zip creation")
                                get_updater().call_in_main(texts['create'].setPlainText, "Compress files and folders into a zip\n\nFiles to be compressed:")
                                time.sleep(0.5)
                                zipObj.close()
                                files = []
                                try: 
                                    os.remove(zipfilename)
                                except: 
                                    log("[ WARN ] Unable to remove zip file")
                                files = []
                                sys.exit("User Killed zip creation process")
                            else:
                                time.sleep(0.01)
                        t.join()
                        log('[  OK  ] File "'+str(path[0].split('/')[-1])+'" added successfully')
                    else:
                        log('[ WARN ] File "'+str(path[0].split('/')[-1])+'" skipped because it is the output zip')
                except Exception as e:
                    allDone = False
                    log('[FAILED] Unable to add file "'+str(path)+'"')
                    if(debugging):
                        raise e
                    get_updater().call_in_main(throw_warning, "Unable to add file!", 'Unable to add file "' +str(path[0].split('/')[-1])+'"\nThis file is going to be skipped.\n\nError reason:\n'+str(e))
                finally:
                    actualFile += 1
                    refreshProgressbar(
                        'create', actualFile, totalFiles, path[0], os.path.getsize(path[1]))
            elif path[2] == 'folder':
                try:
                    os.chdir(path[1])
                    for folderName, subfolders, filenames in os.walk('./'):
                        for filename in filenames:
                            try:
                                actualFile += 1
                                refreshProgressbar('create', actualFile, totalFiles, filename, os.path.getsize(
                                    os.path.abspath('./'+folderName+'/'+filename)))
                                if not(filename[0:2] == '._'):
                                    filePath = './' + \
                                        path[0].split('/')[-1] + \
                                        '/'+folderName+'/'+filename
                                    if not os.path.abspath(filename).replace('\\', '/') == zipfilename:
                                        t = KillableThread(target=pureCompress, args=(
                                            zipObj, folderName+'/'+filename, filePath, compression_type,))
                                        t.daemon = True
                                        t.start()
                                        while t.is_alive():
                                            if not continueCreating:
                                                log("[ WARN ] User cancelled the zip creation!")
                                                get_updater().call_in_main(progressbars['create'].setMaximum, 1)
                                                get_updater().call_in_main(progressbars['create'].setValue, 0)
                                                get_updater().call_in_main(progressbars['create'].setFormat, "")
                                                get_updater().call_in_main(taskbprogress.hide)
                                                t.shouldBeRuning=False
                                                files = []
                                                get_updater().call_in_main(throw_warning, "SomePythonThings Zip Manager", "User cancelled the zip creation")
                                                get_updater().call_in_main(texts['create'].setPlainText, "Compress files and folders into a zip\n\nFiles to be compressed:")
                                                time.sleep(0.5)
                                                zipObj.close()
                                                try: 
                                                    os.remove(zipfilename)
                                                except: 
                                                    log("[ WARN ] Unable to remove zip file")
                                                files = []
                                                sys.exit("User Killed zip creation process")
                                            else:
                                                time.sleep(0.01)

                                        t.join()
                                        log('[  OK  ] File ' +
                                              filename+' added successfully')
                                    else:
                                        log('[ WARN ] File "'+os.path.abspath(filename).replace(
                                            '\\', '/')+'" skipped because it is the output zip')
                            except Exception as e:
                                if(debugging):
                                    raise e
                                log(
                                    '[FAILED] Impossible to add file '+filename)
                                allDone = False
                                get_updater().call_in_main(throw_warning, "Unable to add file!", 'Unable to add file "' +
                                                          filename+'"\nThis file is going to be skipped.\n\nError reason:\n'+str(e))
                except Exception as e:
                    allDone = False
                    if(debugging):
                        raise e
                    log('[FAILED] Unable to add folder "'+str(path)+'"')
                    get_updater().call_in_main(throw_warning, "Unable to add folder!", 'Unable to add folder "' +
                                              str(path)+'"\nThis folder is going to be skipped.\n\nError reason:\n'+str(e))
        zipObj.close()
        refreshProgressbar('create', totalFiles, totalFiles,
                           zipfilename, os.path.getsize(zipfilename))
        notify("File compression done!", "SomePythonThings Zip Manager has finished compressing the selected files and folders.")
        if allDone:
            get_updater().call_in_main(throw_info, "SomepythonThings Zip Manager",
                                      'The Zip file was created sucessfully!')
            log('[  OK  ] zip file created sucessfully')
        else:
            get_updater().call_in_main(throw_warning, "SomePythonThings Zip Manager",
                                      'The Zip file was created with some errors')
            log('[ WARN ] zip file created with errors')
        openOnExplorer(zipfilename)
        files = []
        return 1
    except Exception as e:
        if(debugging):
            raise e
        log('[FAILED] Error occurred while creating zip File')
        try:
            get_updater().call_in_main(throw_error, "SomePythonThings Zip Manager",
                                      "Unable to create zip file "+zipfilename+".\n\nError reason:\n"+str(e))
        except:
            get_updater().call_in_main(throw_error, "SomePythonThings Zip Manager",
                                      "Unable to create zip file.\n\nError reason:\n"+str(e))
        return 0

def cancelZipCreation():
    global continueCreating, files
    files = []
    continueCreating = False
    log("[ WARN ] Sending cancel signal to compression thread")

def cancelZipExtraction():
    global continueExtracting, zip
    zip = ''
    continueExtracting = False
    log("[ WARN ] Sending cancel signal to extraction thread")

def createZip():
    global files, zipManager
    global allDone
    allDone = True
    try:
        log('[      ] Preparing zip file')
        if(len(files) < 1):
            throw_warning("SomePythonThings Zip Manager",
                          "Please add at least one file or one folder to the zip!")
            return 0
        zipfilename = QtWidgets.QFileDialog.getSaveFileName( zipManager, 'Save the zip file', files[0][0]+".zip", zip_files)[0]
        if zipfilename == "":
            log("[ WARN ] User aborted dialog")
            return 0
        file = open(zipfilename, 'w')
        log('[  OK  ] zip file created succesfully')
        zipfilename = str(file.name)
        file.close()
        log('[      ] Creating zip file on '+str(zipfilename))
        t = Thread(target=heavy_createZip, args=(zipfilename, files))
        t.start()
        t.daemon = True
    except:
        pass


def openFile():
    global files, zipManager, texts
    try:
        log('[      ] Dialog in process')

        filepaths = QtWidgets.QFileDialog.getOpenFileNames(zipManager, "Select some files to compress them", '')
        log('[  OK  ] Dialog Completed')
        if(filepaths[0] == []):
            log("[ WARN ] User aborted dialog")
            return 0
        for filepath in filepaths[0]:
            file = open(filepath, 'r')
            filename = file.name
            file.close()
            try:
                files.append([filename, os.path.dirname(filename), 'file'])
                log('[  OK  ] File "'+str(filename)+'" processed')
                texts['create'].appendPlainText("- "+str(files[-1][0]))
            except:
                log('[ FAIL ] Unable to process file "'+filepath+'"')
                throw_error("Error processing file!",
                            "Unable to read file \""+filename+"\"")
                try:
                    file.close()
                except:
                    pass
    except Exception as e:
        throw_error("SomePythonThings Zip Manager", "An error occurred while selecting one or more files. \n\nError detsils: "+str(e))
        log('[FAILED] Unable to open file. Returning value 0')


def openFolder():
    global files, zipManager
    log('[      ] Dialog in process')
    folder = QtWidgets.QFileDialog.getExistingDirectory(zipManager, 'Select a folder to compress it')
    if folder == "":
        log("[ WARN ] User aborted the dialog")
        return 0
    log('[  OK  ] Dialog Completed')
    try:
        files.append([folder, folder, 'folder'])
        texts['create'].appendPlainText("- "+folder+"\n")
        log('[  OK  ] Folder selected. Returning value "'+str(files[-1])+'"')
        return str(folder)
    except:
        log('[FAILED] openFolder() failed. Returning value 0')
        throw_error("Error processing folder!", "Unable to read folder \""+folder+"\"")


def openZIP():
    global zip
    global texts
    try:
        log('[      ] Dialog in process')
        filepath = QtWidgets.QFileDialog.getOpenFileName(zipManager, 'Select a zip file to extract it', '', zip_files)
        if(filepath[0] == ""):
            log("[ WARN ] User aborted the dialog")
            return 0
        file = open(filepath[0], 'r')
        log('[  OK  ] Dialog Completed')
        zip = str(file.name)
        log('[      ] Closing file')
        file.close()
        log('[  OK  ] File Closed. Returning value "'+str(zip)+'"')
        texts['extract'].appendPlainText(
            "{0} ({1:.3f} MB)".format(zip, os.path.getsize(zip)/1000000.))
        return 0
    except Exception as e:
        throw_error("SomePythonThings Zip Manager", "Unable to select zip file.\n\nReason:\n"+str(e))
        return 1

def pure_extract(zipObj, file, directory):
    zipObj.extract(file, directory)

def extractZip():
    global zip
    if(zip == ''):
        throw_warning("SomePythonThings Zip Manager", "Please select one zip file to start the extraction.")
    else:
        try:
            log('[      ] Dialog in proccess')
            directory = QtWidgets.QFileDialog.getExistingDirectory(zipManager, 'Select the destination folder where the zip is going to be extracted')
            if(directory == ''):
                log("[ WARN ] User aborted the dialog")
                return 0
            log('[  OK  ] zip file selected successfully')
            directory = str(directory)
            if not(directory == ''):
                t = Thread(target=heavyExtract, args=(directory, zip))
                t.daemon = True
                t.start()
        except Exception as e:
            log('[FAILED] Error occurred while extracting zip File')
            throw_error("SomePythonThings Zip Manager",
                        'Unable to extract the zip\n\nReason:\n'+str(e))

def heavyExtract(directory, zip):
    try:
        global continueExtracting
        continueExtracting=True
        error = False
        log('[      ] Extracting zip file on '+str(directory))
        totalFiles = 0
        archive = ZipFile(zip)
        for file in archive.namelist():
            totalFiles += 1
        actualFile = 0
        for file in archive.namelist():
            try:
                get_updater().call_in_main(refreshProgressbar,'extract', actualFile, totalFiles, file, 0)
                t = KillableThread(target=pure_extract, args=( archive, file, directory))
                t.daemon = True
                t.start()
                while t.is_alive():
                    if not continueExtracting:
                        log("[ WARN ] User cancelled the zip extraction!")
                        get_updater().call_in_main(progressbars['extract'].setMaximum, 1)
                        get_updater().call_in_main(progressbars['extract'].setValue, 0)
                        get_updater().call_in_main(progressbars['extract'].setFormat, "")
                        get_updater().call_in_main(taskbprogress.hide)
                        t.shouldBeRuning=False
                        get_updater().call_in_main(throw_warning, "SomePythonThings Zip Manager", "User cancelled the zip extraction")
                        get_updater().call_in_main(texts['extract'].setPlainText, "Extract files and folders from a zip\n\nZip file to be extracted:")
                        archive.close()
                        sys.exit("User killed zip creation process")
                    else:
                        time.sleep(0.01)
                t.join()
                log('[  OK  ] File '+file.split('/')
                    [-1]+' extracted successfully')
            except Exception as e:
                log('[ WARN ] Unable to extract file ' +
                    file.split('/')[-1])
                get_updater().call_in_main(throw_warning,"SomePythonThings Zip Manager", 'Unable to extract file '+file.split('/')[-1]+"\n\nReason:\n"+str(e))
                error = True
            finally:
                actualFile += 1
        get_updater().call_in_main(refreshProgressbar,'extract', totalFiles, totalFiles, zip, os.path.getsize(zip))
        zip = ''
        time.sleep(0.1)
        notify("File extraction done!", "SomePythonThings Zip Manager has finished extracting the selected files and folders.")
        if error:
            log('[ WARN ] Zip file extracted with some errors')
            get_updater().call_in_main(throw_warning,"SomePythonThings Zip Manager", 'Zip file extracted with some errors')
        else:
            log('[  OK  ] Zip file extracted sucessfully')
            get_updater().call_in_main(throw_info,"SomePythonThings Zip Manager", 'Zip file extracted sucessfully')
    except Exception as e:
        log('[FAILED] Error occurred while extracting zip File')
        get_updater().call_in_main(throw_error, "SomePythonThings Zip Manager", 'Unable to extract the zip\n\nReason:\n'+str(e))


def throw_info(title, body):
    global zipManager
    log("[ INFO ] "+body)
    msg = QtWidgets.QMessageBox(zipManager)
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText(body)
    msg.setWindowTitle(title)
    msg.exec_()


def throw_warning(title, body, warning=None):
    global zipManager
    log("[ WARN ] "+body)
    if(warning != None ):
        log("\t Warning reason: "+warning)
    msg = QtWidgets.QMessageBox(zipManager)
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setText(body)
    msg.setWindowTitle(title)
    msg.exec_()


def throw_error(title, body, error="Not Specified"):
    global zipManager
    log("[ ERROR ] "+body+"\n\tError reason: "+error)
    msg = QtWidgets.QMessageBox(zipManager)
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setText(body)
    msg.setWindowTitle(title)
    msg.exec_()


def updates_thread():
    log("[      ] Starting check for updates thread...")
    checkUpdates_py()

    
def quitZipManager():
    log("[ INFO ] Quitting application...")
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


def openOnExplorer(file):
    if    (_platform == 'win32'):
        try:
            os.system('start explorer /select,"{0}"'.format(file.replace("/", "\\")))
        except:
            log("[ WARN ] Unable to show file {0} on file explorer.".format(file))
    #elif (_platform == 'darwin'):
        #try:
        #    os.system("open "+file.)
        #except:
        #    log("[ WARN ] Unable to show file {0} on finder.".format(file))
    elif (_platform == 'linux' or _platform == 'linux2'):
        try:
            t = Thread(target=os.system, args=("xdg-open "+file,))
            t.daemon=True
            t.start()
        except:
            log("[ WARN ] Unable to show file {0} on default file explorer.".format(file))

def resizeWidgets():
    global zipManager, buttons, texts, progressbars, font

    separation20=int((zipManager.height()/100)*3.2)
    separation10=int((zipManager.height()/100)*1.6)

    btn_full_width = int((zipManager.width()/2)-40)-10
    btn_half_width = int((((zipManager.width()/2)-40)/2)-10)
    btn_full_height = int(((zipManager.height())-25)/5)+10
    btn_half_height = int(((zipManager.height())-25)/10)
    if(_platform == 'darwin'):
        btn_1st_row = separation20+12
    else:
        btn_1st_row = separation20+25
    btn_2nd_row = btn_1st_row+btn_half_height+separation10
    btn_1st_column = 20
    btn_2nd_column = btn_1st_column+btn_half_width+10
    btn_3rd_column = int(zipManager.width()/2)+btn_1st_column
    btn_4th_column = int(zipManager.width()/2)+btn_2nd_column

    text_width = btn_full_width
    text_height = int((((zipManager.height())-25)/100*48))
    text_1st_row = int(btn_2nd_row+btn_half_height+separation20)
    text_1st_column = btn_1st_column
    text_2nd_column = btn_3rd_column

    pgsbar_1st_column = text_1st_column
    pgsbar_2nd_column = text_2nd_column
    pgsbar_1st_row = text_1st_row+text_height+separation20
    pgsbar_width = text_width
    pgsbar_height = int((((zipManager.height())-25)/100*5))

    btn_cancel_1st_row = pgsbar_1st_row+pgsbar_height+separation20

    buttons["sel_file"].resize(btn_half_width, btn_half_height)
    buttons["sel_file"].move(btn_1st_column, btn_1st_row)
    buttons["sel_folder"].resize(btn_half_width, btn_half_height)
    buttons["sel_folder"].move(btn_1st_column, btn_2nd_row)
    buttons["create_zip"].resize(btn_half_width, btn_half_height)
    buttons["create_zip"].move(btn_1st_column, btn_cancel_1st_row)
    buttons["clear_files"].resize(btn_half_width, btn_half_height)
    buttons["clear_files"].move(btn_2nd_column, btn_1st_row)
    buttons["clear_zip"].resize(btn_half_width, btn_full_height)
    buttons["clear_zip"].move(btn_4th_column, btn_1st_row)
    buttons["sel_zip"].resize(btn_half_width, btn_full_height)
    buttons["sel_zip"].move(btn_3rd_column, btn_1st_row)
    buttons["extract_zip"].resize(btn_half_width, btn_half_height)
    buttons["extract_zip"].move(btn_3rd_column, btn_cancel_1st_row)

    texts["create"].move(text_1st_column, text_1st_row)
    texts["create"].resize(text_width, text_height)
    texts["extract"].move(text_2nd_column, text_1st_row)
    texts["extract"].resize(text_width, text_height)

    
    buttons["cancel_create"].move(btn_2nd_column, btn_cancel_1st_row)
    buttons["cancel_create"].resize(btn_half_width, btn_half_height)
    buttons["cancel_extract"].move(btn_4th_column, btn_cancel_1st_row)
    buttons["cancel_extract"].resize(btn_half_width, btn_half_height)

    progressbars["create"].setGeometry(pgsbar_1st_column, pgsbar_1st_row, pgsbar_width, pgsbar_height)
    progressbars["extract"].setGeometry( pgsbar_2nd_column, pgsbar_1st_row, pgsbar_width, pgsbar_height)


    lists['compression'].move(btn_2nd_column, int(btn_2nd_row+btn_half_height/2))
    lists['compression'].resize(btn_half_width, int(btn_half_height/2))

    labels['compression'].move(btn_2nd_column, btn_2nd_row)
    labels['compression'].resize(btn_half_width, int(btn_half_height/2))

    

# main code
if __name__ == '__main__':

    log("[      ] Actual dircetory is {0}".format(os.getcwd()))
    if _platform == "linux" or _platform == "linux2":
        log("[  OK  ] OS detected is linux")
        realpath="/bin"
        font = "Ubuntu Mono"
    
    elif _platform == "darwin":
        log("[  OK  ] OS detected is macOS")
        font = "Courier"
        realpath = "/Applications/SomePythonThings Zip Manager.app/Contents/Resources"
    
    elif _platform == "win32":
        if int(platform.release()) >= 10: #Font check: os is windows 10
            font = "Cascadia Mono"
            log("[  OK  ] OS detected is win32 release 10 ")
        else:# os is windows 7/8
            font="Consolas"
            log("[  OK  ] OS detected is win32 release 8 or less ")
        if(os.path.exists("\\Program Files\\SomePythonThingsZipManager")):
            realpath = "/Program Files/SomePythonThingsZipManager"
            print("[  OK  ] Directory set to /Program Files/SomePythonThingsZipManager/")
        else:
            realpath = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
            print("[ WARN ] Directory /Program Files/SomePythonThingsZipManager/ not found, getting working directory...")
    else:
        log("[ WARN ] Unable to detect OS")

    log("[  OK  ] Platform is {0}, font is {1} and real path is {2}".format(_platform, font, realpath))
    
    background_picture_path='{0}/background-zipmanager.png'.format(realpath.replace('c:', 'C:'))
    black_picture_path='{0}/black-zipmanager.png'.format(realpath.replace('c:', 'C:'))
    class Ui_MainWindow(object):
        def setupUi(self, MainWindow):
            global background_picture_path
            MainWindow.setObjectName("MainWindow")
            MainWindow.setWindowTitle("MainWindow")
            self.centralwidget = QtWidgets.QWidget(MainWindow)
            self.centralwidget.setObjectName("centralwidget")
            self.centralwidget.setStyleSheet("""border-image: url(\""""+background_picture_path+"""\") 0 0 0 0 stretch stretch;""")
            log("[      ] Background picture real path is "+background_picture_path)
            MainWindow.setCentralWidget(self.centralwidget)
            QtCore.QMetaObject.connectSlotsByName(MainWindow)

    class Window(QtWidgets.QMainWindow):
        resized = QtCore.pyqtSignal()
        keyRelease = QtCore.pyqtSignal(int)

        def __init__(self, parent=None):
            super(Window, self).__init__(parent=parent)
            ui = Ui_MainWindow()
            ui.setupUi(self)
            self.resized.connect(resizeWidgets)

        def resizeEvent(self, event):
            self.resized.emit()
            return super(Window, self).resizeEvent(event)

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
        zipManager.resize(1200, 700)
        zipManager.setWindowTitle('SomePythonThings Zip Manager') 
        zipManager.setStyleSheet("""
            * 
            {
                color: #DDDDDD;
                font-weight: bold;
                font-size:14px;
                font-family:"""+font+""";
                /*background-color: #333333;
            */}

            QPushButton {
                border-image: none;
                background-color: #333333;
                border-image: url(\""""+black_picture_path+"""\") 0 0 0 0 stretch stretch;
                /*border: 1px solid black;
                */width: 80px;
                height: 30px;
                border-radius: 3px;
            }

            QMessageBox 
            {
                background-color: #282828;
            }

            QLineEdit 
            {
                background-color: #282828;
            }

            QInputDialog 
            {
                background-color: #282828;
            }

            QPushButton 
            {
                background-color: #252525;
            }

            QScrollBar 
            {
                background-color: rgba(0, 0, 0, 0.0);
            }

            QScrollBar::vertical 
            {
                background-color: rgba(0, 0, 0, 0.0);
            }

            QScrollBar::handle:vertical 
            
            {
                margin-top: 17px;
                margin-bottom: 17px;
                border: none;
                min-height: 30px;
                border-radius: 3px;
                border: 1px solid black;
                background-color: rgba(0, 0, 0, 0.6);
            }

            QScrollBar::add-line:vertical 
            {
                border: none;
                border-radius: 3px;
                border: 1px solid black;
                background-color: rgba(0, 0, 0, 0.6);
            }

            QScrollBar::sub-line:vertical 
            {
                border: none;
                border-radius: 3px;
                border: 1px solid black;
                background-color: rgba(0, 0, 0, 0.6);
            }

            QLabel
            {   
                border-image: none;
                padding: 3px;
                border-radius: 3px;
                
            }

            QComboBox
            {   
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
            }
            QAbstractItemView{
                background-color: rgb(41, 41, 41);
                margin: 0px;
                border-radius: 3px;
            }

            QMenuBar{
                background-color: #333333;
            }

            QMenu{
                background-color: #333333;
            }

            QMenu::item {
                border: 5px solid #333333;
                border-right: 10px solid #333333;
            }
            QMenu::item:selected {
                background-color: #000000;
                border:5px solid  #000000;
            }
            QMenuBar::item{
                background-color: #333333;
                border:5px solid  #333333;

            }
            QMenuBar::item:selected{
                background-color: #000000;
                border:5px solid  #000000;

            }
        """)
        
        try:
            zipManager.setWindowIcon(QtGui.QIcon("{0}/icon-zipmanager.png".format(realpath)))
        except:
            pass
        zipManager.setMinimumSize(600, 450)
        buttons["sel_file"] = QtWidgets.QPushButton(zipManager)
        buttons["sel_file"].setText("Add files")
        buttons["sel_file"].clicked.connect(openFile)
        buttons["sel_folder"] = QtWidgets.QPushButton(zipManager)
        buttons["sel_folder"].setText("Add folder")
        buttons["sel_folder"].clicked.connect(openFolder)
        buttons["create_zip"] = QtWidgets.QPushButton(zipManager)
        buttons["create_zip"].setText("Create Zip")
        buttons["create_zip"].clicked.connect(createZip)
        buttons["clear_files"] = QtWidgets.QPushButton(zipManager)
        buttons["clear_files"].setText("Clear files")
        buttons["clear_files"].clicked.connect(clearFiles)
        buttons["clear_zip"] = QtWidgets.QPushButton(zipManager)
        buttons["clear_zip"].setText("Clear files")
        buttons["clear_zip"].clicked.connect(clearZip)
        buttons["sel_zip"] = QtWidgets.QPushButton(zipManager)
        buttons["sel_zip"].setText("Select zip")
        buttons["sel_zip"].clicked.connect(openZIP)
        buttons["extract_zip"] = QtWidgets.QPushButton(zipManager)
        buttons["extract_zip"].setText("Extract Zip")
        buttons["extract_zip"].clicked.connect(extractZip)
        buttons["cancel_extract"] = QtWidgets.QPushButton(zipManager)
        buttons["cancel_extract"].setText("Cancel Extraction")
        buttons["cancel_extract"].clicked.connect(cancelZipExtraction)
        buttons["cancel_create"] = QtWidgets.QPushButton(zipManager)
        buttons["cancel_create"].setText("Cancel Creation")
        buttons["cancel_create"].clicked.connect(cancelZipCreation)

        texts["create"] = QtWidgets.QPlainTextEdit(zipManager)
        texts["create"].setReadOnly(True)
        texts["create"].setPlainText("Compress files and folders into a zip\n\nFiles to be compressed:")
        texts["extract"] = QtWidgets.QPlainTextEdit(zipManager)
        texts["extract"].setReadOnly(True)
        texts["extract"].setPlainText("Extract files and folders from a zip\n\nZip file to be extracted:")

        progressbars["create"] = QtWidgets.QProgressBar(zipManager)
        progressbars["create"].setFormat("Compressed %v out of %m files (%p%)")
        progressbars["extract"] = QtWidgets.QProgressBar(zipManager)
        progressbars["extract"].setFormat("Extracted %v out of %m files (%p%)")


        labels['compression'] = QtWidgets.QLabel(zipManager)
        labels['compression'].setText('Compression algorithm:')

        lists['compression'] = QtWidgets.QComboBox(zipManager)
        i = 0
        for compression_type in ['Deflated', 'BZIP2', 'LZMA', 'Without Compression']:
            lists['compression'].insertItem(i, compression_type)
            i += 1
        
        menuBar = zipManager.menuBar()
        fileMenu = menuBar.addMenu("File")
        helpMenu = menuBar.addMenu("Help")
        quitAction = QtWidgets.QAction(" Quit", zipManager)
        quitAction.setShortcut("")
        openHelpAction = QtWidgets.QAction(" Online manual", zipManager)
        openHelpAction.setShortcut("")
        aboutAction = QtWidgets.QAction(" About SomePythonThings Zip Manager", zipManager)
        aboutAction.setShortcut("")
        updatesAction = QtWidgets.QAction(" Check for updates", zipManager)
        updatesAction.setShortcut("")
        updatesAction.triggered.connect(checkDirectUpdates)
        quitAction.triggered.connect(quitZipManager)
        aboutAction.triggered.connect(partial(throw_info, "About SomePythonThings Zip Manager", "SomePythonThings Zip Manager\nVersion "+str(actualVersion)+"\n\nThe SomePythonThings Project\n\n © 2020 SomePythonThings\nhttps://www.somepythonthings.tk"))
        openHelpAction.triggered.connect(openHelp)
        fileMenu.addAction(quitAction)
        helpMenu.addAction(openHelpAction)
        helpMenu.addAction(updatesAction)
        helpMenu.addAction(aboutAction)
        
        labels['compression'].setStyleSheet("""
            QLabel
            {
                border-radius: 3px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
                border: 1px solid black;
                background-color: rgba(0, 0, 0, 0.5);
                border-bottom-color: rgba(0, 0, 0, 0.5);
            }
            """)

        for button in ["sel_file", "sel_folder", "create_zip", "clear_files", "sel_zip", "extract_zip", "extract_zip", "create_zip"]:
            buttons[button].setStyleSheet('''
            QPushButton
            {
                border-image: none;
                background-image: none;
                border: 1px solid black;
                background-color: rgba(0, 0, 0, 0.5);
                font-size:20px;
                border-radius: 3px;
                color: #DDDDDD;
                font-family: \"'''+font+'''\", monospace;
                font-weight: bold;
            }
            QPushButton::hover
            {
                background-color: rgba(0, 0, 0, 0.4);
            }
            ''')
        for button in ["clear_files", "clear_zip", "cancel_create", "cancel_extract"]:
            buttons[button].setStyleSheet('''
            QPushButton
            {
                border-image: none;
                background-image: none;
                border: 1px solid black;
                background-color: rgba(0, 0, 0, 0.5);
                font-size:20px;
                border-radius: 3px;
                color: #DDDDDD;
                font-family: \"'''+font+'''\", monospace;
                font-weight: bold;
            }
            QPushButton::hover
            {
                border: 1px solid rgb(155, 0, 0);
                background-color: rgba(205, 0, 0, 0.7);
            }
            ''')
        for button in ["extract_zip", "create_zip"]:
            buttons[button].setStyleSheet('''
            QPushButton
            {
                border-image: none;
                background-image: none;
                border: 1px solid black;
                background-color: rgba(0, 0, 0, 0.5);
                font-size:20px;
                border-radius: 3px;
                color: #DDDDDD;
                font-family: \"'''+font+'''\", monospace;
                font-weight: bold;
            }
            QPushButton::hover
            {
                border: 1px solid rgb(0, 103, 1);
                background-color: rgba(0, 153, 51, 0.7);
            }
            ''')
        for text in ["create", "extract"]:
            texts[text].setStyleSheet('''
            QPlainTextEdit
            {
                border-image: none;
                background-image: none;
                border: 1px solid black;
                background-color: rgba(0, 0, 0, 0.5);
                font-size:15px;
                border-radius: 3px;
                color: #DDDDDD;
                font-family: \"'''+font+'''\", monospace;
                font-weight: bold;
                padding: 5px;
            }
            ''')
        for progressbar in ["create", "extract"]:
            progressbars[progressbar].setStyleSheet('''
            QProgressBar
            {
                text-align: center;
                border-image: none;
                background-image: none;
                border: 1px solid black;
                background-color: rgba(0, 0, 0, 0.5);
                font-size:17px;
                border-radius: 3px;
                color: #DDDDDD;
                font-family: \"'''+font+'''\", monospace;
                font-weight: bold;
            }
            QProgressBar::chunk
            {
                border-radius: 3px;
                background-color: rgba(0, 255, 0, 0.5);
            }
            ''')
        zipManager.show()
        if(_platform == "win32"):
            from PyQt5 import QtWinExtras
            loadbutton = QtWinExtras.QWinTaskbarButton(zipManager)
            loadbutton.setWindow(zipManager.windowHandle())
            taskbprogress = loadbutton.progress()
            taskbprogress.setRange(0, 100)
            taskbprogress.setValue(0)
            taskbprogress.show()
        resizeWidgets()
        try:
            zip = sys.argv[1]
            extractFirstZip()
        except:
            zip = ''
        updates_thread()
        app.exec_()
    except Exception as e:
        if not debugging:
            throw_error("Fatal Error!", "SomePythonThings Zip Manager crashed by a fatal error. If it's the first time you see that, just reopen the program. If it's not the first time, please mail me at somepythonthingschannel@gmail.com and send me the details of the error (This would be very helpful ;D )\n\nException details: \nException Type: {0}\n\nException Arguments:\n{1!r}".format(type(e).__name__, e.args)+"\n\nException Comments:\n"+str(e))
        else:
            raise e
    log('[ EXIT ] Reached end of the script')
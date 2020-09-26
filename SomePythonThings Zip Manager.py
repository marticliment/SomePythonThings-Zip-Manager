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

#Globals
ZIP=""
font = ""
realpath="."
allDone = True
zip_files = ('Zip Files (*.zip);;All files (*.*)')
files = []
continueExtracting = True
continueCreating = True
buttons = {}
texts = {}
progressbars = {}

#Functions
def extractFirstZip():
    print("[      ] Checking command line arguments")
    if ZIP != '':
        print('[  OK  ] Found one argument')
        try:
            if __name__ == "__main__":
                extractZip()
        except Exception as e:
            throw_error("SomePythonThings Zip Manager",
                        "Unable to extract zip.\n\nReason:\n{0}".format(str(e)))


def checkUpdates_py():
    global zipManager
    actualVersion = 2.1
    try:
        response = urllib.request.urlopen(
            "http://www.somepythonthings.tk/versions/zip.ver")
        response = response.read().decode("utf8")
    except:
        print("[ WARN ] Unacble to reach http://www.somepythonthings.tk/versions/zip.ver. Are you connected to the internet?")
        return False
    if float(response.split("///")[0]) > actualVersion:
        if QtWidgets.QMessageBox.Yes == QtWidgets.QMessageBox.question(zipManager, 'SomePythonThings Zip Manager', "There are some updates available for SomePythonThings Zip Manager:\nYour version: "+str(actualVersion)+"\nNew version: "+str(response.split("///")[0])+"\nNew features: \n"+response.split("///")[1]+"\nDo you want to go download and install them?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes):

            #                'debian': debian link in posotion 2                  'win32' Windows 32bits link in position 3           'win64' Windows 64bits in position 4                   'macos' macOS 64bits INTEL in position 5
            downloadUpdates({'debian': response.split("///")[2].replace('\n', ''), 'win32': response.split("///")[3].replace('\n', ''), 'win64': response.split("///")[4].replace('\n', ''), 'macos':response.split("///")[5].replace('\n', '')})
            return True
        else:
            print("[ WARN ] User aborted update!")
            return False
    else:
        print("[  OK  ] No updates found")
        return False


def pureUpdate_win(url):
    try:
        global texts
        os.system('cd %windir%\\..\\ & mkdir SomePythonThings')
        time.sleep(0.01)
        os.chdir("{0}/../SomePythonThings".format(os.environ['windir']))
        get_updater().call_latest(refreshProgressbar, 'create', 1, 2,"SomePythonThings-Zip-Manager-Updater.exe", 50000000)
        time.sleep(0.05)
        get_updater().call_latest(refreshProgressbar, 'extract', 1, 2,"SomePythonThings-Zip-Manager-Updater.exe", 50000000)
        time.sleep(0.05)
        get_updater().call_latest(texts["create"].setPlainText, "The installer is being downloaded. Please wait until the download process finishes. This shouldn't take more than a couple of minutes.\n\nPlease DO NOT close the application")
        time.sleep(0.07)
        get_updater().call_latest(texts["extract"].setPlainText, "The installer is being downloaded. Please wait until the download process finishes. This shouldn't take more than a couple of minutes.\n\nPlease DO NOT close the application")
        time.sleep(0.05)

        filedata = urlopen(url)
        datatowrite = filedata.read()
        filename = ""
        with open("{0}/../SomePythonThings/SomePythonThings-Zip-Manager-Updater.exe".format(os.environ['windir']), 'wb') as f:
            f.write(datatowrite)
            filename = f.name
        get_updater().call_latest(refreshProgressbar, 'create', 1, 1, "SomePythonThings-Zip-Manager-Updater.exe", 50000000)
        time.sleep(0.05)
        get_updater().call_latest(refreshProgressbar, 'extract', 1, 1,"SomePythonThings-Zip-Manager-Updater.exe", 50000000)
        time.sleep(0.05)
        get_updater().call_latest(texts["create"].setPlainText, "Please follow on-screen instructions to continue")
        time.sleep(0.05)
        get_updater().call_latest(texts["extract"].setPlainText, "Please follow on-screen instructions to continue")
        time.sleep(0.05)
        print(
            "[  OK  ] file downloaded to C:\\SomePythonThings\\{0}".format(filename))
        get_updater().call_latest(finalUpdatePart, filename)
    except Exception as e:
        get_updater().call_latest(throw_error, "SomePythonThings Zip Manager", "An error occurred when downloading the SomePythonTings Zip Manager installer. Please check your internet connection and try again later\n\nError Details:\n{0}".format(str(e)))


def finalUpdatePart(filename):
    try:
        throw_info("SomePythonThings Zip Manager Updater", "The file has been downloaded successfully and the setup will start now. When clicking OK, the application will close and a User Account Control window wil, appear. Click Yes on the User Account Control Pop-up asking for permissions to launch SomePythonThings-Zip-Manager-Updater.exe. Then follow the on-screen instructions.")
        p1 = os.system('start /B start /B {0}'.format(filename))
        print(p1)
        get_updater().call_latest(sys.exit)
        sys.exit()
    except Exception as e:
        throw_error("SomePythonThings Zip Manager Updater", "An error occurred when downloading the SomePythonTings Zip Manager installer. Please check your internet connection and try again later\n\nError Details:\n{0}".format(str(e)))


def downloadUpdates(links):
    print(
        '[  OK  ] Reached downloadUpdates. Download links are "{0}"'.format(links))
    if _platform == 'linux' or _platform == 'linux2':  # If the OS is linux
        print("[  OK  ] platform is linux, starting auto-update...")
        throw_info("SomePythonThings Updater", "The new version is going to be downloaded and installed automatically. \nThe installation time may vary depending on your internet connection and your computer's performance, but it shouldn't exceed a few minutes.\nPlease DO NOT kill the program until the update is done, because it may corrupt the executable files.\nClick OK to start downloading.")
        get_updater().call_latest(refreshProgressbar, 'create', 1, 3,"SomePythonThings-Zip-Manager-Updater.deb", 50000000)
        time.sleep(0.05)
        get_updater().call_latest(refreshProgressbar, 'extract', 1, 3,"SomePythonThings-Zip-Manager-Updater.deb", 50000000)
        time.sleep(0.05)
        get_updater().call_latest(texts["create"].setPlainText, "The installer is being downloaded. Please wait until the download process finishes. This shouldn't take more than a couple of minutes.\n\nPlease DO NOT close the application")
        time.sleep(0.07)
        get_updater().call_latest(texts["extract"].setPlainText, "The installer is being downloaded. Please wait until the download process finishes. This shouldn't take more than a couple of minutes.\n\nPlease DO NOT close the application")
        time.sleep(0.07)
        p1 = os.system(
            'cd; rm somepythonthings-zip-manager_update.deb; wget -O "somepythonthings-zip-manager_update.deb" {0}'.format(links['debian']))
        if(p1 == 0):  # If the download is done
            get_updater().call_latest(refreshProgressbar, 'create', 2, 3,"SomePythonThings-Zip-Manager-Updater.deb", 50000000)
            time.sleep(0.05)
            get_updater().call_latest(refreshProgressbar, 'extract', 2, 3,"SomePythonThings-Zip-Manager-Updater.deb", 50000000)
            time.sleep(0.05)
            get_updater().call_latest(texts["create"].setPlainText, "The program is being installed. Please wait until the installation process finishes. This shouldn't take more than a couple of minutes.\n\nPlease DO NOT close the application")
            time.sleep(0.07)
            get_updater().call_latest(texts["extract"].setPlainText, "The program is being installed. Please wait until the installation process finishes. This shouldn't take more than a couple of minutes.\n\nPlease DO NOT close the application")
            time.sleep(0.07)
            p2 = os.system('cd; echo "{0}" | sudo -S apt install ./"somepythonthings-zip-manager_update.deb"'.format(QtWidgets.QInputDialog.getText(zipManager, "Autentication needed - SomePythonThings Zip Manager",
                                                                                                                                                    "Please write your password to perform the update. \nThis password is NOT going to be stored anywhere in any way and it is going to be used ONLY for the update.\nIf you want, you can check that on the source code on github: \n(https://github.com/martinet101/SomePythonThings-Zip-Manager/)\n\nPassword:", QtWidgets.QLineEdit.Password, '')[0]))
            if(p2 == 0):  # If the installation is done
                p3 = os.system(
                    'cd; rm "./somepythonthings-zip-manager_update.deb"')
                if(p3 != 0):  # If the downloaded file cannot be removed
                    print("[ WARN ] Could not delete update file.")
                throw_info("SomePythonThings Manager Updater",
                           "The update has been applied succesfully. Please reopen the application")
                sys.exit()
            else:  # If the installation is falied on the 1st time
                p4 = os.system('cd; echo "{0}" | sudo -S apt install ./"somepythonthings-zip-manager_update.deb"'.format(QtWidgets.QInputDialog.getText(zipManager, "Autentication needed - SomePythonThings Zip Manager",
                                                                                                                                                        "An error occurred while autenticating. Insert your password again (This attempt will be the last one)\n\nPassword:", QtWidgets.QLineEdit.Password, '')[0]))
                if(p4 == 0):  # If the installation is done on the 2nd time
                    throw_info("SomePythonThings Zip Manager Updater",
                               "The update has been applied succesfully. Please reopen the application")
                    os.system(
                        'cd; rm "./somepythonthings-zip-manager_update.deb"')
                    sys.exit()
                else:  # If the installation is falied on the 2nd time
                    throw_error("SomePythonThings", "An error occurred while downloading the update. You have to be logged on with an administrator account to perform this operation. If the problem persists, try to download and install the program manually.")
                    webbrowser.open_new(
                        'https://www.somepythonthings.tk/programs/somepythonthings-zip-manager/')
        else:  # If the download is falied
            throw_error("SomePythonThings", "An error occurred while downloading the update. Check your internet connection. If the problem persists, try to download and install the program manually.")
            webbrowser.open_new(
                'https://www.somepythonthings.tk/programs/somepythonthings-zip-manager/')
    elif _platform == 'win32':  # if the OS is windows
        print('win32')
        url = ""
        if(platform.architecture()[0] == '64bit'):  # if OS is 64bits
            url = (links["win64"])
        else:  # is os is not 64bits
            url = (links['win32'])
        print(url)
        get_updater().call_latest(throw_info, "SomePythonThings Update", "The new version is going to be downloaded and prepared for the installation. \nThe download time may vary depending on your internet connection and your computer's performance, but it shouldn't exceed a few minutes.\nClick OK to continue.")
        t = Thread(target=pureUpdate_win, args=(url,))
        t.start()
        #throw_info("SomePythonThings Zip Manager Updater","The update is being downloaded and the installer is going to be launched at the end. Please, don't quit the application until the process finishes.")
    elif _platform == 'darwin':
        print("[  OK  ] platform is macOS, starting auto-update...")
        t = Thread(target=macOS_Download, args=(links,))
        t.start()
    else:  # If os is unknown
        webbrowser.open_new(
            'https://www.somepythonthings.tk/programs/somepythonthings-zip-manager/')

def macOS_Download(links):
    get_updater().call_latest(throw_info, "SomePythonThings Updater", "The new version is going to be downloaded and installed automatically. \nThe installation time may vary depending on your internet connection and your computer's performance, but it shouldn't exceed a few minutes.\nPlease DO NOT kill the program until the update is done, because it may corrupt the executable files.\nClick OK to start downloading.")
    get_updater().call_latest(refreshProgressbar, 'create', 1, 2,"SomePythonThings-Zip-Manager-Updater.dmg", 50000000)
    time.sleep(0.05)
    get_updater().call_latest(refreshProgressbar, 'extract', 1, 2,"SomePythonThings-Zip-Manager-Updater.dmg", 50000000)
    time.sleep(0.05)
    get_updater().call_latest(texts["create"].setPlainText, "The installer is being downloaded. Please wait until the download process finishes. This shouldn't take more than a couple of minutes.\n\nPlease DO NOT close the application")
    time.sleep(0.07)
    get_updater().call_latest(texts["extract"].setPlainText, "The installer is being downloaded. Please wait until the download process finishes. This shouldn't take more than a couple of minutes.\n\nPlease DO NOT close the application")
    time.sleep(0.05)
    p1 = os.system(
        'cd; rm somepythonthings-zip-manager_update.dmg; wget -O "somepythonthings-zip-manager_update.dmg" {0}'.format(links['macos']))
    if(p1 == 0):  # If the download is done
        get_updater().call_latest(macOS_install)
    else:  # If the download is falied
        throw_error("SomePythonThings Zip Manager Updater", "An error occurred while downloading the update. Check your internet connection. If the problem persists, try to download and install the program manually.")
        webbrowser.open_new(
            'https://www.somepythonthings.tk/programs/somepythonthings-zip-manager/')

def macOS_install():
    get_updater().call_latest(refreshProgressbar, 'create', 1, 1, "SomePythonThings-Zip-Manager-Updater.dmg", 50000000)
    time.sleep(0.05)
    get_updater().call_latest(refreshProgressbar, 'extract', 1, 1,"SomePythonThings-Zip-Manager-Updater.dmg", 50000000)
    time.sleep(0.05)
    get_updater().call_latest(texts["create"].setPlainText, "Please follow on-screen instructions to continue")
    time.sleep(0.05)
    get_updater().call_latest(texts["extract"].setPlainText, "Please follow on-screen instructions to continue")
    time.sleep(0.05)
    throw_info("SomePythonThings Zip Manager Updater", "The updaye file has been downloaded successfully. When you click OK, SomePYthonThings Zip Manager is going to be closed and a DMG file will automatically be opened. Then, you'll need to drag the application on the DMG to the applications folder (also on the DMG). Click OK to continue")
    p2 = os.system('cd; open ./"somepythonthings-zip-manager_update.dmg"')
    sys.exit()
    print("[ INFO ] macOS installation unix output code is \"{0}\"".format(p2))

def clearZip():
    global ZIP, texts
    ZIP = ''
    print('[  OK  ] Zip file cleared')
    texts["extract"].setPlainText("Extract files and folders from a zip\n\nZip file to be extracted:")


def clearFiles():
    global files, texts
    files = []
    print('[  OK  ] Files list cleared')
    texts["create"].setPlainText("Compress files and folders into a zip\n\nFiles to be compressed:")


def refreshProgressbar(progressbar, actual, total, filename, size):
    global progressbars, texts
    get_updater().call_latest(progressbars[progressbar].setMaximum, (int(total)))
    get_updater().call_latest(progressbars[progressbar].setValue, (int(actual)))
    if not size == 0:
        get_updater().call_latest(texts[progressbar].appendPlainText, (" - Processing {0} ({1:.2f} MB)".format(filename, size/1000000)))
    else:
        get_updater().call_latest(texts[progressbar].appendPlainText, ( " - Processing {0}".format(filename)))
    get_updater().call_latest(texts[progressbar].moveCursor, QtGui.QTextCursor.End)
    return 0


def pureCompress(zipObj, a, b, c):
    zipObj.write(a, b, c)


def heavy_createZip(zipfilename, files):
    global zipManager, continueCreating, allDone, texts, progressbars
    try:
        zipObj = ZipFile(zipfilename, 'w')
        totalFiles = 0
        i = 0
        for path in files:
            print(path)
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
        print('[ INFO ] Total number of files: '+str(totalFiles))
        progressbars['create'].setMaximum(totalFiles)
        actualFile = 0
        continueCreating = True
        for path in files:
            if path[2] == 'file':
                try:
                    os.chdir(path[1])
                    if not zipfilename == path[0]:
                        t = KillableThread(target=pureCompress, args=(zipObj, path[0].split('/')[-1], path[0].split('/')[-1], zipfile.ZIP_DEFLATED,))
                        t.daemon = True
                        t.start()
                        while t.is_alive():
                            if not continueCreating:
                                print("[ WARN ] User cancelled the zip creation!")
                                t.shouldBeRuning=False
                                files = []
                                get_updater().call_latest(throw_warning, "SomePythonThings Zip Manager", "User cancelled the zip creation")
                                get_updater().call_latest(texts['create'].setPlainText, "Compress files and folders into a zip\n\nFiles to be compressed:")
                                get_updater().call_latest(progressbars['create'].setMaximum, 1)
                                get_updater().call_latest(progressbars['create'].setValue, 0)
                                time.sleep(0.5)
                                zipObj.close()
                                files = []
                                try: 
                                    os.remove(zipfilename)
                                except: 
                                    print("[ WARN ] Unable to remove zip file")
                                files = []
                                sys.exit("User Killed zip creation process")
                            else:
                                time.sleep(0.01)
                        t.join()
                        print('[  OK  ] File "'+str(path[0].split('/')
                                                    [-1])+'" added successfully')
                    else:
                        print('[ WARN ] File "'+str(path[0].split('/')
                                                    [-1])+'" skipped because it is the output zip')
                except Exception as e:
                    allDone = False
                    print('[FAILED] Unable to add file "'+str(path)+'"')
                    get_updater().call_latest(throw_warning, "Unable to add file!", 'Unable to add file "' +filename+'"\nThis file is going to be skipped.\n\nError reason:\n'+str(e))
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
                                            zipObj, folderName+'/'+filename, filePath, zipfile.ZIP_DEFLATED,))
                                        t.daemon = True
                                        t.start()
                                        while t.is_alive():
                                            if not continueCreating:
                                                print("[ WARN ] User cancelled the zip creation!")
                                                t.shouldBeRuning=False
                                                files = []
                                                get_updater().call_latest(throw_warning, "SomePythonThings Zip Manager", "User cancelled the zip creation")
                                                get_updater().call_latest(texts['create'].setPlainText, "Compress files and folders into a zip\n\nFiles to be compressed:")
                                                get_updater().call_latest(progressbars['create'].setMaximum, 1)
                                                get_updater().call_latest(progressbars['create'].setValue, 0)
                                                time.sleep(0.5)
                                                zipObj.close()
                                                try: 
                                                    os.remove(zipfilename)
                                                except: 
                                                    print("[ WARN ] Unable to remove zip file")
                                                files = []
                                                sys.exit("User Killed zip creation process")
                                            else:
                                                time.sleep(0.01)

                                        t.join()
                                        print('[  OK  ] File ' +
                                              filename+' added successfully')
                                    else:
                                        print('[ WARN ] File "'+os.path.abspath(filename).replace(
                                            '\\', '/')+'" skipped because it is the output zip')
                            except Exception as e:
                                print(
                                    '[FAILED] Impossible to add file '+filename)
                                allDone = False
                                get_updater().call_latest(throw_warning, "Unable to add file!", 'Unable to add file "' +
                                                          filename+'"\nThis file is going to be skipped.\n\nError reason:\n'+str(e))
                except Exception as e:
                    allDone = False
                    print('[FAILED] Unable to add folder "'+str(path)+'"')
                    get_updater().call_latest(throw_warning, "Unable to add folder!", 'Unable to add folder "' +
                                              str(path)+'"\nThis folder is going to be skipped.\n\nError reason:\n'+str(e))
        zipObj.close()
        refreshProgressbar('create', totalFiles, totalFiles,
                           zipfilename, os.path.getsize(zipfilename))
        if allDone:
            get_updater().call_latest(throw_info, "SomepythonThings Zip Manager",
                                      'The Zip file was created sucessfully!')
            print('[  OK  ] ZIP file created sucessfully')
        else:
            get_updater().call_latest(throw_warning, "SomePythonThings Zip Manager",
                                      'The Zip file was created with some errors')
            print('[ WARN ] ZIP file created with errors')
        openOnExplorer(zipfilename)
        files = []
        return 1
    except Exception as e:
        print('[FAILED] Error occurred while creating ZIP File')
        try:
            get_updater().call_latest(throw_error, "SomePythonThings Zip Manager",
                                      "Unable to create zip file "+zipfilename+".\n\nError reason:\n"+str(e))
        except:
            get_updater().call_latest(throw_error, "SomePythonThings Zip Manager",
                                      "Unable to create zip file.\n\nError reason:\n"+str(e))
        return 0

def cancelZipCreation():
    global continueCreating, files
    files = []
    continueCreating = False
    print("[ WARN ] Sending cancel signal to compression thread")

def cancelZipExtraction():
    global continueExtracting, ZIP
    ZIP = ''
    continueExtracting = False
    print("[ WARN ] Sending cancel signal to extraction thread")

def createZip():
    global files, zipManager
    global allDone
    allDone = True
    try:
        print('[      ] Preparing zip file')
        if(len(files) < 1):
            throw_warning("SomePythonThings Zip Manager",
                          "Please add at least one file or one folder to the zip!")
            return 0
        zipfilename = QtWidgets.QFileDialog.getSaveFileName( zipManager, 'Save the zip file', files[0][0]+".zip", zip_files)[0]
        if zipfilename == "":
            print("[ WARN ] User aborted dialog")
            return 0
        file = open(zipfilename, 'w')
        print('[  OK  ] ZIP file created succesfully')
        zipfilename = str(file.name)
        file.close()
        print('[      ] Creating ZIP file on '+str(zipfilename))
        t = Thread(target=heavy_createZip, args=(zipfilename, files))
        t.start()
        t.daemon = True
    except:
        pass


def openFile():
    global files, zipManager, texts
    try:
        print('[      ] Dialog in process')

        filepath = QtWidgets.QFileDialog.getOpenFileName(zipManager, "QtWidgets.QFileDialog.getOpenFileName()", 'Select a file to compress it')
        if(filepath[0] == ''):
            print("[ WARN ] User aborted dialog")
            return 0
        file = open(filepath[0], 'r')
        filename = file.name
        print('[  OK  ] Dialog Completed')
        try:
            files.append([file.name, os.path.dirname(file.name), 'file'])
            print('[  OK  ] File "'+str(file.name)+'" processed')
            texts['create'].appendPlainText("- "+str(files[-1][0]))
            file.close()
            return filename
        except:
            print('[ FAIL ] Unable to process file "'+filepath+'"')
            throw_error("Error processing file!",
                        "Unable to read file \""+filename+"\"")
            try:
                file.close()
            except:
                pass
        return 1
    except:
        print('[FAILED] openFile() failed. Returning value 0')
        try:
            file.close()
        except:
            pass
        return 0


def openFolder():
    global files, zipManager
    try:
        print('[      ] Dialog in process')
        folder = QtWidgets.QFileDialog.getExistingDirectory(zipManager, 'Select a folder to compress it')
        if folder == "":
            print("[ WARN ] User aborted the dialog")
            return 0
        print('[  OK  ] Dialog Completed')
        files.append([folder, folder, 'folder'])
        texts['create'].appendPlainText("- "+folder+"\n")
        print('[  OK  ] Folder selected. Returning value "'+str(files[-1])+'"')
        return str(folder)
    except:
        print('[FAILED] openFolder() failed. Returning value 0')
        throw_error("Error processing folder!",
                    "Unable to read folder \""+folder+"\"")


def openZIP():
    global ZIP
    global texts
    try:
        print('[      ] Dialog in process')
        filepath = QtWidgets.QFileDialog.getOpenFileName(zipManager, 'Select a zip file to extract it', '', zip_files)
        if(filepath[0] == ""):
            print("[ WARN ] User aborted the dialog")
            return 0
        file = open(filepath[0], 'r')
        print('[  OK  ] Dialog Completed')
        ZIP = str(file.name)
        print('[      ] Closing file')
        file.close()
        print('[  OK  ] File Closed. Returning value "'+str(ZIP)+'"')
        texts['extract'].appendPlainText(
            "{0} ({1:.3f} MB)".format(ZIP, os.path.getsize(ZIP)/1000000.))
        return 0
    except Exception as e:
        print('[FAILED] openZIP() failed. Returning value 0')
        throw_warning("SomePythonThings Zip Manager",
                      "Unable to select ZIP file.\n\nReason:\n"+str(e))
        try:
            file.close()
        except:
            pass
        return 1


def pure_extract(zipObj, file, directory):
    zipObj.extract(file, directory)


def extractZip():
    global ZIP
    if(ZIP == ''):
        throw_warning("SomePythonThings Zip Manager", "Please select one zip file to start the extraction.")
    else:
        try:
            print('[      ] Dialog in proccess')
            directory = QtWidgets.QFileDialog.getExistingDirectory(zipManager, 'Select the destination folder where the zip is going to be extracted')
            if(directory == ''):
                print("[ WARN ] User aborted the dialog")
                return 0
            print('[  OK  ] ZIP file selected successfully')
            directory = str(directory)
            if not(directory == ''):
                t = Thread(target=heavyExtract, args=(directory, ZIP))
                t.daemon = True
                t.start()
        except Exception as e:
            print('[FAILED] Error occurred while extracting ZIP File')
            throw_error("SomePythonThings Zip Manager",
                        'Unable to extract the zip\n\nReason:\n'+str(e))

def heavyExtract(directory, ZIP):
    try:
        global continueExtracting
        continueExtracting=True
        error = False
        print('[      ] Extracting ZIP file on '+str(directory))
        totalFiles = 0
        archive = ZipFile(ZIP)
        for file in archive.namelist():
            totalFiles += 1
        actualFile = 0
        for file in archive.namelist():
            try:
                get_updater().call_latest(refreshProgressbar,'extract', actualFile, totalFiles, file, 0)
                t = KillableThread(target=pure_extract, args=( archive, file, directory))
                t.daemon = True
                t.start()
                while t.is_alive():
                    if not continueExtracting:
                        print("[ WARN ] User cancelled the zip extraction!")
                        t.shouldBeRuning=False
                        ZIP=''
                        get_updater().call_latest(throw_warning, "SomePythonThings Zip Manager", "User cancelled the zip extraction")
                        get_updater().call_latest(texts['extract'].setPlainText, "Extract files and folders from a zip\n\nZip file to be extracted:")
                        get_updater().call_latest(progressbars['extract'].setMaximum, 1)
                        get_updater().call_latest(progressbars['extract'].setValue, 0)
                        archive.close()
                        ZIP = ''
                        sys.exit("User killed zip creation process")
                    else:
                        time.sleep(0.01)
                t.join()
                print('[  OK  ] File '+file.split('/')
                    [-1]+' extracted successfully')
            except Exception as e:
                print('[ WARN ] Unable to extract file ' +
                    file.split('/')[-1])
                get_updater().call_latest(throw_warning,"SomePythonThings Zip Manager", 'Unable to extract file '+file.split('/')[-1]+"\n\nReason:\n"+str(e))
                error = True
            finally:
                actualFile += 1
        get_updater().call_latest(refreshProgressbar,'extract', totalFiles, totalFiles, ZIP, os.path.getsize(ZIP))
        ZIP = ''
        time.sleep(0.1)
        if error:
            print('[ WARN ] Zip file extracted with some errors')
            get_updater().call_latest(throw_warning,"SomePythonThings Zip Manager", 'Zip file extracted with some errors')
        else:
            print('[  OK  ] Zip file extracted sucessfully')
            get_updater().call_latest(throw_info,"SomePythonThings Zip Manager", 'Zip file extracted sucessfully')
    except Exception as e:
        print('[FAILED] Error occurred while extracting ZIP File')
        get_updater().call_latest(throw_error, "SomePythonThings Zip Manager", 'Unable to extract the zip\n\nReason:\n'+str(e))


def throw_info(title, body):
    global zipManager
    print("[ INFO ] "+body)
    msg = QtWidgets.QMessageBox(zipManager)
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText(body)
    msg.setWindowTitle(title)
    msg.exec_()


def throw_warning(title, body, warning="Not Specified"):
    global zipManager
    print("[ WARN ] "+body+"\n\tWarning reason: "+warning)
    msg = QtWidgets.QMessageBox(zipManager)
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setText(body)
    msg.setWindowTitle(title)
    msg.exec_()


def throw_error(title, body, error="Not Specified"):
    global zipManager
    print("[ ERROR ] "+body+"\n\tError reason: "+error)
    msg = QtWidgets.QMessageBox(zipManager)
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setText(body)
    msg.setWindowTitle(title)
    msg.exec_()


def updates_thread():
    print("[      ] Starting check for updates thread...")
    checkUpdates_py()

def openOnExplorer(file):
    if    (_platform == 'win32'):
        try:
            os.system('start explorer /select,"{0}"'.format(file.replace("/", "\\")))
        except:
            print("[ WARN ] Unable to show file {0} on file explorer.".format(file))
    #elif (_platform == 'darwin'):
        #try:
        #    os.system("open "+file.)
        #except:
        #    print("[ WARN ] Unable to show file {0} on finder.".format(file))
    elif (_platform == 'linux' or _platform == 'linux2'):
        try:
            t = Thread(target=os.system, args=("xdg-open "+file,))
            t.daemon=True
            t.start()
        except:
            print("[ WARN ] Unable to show file {0} on default file explorer.".format(file))

def resizeWidgets():
    global zipManager, buttons, texts, progressbars, font

    btn_full_width = int((zipManager.width()/2)-40)-10
    btn_half_width = int((((zipManager.width()/2)-40)/2)-10)
    btn_full_height = int(zipManager.height()/5)+10
    btn_half_height = int(zipManager.height()/10)
    btn_1st_row = 20
    btn_2nd_row = btn_1st_row+btn_half_height+10
    btn_1st_column = 20
    btn_2nd_column = btn_1st_column+btn_half_width+10
    btn_3rd_column = int(zipManager.width()/2)+btn_1st_column
    btn_4th_column = int(zipManager.width()/2)+btn_2nd_column

    text_width = btn_full_width
    text_height = int((zipManager.height()/100*49.5))
    text_1st_row = int(btn_2nd_row+btn_half_height+20)
    text_1st_column = btn_1st_column
    text_2nd_column = btn_3rd_column

    pgsbar_1st_column = text_1st_column
    pgsbar_2nd_column = text_2nd_column
    pgsbar_1st_row = text_1st_row+text_height+20
    pgsbar_width = text_width
    pgsbar_height = int((zipManager.height()/100*5))

    btn_cancel_1st_row = pgsbar_1st_row+pgsbar_height+20

    buttons["sel_file"].resize(btn_half_width, btn_half_height)
    buttons["sel_file"].move(btn_1st_column, btn_1st_row)
    buttons["sel_folder"].resize(btn_half_width, btn_half_height)
    buttons["sel_folder"].move(btn_1st_column, btn_2nd_row)
    buttons["create_zip"].resize(btn_half_width, btn_half_height)
    buttons["create_zip"].move(btn_1st_column, btn_cancel_1st_row)
    buttons["clear_files"].resize(btn_half_width, btn_full_height)
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
            border: 1px solid rgb(205, 0, 0);
            background-color: rgb(205, 0, 0);
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
            border: 1px solid rgb(0, 153, 51);
            background-color: rgb(0, 153, 51);
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
            font-size:17px;
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


# main code
if __name__ == '__main__':

    print("[      ] Actual dircetory is {0}".format(os.getcwd()))
    if _platform == "linux" or _platform == "linux2":
        realpath="/bin"
        font = "Ubuntu Mono"
    
    elif _platform == "darwin":
        font = "Courier New"
        realpath = "/Applications/SomePythonThings Zip Manager.app/Contents/Resources"
    
    elif _platform == "win32":
        font = "Cascadia Mono"
        realpath = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')

    print("[  OK  ] Platform is {0}, font is {1} and real path is {2}".format(_platform, font, realpath))
    
    background_picture_path='{0}/background-zipmanager.png'.format(realpath.replace('c:', 'C:'))
    class Ui_MainWindow(object):
        def setupUi(self, MainWindow):
            global background_picture_path
            MainWindow.setObjectName("MainWindow")
            MainWindow.setWindowTitle("MainWindow")
            self.centralwidget = QtWidgets.QWidget(MainWindow)
            self.centralwidget.setObjectName("centralwidget")
            self.centralwidget.setStyleSheet("""border-image: url(\""""+background_picture_path+"""\") 0 0 0 0 stretch stretch;""")
            print("[      ] Background picture real path is "+background_picture_path)
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
    zipManager.resize(1200, 700)
    zipManager.setWindowTitle('SomePythonThings Zip Manager')
    zipManager.setStyleSheet("""
        QScrollBar:vertical {
            background-color: rgba(0, 0, 0, 0.0)
        }

        QScrollBar::handle:vertical {
            border-radius: 3px;
            min-height: 30px;
            background-color:  rgba(0, 0, 0, 1.0)
        }

        QScrollBar::add-line:vertical {
            background: none;
            height: 45px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }

        QScrollBar::sub-line:vertical {
            background: none;
            height: 45px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }

        QScrollBar::up-arrow:vertical {
        }

        QScrollBar::down-arrow:vertical {
        }""")

    
    try:
        zipManager.setWindowIcon(QtGui.QIcon("{0}/icon-zipmanager.png".format(realpath)))
    except:
        pass
    zipManager.setMinimumSize(600, 450)
    buttons["sel_file"] = QtWidgets.QPushButton(zipManager)
    buttons["sel_file"].setText("Add file")
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

    zipManager.show()
    resizeWidgets()
    try:
        ZIP = sys.argv[1]
        extractFirstZip()
    except:
        ZIP = ''
    updates_thread()
    app.exec_()

    print('[ EXIT ] Reached end of the script')

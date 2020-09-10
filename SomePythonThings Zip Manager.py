

def extractFirstZip():
    print("[      ] Checking command line arguments")
    if ZIP != '':
        print('[  OK  ] Found one argument')
        try:
            if __name__=="__main__":
                extractZip()
        except Exception as e :
            throw_error("SomePythonThings Zip Manager", "Unable to extract zip.\n\nReason:\n{0}".format(str(e)))





def checkUpdates_py():
    global zipManager
    actualVersion = 2.0
    try:
        response = urllib.request.urlopen("http://www.somepythonthings.tk/versions/zip.ver")
        response = response.read().decode("utf8")
        if float(response.split("///")[0])>actualVersion:
            if QMessageBox.Yes ==QMessageBox.question(zipManager, 'SomePythonThings Zip Manager', "There are some updates available for SomePythonThings Zip Manager:\nYour version: "+str(actualVersion)+"\nNew version: "+str(response.split("///")[0])+"\nNew features: \n"+response.split("///")[1]+"\nDo you want to go to the web and download them?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes):
                downloadUpdates()
        else:
            return False
    except:
        return False





def downloadUpdates():
    webbrowser.open_new('https://www.somepythonthings.tk/programs/somepythonthings-zip-manager/')





def clearFiles():
    global files, texts
    files = []
    print('[  OK  ] Files list cleared')
    texts["create"].setPlainText("Files to be compressed:")



def refreshProgressbar(progressbar, actual, total, filename, size):
    global progressbars, texts
    progressbars[progressbar].setMaximum(int(total))
    progressbars[progressbar].setValue(int(actual))
    if not size==0:
        texts[progressbar].appendPlainText("{0:.2f}% Completed. Processing file {1} ({2:.2f} MB)".format(actual/total*100.0, filename, size/1000000))
    else:
        texts[progressbar].appendPlainText("{0:.2f}% Completed. Processing file {1}".format(actual/total*100.0, filename))
    return 0

def pureCompress(zipObj, a, b, c):
    zipObj.write(a, b, c)

def createZip():
    global files, zipManager
    global allDone
    allDone = True
    try:
        print('[      ] Preparing zip file')
        if(len(files)<1):
            throw_warning("SomePythonThings Zip Manager", "Please add at least one file or one folder to the zip!")
            return 0
        zipfilename = QtWidgets.QFileDialog.getSaveFileName(zipManager, 'Save Zip File', files[0][0]+".zip", zip_files)[0]#options=QtWidgets.QFileDialog.DontUseNativeDialog
        if zipfilename == "":
            print("[ WARN ] User aborted dialog")
            return 0
        #throw_warning("SomePythonThings Zip Manager", "Because creating files is a heavy thing, the program may crash during the whole process.\nJust DO NOT close it. Just let him finish.")
        p = Process(target=loadingScreen, args=("creating the zip file",))
        p.start()
        file = open(zipfilename, 'w')
        print('[  OK  ] ZIP file created succesfully')
        zipfilename = str(file.name)
        file.close()
        print('[      ] Creating ZIP file on '+str(zipfilename))
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
        for path in files:
            if path[2] == 'file':
                try:
                    os.chdir(path[1])
                    if not zipfilename == path[0]:
                        zipObj.write(path[0].split('/')[-1], path[0].split('/')[-1], zipfile.ZIP_DEFLATED)
                        print('[  OK  ] File "'+str(path[0].split('/')[-1])+'" added successfully')
                    else:
                        print('[ WARN ] File "'+str(path[0].split('/')[-1])+'" skipped because it is the output zip')
                except Exception as e:
                    allDone = False
                    print('[FAILED] Unable to add file "'+str(path)+'"')
                    throw_warning("Unable to add file!", 'Unable to add file "'+filename+'"\nThis file is going to be skipped.\n\nError reason:\n'+str(e))
                finally:
                    actualFile += 1
                    refreshProgressbar('create', actualFile, totalFiles, path[0], os.path.getsize(path[1]))
            elif path[2] == 'folder':
                try:
                    os.chdir(path[1])
                    for folderName, subfolders, filenames in os.walk('./'):
                        for filename in filenames:
                            try:
                                actualFile += 1
                                refreshProgressbar('create', actualFile, totalFiles, filename, os.path.getsize(os.path.abspath('./'+folderName+'/'+filename)))
                                if not(filename[0:2] == '._'):
                                    filePath = './'+path[0].split('/')[-1]+'/'+folderName+'/'+filename
                                    if not os.path.abspath(filename).replace('\\', '/') == zipfilename:
                                        t = Thread(target=pureCompress, args=(zipObj, folderName+'/'+filename, filePath, zipfile.ZIP_DEFLATED,))
                                        t.start()
                                        t.join()
                                        #zipObj.write(folderName+'/'+filename, filePath, zipfile.ZIP_DEFLATED)
                                        print('[  OK  ] File '+filename+' added successfully')
                                    else:
                                        print('[ WARN ] File "'+os.path.abspath(filename).replace('\\', '/')+'" skipped because it is the output zip')
                            except Exception as e:
                                print('[FAILED] Impossible to add file '+filename)
                                allDone = False
                                throw_warning("Unable to add file!", 'Unable to add file "'+filename+'"\nThis file is going to be skipped.\n\nError reason:\n'+str(e))
                except Exception as e:
                    allDone = False
                    print('[FAILED] Unable to add folder "'+str(path)+'"')
                    throw_warning("Unable to add folder!", 'Unable to add folder "'+str(path)+'"\nThis folder is going to be skipped.\n\nError reason:\n'+str(e))
        zipObj.close()
        refreshProgressbar('create', totalFiles, totalFiles, zipfilename, os.path.getsize(zipfilename))
        if allDone:
            p.kill()
            throw_info("SomepythonThings Zip Manager", 'The Zip file was created sucessfully!')
            print('[  OK  ] ZIP file created sucessfully')
        else:
            p.kill()
            throw_warning("SomePythonThings Zip Manager", 'The Zip file was created with some errors')
            print('[ WARN ] ZIP file created with errors')
        files = []
        return 1
    except Exception as e:
        print('[FAILED] Error occurred while creating ZIP File')
        try: 
            p.kill()
            throw_error("SomePythonThings Zip Manager", "Unable to create zip file "+zipfilename+".\n\nError reason:\n"+str(e))
        except:
            p.kill()
            throw_error("SomePythonThings Zip Manager", "Unable to create zip file.\n\nError reason:\n"+str(e))
        return 0





def openFile():
    global files, zipManager, texts
    if True:
        print('[      ] Dialog in process')
        
        filepath = QtWidgets.QFileDialog.getOpenFileName(zipManager, "QtWidgets.QFileDialog.getOpenFileName()", 'Select File')
        if(filepath[0]==''):
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
            throw_error("Error processing file!", "Unable to read file \""+filename+"\"")
            try:
                file.close()
            except:
                pass
        return 1
    else:
        print('[FAILED] openFile() failed. Returning value 0')
        try:
            file.close()
        except:
            pass
        finally:
            return 0





def openFolder():
    global files, zipManager
    try:
        print('[      ] Dialog in process')
        folder = QtWidgets.QFileDialog.getExistingDirectory(zipManager, 'Select Folder')
        if folder=="":
            print("[ WARN ] User aborted the dialog")
            return 0
        print('[  OK  ] Dialog Completed')
        files.append([folder, folder, 'folder'])
        texts['create'].appendPlainText("- "+folder+"\n")
        print('[  OK  ] Folder selected. Returning value "'+str(files[-1])+'"')
        return str(folder)
    except:
        print('[FAILED] openFolder() failed. Returning value 0')
        throw_error("Error processing folder!", "Unable to read folder \""+folder+"\"")
        





def openZIP():
    global ZIP
    global texts
    try:
        print('[      ] Dialog in process')
        filepath = QtWidgets.QFileDialog.getOpenFileName(zipManager, 'Select File', '', zip_files)
        if(filepath[0]==""):
            print("[ WARN ] User aborted the dialog")
            return 0
        file = open(filepath[0], 'r')
        print('[  OK  ] Dialog Completed')
        ZIP = str(file.name)
        print('[      ] Closing file')
        file.close()
        print('[  OK  ] File Closed. Returning value "'+str(ZIP)+'"')
        texts['extract'].appendPlainText("{0} ({1:.3f} MB)".format(ZIP, os.path.getsize(ZIP)/1000000.))
    except Exception as e:
        print('[FAILED] openZIP() failed. Returning value 0')
        throw_warning("SomePythonThings Zip Manager", "Unable to select ZIP file.\n\nReason:\n"+str(e))
        try:
            file.close()
        except:
            pass
        finally:
            return 0

def pure_extract(zipObj, file, directory):
    zipObj.extract(file, directory)

def extractZip():
    global ZIP
    error=False
    try:
        print('[      ] Dialog in proccess')
        directory = QtWidgets.QFileDialog.getExistingDirectory(zipManager, 'Select Folder')
        if(directory==''):
            print("[ WARN ] User aborted the dialog")
            return 0
        p = Process(target=loadingScreen, args=("creating the zip file",))
        p.start()
        print('[  OK  ] ZIP file selected successfully')
        directory = str(directory)
        if not(directory == ''):
            print('[      ] Extracting ZIP file on '+str(directory))
            totalFiles = 0
            archive = ZipFile(ZIP)
            for file in archive.namelist():
                totalFiles += 1
            actualFile=0
            for file in archive.namelist():
                try:
                    t = Thread(target=pure_extract, args=(archive, file, directory))
                    t.start()
                    t.join()
                    #archive.extract(file, directory)
                    refreshProgressbar('extract', actualFile, totalFiles, file, 0)
                    print('[  OK  ] File '+file.split('/')[-1]+' extracted successfully' )
                except Exception as e:
                    print('[ WARN ] Unable to extract file '+file.split('/')[-1])
                    throw_warning("SomePythonThings Zip Manager", 'Unable to extract file '+file.split('/')[-1]+"\n\nReason:\n"+str(e))
                    error=True
                finally:
                    actualFile+= 1
            refreshProgressbar('extract', 1, 1, ZIP, os.path.getsize(ZIP))
            ZIP = ''
        if error:
            p.kill()
            print('[ WARN ] Zip file extracted with some errors')
            throw_warning("SomePythonThings Zip Manager", 'Zip file extracted with some errors')
        else:
            p.kill()
            print('[  OK  ] Zip file extracted sucessfully')
            throw_info("SomePythonThings Zip Manager", 'Zip file extracted sucessfully')
    except Exception as e:
        try: 
            p.kill()
        except: pass
        print('[FAILED] Error occurred while extracting ZIP File')
        throw_error("SomePythonThings Zip Manager", 'Unable to extract the zip\n\nReason:\n'+str(e))




def throw_info(title, body):
    global zipManager
    print("[ INFO ] "+body)
    msg = QMessageBox(zipManager)
    msg.setIcon(QMessageBox.Information)
    msg.setText(body)
    msg.setWindowTitle(title)
    msg.exec_()



def throw_warning(title, body):
    global zipManager
    print("[ WARN ] "+body)
    msg = QMessageBox(zipManager)
    msg.setIcon(QMessageBox.Warning)
    msg.setText(body)
    msg.setWindowTitle(title)
    msg.exec_()

def throw_error(title, body):
    global zipManager
    print("[ ERROR ] "+body)
    msg = QMessageBox(zipManager)
    msg.setIcon(QMessageBox.Critical)
    msg.setText(body)
    msg.setWindowTitle(title)
    msg.exec_()


def updates_thread():
    print("[      ] Starting check for updates thread...")
    checkUpdates_py()
    print("[ EXIT ] Reached the end of the update checker thread")





def loadingScreen(job):
    app = QApplication(sys.argv)

    window = QtWidgets.QMainWindow()
    QtWidgets.QApplication.setStyle('fusion')
    try:
        window.setWindowIcon(QtGui.QIcon("./icon-zipmanager.png"))
    except: 
        pass
    msg = QMessageBox(window)
    msg.setIcon(QMessageBox.Information)
    msg.setText("SomePythonThings Zip Manager is {0}. The main window may have stopped responding, but don't panic! This window will close automatically when the work is done.".format(job))
    msg.setWindowTitle("SomePythonThings Zip Manager")
    msg.exec_()
    while True:
        msg = QMessageBox(window)
        msg.setIcon(QMessageBox.Information)
        msg.setText("SomePythonThings Zip Manager is {0}. The main window may have stopped responding, but don't panic! This window will close automatically when the work is done.\n\nNote: Don't close this window because it will reappear until the job is done.".format(job))
        msg.setWindowTitle("SomePythonThings Zip Manager")
        msg.exec_()

    app.exec_()


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
    text_height = int((zipManager.height()/100*60))
    text_1st_row = int(btn_2nd_row+btn_half_height+20)
    text_1st_column = btn_1st_column
    text_2nd_column = btn_3rd_column

    pgsbar_1st_column = text_1st_column
    pgsbar_2nd_column = text_2nd_column
    pgsbar_1st_row = text_1st_row+text_height+20
    pgsbar_width = text_width
    pgsbar_height = int((zipManager.height()/100*5))

    btn_cancel_1st_row = pgsbar_1st_row+pgsbar_height+10

    buttons["sel_file"].resize(btn_half_width, btn_half_height)
    buttons["sel_file"].move(btn_1st_column, btn_1st_row)
    buttons["sel_folder"].resize(btn_half_width, btn_half_height)
    buttons["sel_folder"].move(btn_2nd_column, btn_1st_row)
    buttons["create_zip"].resize(btn_half_width, btn_half_height)
    buttons["create_zip"].move(btn_2nd_column, btn_2nd_row)
    buttons["clear_files"].resize(btn_half_width, btn_half_height)
    buttons["clear_files"].move(btn_1st_column, btn_2nd_row)
    buttons["sel_zip"].resize(btn_half_width, btn_full_height)
    buttons["sel_zip"].move(btn_3rd_column, btn_1st_row)
    buttons["extract_zip"].resize(btn_half_width, btn_full_height)
    buttons["extract_zip"].move(btn_4th_column, btn_1st_row)

    texts["create"].move(text_1st_column, text_1st_row)
    texts["create"].resize(text_width, text_height)
    texts["extract"].move(text_2nd_column, text_1st_row)
    texts["extract"].resize(text_width, text_height)

    progressbars["create"].setGeometry(pgsbar_1st_column, pgsbar_1st_row, pgsbar_width, pgsbar_height)
    progressbars["extract"].setGeometry(pgsbar_2nd_column, pgsbar_1st_row, pgsbar_width, pgsbar_height)

    for button in ["sel_file", "sel_folder", "create_zip", "clear_files", "sel_zip", "extract_zip"]:
        buttons[button].setStyleSheet('''
        QPushButton
        {
            border-image: none;
            background-image: none;
            border: none;
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
    for button in ["clear_files"]:
        buttons[button].setStyleSheet('''
        QPushButton
        {
            border-image: none;
            background-image: none;
            border: none;
            background-color: rgba(0, 0, 0, 0.5);
            font-size:20px;
            border-radius: 3px;
            color: #DDDDDD;
            font-family: \"'''+font+'''\", monospace;
            font-weight: bold;
        }
        QPushButton::hover
        {
            background-color: rgba(205, 0, 0, 1.0);
        }
        ''')
    for text in ["create", "extract"]:
        texts[text].setStyleSheet('''
        QPlainTextEdit
        {
            border-image: none;
            background-image: none;
            border: none;
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
            border-image: none;
            background-image: none;
            border: none;
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


import sys, struct, urllib.request, webbrowser, os, os.path, zipfile
from multiprocessing import Process
from threading import Thread
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import *
from zipfile import ZipFile
from sys import platform as _platform
import time

#main code

if __name__ == '__main__':
    if(len(sys.argv)>1):
        if sys.argv[1]=="--multiprocessing-fork":
            loadingScreen("working")
    print("[      ] Actual dircetory is {0}".format(os.getcwd()))
    font = ""
    if _platform == "linux" or _platform == "linux2":
        os.chdir('/bin/')
        font = "Ubuntu Mono"
    elif _platform == "darwin":
        font = "Courier New"
        try:
            os.chdir("/Applications/SomePythonThings Zip Manager.app/Contents/Resources")
            print("[      ] Changing dir to {0}".format("/Applications/SomePythonThings Zip Manager.app/Contents/Resources"))
        except:
            pass
    elif _platform == "win32":
        font = "Consolas"
        try:
            os.chdir(os.path.dirname(os.path.realpath(__file__)))
            print("[      ] Changing dir to {0}".format(os.path.dirname(os.path.realpath(__file__))))
        except:
            pass
    print("[  OK  ] Platform is {0}, so font will be {1}".format(_platform, font))
    allDone = True
    zip_files = ('Zip Files (*.zip);;All files (*.*)')
    files = []

    class Ui_MainWindow(object):
        def setupUi(self, MainWindow):
            MainWindow.setObjectName("MainWindow")
            MainWindow.setWindowTitle("MainWindow")
            self.centralwidget = QtWidgets.QWidget(MainWindow)
            self.centralwidget.setObjectName("centralwidget")
            MainWindow.setCentralWidget(self.centralwidget)
            QtCore.QMetaObject.connectSlotsByName(MainWindow)
    class Window(QtWidgets.QMainWindow):
        resized = QtCore.pyqtSignal()
        keyRelease = QtCore.pyqtSignal(int)
        def  __init__(self, parent=None):
            super(Window, self).__init__(parent=parent)
            ui = Ui_MainWindow()
            ui.setupUi(self)
            self.resized.connect(resizeWidgets)
        def resizeEvent(self, event):
            self.resized.emit()
            return super(Window, self).resizeEvent(event)
        
            
    QtWidgets.QApplication.setStyle('fusion')
    app = QtWidgets.QApplication(sys.argv)
    QtWidgets.QApplication.setStyle('fusion')
    zipManager = Window()
    zipManager.resize(1200, 600)
    zipManager.setWindowTitle('SomePythonThings Zip Manager')
    zipManager.setStyleSheet("""
        #centralwidget {
            border-image: url(./background-zipmanager.jpg) 0 0 0 0 stretch stretch
        }
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
        zipManager.setWindowIcon(QtGui.QIcon("./icon-zipmanager.png"))
    except: 
        pass
    zipManager.setMinimumSize(600, 450)
    buttons={}
    texts={}
    progressbars={}
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
    buttons["clear_files"].setText("Clear file list")
    buttons["clear_files"].clicked.connect(clearFiles)
    buttons["sel_zip"] = QtWidgets.QPushButton(zipManager)
    buttons["sel_zip"].setText("Select zip")
    buttons["sel_zip"].clicked.connect(openZIP)
    buttons["extract_zip"] = QtWidgets.QPushButton(zipManager)
    buttons["extract_zip"].setText("Extract Zip")
    buttons["extract_zip"].clicked.connect(extractZip)

    texts["create"] = QtWidgets.QPlainTextEdit(zipManager)
    texts["create"].setReadOnly(True)
    texts["create"].setPlainText("Compress files and folders into a zip\n\nFiles to be compressed:")
    texts["extract"] = QtWidgets.QPlainTextEdit(zipManager)
    texts["extract"].setReadOnly(True)
    texts["extract"].setPlainText("Extract files and folders from a zip\n\nZip file to be extracted:")
    
    progressbars["create"] =  QtWidgets.QProgressBar(zipManager)
    progressbars["create"].setFormat("")
    progressbars["extract"] =  QtWidgets.QProgressBar(zipManager)
    progressbars["extract"].setFormat("")

    zipManager.show()
    resizeWidgets()
    try:
        ZIP = sys.argv[1]
        if not ZIP=="--multiprocessing-fork":
            extractFirstZip()
    except:
        ZIP = ''
    updates_thread()
    app.exec_() 

    print('[ EXIT ] Reached end of the script')

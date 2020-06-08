allDone = True
try:
    #!/bin/python3
    print
except:
    pass
print('[  HI  ] Welome to SPT Zip Manager Log!')
import sys
try:
    ZIP = sys.argv[1]
except:
    ZIP = ''
print('[  OK  ] Collected command line arguments')
import eel
files = []
from tkinter.filedialog import *
from tkinter.messagebox import *
from tkinter import Tk
print('[  OK  ] Step Completed')
@eel.expose
def extractFirstZip():
    print("[ WAIT ] Checking command line arguments")
    if ZIP != '':
        print('[  OK  ] Found one argument')
        try:
            eel.showExtract()()
            extractZip()
        except:
            pass
print('[  OK  ] Step Completed')
@eel.expose
def checkUpdates_py():
    actualVersion = 1.2
    if True:
        import struct
        import urllib.request
        response = urllib.request.urlopen("http://www.somepythonthings.tk/versions/zip.html")
        response = response.read().decode("utf8")
        if float(response)>actualVersion:
            root = Tk()
            root.attributes("-alpha", 0.0)
            if askquestion('Found Updates', 'We found new updates for SomePythonThings ZIP manager! Do you want to download them?') == 'yes':
                downloadUpdates()
            root.destroy();
            root.mainloop();
        else:
            return False
    else:
        return False
print('[  OK  ] Step Completed')
@eel.expose
def downloadUpdates():
    import webbrowser
    webbrowser.open_new('https://www.somepythonthings.tk/programs/somepythonthings-zip-manager/')
print('[  OK  ] Step Completed')
@eel.expose
def clearZipFiles():
    global files
    files = []
    print('[  OK  ] Files list cleared')
print('[  OK  ] Step Completed')
def errorAddingFile(path):
    eel.showFileError(str(path))
print('[  OK  ] Step Completed')
def JSAlert(a):
    eel.showAlert(a)
print('[  OK  ] Step Completed')
@eel.expose
def createZip():
    import os
    from zipfile import ZipFile
    import zipfile
    global files
    global allDone
    allDone = True
    if True:
        print('[ WAIT ] Preparing zip file')
        root = Tk()
        root.attributes("-alpha", 0.0)
        file = asksaveasfile(mode='w', defaultextension="*.zip", title="Save ZIP", initialfile='Zip folder.zip', filetypes=[("ZIP file", "*.zip")])
        root.destroy();
        root.mainloop();
        print('[  OK  ] ZIP file created succesfully')
        filename = str(file.name)
        file.close()
        print('[ WAIT ] Creating ZIP file on '+str(filename))
        zipObj = ZipFile(filename, 'w')
        totalFiles = 0
        import os.path
        import os
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
        actualFile = 0
        for path in files:
            if path[2] == 'file':
                try:
                    os.chdir(path[1])
                    zipObj.write(path[0].split('/')[-1], path[0].split('/')[-1], zipfile.ZIP_DEFLATED)
                    print('[  OK  ] File "'+str(path[0].split('/')[-1])+'" added successfully')
                except:
                    allDone = False
                    errorAddingFile(path)
                    print('[FAILED] Unable to add file "'+str(path)+'"')
                finally:
                    actualFile += 1
                    eel.progressbar(actualFile*100/(totalFiles))()
            elif path[2] == 'folder':
                try:
                    os.chdir(path[1])
                    for folderName, subfolders, filenames in os.walk('./'):
                        for filename in filenames:
                            actualFile += 1
                            eel.progressbar(actualFile*100/(totalFiles))()
                            if not(filename[0:2] == '._'):
                                try:
                                    filePath = './'+path[0].split('/')[-1]+'/'+folderName+'/'+filename
                                    zipObj.write(folderName+'/'+filename, filePath, zipfile.ZIP_DEFLATED)
                                    print('[  OK  ] File '+filename+' added successfully')
                                except:
                                    print('[FAILED] Impossible to add file '+filename)
                                    allDone = False
                                    eel.yellowProgressbar()()
                except:
                    allDone = False
                    errorAddingFile(path)
                    print('[FAILED] Unable to add folder "'+str(path)+'"')
        zipObj.close()
        eel.completeProgressbar()()
        eel.sleep(0.2)
        if allDone:
            JSAlert('The Zip file was created sucessfully!')
            print('[  OK  ] ZIP file created sucessfully')
        else:
            JSAlert('The Zip file was created with some errors :(')
            print('[ WARN ] ZIP file created with errors')
        files = []
        return 1
    else:
        print('[FAILED] Error occurred while creating ZIP File')
        return 0
    print('Function done')
print('[  OK  ] Step Completed')
@eel.expose
def openFile():
    import os
    global files
    try:
        print('[ WAIT ] Dialog in process')
        root = Tk()
        root.attributes("-alpha", 0.0)
        file = askopenfile(mode='r', defaultextension='*.*', filetypes=[("All files", "*.*")])
        root.destroy();
        root.mainloop();
        print('[  OK  ] Dialog Completed')
        files.append([file.name, os.path.dirname(file.name), 'file'])
        print('[ WAIT ] Closing file')
        file.close()
        print('[  OK  ] File Closed. Returning value "'+str(files[-1])+'"')
        return str(file.name)
    except:
        print('[FAILED] openFile() failed. Returning value 0')
        try:
            file.close()
        except:
            pass
        finally:
            return 0
print('[  OK  ] Step Completed')
@eel.expose
def openFolder():
    import os
    global files
    try:
        print('[ WAIT ] Dialog in process')
        root = Tk()
        root.attributes("-alpha", 0.0)
        folder = askdirectory()
        root.destroy();
        root.mainloop();
        print('[  OK  ] Dialog Completed')
        files.append([folder, folder, 'folder'])
        print('[  OK  ] Folder selected. Returning value "'+str(files[-1])+'"')
        return str(folder)
    except:
        print('[FAILED] openFolder() failed. Returning value 0')
print('[  OK  ] Step Completed')
@eel.expose
def openZIP():
    import os
    global ZIP
    try:
        print('[ WAIT ] Dialog in process')
        root = Tk()
        root.attributes("-alpha", 0.0)
        file = askopenfile(mode='r', defaultextension='*.ZIP', filetypes=[("ZIP Files", "*.ZIP")])
        root.destroy();
        root.mainloop();
        print('[  OK  ] Dialog Completed')
        ZIP = str(file.name)
        print('[ WAIT ] Closing file')
        file.close()
        print('[  OK  ] File Closed. Returning value "'+str(ZIP)+'"')
        return str(ZIP)
    except:
        print('[FAILED] openZIP() failed. Returning value 0')
        try:
            file.close()
        except:
            pass
        finally:
            return 0
print('[  OK  ] Step Completed')
@eel.expose
def extractZip():
    import os
    from zipfile import ZipFile
    global ZIP
    try:
        print('[ WAIT ] Dialog in proccess')
        root = Tk()
        root.attributes("-alpha", 0.0)
        directory = askdirectory()
        root.destroy()
        root.mainloop()
        print('[  OK  ] ZIP file created succesfully')
        directory = str(directory)
        if not(directory == ''):
            print('[ WAIT ] Extracting ZIP file on '+str(directory))
            with ZipFile(ZIP,"r") as zip_ref:
                zip_ref.extractall(directory)
            eel.nextStepExtractProgressBar()()
            eel.sleep(0.2)
            JSAlert('Zip extracted sucessfully!')
            eel.resetExtractProgressBar()()
            ZIP = ''
            print('[  OK  ] ZIP file created sucessfully')
        return 1
    except:
        print('[FAILED] Error occurred while creating ZIP File')
        JSAlert('An error occurred while extracting the Zip')
        return 0
    print('Function done')
print('[  OK  ] Finished loading functions')
print('[ WAIT ] Starting server on localhost')
eel.init('web')
print("[  OK  ] Server started successfully")
print('[  OK  ] Started interface')
checkUpdates_py()
eel.start('index.html', mode='chrome', size=(900, 500), port=0)

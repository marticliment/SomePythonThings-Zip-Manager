
allDone = True
all_files = ('All Files (*.*)', 'All files (*.*)')
zip_files = ('Zip Files (*.zip)', 'All files (*.*)')
try:
    from ctypes import windll#, pointer, wintypes
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass
print('[      ] SomePythonThings Zip Manager v2.0 debugging log')
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
print('[  OK  ] Function loaded correctly')
@eel.expose
def extractFirstZip():
    print("[      ] Checking command line arguments")
    if ZIP != '':
        print('[  OK  ] Found one argument')
        try:
            eel.showExtract()()
            extractZip()
        except:
            pass
print('[  OK  ] Function loaded correctly')
@eel.expose
def checkUpdates_py():
    actualVersion = 1.3
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
print('[  OK  ] Function loaded correctly')
@eel.expose
def downloadUpdates():
    import webbrowser
    webbrowser.open_new('https://www.somepythonthings.tk/programs/somepythonthings-zip-manager/')
print('[  OK  ] Function loaded correctly')
@eel.expose
def clearZipFiles():
    global files
    files = []
    print('[  OK  ] Files list cleared')
print('[  OK  ] Function loaded correctly')
def errorAddingFile(path):
    eel.showFileError(str(path))
print('[  OK  ] Function loaded correctly')
def JSAlert(a):
    eel.showAlert(a)
print('[  OK  ] Function loaded correctly')
@eel.expose
def createZip():
    import os
    from zipfile import ZipFile
    import zipfile
    global files
    global allDone
    allDone = True
    if True:
        print('[      ] Preparing zip file')
        root = Tk()
        root.attributes("-alpha", 0.0)
        root.lift()
        file = asksaveasfile(mode='w', defaultextension="*.zip", title="Save ZIP", initialfile='Zip folder.zip', filetypes=[("ZIP file", "*.zip")])
        root.destroy();
        root.mainloop();
        eel.startLoading()
        print('[  OK  ] ZIP file created succesfully')
        zipfilename = str(file.name)
        file.close()
        print('[      ] Creating ZIP file on '+str(zipfilename))
        zipObj = ZipFile(zipfilename, 'w')
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
                    if not zipfilename == path[0]:
                        zipObj.write(path[0].split('/')[-1], path[0].split('/')[-1], zipfile.ZIP_DEFLATED)
                        print('[  OK  ] File "'+str(path[0].split('/')[-1])+'" added successfully')
                    else:
                        print('[ WARN ] File "'+str(path[0].split('/')[-1])+'" skipped because it is the output zip')
                except:
                    allDone = False
                    errorAddingFile(path)
                    print('[FAILED] Unable to add file "'+str(path)+'"')
                finally:
                    actualFile += 1
                    eel.progressbar(actualFile*100/(totalFiles), path[0])()
            elif path[2] == 'folder':
                try:
                    os.chdir(path[1])
                    for folderName, subfolders, filenames in os.walk('./'):
                        for filename in filenames:
                            actualFile += 1
                            eel.progressbar(actualFile*100/(totalFiles), filename)()
                            if not(filename[0:2] == '._'):
                                try:
                                    filePath = './'+path[0].split('/')[-1]+'/'+folderName+'/'+filename
                                    if not os.path.abspath(filename).replace('\\', '/') == zipfilename:
                                        zipObj.write(folderName+'/'+filename, filePath, zipfile.ZIP_DEFLATED)
                                        print('[  OK  ] File '+filename+' added successfully')
                                    else:
                                        print('[ WARN ] File "'+os.path.abspath(filename).replace('\\', '/')+'" skipped because it is the output zip')
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
print('[  OK  ] Function loaded correctly')
@eel.expose
def openFile():
    import os
    global files
    global window
    global all_files
    if True:
        print('[      ] Dialog in process')
        root = Tk()
        root.attributes("-alpha", 0.0)
        root.lift()
        file = askopenfile(mode='r', defaultextension='*.ZIP', filetypes=[("ZIP Files", "*.ZIP")])
        root.destroy();
        root.mainloop();
        filename = file.name
        print('[  OK  ] Dialog Completed')
        try:
            files.append([file.name, os.path.dirname(file.name), 'file'])
            print('[  OK  ] File "'+str(file.name)+'" processed')
            file.close()
            return filename
        except:
            print('[ FAIL ] Unable to process file "'+f.split('\\')[-1]+'"')
            try:
                file.close()
            except:
                pass
        return new_files
    else:
        print('[FAILED] openFile() failed. Returning value 0')
        try:
            file.close()
        except:
            pass
        finally:
            return 0
print('[  OK  ] Function loaded correctly')
@eel.expose
def openFolder():
    import os
    global files
    try:
        print('[      ] Dialog in process')
        root = Tk()
        root.attributes("-alpha", 0.0)
        root.lift()
        folder = askdirectory()
        root.destroy();
        root.mainloop();
        print('[  OK  ] Dialog Completed')
        files.append([folder, folder, 'folder'])
        print('[  OK  ] Folder selected. Returning value "'+str(files[-1])+'"')
        return str(folder)
    except:
        print('[FAILED] openFolder() failed. Returning value 0')
print('[  OK  ] Function loaded correctly')
@eel.expose
def openZIP():
    import os
    global ZIP
    try:
        print('[      ] Dialog in process')
        root = Tk()
        root.attributes("-alpha", 0.0)
        root.lift()
        file = askopenfile(mode='r', defaultextension='*.ZIP', filetypes=[("ZIP Files", "*.ZIP")])
        root.destroy();
        root.mainloop();
        print('[  OK  ] Dialog Completed')
        ZIP = str(file.name)
        print('[      ] Closing file')
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
print('[  OK  ] Function loaded correctly')
@eel.expose
def extractZip():
    import os
    from zipfile import ZipFile
    global ZIP
    error=False
    try:
        print('[      ] Dialog in proccess')
        root = Tk()
        root.attributes("-alpha", 0.0)
        root.lift()
        directory = askdirectory()
        root.destroy()
        root.mainloop()
        print('[  OK  ] ZIP file created succesfully')
        directory = str(directory)
        eel.startLoading_extracting()
        if not(directory == ''):
            print('[      ] Extracting ZIP file on '+str(directory))
            totalFiles = 0
            archive = ZipFile(ZIP)
            for file in archive.namelist():
                totalFiles += 1
            actualFile=0
            for file in archive.namelist():
                try:
                    archive.extract(file, directory)
                    eel.extractProgressBar(actualFile/totalFiles*100, file.split('/')[-1])()
                    print('[  OK  ] File '+file.split('/')[-1]+' extracted successfully' )
                except:
                    print('[ WARN ] Unable to extract file '+file.split('/')[-1])
                    eel.yellowExtractProgressBar()
                    error=True
                finally:
                    actualFile+= 1
            eel.extractProgressBar(100, 'Zip Extracted!')()
            eel.nextStepExtractProgressBar()()
            eel.sleep(0.3)
            eel.resetExtractProgressBar()()
            ZIP = ''
        if error:
            print('[ WARN ] Zip file extracted with some errors')
            JSAlert('Zip file extracted with some errors :v')
        else:
            print('[  OK  ] Zip file extracted sucessfully')
            JSAlert('Zip file extracted sucessfully')
    except:
        print('[FAILED] Error occurred while extracting ZIP File')
        JSAlert('An error occurred while extracting the Zip')
    print('[  OK  ] Extract function done!')

    
def server_thread():
    global kill_server
    print('[      ] Starting server on localhost')
    eel.start('index.html',mode='chrome', size=(900, 500), port=9674,  block=True)
    print('[  OK  ] Server started')
try:
    print('[  OK  ] Finished loading functions')
    import eel
    eel.init('web')
    if __name__ == '__main__':
        from threading import Thread
        t = Thread(target=server_thread)
        t.start()
        checkUpdates_py()
        print('[      ] Checking for updates...')
        t.join()
        print('[ EXIT ] Reached end of the script')
except:
    from tkinter.messagebox import showerror
    print('[FATAL ] Fatal error occurred')
    showerror(title='SomePythonThings Zip Manager', message='An error has occurred while running SomePythonThings Zip Manager. Try to run the program later. If the error persists, please report it at https://github.com/martinet101/SomePythonThings-Zip-Manager/issues\n\nError details:\n'+str(sys.exc_info()))

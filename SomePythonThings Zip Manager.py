print('[  HI  ] Welome to SPT Zip Manager Log!')
import eel
files = []
ZIP = ''
from tkinter.filedialog import *
from tkinter.messagebox import *
from tkinter import Tk
print('[  OK  ] Step Completed')
@eel.expose
def checkUpdates_py():
    actualVersion = 1.0
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
    global files
    try:
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
        for path in files:
            try:
                os.chdir(path[-1])
                zipObj.write(path[0].split('/')[-1])
                print('[  OK  ] File "'+str(path)+'" added successfully')
            except:
                errorAddingFile(path)
                print('[FAILED] Unable to add file "'+str(path)+'"')
        zipObj.close()
        JSAlert('ZIP Created Sucessfully!')
        files = []
        print('[  OK  ] ZIP file created sucessfully')
        return 1
    except:
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
        files.append([file.name, os.path.dirname(file.name)])
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
    if True:
        print('[ WAIT ] Dialog in proccess')
        root = Tk()
        root.attributes("-alpha", 0.0)
        directory = askdirectory()
        root.destroy()
        root.mainloop()
        print('[  OK  ] ZIP file created succesfully')
        directory = str(directory)
        print('[ WAIT ] Extracting ZIP file on '+str(directory))
        with ZipFile(ZIP,"r") as zip_ref:
            zip_ref.extractall(directory)
        JSAlert('ZIP Created Sucessfully!')
        ZIP = ''
        print('[  OK  ] ZIP file created sucessfully')
        return 1
    else:
        print('[FAILED] Error occurred while creating ZIP File')
        return 0
    print('Function done')
print('[  OK  ] Finished loading functions')
print('[ WAIT ] Starting server on localhost:9457')
eel.init('web')
print("[  OK  ] Server started successfully")
print('[  OK  ] Started interface')
checkUpdates_py()
eel.start('index.html', mode='chrome', size=(900, 500), port=9457)

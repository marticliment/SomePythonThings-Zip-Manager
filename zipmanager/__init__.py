<<<<<<< Updated upstream
import os, sys, time

os.environ["QT_MAC_WANTS_LAYER"] = "1"
if hasattr(sys, 'frozen'):
    print(os.path.dirname(sys.executable))
    sys.path.append(os.path.dirname(sys.executable))
sys.argv.append("--enable-smooth-scrolling")

from sys import platform as _platform
import MainWindow, platform, traceback, webbrowser
from threading import Thread
print(os.getcwd())
from Tools import *


from PySide2 import QtWidgets, QtCore, QtGui

class MainApplication():
    def __init__(self):
        try:
            log("[        ] Starting main application...")

            Thread(target=logToFileWorker, daemon=True).start()


            if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
                QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
            if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
                QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
            
            
            
            os.chdir(os.path.expanduser("~"))

            self.app = QtWidgets.QApplication(sys.argv)
            setMainApp(self.app)

            self.app.w = MainWindow.Window(app=self.app)

            
            self.app.trayIcon = QtWidgets.QSystemTrayIcon(self.app)
            self.app.trayIcon.setIcon(QtGui.QIcon(getPath("zip.ico")))
            self.app.trayIcon.setToolTip("SomePythonThings Zip Manager is running")
            self.app.trayIcon.show()


            for argument in sys.argv[1:]:
                if(os.path.isfile(argument)):
                    self.app.w.addExtractTab(argument)

            log("[   OK   ] Main application loaded...")

            self.app.exec_()
        except Exception as e:
            log("[ FAILED ] A FATAL ERROR OCCURRED. PROGRAM WILL BE TERMINATED AFTER ERROR REPORT")
            os_info = f"" + \
            f"                        OS: {platform.system()}\n"+\
            f"                   Release: {platform.release()}\n"+\
            f"           OS Architecture: {platform.machine()}\n"+\
            f"          APP Architecture: {platform.architecture()[0]}\n"+\
            f"                   Program: SomePythonThings Zip Manager Version {version}"+\
            "\n\n-----------------------------------------------------------------------------------------"
            traceback_info = "Traceback (most recent call last):\n"
            try:
                for line in traceback.extract_tb(e.__traceback__).format():
                    traceback_info += line
                traceback_info += f"\n{type(e).__name__}: {str(e)}"
            except:
                traceback_info += "\nUnable to get error traceback"
            print(os_info+"\n"+traceback_info)
            try:
                msg = QtWidgets.QMessageBox()
                try: msg.setParent(self.app)
                except:pass
                msg.setWindowTitle("SomePythonThings Zip Manager")
                msg.setText("SomePythonThings Zip Manager crashed because of a fatal error. To get more info about this error click on the \"Show Details\" button.\n\nAn Error Report will be generated and opened automatically.\n\nSending the report would be very appreciated. Sorry for any inconveniences.")
            except: pass
            try:
                msg.setDetailedText(traceback_info)
                msg.exec_()
            except: pass
            import webbrowser
            with open(tempDir.name.replace('\\', '/')+'/log.txt', 'r') as f:
                webbrowser.open("https://www.somepythonthings.tk/error-report/?appName=SomePythonThings Zip Manager&errorBody="+os_info.replace('\n', '{l}').replace(' ', '{s}')+"{l}{l}{l}{l}SomePythonThings Zip Manager Log:{l}"+str(f.read()+"\n\n\n\n"+traceback_info).replace('\n', '{l}').replace(' ', '{s}'))
            
            if(debugging):
                raise e

MainApplication()
=======
<<<<<<< HEAD
import os, sys, time

os.environ["QT_MAC_WANTS_LAYER"] = "1"
if hasattr(sys, 'frozen'):
    print(os.path.dirname(sys.executable))
    sys.path.append(os.path.dirname(sys.executable))
sys.argv.append("--enable-smooth-scrolling")

from sys import platform as _platform
import MainWindow, platform, traceback, webbrowser
from threading import Thread
print(os.getcwd())
from Tools import *


from PySide2 import QtWidgets, QtCore, QtGui

class MainApplication():
    def __init__(self):
        try:
            log("[        ] Starting main application...")

            Thread(target=logToFileWorker, daemon=True).start()


            if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
                QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
            if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
                QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
            
            
            
            os.chdir(os.path.expanduser("~"))

            self.app = QtWidgets.QApplication(sys.argv)
            setMainApp(self.app)

            self.app.w = MainWindow.Window(app=self.app)

            
            self.app.trayIcon = QtWidgets.QSystemTrayIcon(self.app)
            self.app.trayIcon.setIcon(QtGui.QIcon(getPath("zip.ico")))
            self.app.trayIcon.setToolTip("SomePythonThings Zip Manager is running")
            self.app.trayIcon.show()


            for argument in sys.argv[1:]:
                if(os.path.isfile(argument)):
                    self.app.w.addExtractTab(argument)

            log("[   OK   ] Main application loaded...")

            self.app.exec_()
        except Exception as e:
            log("[ FAILED ] A FATAL ERROR OCCURRED. PROGRAM WILL BE TERMINATED AFTER ERROR REPORT")
            os_info = f"" + \
            f"                        OS: {platform.system()}\n"+\
            f"                   Release: {platform.release()}\n"+\
            f"           OS Architecture: {platform.machine()}\n"+\
            f"          APP Architecture: {platform.architecture()[0]}\n"+\
            f"                   Program: SomePythonThings Zip Manager Version {version}"+\
            "\n\n-----------------------------------------------------------------------------------------"
            traceback_info = "Traceback (most recent call last):\n"
            try:
                for line in traceback.extract_tb(e.__traceback__).format():
                    traceback_info += line
                traceback_info += f"\n{type(e).__name__}: {str(e)}"
            except:
                traceback_info += "\nUnable to get error traceback"
            print(os_info+"\n"+traceback_info)
            try:
                msg = QtWidgets.QMessageBox()
                try: msg.setParent(self.app)
                except:pass
                msg.setWindowTitle("SomePythonThings Zip Manager")
                msg.setText("SomePythonThings Zip Manager crashed because of a fatal error. To get more info about this error click on the \"Show Details\" button.\n\nAn Error Report will be generated and opened automatically.\n\nSending the report would be very appreciated. Sorry for any inconveniences.")
            except: pass
            try:
                msg.setDetailedText(traceback_info)
                msg.exec_()
            except: pass
            import webbrowser
            with open(tempDir.name.replace('\\', '/')+'/log.txt', 'r') as f:
                webbrowser.open("https://www.somepythonthings.tk/error-report/?appName=SomePythonThings Zip Manager&errorBody="+os_info.replace('\n', '{l}').replace(' ', '{s}')+"{l}{l}{l}{l}SomePythonThings Zip Manager Log:{l}"+str(f.read()+"\n\n\n\n"+traceback_info).replace('\n', '{l}').replace(' ', '{s}'))
            
            if(debugging):
                raise e

MainApplication()
=======
import os, sys, time

os.environ["QT_MAC_WANTS_LAYER"] = "1"
if hasattr(sys, 'frozen'):
    print(os.path.dirname(sys.executable))
    sys.path.append(os.path.dirname(sys.executable))
sys.argv.append("--enable-smooth-scrolling")

from sys import platform as _platform
import MainWindow, platform, traceback, webbrowser
from threading import Thread
print(os.getcwd())
from Tools import *


from PySide2 import QtWidgets, QtCore, QtGui

class MainApplication():
    def __init__(self):
        try:
            log("[        ] Starting main application...")

            Thread(target=logToFileWorker, daemon=True).start()


            if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
                QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
            if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
                QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
            
            
            
            os.chdir(os.path.expanduser("~"))

            self.app = QtWidgets.QApplication(sys.argv)
            setMainApp(self.app)

            self.app.w = MainWindow.Window(app=self.app)

            
            self.app.trayIcon = QtWidgets.QSystemTrayIcon(self.app)
            self.app.trayIcon.setIcon(QtGui.QIcon(getPath("zip.ico")))
            self.app.trayIcon.setToolTip("SomePythonThings Zip Manager is running")
            self.app.trayIcon.show()


            for argument in sys.argv[1:]:
                if(os.path.isfile(argument)):
                    self.app.w.addExtractTab(argument)

            log("[   OK   ] Main application loaded...")

            self.app.exec_()
        except Exception as e:
            log("[ FAILED ] A FATAL ERROR OCCURRED. PROGRAM WILL BE TERMINATED AFTER ERROR REPORT")
            os_info = f"" + \
            f"                        OS: {platform.system()}\n"+\
            f"                   Release: {platform.release()}\n"+\
            f"           OS Architecture: {platform.machine()}\n"+\
            f"          APP Architecture: {platform.architecture()[0]}\n"+\
            f"                   Program: SomePythonThings Zip Manager Version {version}"+\
            "\n\n-----------------------------------------------------------------------------------------"
            traceback_info = "Traceback (most recent call last):\n"
            try:
                for line in traceback.extract_tb(e.__traceback__).format():
                    traceback_info += line
                traceback_info += f"\n{type(e).__name__}: {str(e)}"
            except:
                traceback_info += "\nUnable to get error traceback"
            print(os_info+"\n"+traceback_info)
            try:
                msg = QtWidgets.QMessageBox()
                try: msg.setParent(self.app)
                except:pass
                msg.setWindowTitle("SomePythonThings Zip Manager")
                msg.setText("SomePythonThings Zip Manager crashed because of a fatal error. To get more info about this error click on the \"Show Details\" button.\n\nAn Error Report will be generated and opened automatically.\n\nSending the report would be very appreciated. Sorry for any inconveniences.")
            except: pass
            try:
                msg.setDetailedText(traceback_info)
                msg.exec_()
            except: pass
            import webbrowser
            with open(tempDir.name.replace('\\', '/')+'/log.txt', 'r') as f:
                webbrowser.open("https://www.somepythonthings.tk/error-report/?appName=SomePythonThings Zip Manager&errorBody="+os_info.replace('\n', '{l}').replace(' ', '{s}')+"{l}{l}{l}{l}SomePythonThings Zip Manager Log:{l}"+str(f.read()+"\n\n\n\n"+traceback_info).replace('\n', '{l}').replace(' ', '{s}'))
            
            if(debugging):
                raise e

MainApplication()
>>>>>>> d2c6635dea116061bc2ba7114a5b2453fd18553a
>>>>>>> Stashed changes
sys.exit(0)
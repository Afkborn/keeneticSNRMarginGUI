
import re
from Python.Keenetic import Keenetic

DRIVERPATH = r"Driver\chromedriver.exe" 

USERNAME = None
PASSWORD = None

from sys import argv
from os import getcwd, path, remove
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox,QDialog
from UI.Login import Ui_loginScreen # benim oluşturduğum Uİ dosyasının PY yaptıktan  sonra import ettim
from UI.MainScreen import Ui_mainScreen


class LoginWindow(QtWidgets.QMainWindow, Ui_loginScreen):
    """Login Screen"""
    def __init__(self, *args, obj=None, **kwargs):
        profileLocation = getcwd() + "\Profile\chromeProfile"
        self.keenetic = Keenetic(DRIVERPATH,profileLocation,True)
        super(LoginWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.rememberMe = False
        self.__checkRemember()
        if self.rememberMe:
            self.cbRM.setChecked(True)
        self.btnLogin.clicked.connect(self.__login)
        
    def __checkRemember(self):
        fileLoc = r"Profile\rm.bk"
        if path.exists(fileLoc):
            with open(fileLoc,"r",encoding="utf-8") as f:
                username, password = f.read().split(",")
                self.txtUsername.setText(username)
                self.txtPassword.setText(password)
                self.rememberMe = True
    
    def __rememberMeFunc(self,username,password):
        fileLoc = r"Profile\rm.bk"
        with open(fileLoc,"w",encoding="utf-8") as w:
            txt = f"{username},{password}"
            w.write(txt)
    
    def __notRememberMe(self):
        fileLoc = r"Profile\rm.bk"
        if path.exists(fileLoc):
            remove(fileLoc)

    def __login(self) -> None:
        username = self.txtUsername.text().strip()
        password = self.txtPassword.text().strip()
        if username != "" and username != None and password != "" and password != None:

            self.keenetic.openBrowser()
            USERNAME = username
            PASSWORD = password
            self.keenetic.loginPanel(USERNAME,PASSWORD)
            if self.keenetic.getLoginStatus():
                if self.cbRM.isChecked():
                    self.__rememberMeFunc(USERNAME,PASSWORD)
                else:
                    self.__notRememberMe()
                dlg = MainScreen(self.keenetic,self)
                self.hide()
                dlg.exec()
            else:
                QMessageBox.about(self, "Error", "Check username and password!")

class MainScreen(QDialog):
    """Main Screen."""
    def __init__(self, browser, parent=None):
        super().__init__(parent)
        self.ui = Ui_mainScreen()
        self.browser = browser
        self.ui.setupUi(self)
        self.ui.btnGet.clicked.connect(self.__getSNR)
        self.ui.rbCustom.toggled.connect(self.__checkRB)
        self.ui.rbBrowsing.toggled.connect(self.__checkRB)
        self.ui.rbDownload.toggled.connect(self.__checkRB)
        self.ui.btnSave.clicked.connect(self.__setSNR)
        self.ui.btnExit.clicked.connect(self.__exit)

    def __setSNR(self):
        result = False
        if self.choise == 0:
            if self.ui.rbCustom.isChecked() == True:
                newSNRMargin = self.ui.txtNewSNR.text()
            elif self.ui.rbDownload.isChecked() == True:
                newSNRMargin = 4
            else:
                newSNRMargin = 7
        else:
            newSNRMargin = self.ui.txtNewSNR.text()

        result = self.browser.changeSNRMargin(self.choise,int(newSNRMargin))


        if result:
            vdsl,adsl = self.browser.getSNRMargin()
            if self.choise == 0:
                if vdsl == int(newSNRMargin):
                    QMessageBox.about(self, ":)", "Succesful!")
                else:
                    QMessageBox.about(self, ":(", "Error!")
            else:
                if adsl == int(newSNRMargin):
                    QMessageBox.about(self, ":)", "Succesful!")
                else:
                    QMessageBox.about(self, ":(", "Error!")   
        else:
            print(result)
            QMessageBox.about(self, ":(", "Error!")

    def __exit(self):
        exit()

    def __checkRB(self):
        if self.ui.rbCustom.isChecked():
            self.ui.txtNewSNR.setEnabled(True)
            self.ui.txtNewSNR.setText("0")
        elif self.ui.rbBrowsing.isChecked():
            self.ui.txtNewSNR.setText("7")
            self.ui.txtNewSNR.setEnabled(False)
        elif self.ui.rbDownload.isChecked():
            self.ui.txtNewSNR.setText("4")
            self.ui.txtNewSNR.setEnabled(False)

    def __getSNR(self):
        self.choise = 0 #VDSL
        if self.ui.rbADSL.isChecked():
            self.choise = 1 #ADSL
        vdsl,adsl = self.browser.getSNRMargin()
        if self.choise == 0:
            self.ui.txtSNR.setText(str(vdsl))
            self.maxSNR = 30
            self.minSNR = 0
            if vdsl == 7:
                self.ui.rbBrowsing.setChecked(True)
                self.ui.rbCustom.setChecked(False)
                self.ui.rbDownload.setChecked(False)
                self.ui.txtNewSNR.setEnabled(False)
                self.ui.txtNewSNR.setText("7")
            elif vdsl == 4:
                self.ui.rbBrowsing.setChecked(False)
                self.ui.rbCustom.setChecked(False)
                self.ui.rbDownload.setChecked(True)
                self.ui.txtNewSNR.setEnabled(False)
                self.ui.txtNewSNR.setText("4")
            else:
                self.ui.rbBrowsing.setChecked(False)
                self.ui.rbCustom.setChecked(True)
                self.ui.rbDownload.setChecked(False)
                self.ui.txtNewSNR.setEnabled(True)
                self.ui.txtNewSNR.setText("0")

        else:
            self.maxSNR = 10
            self.minSNR = -10
            self.ui.rbBrowsing.setChecked(False)
            self.ui.rbCustom.setChecked(True)
            self.ui.rbDownload.setChecked(False)
            self.ui.txtSNR.setText(adsl)
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(argv)
    window = LoginWindow()
    window.show()
    app.exec()


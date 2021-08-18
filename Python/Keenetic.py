
from typing import Tuple
from selenium.webdriver import Chrome,ChromeOptions
from selenium.webdriver import ActionChains
from time import sleep

import logging
from datetime import datetime as dt
from os import getcwd


ADSLMARGINCB = '//*[@id="cp-main-container"]/div/div[1]/div[1]/div/div[2]/div/form/div[4]/ng-include/ndm-details/div/div[2]/fieldset/div[2]/ndm-selectbox2/div/div[2]/a/div'
VDSLMARGINCB = '//*[@id="cp-main-container"]/div/div[1]/div[1]/div/div[2]/div/form/div[4]/ng-include/ndm-details/div/div[2]/fieldset/div[3]/ndm-selectbox2/div/div[2]/a/div'



def printTime():
    """Saat_Dakika_Gün_Ay şeklinde döner"""
    parser = dt.now()
    return parser.strftime("%H_%M_%d_%m")



class Keenetic:
    __isLogin = False

    def __init__(self,driverLoc,chromeProfileLoc,headless = False) -> None:
        self.driverLocation = driverLoc
        self.headless = headless
        self.chromeProfileLoc = chromeProfileLoc

    def openBrowser(self):
        """open chrome"""
        options = ChromeOptions()
        options.add_argument(f"user-data-dir={self.chromeProfileLoc}")
        options.add_argument("--log-level=3")
        options.headless = self.headless
        self.browser = Chrome(executable_path=self.driverLocation,options=options)
        self.browser.set_window_position(0,0)
        self.browser.set_window_size(1024,768)

    def loginPanel(self,username,password):
        """Login gateway panel"""
        self.browser.get('http://192.168.1.1/')
        self.__username = username
        self.__password = password
        sleep(2)
        if self.browser.current_url != "http://192.168.1.1/dashboard":
            usernameInput = self.browser.find_element_by_xpath('/html/body/ndm-layout/div/div/div/div/section/div[1]/div[1]/div/section[2]/form/div[1]/div/div[3]/div/div[1]/label[1]/input')
            passwordInput = self.browser.find_element_by_xpath('/html/body/ndm-layout/div/div/div/div/section/div[1]/div[1]/div/section[2]/form/div[2]/div/div[3]/div/div[1]/label[1]/input')
            usernameInput.send_keys(self.__username)
            passwordInput.send_keys(self.__password)
            sleep(0.1)
            loginButton = self.browser.find_element_by_xpath('/html/body/ndm-layout/div/div/div/div/section/div[1]/div[1]/div/section[2]/form/ndm-button/button')
            loginButton.click()
            sleep(2)
            if self.browser.current_url == 'http://192.168.1.1/dashboard':
                self.__isLogin = True
        else:
            self.__isLogin = True

    def getLoginStatus(self):
        return self.__isLogin

    def getSNRMargin(self) -> tuple():
        """Return vdslMargin, adslMargin as int. Login required."""
        if self.__isLogin:
            self.browser.get('http://192.168.1.1/controlPanel/dsl')
            sleep(3)
            ekHatAyarlariLabel = self.browser.find_element_by_xpath('//*[@id="cp-main-container"]/div/div[1]/div[1]/div/div[2]/div/form/div[4]/ng-include/ndm-details/div/div[1]/a/span')
            ekHatAyarlariLabel.click()
            adslMarginCB = self.browser.find_element_by_xpath(ADSLMARGINCB)
            vdslMarginCB = self.browser.find_element_by_xpath(VDSLMARGINCB)
            self.__vdslSNRMargin = int(str(vdslMarginCB.get_attribute('title')).replace("(Varsayılan)","").replace("dB",""))
            self.__adslSNRMargin = int(str(adslMarginCB.get_attribute('title')).replace("(Varsayılan)","").replace("dB",""))
            return (self.__vdslSNRMargin, self.__adslSNRMargin)
        else:
            return (None,None)

    def __pressSave(self):
        self.__clickXY(84,586)


    def __clickXY(self,x,y):
        action = ActionChains(self.browser)
        action.move_by_offset(x,y)
        action.click()
        action.perform()
        action.reset_actions()


    def changeSNRMargin(self,type = 0,value = 8):
        """Change SNR margin. type = 0 for VDSL, 1 for ADSL. value for ADSL -10/+10, for VDSL 0/+30"""
        if self.__isLogin:
            if self.browser.current_url != "http://192.168.1.1/controlPanel/dsl":
                self.browser.get("http://192.168.1.1/controlPanel/dsl")
                sleep(2)
            if type == 0:
                #VDSL
                if value <= 30 and value >= 0:
                    try:
                        sleep(2)
                        ekhatAyarXPath = '//*[@id="cp-main-container"]/div/div[1]/div[1]/div/div[2]/div/form/div[4]/ng-include/ndm-details/div/div[1]/a'
                        ekHatAyarYazi = self.browser.find_element_by_xpath(ekhatAyarXPath)
                        if ekHatAyarYazi.text == "Ek hat ayarlarını göster":
                            ekHatAyarYazi.click()
                        sleep(0.1)
                        eskiSNRXPath = '//*[@id="cp-main-container"]/div/div[1]/div[1]/div/div[2]/div/form/div[4]/ng-include/ndm-details/div/div[2]/fieldset/div[3]/ndm-selectbox2/div/div[2]/a/div/span[2]/span'
                        eskiMargin = (self.browser.find_element_by_xpath(eskiSNRXPath).text).replace('(Varsayılan)',"")
                        assagiOkxPath = '//*[@id="cp-main-container"]/div/div[1]/div[1]/div/div[2]/div/form/div[4]/ng-include/ndm-details/div/div[2]/fieldset/div[3]/ndm-selectbox2/div/div[2]/a/i'
                        self.browser.find_element_by_xpath(assagiOkxPath).click()
                        sleep(0.1)
                        dbs = self.browser.find_element_by_xpath('/html/body/ndm-layout/div/div[2]/div[2]/div/div/div/div/div[1]/div[1]/div/div[2]/div/form/div[4]/ng-include/ndm-details/div/div[2]/fieldset/div[3]/ndm-selectbox2/div/div[2]/div/ul')
                        dbs = dbs.find_elements_by_css_selector("li")

                        tiklanacakDbs = ""
                        for i in dbs:
                            tiklanacakDbsValue = i.get_attribute('data-ndm-option-value')
                            if tiklanacakDbsValue == str(value):
                                tiklanacakDbs = i
                        

                        tiklanacakDbs.click()
                        self.__pressSave()
                        sleep(2)
                        return True
                    except Exception as e:
                        print(f"Error detail {e}")
                        return False
            else:
                #ADSL
                if value <= 10 and value >= -10:
                    try:
                        sleep(2)
                        ekhatAyarXPath = '//*[@id="cp-main-container"]/div/div[1]/div[1]/div/div[2]/div/form/div[4]/ng-include/ndm-details/div/div[1]/a'
                        self.browser.find_element_by_xpath(ekhatAyarXPath).click()
                        eskiSNRXPath = '//*[@id="cp-main-container"]/div/div[1]/div[1]/div/div[2]/div/form/div[4]/ng-include/ndm-details/div/div[2]/fieldset/div[2]/ndm-selectbox2/div/div[2]/a/div/span[2]/span'
                        eskiMargin = (self.browser.find_element_by_xpath(eskiSNRXPath).text).replace('(Varsayılan)',"")
                        sleep(0.1)
                        assagiOkxPath = '//*[@id="cp-main-container"]/div/div[1]/div[1]/div/div[2]/div/form/div[4]/ng-include/ndm-details/div/div[2]/fieldset/div[2]/ndm-selectbox2/div/div[2]/a/i'
                        sleep(0.1)
                        self.browser.find_element_by_xpath(assagiOkxPath).click()
                        dbs = self.browser.find_element_by_xpath('/html/body/ndm-layout/div/div[2]/div[2]/div/div/div/div/div[1]/div[1]/div/div[2]/div/form/div[4]/ng-include/ndm-details/div/div[2]/fieldset/div[2]/ndm-selectbox2/div/div[2]/div/ul')
                        dbs = dbs.find_elements_by_css_selector("li")
                        tiklanacakDbs = None
                        for i in dbs:
                            tiklanacakDbsValue = i.get_attribute('data-ndm-option-value')
                            if tiklanacakDbsValue == str(value):
                                tiklanacakDbs = i
                        tiklanacakDbs.click()
                        self.__pressSave()
                        sleep(2)
                        return True
                    except Exception as e:
                        print(f"Error detail {e}")
                        return False

   
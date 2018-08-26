import selenium
from selenium import webdriver
import os
import configparser
import time
import threading
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.chrome.options import Options

def CheckAsinIfExists(browser,ASIN):
    AsinLink = 'https://www.amazon.co.jp/dp/' + ASIN
    #print('AsinLink is '+AsinLink)
    for link in browser.find_elements_by_xpath("//*[@href]"):#获取当前页面的href
        if link.get_attribute('href') == AsinLink:
            return True
    return False

def CheckAsinIfOK(cf,asin):
    Status = False
    try:
        if cf.get("Status",asin) == 1:
            Status = True
    except:
        Status = False
    finally:
        return Status


def GetAsinData(cf,ASIN):
    errStatus = False
    isExists = False
    while isExists == False:
        #chrome_options = Options()
        #chrome_options.add_argument("--headless")
        #browser = webdriver.Chrome(chrome_options=chrome_options)
        browser = webdriver.Chrome()
        browser.get("http://www.surtime.com")
        browser.find_element_by_id("loginLink").click()
        browser.find_element_by_id("UserName").send_keys(username)
        browser.find_element_by_id("Password").send_keys(password)
        browser.find_element_by_class_name("btn-primary").submit()
        browser.get("http://www.surtime.com/ASINAnalysisQuery/ASINAnalysisQuery")
        if CheckAsinIfExists(browser, ASIN):
            print(ASIN + " is OK")
            isExists = True
            cf.set("Status", ASIN, "1")
            cf.write(open('account.inf', 'w'))
            browser.quit()
        else:
            try:
                print("It's not here")
                browser.find_element_by_id("Country").find_elements_by_tag_name("option")[6].click()
                browser.find_element_by_id("ASIN").send_keys(ASIN)
                browser.find_element_by_id("loading3").click()
                time.sleep(90)
                if errStatus == False:
                    if CheckAsinIfExists(browser, ASIN):
                        print(ASIN + " is OK")
                        isExists = True
                        cf.set("Status", ASIN, "1")
                        cf.write(open('account.inf', 'w'))
                    else:
                        print(ASIN + " is not here")
                        isExists = False
                        cf.set("Status", ASIN, "0")
                        cf.write(open('account.inf', 'w'))
                else:
                    errStatus = False
                browser.quit()
            except UnexpectedAlertPresentException:
                result = EC.alert_is_present()(browser)
                if result:
                    result.accept()
                print(ASIN + " alert...........")
                errStatus = True
                browser.quit()
                pass

if __name__ == '__main__':
    if os.path.exists("account.inf"):
        threads = []
        cf = configparser.ConfigParser()
        cf.read("account.inf")
        username = cf.get("account", "username")
        password = cf.get("account", "password")
        asinitems = cf.items("ASIN")
        for i in range(0,len(asinitems)):
            if CheckAsinIfOK(cf, asinitems[i][1]) == False:
                t = threading.Thread(target=GetAsinData, args=(cf, asinitems[i][1],))
                threads.append(t)

        for t in threads:
            t.setDaemon(True)
            t.start()

        for t in threads:
            t.join()
    else:
        print("account.inf is noexists!")


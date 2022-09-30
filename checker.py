import cv2
import pyautogui as pyag
import time
from datetime import datetime
import csv
import logging
import os


class Checker():
    def __init__(self, interval = 1):
        self.interval = interval
        self.running = False
        self.checks_done = 0
        self.time_started = 0
        self.offScreenX = 760
        self.offScreenY = 146
        self.repeat = False
        self.lastState = ""
        pyag.PAUSE = 0
        self.logging = logging.getLogger("Checker")
    
    #Locates an image and returns center position of it
    def locateCenter(self, needle, haystack):
        points = pyag.locate(needle,haystack)
        if points is not None:
            return (points.left + points.width/2), (points.top + points.height/2)
        else:
            return None
    
    def click_offset(self, point, offsetX = 0, offsetY = 0):
        X_offset = point[0] + offsetX + self.offScreenX
        Y_offset = point[1] + offsetY + self.offScreenY
        pyag.click(X_offset, Y_offset)
    
    def postDate(self, point):
        self.lastState= postDate.__name__
        X_offset = 975 + self.offScreenX
        self.logging.info("Post-dated prescription, accepting...")
        self.click_offset(point,975)
    
    def addPatient(self,point):
        self.lastState = addPatient.__name__
        X_offset = 846 + self.offScreenX
        self.logging.info("Patient missing, adding new patient...")
        self.click_offset(point, 846)
        self.logging.info("Looking for yes button...")
        yes_button_image = cv2.imread('yes2.png')
        yes_button = self.locateCenter(yes_button_image, pyag.screenshot())
        tries = 1
        while yes_button is None:
            self.lastState="addPatient_yesButton"
            pyag.press("tab")
            time.sleep(1)
            yes_button = self.locateCenter(yes_button_image, pyag.screenshot())
            self.logging.info(f"Looking for yes button. ({tries})")
            if tries > 15:
                return True
            tries += 1
        self.click_offset(yes_button)
    
    def drugDoubling(self,point):
        self.lastState = drugDoubling.__name__
        self.logging.info("Drug Doubling, acccepting...")
        self.click_offset(point, 820)
        time.sleep(1)
    
    def drugTherapy(self,point):
        self.lastState = drugTherapy.__name__
        self.logging.info("Drug Therapy, acccepting...")
        self.click_offset(point, 820)
        time.sleep(1)
    
    def highRiskItem(self,point):
        self.lastState = highRiskItem.__name__
        self.logging.info("High risk item, accepting...")
        self.click_offset(point,820)
    
    def specialContainer(self,point):
        self.lastState = specialContainer.__name__
        self.logging.info("Special container, accepting...")
        self.click_offset(point,835)
    
    def skip(self):
        self.lastState=skip.__name__
        tries = 0
        self.logging.info("Looking for skip button...")
        skip_button_image = cv2.imread("skip.png")
        skip_button = self.locateCenter(skip_button_image, pyag.screenshot())
        while skip_button is None:
            skip_button = self.locateCenter(skip_button_image, pyag.screenshot())
            if tries > 15:
                return True
            tries += 1
        self.logging.error("Skipping prescription!")
        self.click_offset(skip_button)

    def start(self):
        self.running = True
        self.time_started = time.time()
        tries = 0

        pnm_img = cv2.imread(os.path.join(os.getcwd(),'checks','patient_no_match.png'))
        dd_img = cv2.imread(os.path.join(os.getcwd(),'checks','drug_doubling.png'))
        dt_img = cv2.imread(os.path.join(os.getcwd(),'checks','drug_therapy.png'))
        dab_img = cv2.imread(os.path.join(os.getcwd(),'checks','do_another.png'))
        odw_img = cv2.imread(os.path.join(os.getcwd(),'checks','out_dispense_window.png'))
        sdc_img = cv2.imread(os.path.join(os.getcwd(),'checks','7_day_check.png'))
        pdp_img = cv2.imread(os.path.join(os.getcwd(),'checks','post_date.png'))
        cs_img = cv2.imread(os.path.join(os.getcwd(),'checks','clinically_unsuitable.png'))
        hri_img = cv2.imread(os.path.join(os.getcwd(),'checks','high_risk_item.png'))
        sc_img = cv2.imread(os.path.join(os.getcwd(),'checks','special_container.png'))
        ca_img = cv2.imread(os.path.join(os.getcwd(),'checks','check_another.png'))

        self.logging.warn("Starting Checker! Open titan on checking screen!")

        while self.running:
            try:
                time.sleep(self.interval)
                screenshot = pyag.screenshot(region= (self.offScreenX, self.offScreenY, 760, 1080))

                clinically_unsuitable = self.locateCenter(cs_img,screenshot)
                out_dispense_window = self.locateCenter(odw_img, screenshot)
                seven_day_check = self.locateCenter(sdc_img, screenshot)
                post_date = self.locateCenter(pdp_img, screenshot)
                patient_no_match = self.locateCenter(pnm_img, screenshot)
                drug_doubling = self.locateCenter(dd_img, screenshot)
                drug_therapy = self.locateCenter(dt_img, screenshot)
                do_another_button = self.locateCenter(dab_img, screenshot)
                high_risk_item = self.locateCenter(hri_img, screenshot)
                special_container = self.locateCenter(sc_img, screenshot)
                check_another = self.locateCenter(ca_img, screenshot)

                if clinically_unsuitable is not None:
                    self.logging.error("Prescription clinically unsuitable!")
                    self.skip()
                
                if seven_day_check is not None:
                    self.logging.error("Patient has 7 day check!")
                    self.skip()
                    time.sleep(3)
                
                if out_dispense_window is not None:
                    self.logging.error("Prescription already checked!")
                    self.skip()
                
                if special_container is not None:
                    self.specialContainer(special_container)
                
                if post_date is not None:
                    self.postDate(post_date)
                
                if high_risk_item is not None:
                    self.highRiskItem(high_risk_item)
                
                if drug_therapy is not None:
                    self.drugTherapy(drug_therapy)
                
                if drug_doubling is not None:
                    self.drugDoubling(drug_doubling)
                
                if do_another_button is not None:
                    self.logging.info("No checks for this patient! NEXT!")
                    self.click_offset(do_another_button)
                    self.checks = self.checks + 1
                    tries = 0

                if check_another is not None:
                    self.logging.info("No checks for this patient! NEXT!")
                    self.click_offset(check_another)
                    self.check = self.checks + 1
                    tries = 0

                if clinically_unsuitable is None and out_dispense_window is None and seven_day_check is None and post_date is None and patient_no_match is None and drug_doubling is None and drug_therapy is None and do_another_button is None and high_risk_item is None and special_container is None and check_another is None:
                    self.logging.error("Something went wrong! skipping cycle!")
                    tries += 1
                    if tries > 15:
                        self.logging.error("Can't find any checks! Looking for skip button!")
                        self.skip()
                        tries = 0

            except Exception as e:
                print(e)
                self.finish()
    
    def finish(self):
        self.running = False
        self.logging.info(f"Checks done: {self.checks_done}")
        self.logging.info(f"Total time running: {time.time() - self.time_started}")
        with open("log.csv", "a") as f:
            writer = csv.writer(f)
            data = [datetime.today().strftime("%d/%m/%Y"), self.checks_done,0, time.time() - self.time_started]
            writer.writerow(data)
        if self.repeat:
            self.start()
    
    





    
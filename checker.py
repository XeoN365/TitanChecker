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
        
    def acceptPrescription(self,point):
        self.lastState = self.acceptPrescription.__name__
        offSetRegion = (self.offScreenX + point[0]-50,self.offScreenY + point[1]-40,1220,110)
        screenshot = pyag.screenshot(region = offSetRegion)
        accept_button = cv2.imread(os.path.join(os.getcwd(),'TitanChecker','checks','accept_button.png'))
        accept = self.locateCenter(accept_button, screenshot)
        tries = 0
        while accept is None:
            screenshot = pyag.screenshot(region = offSetRegion)
            accept = self.locateCenter(accept_button, screenshot)
            time.sleep(1)
            self.logging.info("Looking for accept button")
            tries += 1
            if tries > 3:
                return True
        pyag.click(accept[0] + offSetRegion[0], accept[1] + offSetRegion[1] )
    
    #Locates an image and returns center position of it
    def locateCenter(self, needle, haystack):
        points = pyag.locate(needle,haystack)
        if points is not None:
            return (points.left + points.width/2), (points.top + points.height/2)
        else:
            return None

    def click_offset(self, point, offset = 0):
        pyag.click(point[0] + self.offScreenX + offset, point[1] + self.offScreenY)
    
    def postDate(self, point):
        self.lastState= self.postDate.__name__
        self.acceptPrescription(point)
    
    def addPatient(self,point):
        if self.lastState != "addPatient_yesButton" :
            self.lastState = self.addPatient.__name__
            self.logging.info("Patient missing, adding new patient...")
            self.click_offset(point, 846)
            self.logging.info("Looking for yes button...")
            yes_button_image = cv2.imread(os.path.join(os.getcwd(),'TitanChecker','checks','yes2.png'))
            yes_button = self.locateCenter(yes_button_image, pyag.screenshot())
            tries = 1
            while yes_button is None:
                self.lastState="addPatient_yesButton"
                pyag.press("tab")
                time.sleep(1)
                yes_button = self.locateCenter(yes_button_image, pyag.screenshot())
                self.logging.info(f"Looking for yes button. ({tries})")
                if tries > 30:
                    return True
                tries += 1
            pyag.click(yes_button)
        else:
            time.sleep(1)
    
    def drugDoubling(self,point):
        self.lastState = self.drugDoubling.__name__
        self.acceptPrescription(point)
    
    def drugTherapy(self,point):
        self.lastState = self.drugTherapy.__name__
        self.acceptPrescription(point)
    
    def highRiskItem(self,point):
        self.lastState = self.highRiskItem.__name__
        self.acceptPrescription(point)

    def specialContainer(self,point):
        self.lastState = self.specialContainer.__name__
        self.acceptPrescription(point)
    
    def skip(self):
        self.lastState=self.skip.__name__
        tries = 0
        self.logging.info("Looking for skip button...")
        skip_button_image = cv2.imread(os.path.join(os.getcwd(),'TitanChecker','checks', 'skip.png'))
        skip_button = self.locateCenter(skip_button_image, pyag.screenshot())
        while skip_button is None:
            skip_button = self.locateCenter(skip_button_image, pyag.screenshot())
            if tries > 15:
                return True
            tries += 1
        self.logging.error("Skipping prescription!")
        pyag.click(skip_button)

    def start(self):
        self.running = True
        self.time_started = time.time()
        tries = 0
        cwdpath = os.path.join(os.getcwd(),'TitanChecker','checks')
        pnm_img = cv2.imread(os.path.join(cwdpath,'patient_no_match.png'))
        dd_img = cv2.imread(os.path.join(cwdpath,'drug_doubling.png'))
        dt_img = cv2.imread(os.path.join(cwdpath,'drug_therapy.png'))
        dab_img = cv2.imread(os.path.join(cwdpath,'do_another.png'))
        odw_img = cv2.imread(os.path.join(cwdpath,'out_dispense_window.png'))
        sdc_img = cv2.imread(os.path.join(cwdpath,'7_day_check.png'))
        pdp_img = cv2.imread(os.path.join(cwdpath,'post_date.png'))
        cs_img = cv2.imread(os.path.join(cwdpath,'clinically_unsuitable.png'))
        hri_img = cv2.imread(os.path.join(cwdpath,'high_risk_item.png'))
        sc_img = cv2.imread(os.path.join(cwdpath,'special_container.png'))
        ca_img = cv2.imread(os.path.join(cwdpath,'check_another.png'))
        sp_img = cv2.imread(os.path.join(cwdpath,'already_done.png'))
        nms_img = cv2.imread(os.path.join(cwdpath,'nms.png'))
        cnl_img = cv2.imread(os.path.join(cwdpath, 'close.png'))

        self.logging.info("Starting Checker! Open titan on checking screen!")

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
                already_done = self.locateCenter(sp_img,screenshot)
                nms = self.locateCenter(nms_img, screenshot)
                cancel_btn = self.locateCenter(cnl_img, screenshot)

                if cancel_btn is not None:
                    self.logging.error("Error message showed up!, pressing cancel")#
                    self.click_offset(cancel_btn)

                if already_done is not None:
                    self.logging.error("Prescription already done!")
                    self.skip()

                if nms is not None:
                    self.logging.error("NMS!")
                    self.skip()

                if clinically_unsuitable is not None:
                    self.logging.error("Prescription clinically unsuitable!")
                    self.skip()
                
                if seven_day_check is not None:
                    self.logging.error("Patient has 7 day check!")
                    self.skip()
                    time.sleep(4)
                
                if out_dispense_window is not None or already_done is not None:
                    self.logging.error("Prescription already done!")
                    self.skip()
                
                if nms is not None:
                    self.logging.error("NMS!")
                    self.skip()

                if patient_no_match is not None:
                    self.logging.error("Patient not found!, adding...")
                    self.addPatient(patient_no_match)
                
                if special_container is not None:
                    self.logging.error("Special Container!")
                    self.specialContainer(special_container)
                
                if post_date is not None:
                    self.logging.error("Post date prescription!")
                    self.postDate(post_date)
                
                if high_risk_item is not None:
                    self.logging.error("High risk item!")
                    self.highRiskItem(high_risk_item)
                
                if drug_therapy is not None:
                    self.logging.error("Drug Therapy check!")
                    self.drugTherapy(drug_therapy)
                
                if drug_doubling is not None:
                    self.logging.error("Drug Doubling check!")
                    self.drugDoubling(drug_doubling)
                
                if do_another_button is not None or check_another is not None:
                    self.lastState = "doAnother"
                    self.logging.info("No checks for this patient! NEXT!")

                    button2click = do_another_button if do_another_button is not None else check_another
                    self.click_offset(button2click)
                    self.checks_done = self.checks_done + 1
                    tries = 0

                if clinically_unsuitable is None and out_dispense_window is None and seven_day_check is None and post_date is None and patient_no_match is None and drug_doubling is None and drug_therapy is None and do_another_button is None and high_risk_item is None and special_container is None and check_another is None:
                    self.logging.error("Something went wrong! skipping cycle!")
                    pyag.moveTo(1200,500)
                    pyag.scroll(50)
                    tries += 1
                    if tries > 15:
                        self.logging.error("Can't find any checks! Looking for skip button!")
                        self.skip()
                        tries = 0

            except Exception as e:
                self.logging.error(e)
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
    
    





    
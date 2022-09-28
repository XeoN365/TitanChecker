from checker import Checker
import logging
import git
import os
from dotenv import load_dotenv

load_dotenv()

class Launcher():
    def __init__(self):
        self.checker = Checker()
        self.USERNAME = os.getenv('USERNAME')
        self.TOKEN = os.getenv('TOKEN')
        self.giturl = f"https://{self.USERNAME}:{self.TOKEN}@github.com/XeoN365/TitanChecker.git"
    
    def update(self):
        g = git.Git(self.giturl)
        logging.info("Starting update!")
        g.pull('master', 'main')
        logging.info("Update finished!")
        
if __name__ == "__main__":
    launcher = Launcher()
    launcher.update()
    launcher.checker.start()
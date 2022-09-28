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
        self.logging = logging.getLogger("Launcher")
    
    def update(self):
        try:
            repo = git.Repo.clone_from(self.giturl, os.getcwd())
        except Exception as e:
            repo = git.Repo(os.getcwd())
        q = repo.remotes.master
        q.pull()
        print("done")
        
if __name__ == "__main__":
    launcher = Launcher()
    
    launcher.update()
    #launcher.checker.start()
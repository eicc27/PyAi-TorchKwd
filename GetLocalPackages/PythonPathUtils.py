import os
import platform
import sys

class PPU:
    '''
    A semi-static singleton to define where is your Python.
    '''

    Windows = "Windows"
    Linux = "Linux"

    Python = "Python"
    Conda = Anaconda = "Conda"

    Version = sys.version_info

    def __init__(self, dist: str) -> None:
        self.dist = dist
        self.platform = platform.system()
        self.envPath = self._setEnvPath()


    def _setEnvPath(self) -> str:
        '''
        os: Windows or Linux (now only supports Windows)
        dist: Conda or Python
        '''
        if self.platform == PPU.Windows:
            # print(os.environ)
            env = os.environ["HOMEDRIVE"] + os.environ["HOMEPATH"] # C:\users\username
            if self.dist == PPU.Conda:
                return os.path.join(env, "anaconda3", "Lib", "site-packages")
            elif self.dist == PPU.Python:
                return os.path.join(env, "AppData", "Local", "Programs", "Python", f"Python{PPU.Version.major}{PPU.Version.minor}", "Lib", "site-packages")
    
    def setPackagePath(self, packageName: str) -> str:
        return os.path.join(self.envPath, packageName)
    
    @staticmethod
    def stripPackagePath(packagePath: str):
        L = len("site-packages")
        res =  packagePath[packagePath.find("site-packages") + L:]
        res = res.replace("\\", '.')
        res = res.replace("__init__.py", "") # do some cutting in the tree then
        res = res.replace(".py", "")
        res = res[1:] # only return the last part of the path
        return res.split('.')[-1]

    @staticmethod
    def removeEmptyKeys(info: dict):
        if isinstance(info, dict):
            info_re = dict()
            for key, value in info.items():
                if isinstance(value, dict) or isinstance(value, list):
                    re = PPU.removeEmptyKeys(value)
                    if len(re):
                        info_re[key] = re
                elif type(value) == str and value not in ['', {}, [], 'null']:
                    info_re[key] = value
            return info_re
        elif isinstance(info, list):
            info_re = list()
            for value in info:
                if isinstance(value, dict) or isinstance(value, list):
                    re = PPU.removeEmptyKeys(value)
                    if len(re):
                        info_re.append(re)
                elif type(value) == str and value not in ['', {}, [], 'null']:
                    info_re.append(value)
            return info_re
        

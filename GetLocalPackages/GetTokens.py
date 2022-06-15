'''
指定额外的包来跑
'''

import os
from FileSystem import PythonType, Path, FileType, FileSystem, File
import json
from PythonPathUtils import PPU

PACKAGES = [
    "flask"
]

class Token:
    def __init__(self, token: str, tokenType: str, parent: File = None) -> None:
        self.token = token
        self.tokenType = tokenType
        self.parent = parent
        self.children = []
        self.ftype = FileType.Token


class TokenSystem(FileSystem):
    '''
        The auto-import suggstion system supported by FilsSystem.
    '''

    def __init__(self, root: str) -> None:
        super().__init__(root)
        self._appendTokenNodes(self.root)

    def _appendTokenNodes(self, root: File):
        if root.ftype == FileType.File:
            root.children.extend(self.getTokensByFile(root.fname, root))
            return
        for child in root.children:
            self._appendTokenNodes(child)
        

    @staticmethod
    def getTokensByFile(fpath: str, parent: File) -> list[Token]:
        with open(fpath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        tokens: list[Token] = []
        commentStack: list[str] = []
        for line in lines:
            # single-lined comments or wrapped defs are ignored
            if line.startswith(" ") or line.startswith("\t") or line.startswith("#") or line.startswith("\n"):
                continue
            # multi-lined comments are ignored(using stacks to monitor)
            if line.startswith("\"\"\"") or line.startswith("'''") or line.startswith("r\"\"\"") or line.startswith("r'''"):
                if commentStack:
                    commentStack.clear()
                    continue
                else:
                    commentStack.append('x')
            if commentStack:
                continue
            if line[0].isalpha:
                splits = line.split(" ")
                if len(splits) < 2:
                    continue
                if not splits[1]:
                    continue
                if splits[1].startswith("="):
                    tokens.append(
                        Token(line.split("=")[0].strip(), PythonType.VariableType))
            if line.startswith("def "):
                # 4 is the length of "def "
                tokens.append(
                    Token(line[4:line.find("(")], PythonType.FunctionType))
            if line.startswith("class "):
                # consider the inheritance(ends with "(") and norms(ends with ":")
                index = line.find("(")
                index = line.find(":") if index == -1 else index
                # 6 is the length of "class "
                tokens.append(Token(line[6:index], PythonType.ClassType))
        for token in tokens:
            token.parent = parent
        return tokens
    
    # converts the whole file system into a dict of tokens (flatten)
    def toDict(self, root: File, d: dict = {}) -> dict:
        if isinstance(root, Token): # tokens are leaf nodes
            return
        for child in root.children:
            if not isinstance(child, Token):
                d[PPU.stripPackagePath(child.fname)] = {}
                self.toDict(child, d[PPU.stripPackagePath(child.fname)])
            else:
                d[child.token] = child.tokenType
        return d


if __name__ == "__main__":
    ppu = PPU(PPU.Anaconda)
    for package in PACKAGES:
        packagePath = ppu.setPackagePath(package)
        fs = TokenSystem(packagePath)
        d = fs.toDict(fs.root)
        d = PPU.removeEmptyKeys(d)
        with open(os.path.join(Path.DataPath, f"{package}.json"), "w+", encoding="utf-8") as f:
            json.dump(d, f, indent=4)
    

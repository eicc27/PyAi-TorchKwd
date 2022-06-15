import os
import pickle


class FileType:
    File = "file"
    Folder = "folder"
    Token = "token"


class PythonType:
    FunctionType = "function"
    ClassType = "class"
    VariableType = "variable"


class Path:
    BasePath = os.path.join(".", "GetLocalPackages")
    PackagePath = os.path.join(BasePath, "TestPackages")
    DataPath = os.path.join(BasePath, "Data")

# tree node of FileSystem


class File:
    def __init__(self, fname: str, ftype: str, parent=None, children: list = []) -> None:
        self.fname = fname
        self.ftype = ftype
        self.parent = parent
        self.children = children


class FileSystem:
    '''
    This class stores a filesystem containing only Python files.
    The file path of each node is stored in a relative path from the root.

    Parameters
    -----
    `root`: `str`, the path of the root folder
    '''

    def __init__(self, root: str) -> None:
        self.root = File(root, FileType.Folder, None, [])
        self._createTree()
        self._cutLeaves(self.root)

    def getNodeByName(self, target: File, root: File):
        '''
        Searches the file system for a file with the given name.

        Parameters
        -----
        `target`: `File`, the name of the file to search for
        `root`: `File`, the root node of the file system(if specified then search in the sub-tree of root)
        
        Returns
        -----
        `File`: the file with the given name if found, otherwise None
        '''
        # fails
        if not root:
            return None
        # finds 
        if root.fname == target.fname:
            return root
        for child in root.children:
            if child.fname == target.fname:
                return child
            # recursively search
            result = self.getNodeByName(target, child)
            if result:
                return result
    
    def _createTree(self):
        '''
        Uses `os.walk` to simplify node insertion.
        Note that folders always appears before files in children list to make the search faster.
        '''
        for root, folders, files in os.walk(self.root.fname, True):
            if root == self.root.fname:
                self.root.children.extend(
                    [File(os.path.join(root, f), FileType.Folder, self.root, []) for f in folders]
                )
                self.root.children.extend(
                    [File(os.path.join(root, f), FileType.File, self.root, [])
                     for f in files if f.endswith(".py")]
                )
                continue
            # when not root
            # firstly search the node "root" by name
            node: File = self.getNodeByName(File(root, FileType.Folder, None, []), self.root)
            # then add the children
            node.children.extend(
                [File(os.path.join(root, f), FileType.Folder, node, []) for f in folders]
            )
            node.children.extend(
                [File(os.path.join(root, f), FileType.File, node, [])
                 for f in files if f.endswith(".py")]
            )
    
    def _cutLeaves(self, root: File, type: list = [FileType.Folder]):
        '''
        If the folder is (recursively) empty, remove it from the tree.
        '''
        if root.ftype in type and not root.children:
            root.parent.children.remove(root)
            if not root.parent.children:
                root.parent.parent.children.remove(root.parent)
                del root.parent
            del root
            return
        for child in root.children:
            self._cutLeaves(child, type)

if __name__ == "__main__":
    fs = FileSystem(Path.PackagePath)
    print(fs.getNodeByName(File(r"__init__.py", FileType.File), fs.root))
    

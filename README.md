# An import auto completeion for Python

Free-of-ast. Not free-of-trees.

## Steps

### In Python

`FileSystem`: File type & Folder type tree-building.

**os.walk** -> **file tree** -> **filter** (non-python leaves) -> **cutting** (empty folders)

`TokenSystem`: File type & Token type tree-building. (Tokens are not recursively searched in files)

**getToken** -> **token tree** -> **pythonize** -> **cutting** (empty usage of files)
-> **flatten** to dict

### In TS

prerequisites: **read `Data` trees**

**input token stripping** -> **tree searching** -> **code** autocompletion -> **import** AC

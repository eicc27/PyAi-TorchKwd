import ast

s = '''
from os import mkdir as dir
os.mkdir("./test", s="")
'''

print(ast.dump(ast.parse(s), indent=4))
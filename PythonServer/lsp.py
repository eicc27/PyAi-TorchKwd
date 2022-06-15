import os
from flask import Flask
from json import load
import ast
from urllib.parse import unquote
# localhost:5000
app = Flask(__name__)

@app.route('/getScript/<packageName>')
def getScript(packageName: str):
    print(os.path.realpath("."))
    return load(open(f"./GetLocalPackages/Data/{packageName}.json", encoding='utf-8'))


@app.route('/getast/<pystr>')
def getAST(pystr: str):
    # decodes http-encoded pystr first
    pystr = unquote(pystr)
    try:
        return ast.dump(ast.parse(pystr))
    except SyntaxError:
        return ""

if __name__ == "__main__":
    app.run(ssl_context="adhoc")

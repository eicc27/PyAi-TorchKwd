import * as vscode from 'vscode';
import { readFileSync, readdirSync } from 'fs';
import * as common from './common';
import { LineUtils } from './LineUtils';



interface PythonAutoImportToken {
    fromToken: string,
    importToken: string,
    importContentType: string
}

class PythonAutoImportProvider implements vscode.CompletionItemProvider {

    public static DATA_PATH = "C:\\Users\\13917\\test\\GetLocalPackages\\Data\\";

    public static DATA_FILES = readdirSync(this.DATA_PATH);

    private importData: any = {};

    private targetToken = "test";

    public static getValues = function getJSONValues(json: any) {
        let res: any[] = [];
        for (var k in json) {
            if (json.hasOwnProperty(k)) {
                res.push(json[k]);
            }
        }
        return res;
    }

    public searchEverywhere(kwd: string, root: any, module: string, results: PythonAutoImportToken[] = [], dirpath: string[] = [], maxsize = 1000): PythonAutoImportToken[] {
        for (var k in root) {
            let v = root[k];
            if (k.startsWith(kwd)) {
                if (results.length <= maxsize) {
                    results.push({
                        fromToken: module + '.' + dirpath.join('.'),
                        importToken: k,
                        importContentType: typeof v === "string" ? v : "module"
                    });
                }
            }
            if (typeof v !== "string")
                this.searchEverywhere(kwd, v, module, results, dirpath.concat(k), maxsize);
        }
        return results;
    }

    private getImports(document: vscode.TextDocument) {
        this.importData = {};
        let imports = LineUtils.getImports(document);
        // console.log(imports)
        // read imported files from jsons
        // search imports in DATA_FILES
        for (let i = 0; i < imports.length; i++) {
            let imp = imports[i];
            if (!PythonAutoImportProvider.DATA_FILES.includes(`${imp}.json`)) {
                console.log(`Import ${imp} is not yet known.`);
                continue;
            }
            this.importData[imp] = JSON.parse(readFileSync(PythonAutoImportProvider.DATA_PATH + `${imp}.json`, 'utf-8'));
        }
        // console.log(this.importData);
    }

    public async provideCompletionItems(document: vscode.TextDocument, position: vscode.Position, token: vscode.CancellationToken, context: vscode.CompletionContext): Promise<vscode.CompletionItem[] | vscode.CompletionList<vscode.CompletionItem> | null | undefined> {
        this.getImports(document);
        if (this.importData == {})
            return null;
        // console.log(this.importData);
        // gets the characters before
        const line = document.lineAt(position.line).text;
        const before = line.substring(0, position.character).replace(/^\s+/g, '');
        let isExpression = true;
        await common.axiosIgnoreSSL.get(`${common.LOCALHOST}/getast/${before}`).then(
            async (res) => {
                let data = String(res.data);
                // console.log(data);
                if (data.includes("value=Name(id='")) {
                    this.targetToken = data.split("value=Name(id='")[1].split("'")[0];
                }
                else 
                    isExpression = false;
            }
        );
        if (!isExpression)
            return null;
        // console.log(this.targetToken);
        const results: PythonAutoImportToken[] = [];
        for (let module in this.importData) {
            // console.log(module);
            results.push(...this.searchEverywhere(this.targetToken, this.importData[module], module,));
        }
        // console.log(results.length);
        return results.map(result => {
            if (result.fromToken.endsWith("."))
                result.fromToken = result.fromToken.substring(0, result.fromToken.length - 1);
            let completionKind = vscode.CompletionItemKind.Constant;
            switch (result.importContentType) {
                case "module":
                    completionKind = vscode.CompletionItemKind.Module;
                    break;
                case "class":
                    completionKind = vscode.CompletionItemKind.Class;
                    break;
                case "function":
                    completionKind = vscode.CompletionItemKind.Function;
                    break;
                case "variable":
                    completionKind = vscode.CompletionItemKind.Variable;
                    break;
            }
            const item = new vscode.CompletionItem(result.importToken, completionKind);
            item.detail = result.fromToken;
            item.documentation = result.fromToken;
            // adds from ... import ... at the beginning of the file
            item.additionalTextEdits = [
                vscode.TextEdit.insert(new vscode.Position(0, 0),
                    `from ${result.fromToken} import ${result.importToken}\n`)
            ];
            
            return item;
        });
    }
}

export { PythonAutoImportProvider };
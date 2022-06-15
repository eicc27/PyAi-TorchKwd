import * as vscode from 'vscode';
import { readFileSync, readdirSync } from 'fs';
import * as common from './common';
import { LineUtils } from './LineUtils';

class PyTorchNNModulesParameterProvider implements vscode.CompletionItemProvider {

    public static DATA_PATH = "C:\\Users\\13917\\test\\GetTorchNNModules\\TorchNNModules\\";

    public static DATA_FILES = readdirSync(this.DATA_PATH);

    private params: string[] = [];

    public static getData = function getJSONData() {
        let dataJSON: any = {};
        PyTorchNNModulesParameterProvider.DATA_FILES.forEach(file => {
            dataJSON[file.split('.')[0]] = (JSON.parse(readFileSync(PyTorchNNModulesParameterProvider.DATA_PATH + file, 'utf-8')));
        });
        return dataJSON;
    };

    public static DATA = this.getData();

    // detects whether the line contains a module(RNN, LSTM, GRU, ...)
    public static isAvailable(line: string): number {
        require("child_process")
        let res: number = -1;
        for (let i in PyTorchNNModulesParameterProvider.DATA_FILES) { // file: xxx.json
            let file = PyTorchNNModulesParameterProvider.DATA_FILES[i];
            res = line.indexOf(file.split(".")[0]); // get module name
            if (res != -1) {
                return res;
            }
        }
        return res
    }

    private getParametersInLine(line: string) {
    }

    public async provideCompletionItems(document: vscode.TextDocument, position: vscode.Position, token: vscode.CancellationToken, context: vscode.CompletionContext):
        Promise<vscode.CompletionItem[] | vscode.CompletionList<vscode.CompletionItem> | null | undefined> {
        let line = document.lineAt(position.line).text;
        const ModuleStart = PyTorchNNModulesParameterProvider.isAvailable(line);
        if (ModuleStart === -1)
            return null;
        // console.log(line);
        const moduleName = line.substring(ModuleStart, line.indexOf('('));
        const moduleData = PyTorchNNModulesParameterProvider.DATA[moduleName];
        let res: vscode.CompletionItem[] = [];
        if (!line.endsWith(')'))
            line += ')';
        this.params = [];
        await common.axiosIgnoreSSL.get(`${common.LOCALHOST}/getast/${line}`).then(
           async (response) => {
            let data = String(response.data);
            // console.log(data);
            if (data.includes("keywords=[")) {
                let keywords = data.split("keywords=[")[1].split(']')[0].split("keyword");
                // remove the first element
                keywords.shift();
                // console.log(keywords);
                for (let i in keywords) {
                    // console.log(keywords[i].split("(arg='")[1].split("',")[0]);
                    this.params.push(keywords[i].split("(arg='")[1].split("',")[0]);
                }
            }
           }
        );
        console.log(this.params);
        for (let argument in moduleData) {
            // filters the parameters by the line.
            if (this.params.includes(argument))
                continue;
            let details: any = moduleData[argument];
            let defaultValue = details["default"];
            let typeValue = details["type"]
            let item = new vscode.CompletionItem(argument + "=", vscode.CompletionItemKind.Variable);
            let completionString = "";
            if (typeValue === "None") {
                if (defaultValue == null) {
                    item.detail = `(kwargs) ${argument}`;
                    completionString = `${argument}=`;
                }
                else {
                    item.detail = `(kwargs) ${argument}=${defaultValue}`;
                    completionString = `${argument}=${defaultValue}`;
                }
            }
            else {
                if (defaultValue == null) {
                    item.detail = `(kwargs) ${argument}: ${typeValue}`;
                    completionString = `${argument}=`;
                }
                else {
                    item.detail = `(kwargs) ${argument}: ${typeValue}=${defaultValue}`;
                    completionString = `${argument}=${defaultValue}`;
                }
            }
            // console.log(completionString);
            item.documentation = details["description"];
            item.insertText = new vscode.SnippetString(`${completionString}`);
            res = res.concat(item);
        }
        return res;
    }
}

export { PyTorchNNModulesParameterProvider };
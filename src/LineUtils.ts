import * as vscode from 'vscode';
import * as common from './common';

class LineUtils {

    private static imports: string[] = [];

    public static getImports(document: vscode.TextDocument) {
        // get imported modules from the whole document(Python file)
        for (let i = 0; i < document.lineCount; i++) {
            // strips tabs and spaces at the beginning
            let line = document.lineAt(i).text.replace(/^\s+/g, '');
            // if empty continue
            if (line.length === 0)
                continue;
            // uses ast to parse python through server
            common.axiosIgnoreSSL.get(`${common.LOCALHOST}/getast/${line}`).then(
                async (res) => {
                    let data = String(res.data);
                    // console.log(data);
                    if (data.includes("module=")) {
                        let module = data.split("module='")[1].split("'")[0].split('.')[0];
                        if (!this.imports.includes(module))
                            this.imports.push(module);
                    }
                    else if(data.includes("Import(names=[alias(name='")) {
                        let module = data.split("Import(names=[alias(name='")[1].split("'")[0].split('.')[0];
                        if (!this.imports.includes(module))
                            this.imports.push(module);
                    }                  
                }
            ); 
        }
        return this.imports;
    }
}

export {LineUtils};
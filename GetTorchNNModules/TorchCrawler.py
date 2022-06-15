import json
from lxml import etree
from lxml import html
from urllib import request as req
from html import unescape   

TARGETS = ["RNN", "LSTM", "GRU"]

MODULE_PATH = "./GetTorchNNModules/TorchNNModules/"

class TorchNNCrawler:
    StrongStart = "<strong>"
    StrongEnd = "</strong>"
    UlStart = '<ul class="simple"'
    UlEnd = "</ul>"
    PStart = "<p>"
    PEnd = "</p>"
    Dash = "&#8211;"

    def __init__(self, moduleName: str = 'RNN') -> None:
        self.moduleName = moduleName
        self.website = f"https://pytorch.org/docs/stable/generated/torch.nn.{moduleName}.html"
        self.parametersHtml = self._crawl()
    
    def _crawl(self):
        webpage: str = req.urlopen(self.website).read().decode("utf-8")
        tree = etree.HTML(webpage)
        parametersTree = tree.xpath("//dl/dd/dl[1]/dd/ul")[0]
        res = html.tostring(parametersTree).decode("utf-8")
        # strips res from <ul class="simple"> and </ul>
        res = res.split(self.UlEnd)[0]
        return res[len(self.UlStart):]
    
    def getParameters(self) -> dict[str, dict[str, str]]:
        """
        >>> <p><strong>hidden_size</strong> – The number of features in the hidden state <cite>h</cite></p>
        {"hidden_size": "The number of features in the hidden state h"}
        """
        paragraphs = self.parametersHtml.split(self.PEnd)[:-1]  # strips tail
        res = {}
        for paragraph in paragraphs:
            p = paragraph.split(self.PStart)
            if len(p) > 1:
                p = p[-1]
            else:
                p = p[len(self.PStart):]
            param, desc = p.split(self.Dash)
            # strips param from <strong> and </strong>
            param = param[len(self.StrongStart): -(len(self.StrongEnd) + 1)]
            # print(param)
            type, desc, default = self.parseDesc(desc)
            res[param] = {
                "type": type,
                "description": desc,
                "default": default
            }
        return res
    

    @staticmethod
    # deduces the parameter type from desc and cleans HTML labels in it.
    def parseDesc(desc: str) -> tuple[str, str, str]:
        # firstly decode the html special characters in it
        desc = unescape(desc)
        # then removes the html tags
        desc = html.fromstring(desc).text_content()
        # removes \n
        desc = desc.replace("\n", " ")
        # print(desc)
        # then uses traditional string methods to try to induce the parameter type
        type: str = None
        default: str = None
        # firstly get "Default: "
        if "Default: " in desc:
            default = desc.split("Default: ")[1]
            if "True" in default or "False" in default:
                type = "bool"
            if default[0] in ["'", '"']:
                type = "str"
            if default.isdecimal():
                type = "int"
            if "." in default and default.replace(".", "").isdecimal():
                type = "float"
        # secondly search for "number"
        sentence = desc.split(".")[0].lower()
        if sentence.startswith("the number") or sentence.startswith("the size") \
            or sentence.startswith("number") or sentence.startswith("size"):
            type = "int"
        return type, desc, default


if __name__ == "__main__":
    for target in TARGETS:
        res = TorchNNCrawler(target).getParameters()
        json.dump(res, open(f"{MODULE_PATH}{target}.json", "w+"), indent=4)

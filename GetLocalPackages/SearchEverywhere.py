import json

File: dict = json.load(open("GetLocalPackages\\Data\\matplotlib.json", encoding='utf-8'))

class Res:
    def __init__(self, res: list = [], type: str = "") -> None:
        self.res = res
        self.type = type

def obscureSearching(kwd: str, scope: list[str]):
    for _, s in enumerate(scope):
        if kwd.lower() in s.lower():
            return s
    return None


def searchEverwhere(kwd: str, root: dict, res: list[Res] = [], dirpath: list[str] = []):
    '''
    example:
    {
        "a": {
            "i": {
                "m": 1
            },
            "j": {
                "n": 2
            }
        },
        "b": {
            "k": {
                "o": 1
            },
            "l": {
                "i": 2
            }
        }
    }
    >>> searchEverwhere("i", root)
    res[Res(['a', 'i'], module), Res(['b', 'l', 'i'], keyword)]
    '''
    for k, v in root.items():
        if kwd.lower() in k.lower():
            res.append(Res(dirpath + [k], v if not isinstance(v, dict) else "module"))
        if isinstance(v, dict):
            searchEverwhere(kwd, v, res, dirpath + [k])
        elif isinstance(v, list):
            for _, item in enumerate(v):
                if kwd.lower() in item.lower():
                    res.append(Res(dirpath + [k], v if not isinstance(item, dict) else "module"))
    return res
    

reses = searchEverwhere("exten", File)
for r in reses:
    print(".".join(r.res), r.type)

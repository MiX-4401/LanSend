from json import load as jsonloads

def read_json(path:str) -> dict:
    with open(path, mode="r") as f:
        return jsonloads(f)
    
    
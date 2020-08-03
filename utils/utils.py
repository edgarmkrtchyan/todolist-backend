import json

def getAppConfig():
    with open('configs/config.json') as fp:
        config_lines = fp.readline().strip()
        config_json = json.loads(config_lines)

    return config_json
import json

with open("credentials/yougurt-d4271d634d58.json") as f:
    content = json.load(f)

print(json.dumps(content))

import yaml
import json
with open("config.yaml", "r", encoding="utf-8") as fr:
    config1 = yaml.safe_load(fr)
with open("config.json", "r", encoding="utf-8") as f:
    config2 = json.load(f)

print(config1)
print(config2)
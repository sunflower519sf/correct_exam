import yaml

# 載入配置文件
with open("config.yaml", "r", encoding="utf-8") as fr:
    CONFIG = yaml.safe_load(fr)

CONFIG["read_write_log"]["log_file_name_example"] = CONFIG["read_write_log"]["log_file_name_example"].replace("%name%", "nowtime")

with open("new.yaml", "w", encoding="utf-8") as fw:
    yaml.dump(CONFIG, fw)
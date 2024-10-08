import json

with open("config.json", "r", encoding="utf-8") as config_data:
    config = json.load(config_data)
delimiter = config["read_write_csv"]["data_delimiter"]


def safe_filename(name:str):
    out = ".".join(name.replace("\\", "/").strip("/").split(".")[:-1])
    return f'{out}.csv'


def read_csv(filename):
    filename = safe_filename(filename)
    lst = {}
    with open(f'{filename}', 'r', encoding='utf-8') as csvfile:
        linedata = csvfile.readlines()
        for i in linedata:
            data = i.strip().split(delimiter)
            lst[data[0]] = eval(data[1])
    return lst

def write_dict_csv(filename, lst):
    filename = safe_filename(filename)
    with open(f'{filename}', 'w', encoding='utf-8') as csvfile:
        for i in lst:
            csvfile.write(f'{i}{delimiter}')
            csvfile.write(str(lst[i]))
            csvfile.write("\n")

def write_csv(filename, keyname, value):
    filename = safe_filename(filename)
    with open(f'{filename}', 'a', encoding='utf-8') as csvfile:
        csvfile.write(f'{keyname}{delimiter}{str(value)}\n')


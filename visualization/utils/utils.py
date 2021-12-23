import xml.etree.ElementTree as ET


def open_file(path):
    input_path = path
    try:
        with open(input_path, "rb") as input_file: 
            data = input_file.read()
    except OSError as exception:
        print(f"Couldn't load {input_path}: {exception}")
        return
    return data

def save_file_binary(data,path, overwrite=False):
    output_path = path
    mode = "xb"
    if(overwrite):
        mode="wb"
    try:
        with open(output_path, mode) as output_file:
            output_file.write(data)
    except OSError as exception:
        print(f"Couldn't load {output_path}: {exception}")
        return
    return data

def save_file_text(data,path, overwrite=False):
    output_path = path
    mode = "xt"
    if(overwrite):
        mode="wt"
    try:
        with open(output_path, mode) as output_file:
            output_file.write(data)
    except OSError as exception:
        print(f"Couldn't load {output_path}: {exception}")
        return
    return data

def read_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()
    return (tree,root)
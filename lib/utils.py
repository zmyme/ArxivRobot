import pickle
import time
import os
import re
import platform

def detect_platform():
    p = 'Unknown'
    if platform.platform().find('Windows') != -1:
        p = 'Windows'
    elif platform.platform().find('Linux') != -1:
        p = 'Linux'
    return p

def ensure_dir_exist(directory, show_info = True):
    exist = os.path.isdir(directory)
    if not exist:
        print('directory', directory, ' not found, creating...')
        os.mkdir(directory)

def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, " ", title)  # 替换为空格
    return new_title

def list2csv(l):
    csv = ''
    for item in l:
        csv += str(item) + ','
    csv = csv[:-1]
    return csv

def clean_text(string):
    if string is None:
        return ''
    while '\n' in string:
        string = string.replace('\n', ' ')
    splits = clean_split(string)
    string = ''
    for split in splits:
        string += split + ' '
    string = string[:-1]
    return string

def clean_split(string, delimiter=' '):
    sub_strs = string.split(delimiter)
    splits = []
    for sub_str in sub_strs:
        if sub_str is not '':
            splits.append(sub_str)
    return splits

def remove_blank_in_endpoint(string):
    length = len(string)

    first_index = 0
    for i in range(length):
        if is_blank(string[first_index]):
            first_index += 1
        else:
            break

    last_index = length - 1
    for i in range(length):
        if is_blank(string[last_index]):
            last_index -= 1
        else:
            break
    last_index += 1
    return string[first_index:last_index]

def is_blank(ch):
    blank_ch = [' ', '\t', '\n']
    if ch in blank_ch:
        return True
    else:
        return False

def dict_to_arrtibute_string(attributes):
    string = ''
    for key in attributes:
        string += key + '=\"{0}\";'.format(str(attributes[key]))
    return string

def attribute_string_to_dict(attrs):
    attr_dict = {}
    for attr in attrs:
        attr_dict[attr[0]] = attr[1]
    return attr_dict

def save_python_object(obj, save_path):
    with open(save_path, 'wb') as file:
        pickle.dump(obj, file)

def load_python_object(path):
    with open(path, 'rb') as file:
            return pickle.load(file)

def delete_n(string):
    while '\n' in string:
        string = string.replace('\n', ' ')
    return string

def remove_additional_blank(string):
    words = string.split(' ')
    string = ''
    for word in words:
        if word is not '':
            string += word + ' '
    return string[:-1]

def formal_text(text):
    text = delete_n(text)
    text = remove_additional_blank(text)
    return text

def float2str(f, precision=2):
    f = str(f)
    f_base = f[:f.find('.') + precision]
    return f_base

# ========== time realted operation ========== #

def str_day():
    day = time.strftime("%Y-%m-%d", time.localtime())
    return day

def time2str(t):
    localtime = time.localtime(int(t))
    return str_time(localtime)

def str_time(local_time = None):
    if local_time is None:
        local_time = time.localtime()
    day = time.strftime("%Y-%m-%d-%Hh-%Mm-%Ss)", local_time)
    return day

if __name__ == '__main__':
    print(str_day())

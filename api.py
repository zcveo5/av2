import io
import os
import random

key = {'\n': ':', 'q': 'y', 'w': 'h', 'e': 'F', 'r': 'M', 't': '/', 'y': '5', 'u': '0', 'i': '~', 'o': 'D', 'p': '|', 'a': 'n', 's': 'C', 'd': 'm', 'f': 'z', 'g': 'R', 'h': '(', 'j': '4', 'k': 'v', 'l': '.', 'z': '3', 'x': ';', 'c': 's', 'v': 'q', 'b': '2', 'n': '*', 'm': '6', 'Q': '[', 'W': 't', 'E': '}', 'R': 'Q', 'T': 'a', 'Y': '9', 'U': 'J', 'I': ' ', 'O': 'E', 'P': '&', 'A': '7', 'S': '!', 'D': '"', 'F': 'V', 'G': 'd', 'H': '%', 'J': 'X', 'K': '#', 'L': ')', 'Z': 'r', 'X': '8', 'C': 'Y', 'V': 'S', 'B': 'i', 'N': 'O', 'M': 'e', '1': '@', '2': 'N', '3': '\n', '4': 'o', '5': '?', '6': '1', '7': 'W', '8': 'A', '9': '_', '0': 'c', '~': 'w', '!': '>', '@': 'p', '#': '^', '$': 'T', '%': ',', '^': 'P', '&': 'H', '*': 'f', '(': 'b', ')': '=', '_': 'U', '+': 'G', '-': 'u', '=': 'l', '?': '{', '>': 'L', '<': ']', ',': 'g', '.': 'B', '/': '+', '|': '$', '"': 'x', "'": "'", '[': 'I', ']': '-', '{': 'k', '}': 'K', ':': 'j', ';': 'Z', ' ': '<'}

class ArchFile:
    def __init__(self, file, mode):
        self.file = open(file, mode)
        try:
            self.file_text = self.file.read()
        except io.UnsupportedOperation:
            pass

    def create_structure(self, struc):
        self.file.write(f'##[STRUCTURE\n{struc}')
        self.file.flush()

    def create_handlers(self, file_data):
        self.file.write(f'\n\n##[HANDLERS')
        counter = 0
        for i in file_data:
            self.file.write(f'\nHANDLER>[{counter}]\n{i}')
            counter += 1
        self.file.flush()

    def create_f_handlers(self, file_data):
        self.file.write(f'\n\n##[F_HANDLERS')
        counter = 0
        for i in file_data:
            self.file.write(f'\nF_HANDLER>[{counter}]\n{i}')
            counter += 1
        self.file.flush()

    def load_structure(self):
        data = {}
        structure_raw = self.file_text.split('##[')[1]
        structure_raw = structure_raw.split('\n')
        for i in structure_raw:
            if i not in ['STRUCTURE', '', ' ']:
                data.update({i.split('=')[0]: i.split('=')[1]})
        return data

    def load_handlers(self, c):
        handlers_raw = self.file_text.split('##[')[2].split('\n')
        handlers = []
        for i in handlers_raw:
            if i not in ['HANDLERS', '', ' '] and 'HANDLER>' not in i:
                handlers.append(decrypt(i, c))
        return handlers

    def load_f_handlers(self, c):
        handlers_raw = self.file_text.split('##[')[3].split('\n')
        handlers = []
        for i in handlers_raw:
            if i not in ['F_HANDLERS', '', ' '] and 'F_HANDLER>' not in i:
                handlers.append(decrypt(i, c))
        return handlers

def archive(**kw):
    k = random.randint(100, 999)
    file = ArchFile('2', 'w')
    handlers = []
    f_handlers = []
    for i in kw['files']:
        handlers.append(encrypt(open(i, 'r').read(), k))
    for i in kw['folders']:
        for j in kw['folders'][i]:
            try:
                f_handlers.append(encrypt(open(f"{i}/{j}", 'r', encoding='utf-8').read(), k))
            except UnicodeDecodeError:
                try:
                    f_handlers.append(encrypt(open(f"{i}/{j}", 'r', encoding='windows-1251').read(), k))
                except UnicodeDecodeError:
                    f_handlers.append(encrypt('UnicodeDecodeError', k))
    files_inf = []
    files_inf_help = {}
    for i in kw['folders']:
        for j in kw['folders'][i]:
            try:
                files_inf.append(encrypt(open(f"{i}/{j}", 'r').read(), k))
                files_inf_help.update(
                    {i + '/' + j: files_inf.index(encrypt(open(f"{i}/{j}", 'r').read(), k))})
            except UnicodeDecodeError:
                try:
                    files_inf.append(encrypt(open(f"{i}/{j}", 'r', encoding='windows-1251').read(), k))
                    files_inf_help.update({i + '/' + j: files_inf.index(encrypt(open(f"{i}/{j}", 'r', encoding='windows-1251').read(), k))})
                except UnicodeDecodeError:
                    files_inf.append(encrypt('UnicodeDecodeError', k))
    folders = {}
    for i in files_inf_help:
        dir_name = i.split('/')[0]
        tmp = i.split('/').copy()
        tmp.pop(0)
        path_to_file = '/'.join(tmp)
        if dir_name not in folders:
            folders.update({dir_name: [path_to_file + f'>{files_inf_help[i]}']})
        else:
            folders[dir_name].append(path_to_file + f'>{files_inf_help[i]}')
    structure = f'FilesIn={kw['root']}\nFolders={folders}\nFilesInRoot={kw['files']}\nKey={k}'


    file.create_structure(structure)
    file.create_handlers(handlers)
    file.create_f_handlers(files_inf)
    

def un_archive():
    file = ArchFile('2', 'r')
    structure = file.load_structure()
    handlers = file.load_handlers(int(structure['Key']))
    f_handlers = file.load_f_handlers(int(structure['Key']))
    for i in range(len(handlers)):
        with open(eval(structure['FilesInRoot'])[i], 'w'):
            pass
        open(eval(structure['FilesInRoot'])[i], 'w').write(handlers[i])
    for i in eval(structure['Folders']):
        os.makedirs(i, exist_ok=True)
        for j in eval(structure["Folders"])[i]:
            try:
                with open(f'{structure["FilesIn"]}/{i}/{j.split(">")[0]}', 'w') as fl:
                    fl.write(f_handlers[int(j.split(">")[1])])
            except FileNotFoundError:
                tmp = j.split("/").copy()
                tmp.pop(len(tmp) - 1)
                tmp = '/'.join(tmp)
                os.makedirs(f'{structure["FilesIn"]}/{i}/{tmp}')
                with open(f'{structure["FilesIn"]}/{i}/{tmp}/{j.split(">")[0].replace(tmp + "/", '')}', 'w') as fl:
                    fl.write(f_handlers[int(j.split(">")[1])])


def dict_encrypt(data, salt):
    out = []
    for sym in data:
        try:
            out.append(salt[sym])
        except KeyError:
            salt.update({sym: "?"})
            out.append(salt[sym])
    return ''.join(out)


def dict_decrypt(data, salt):
    out = []
    k_list = list(salt.keys())
    v_list = list(salt.values())
    for sym in data:
        try:
            out.append(k_list[v_list.index(sym)])
        except ValueError:
            out.append('?')
    return ''.join(out)


def encrypt(data, c):
    for _ in range(c):
        data = dict_encrypt(data, key)
    return data


def decrypt(data, c):
    for _ in range(c):
        data = dict_decrypt(data, key)
    return data

if __name__ == '__main__':
    #archive(root='.', folders={'data': ['msgr.py', 'run.py'], 'data/data': ['base_data.json', 'btaeui.py', 'DATA.NC'], 'data/data/locale/ru': ['locale.cfg'], 'data/data/locale/en': ['locale.cfg'], 'data/data/theme': ['hh.theme', 'night.theme', 'light.theme'], 'data/plugins/btac': ['auth.py', 'metadata.json', 'mod.py'], 'data/plugins/core': ['metadata.json', 'mod.py']}, files=[])
    un_archive()

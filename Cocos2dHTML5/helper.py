#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sublime
import os
import hashlib
import sys
import codecs
import shutil

# read content from a file
def readFile(path):
    f = codecs.open(path, "r", "utf-8")
    content = f.read()
    f.close()
    return content

# write content to a file
def writeFile(path, content):
    f = codecs.open(path, "w", "utf-8")
    f.write(content)
    f.close()

def create_directory(directory):
    os.makedirs(directory)

# check file extention
def checkFileExt(file,ext):
    ext1 = os.path.splitext(file)[1][1:]
    if ext1 == ext:
        return True
    else:
        return False

def line_no_in_text(file, text):
    with open(file) as myFile:
        for num, line in enumerate(myFile, 1):
            if text in line:
                return num
    return 0

# 
def files_in_dir(dir):
    files_list = []
    for root, dirs, files in os.walk(dir):
        for name in files:
            source_file = os.path.join(root, name)
            files_list.append(source_file)
            ext = os.path.splitext(source_file)[1]
    return files_list

def md5(str):
    return hashlib.md5(str.encode(sys.getfilesystemencoding())).hexdigest()

def isST3():
    return sublime.version()[0] == '3'

def loadSettings(name):
    return sublime.load_settings(name+".sublime-settings")

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

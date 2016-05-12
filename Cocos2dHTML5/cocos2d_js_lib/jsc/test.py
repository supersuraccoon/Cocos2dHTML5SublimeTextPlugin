#!/usr/bin/python
import os
import codecs

print("test.py called")

f = codecs.open("", "r", "utf-8")
content = f.read()
print(content)
f.close()
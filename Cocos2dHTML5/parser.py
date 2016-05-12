#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Author: supersuraccoon
# 
import codecs
import re
import os
import os.path

skip_files = ['CCClass.js']

CC_TYPE_UNKNOWN = 0
CC_TYPE_CONSTANT = 1
CC_TYPE_CLASS = 2
CC_TYPE_CLASS_FUNCTION = 3
CC_TYPE_INSTANCE_FUNCTION = 4
CC_TYPE_OVERRIDE = 5

class CCAPIParser:
    def __init__(self, input_dir, output_file):
        self.input_dir = input_dir
        self.output_file = output_file
        self.cc_instance_functions = {}
        self.cc_class_functions = {}
        self.cc_classes = []
        self.cc_constants = []
        self.definitions = []

    def parse_segment_type(self, segment):
        match = re.compile(r".*@override.*").search(segment)
        if match:
            return CC_TYPE_OVERRIDE
        match1 = re.compile(r".*@constant.*").search(segment)
        match2 = re.compile(r".*@type.*").search(segment)
        if match1 or match2:
            # print 'constant'
            return CC_TYPE_CONSTANT
        else:
            match3 = re.compile(r".*@class.*").search(segment)
            if match3:
                #print 'class'
                return CC_TYPE_CLASS
            else:
                match4 = re.compile(r".* = function.*").search(segment)
                if match4:
                    #print 'class function'
                    return CC_TYPE_CLASS_FUNCTION
                else:
                    match5 = re.compile(r".*@return.*").search(segment)
                    match6 = re.compile(r".*@param.*").search(segment)
                    if match5 or match6:
                        #print 'instance function'
                        return CC_TYPE_INSTANCE_FUNCTION
        #print 'error type'
        return CC_TYPE_UNKNOWN

    def parse_function_params(self, content):
        params = []
        param_list = re.findall('.*@param.*', content, re.M)
        # print param_list
        for param_content in param_list:
            match = re.compile('.*@param {(.*?)}').search(param_content)
            #print param_content
            if match:
                param_type = match.group(1)
                match = re.compile('.*@param\s?{.*?}\s?(.*?\s)').search(param_content)
                param_name = match.group(1).replace('\r', '').replace(' ', '').replace('\"', '\'')
            else:
                param_type = ''
                match = re.compile('.*@param \s?(.*?\s)').search(param_content)
                param_name = match.group(1).replace('\r', '').replace(' ', '').replace('\"', '\'')
            params.append([param_type, param_name])
            #print '--------------'
        return params

    def format_params(self, params):
        p_count = 1
        p_list = []
        for param in params:
            p = '${%d:%s %s}' % (p_count, param[0], param[1])
            p_list.append(p)
            p_count += 1
        return ', '.join(p_list)

    def parse(self, content, file_name, file_path):
        self.class_name = ''
        for x in re.findall(r"(^(?P<identation> *)/\*\*.*$(\r?\n?^(?P=identation) * .*$)*\r?\n?(?P=identation) \*/\r?\n?^.*$)", content, re.M):
            segment = x[0]
            cc_type = self.parse_segment_type(segment)
            # print(segment)
            # print(cc_type)
            if cc_type == CC_TYPE_CLASS_FUNCTION:
                match = re.compile('\s*(cc\..*) = function.*').search(segment)
                function_name = ''
                if match:
                    function_name = match.group(1).replace(' ', '')
                    self.definitions.append([str(function_name), str(self.class_name), file_path, str(match.group(0).replace("\r", "").replace("\n", ""))])
                    if function_name[0] != '_' and not function_name in self.cc_class_functions:
                        # print(function_name)
                        self.cc_class_functions[function_name] = self.parse_function_params(segment)
                else:
                    print('CC_TYPE_CLASS_FUNCTION error: \n' + segment.encode('utf-8') + '\n')
            elif cc_type == CC_TYPE_INSTANCE_FUNCTION:
                match = re.compile('\s*(.*):\s?function.*').search(segment)
                if match:
                    function_name = match.group(1).replace(' ', '')
                    self.definitions.append([str(function_name), str(self.class_name), file_path, str(match.group(0).replace("\r", "").replace("\n", ""))])
                    if function_name[0] != '_' and not function_name in self.cc_instance_functions:
                        # print(function_name)
                        self.cc_instance_functions[function_name] = self.parse_function_params(segment)
                else:
                    print('CC_TYPE_INSTANCE_FUNCTION error: \n' + segment.encode('utf-8') + '\n')
            elif cc_type == CC_TYPE_CONSTANT:
                match = re.compile('\s*(cc\..*) = .*;').search(segment)
                constant_name = ''
                if match:
                    constant_name = match.group(1).replace(' ', '')
                    if not constant_name in self.cc_constants:
                        self.cc_constants.append(constant_name)
                        #print constant_name
                else:
                    print('CC_TYPE_CONSTANT error: \n' + segment.encode('utf-8') + '\n')
            elif cc_type == CC_TYPE_CLASS:
                # match = re.compile('\s*(cc\..*) = cc\..*').search(segment)
                class_list = re.findall('(\s*(cc\..*) = cc\..*)', segment)
                if len(class_list) > 0:
                # if match:
                    # self.class_name = match.group(1).replace(' ', '')
                    self.class_name = class_list[len(class_list) - 1][1].replace(' ', '')
                    if not self.class_name in self.cc_classes:
                        self.cc_classes.append(self.class_name)
                        self.definitions.append([str(self.class_name), str(self.class_name), file_path, str(class_list[len(class_list) - 1][0].replace('\r', '').replace('\n', ''))])
                        # print(self.class_name)
                else:
                    print('CC_TYPE_CLASS error: \n' + segment.encode('utf-8') + '\n')
            else:
                print('UNKONW TYPE: \n' + segment + '\n')
            # print('----------------\n')

    def generate_config_file(self):
        output = codecs.open(self.output_file, "w", "utf-8")
        contents_to_write = ''
        contents_to_write += '{\n'
        contents_to_write += '  \"scope\": \"source.js\",\n'
        contents_to_write += '  \"completions\":\n'
        contents_to_write += '  [\n'
        # start write trigger
        # functions
        for function_name, params in self.cc_instance_functions.items():
            # print api
            contents = '%s(%s)' % (function_name, self.format_params(params))
            contents_to_write += '      {\"trigger\": \"%s\", \"contents\": \"%s\" },\n' % (function_name, contents)
        # functions
        for function_name, params in self.cc_class_functions.items():
            # print api
            contents = '%s(%s)' % (function_name, self.format_params(params))
            # if contents.count('.') > 1:
            #     contents = contents.replace('cc.', '')
            contents_to_write += '      {\"trigger\": \"%s\", \"contents\": \"%s\" },\n' % (function_name, contents)
        # class
        for class_name in self.cc_classes:
            contents_to_write += '      {\"trigger\": \"%s\", \"contents\": \"%s\" },\n' % (class_name, class_name)
        # constant
        for constant_name in self.cc_constants:
            contents_to_write += '      {\"trigger\": \"%s\", \"contents\": \"%s\" },\n' % (constant_name, constant_name)
        contents_to_write = contents_to_write[:-2]
        contents_to_write += '\n'
        contents_to_write += '  ]\n'
        contents_to_write += '}\n'
        output.writelines(contents_to_write)
        output.close()

    def remove_empty_lines(self, content):
        new_contents = []
        for line in content:
            if not line.strip():
                continue
            else:
                new_contents.append(line)
        return ''.join(new_contents)

    def generate_definition_file(self):
        output = open("definition.py", "w")
        buffers = 'data="""%s"""' % self.definitions
        buffers = buffers.replace("'", "\"").replace("\\\\", "/")
        output.write(buffers)
        output.close()

    def generate_auto_completions(self):
        for root, dirs, files in os.walk(self.input_dir):
            for name in files:
                if name in skip_files:
                    continue
                source_file = os.path.join(root, name)
                ext = os.path.splitext(source_file)[1]
                if ext == '.js':
                    print('------ %s begin ------'  % source_file)
                    input = codecs.open(source_file, "r", "utf-8")
                    self.parse(self.remove_empty_lines(input.readlines()), os.path.basename(os.path.splitext(name)[0]), source_file.replace(COCOS2D_HTML5_ROOT, ''))
                    input.close()
                    print('------ %s end ------'  % source_file)
                else:
                    print('skipped: ' + source_file)
        self.generate_config_file()
        self.generate_definition_file()

COCOS2D_HTML5_ROOT = "/Users/supersuraccoon/Desktop/Cocos2d-html5_develop_tutorial/game_engine/Cocos2d-html5-v2.2.2/"

if __name__=="__main__":
    CCAPIParser(COCOS2D_HTML5_ROOT + "cocos2d", "cocos2d_js_lib/auto_completion/cocos2d.sublime-completions").generate_auto_completions()
    # import json
    # import definition
    # print(definition.data)
    # print(json.loads(definition.data))

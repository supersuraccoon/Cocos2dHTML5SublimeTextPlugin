#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Author: supersuraccoon
# 
import sublime
import sublime_plugin
import functools
import os
import datetime
import json
import re
import subprocess
import sys
import time
import codecs
import webbrowser

try:
    import helper
    import definition
except ImportError:
    from . import helper
    from . import definition

FILE_TEMPLATE_PATH = "/Cocos2dJSDev/cocos2d_js_lib/template/file"
PROJECT_TEMPLATE_PATH = "/Cocos2dJSDev/cocos2d_js_lib/template/project"

# init plugin,load definitions
def init():
    global TEMP_PATH
    # addChild
    TEMP_PATH = sublime.packages_path() + "/User/Cocos2dJSDev.cache"
    global DEFINITION_LIST
    DEFINITION_LIST = json.loads(definition.data)
    global RESOURCE_LIST
    RESOURCE_LIST = []

def check_root():
    settings = helper.loadSettings("Cocos2dJSDev")
    cocos2d_html5_root = settings.get("cocos2d_html5_root", "")
    if len(cocos2d_html5_root) == 0:
        return False
    return True

class NewJsFileCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        self.window.run_command("hide_panel")
        self.file_dir = dirs[0]
        self.template_files = helper.files_in_dir(sublime.packages_path() + FILE_TEMPLATE_PATH)
        # list all templates name
        self.template_names = [os.path.basename(x) for x in self.template_files]
        select_template_done = functools.partial(self.select_template_done)
        self.window.show_quick_panel(self.template_names, select_template_done)

    def select_template_done(self, index):
        if index == -1:
            return
        self.selected_template = self.template_files[index]
        input_filename_done = functools.partial(self.input_filename_done, self.file_dir)
        v = self.window.show_input_panel(
            "File Name:", "untitled" + ".js", input_filename_done, None, None)
        v.sel().clear()

    def input_filename_done(self, path, name):
        filePath = os.path.join(path, name)
        print(filePath)
        if os.path.exists(filePath):
            sublime.error_message("Unable to create file, file exists.")
        else:
            # save
            file_name = os.path.basename(os.path.splitext(name)[0])
            template_content = helper.readFile(self.selected_template)
            template_content = template_content.replace("Template", file_name[0].upper() + file_name[1:])
            template_content = template_content.replace("template", file_name[0].lower() + file_name[1:])
            helper.writeFile(filePath, template_content)
            v = sublime.active_window().open_file(filePath)
            # done
            sublime.status_message("js file create done!")
            sublime.message_dialog("js file create done!")

    def is_enabled(self, dirs):
        return len(dirs) == 1

class RunInBrowserCommand(sublime_plugin.WindowCommand):
    def run(self, files):
        # list all browsers
        self.target_file = files[0]
        self.browsers = helper.loadSettings("Cocos2dJSDev").get("browsers")
        self.browser_names = []
        for browser_name in self.browsers.keys():
            self.browser_names.append(browser_name)
        # list all browser name
        select_browser_done = functools.partial(self.select_browser_done)
        self.window.show_quick_panel(self.browser_names, select_browser_done)

    def select_browser_done(self, index):
        if index == -1:
            return
        selected_browser = self.browsers.get(self.browser_names[index])
        if not selected_browser or selected_browser == "":
            sublime.error_message("Browser not set!")
        else:
            # is local server set
            local_server_path = helper.loadSettings("Cocos2dJSDev").get("local_server_path")
            print(selected_browser)
            if local_server_path and local_server_path != "":
                self.target_file = local_server_path + "/" + os.path.basename(self.target_file)
            webbrowser.get(selected_browser + " %s").open_new_tab(self.target_file)

    def is_enabled(self, files):
        if len(files) != 1:
            return False
        if not files[0].endswith(".html"):
            return False
        return True

class CreateDepolyFolderCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        self.window.run_command("hide_panel")
        self.target_directory = dirs[0] + '/' + "deploy"
        if os.path.exists(self.target_directory):
            sublime.error_message(self.target_directory + " exists")
        else:
            helper.create_directory(self.target_directory)
            self.create_ant_folder()
            self.create_jsc_folder()
            sublime.message_dialog("create deploy folder done!")

    def create_ant_folder(self):
        ant_folder = self.target_directory + '/' + 'ant'
        helper.create_directory(ant_folder)
        # create build.xml
        build_file = sublime.packages_path() + "/Cocos2dJSDev/cocos2d_js_lib/ant/build.xml"
        build_content = helper.readFile(build_file)
        build_content = build_content.replace("%MODE%", helper.loadSettings("Cocos2dJSDev").get("ant").get("mode"))
        build_content = build_content.replace("%DEBUG%", helper.loadSettings("Cocos2dJSDev").get("ant").get("debug"))
        build_content = build_content.replace("%OUTPUT.js%", helper.loadSettings("Cocos2dJSDev").get("ant").get("output"))
        build_content = build_content.replace("%COMPLIER_JAR_PATH%", sublime.packages_path() + "/Cocos2dJSDev/cocos2d_js_lib/ant")
        build_content = build_content.replace("%COCOS2D_ROOT_PATH%", helper.loadSettings("Cocos2dJSDev").get("cocos2d_html5_root"))
        helper.writeFile(ant_folder + "/build.xml", build_content)
        # create cocos2d_extern.js
        cocos2d_externs_file = sublime.packages_path() + "/Cocos2dJSDev/cocos2d_js_lib/ant/cocos2d_externs.js"
        cocos2d_externs_content = helper.readFile(cocos2d_externs_file)
        helper.writeFile(ant_folder + "/cocos2d_externs.js", cocos2d_externs_content)

    def create_jsc_folder(self):
        jsc_folder = self.target_directory + '/' + 'jsc'
        helper.create_directory(jsc_folder)
        helper.create_directory(jsc_folder + '/cocos2d_js')
        helper.copytree(sublime.packages_path() + "/Cocos2dJSDev/cocos2d_js_lib/jsc/cocos2d_js", jsc_folder + '/cocos2d_js')
        # create complier_config.json
        complier_config_file = sublime.packages_path() + "/Cocos2dJSDev/cocos2d_js_lib/jsc/compiler_config.json"
        complier_config_content = helper.readFile(complier_config_file)
        helper.writeFile(jsc_folder + "/complier_config.json", complier_config_content)
        # create generate_jsc.py
        generate_jsc_file = sublime.packages_path() + "/Cocos2dJSDev/cocos2d_js_lib/jsc/generate_jsc.py"
        generate_jsc_content = helper.readFile(generate_jsc_file)
        generate_jsc_content = generate_jsc_content.replace("%BINDING_JS_FOLDER%", sublime.packages_path() + "/Cocos2dJSDev/cocos2d_js_lib/jsc/bindings")
        generate_jsc_content = generate_jsc_content.replace("%BIN_EXE_PATH%", sublime.packages_path() + "/Cocos2dJSDev/cocos2d_js_lib/jsc/bin/jsbcc")
        helper.writeFile(jsc_folder + "/generate_jsc.py", generate_jsc_content)

    def is_enabled(self, dirs):
        if len(dirs) == 1 and os.path.basename(dirs[0]) != "deploy":
            return True
        return False

class RunAntCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        self.target_directory = dirs[0]
        ant = "ant";
        if sys.platform.startswith('win32'):
            ant = "ant.bat";
        cmd = {
                'cmd': [ant, "-file", self.target_directory + "/ant/build.xml"],
                'working_dir': sublime.packages_path() + "/Cocos2dJSDev/cocos2d_js_lib/ant/"
        }
        self.window.run_command("exec", cmd);
        
    def is_enabled(self, dirs):
        if len(dirs) == 1 and os.path.basename(dirs[0]) == "deploy":
            return True
        return False

class CompileJscCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        self.target_directory = dirs[0]
        sublime.active_window().open_file(self.target_directory + "/jsc/generate_jsc.py")
        cmd = { 
            'cmd': ["python", self.target_directory + "/jsc/generate_jsc.py"]
        }
        self.window.run_command("exec", cmd);
        
    def is_enabled(self, dirs):
        if len(dirs) == 1 and os.path.basename(dirs[0]) == "deploy":
            return True
        return False    

class CcGotoDefinitionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # select text
        sel = self.view.substr(self.view.sel()[0])
        if len(sel) == 0:
            return
        # find all match file
        self.matchList = []
        showList = []

        for item in DEFINITION_LIST:
            if item[0] == sel:
                self.matchList.append(item)
                showList.append(item[1])
        if len(self.matchList) == 0:
            sublime.error_message("Can not find definition '%s'"%(sel))
        elif len(self.matchList) == 1:
            src_file = helper.loadSettings("Cocos2dJSDev").get("cocos2d_html5_root") + "/" + self.matchList[0][2]
            line_no = helper.line_no_in_text(src_file, self.matchList[0][3])
            self.view.window().open_file(src_file + ":" + str(line_no), sublime.ENCODED_POSITION)
        else:
            # multi match
            on_done = functools.partial(self.on_done)
            self.view.window().show_quick_panel(showList, on_done)
        
    def on_done(self, index):
        if index == -1:
            return
        item = self.matchList[index]
        src_file = helper.loadSettings("Cocos2dJSDev").get("cocos2d_html5_root") + "/" + item[2]
        line_no = helper.line_no_in_text(src_file, item[3])
        self.view.window().open_file(src_file + ":" + str(line_no), sublime.ENCODED_POSITION)
        
    def is_enabled(self):
        return True
        #return helper.checkFileExt(self.view.file_name(), "js")

    def is_visible(self):
        return self.is_enabled()

class CreateCocosProjectCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        self.target_directory = dirs[0]
        helper.copytree(sublime.packages_path() + PROJECT_TEMPLATE_PATH, self.target_directory)
        
    def is_enabled(self, dirs):
        return len(dirs) == 1

class UpdateResourceListCommand(sublime_plugin.WindowCommand):
    def run(self, files):
        self.target_file = files[0]
        resource_content = helper.readFile(self.target_file)
        resources = re.findall(r"\s*{src:\s*(.*)}", resource_content)
        # print param_list
        del RESOURCE_LIST[:]
        for resource in resources:
            RESOURCE_LIST.append(resource)
        sublime.message_dialog("Update Resource List Done!")
        
    def is_enabled(self, files):
        if len(files) != 1:
            return False
        if os.path.basename(files[0]) != "resource.js":
            return False
        return True

class CcResourceListCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.edit = edit
        on_done = functools.partial(self.on_done)
        self.view.window().show_quick_panel(RESOURCE_LIST, on_done)

    def on_done(self, index):
        if index == -1:
            return
        self.view.run_command("cc_insert", { "arg" : RESOURCE_LIST[index]});
        
    def is_enabled(self):
        return helper.checkFileExt(self.view.file_name(), "js")

    def is_visible(self):
        return self.is_enabled()

class CcInsertCommand(sublime_plugin.TextCommand):
    def run(self, edit, arg):
        self.view.insert(edit, self.view.sel()[0].begin(), arg)
    
    def is_enabled(self):
        return True

    def is_visible(self):
        return False

# st3
def plugin_loaded():
    sublime.set_timeout(init, 200)

# st2
if not helper.isST3():
    init()


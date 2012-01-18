import sublime, sublime_plugin
import os, sys
import thread
import subprocess
import functools

class DirectorySettingsEventListener(sublime_plugin.EventListener):
    def on_load(self, view):
        if view.settings().get('use_directory_settings'):
            pass

    
import sublime, sublime_plugin
import os
import os.path
import sys
import thread
import subprocess
import functools
import json

merged_settings_cache = {"/": {}}

# See README for top-level TODOs.
# The most obvious TODO here is to stop using @classmethod everywhere and
# structure things more sanely. I couldn't find documentation, however, on
# (1) how to properly instantiate sublime plugin commands, and 
# (2) how to manage global data (like caches) for sublime plugins
# ...leading to this less than ideal whatnot.

class ClearDirectorySettingsCacheCommand(sublime_plugin.ApplicationCommand):
    """Clear out the cache, presumably because something changed."""
    @classmethod
    def clear_cache(cls):
        global merged_settings_cache
        merged_settings_cache = {"/": {}}

    def run(self):
        ClearDirectorySettingsCacheCommand.clear_cache(cls)

class ReloadDirectorySettingsCommand(sublime_plugin.ApplicationCommand):
    """Clear out the cache and reload settings for all views in all windows."""
    def run(self):
        ClearDirectorySettingsCacheCommand.clear_cache()
        for window in sublime.windows():
            for view in window.views():
                DirectorySettingsEventListener.apply_directory_settings(view)

class DirectorySettingsEventListener(sublime_plugin.EventListener):
    SETTINGS_FILE = ".sublime-settings"

    @classmethod
    def absolute_directory(cls, file_name):
        return os.path.abspath(os.path.dirname(file_name))

    @classmethod
    def parent_directory(cls, directory):
        return os.path.dirname(directory)

    @classmethod
    def is_root_directory(cls, directory):
        return cls.parent_directory(directory) == directory

    @classmethod
    def get_settings_for_directory(cls, directory):
        """Return settings, if any, strictly for this directory."""
        file_name = os.path.join(directory, cls.SETTINGS_FILE)
        settings = {}
        if os.path.exists(file_name):
            with open(file_name) as f:
                try:
                    settings = json.loads(f.read())
                except Exception:
                    settings = {}
        return settings

    @classmethod
    def get_merged_settings_for_directory(cls, directory):
        """Return settings merged from the root down for this directory."""
        global merged_settings_cache
        settings = merged_settings_cache.get(directory)
        merged_settings = None
        if settings is None:
            settings = cls.get_settings_for_directory(directory)
            if not cls.is_root_directory(directory):
                parent_directory = cls.parent_directory(directory)
                parent_merged_settings = cls.get_merged_settings_for_directory(parent_directory)
                merged_settings = dict(parent_merged_settings.items() + settings.items())
        if merged_settings is None:
            merged_settings = settings
        assert (merged_settings is not None)            
        merged_settings_cache[directory] = merged_settings
        return merged_settings

    @classmethod
    def apply_directory_settings(cls, view):
        directory = cls.absolute_directory(view.file_name())
        settings = cls.get_merged_settings_for_directory(directory)
        for name, value in settings.iteritems():
            view.settings().set(name, value)

    def on_load(self, view):
        if view.settings().get("use_directory_settings"):
            DirectorySettingsEventListener.apply_directory_settings(view)




    
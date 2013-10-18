import sublime, sublime_plugin
import os
import json


SETTINGS_FILE = '.sublime-settings'
DIRECTORY_SETTINGS_FLAG = 'directory_settings'
ERASE_MARK = '#ERASE#'

# Global to keep a reference to the currently active DirectorySettings
instance = None


class DirectorySettings:
    """ Holds all the logic to apply per directory settings to a view
    """

    def __init__(self):
        self.reset()

    def _load(self, directory):
        """Return settings, if any, strictly for this directory."""
        try:
            fname = os.path.join(directory, SETTINGS_FILE)
            with open(fname) as f:
                settings = json.loads(f.read())
        except Exception:
            settings = {}

        return settings

    def _get_directory(self, directory):
        """ Return settings merged from the root down for this directory.
        """
        if directory not in self._cache:
            settings = self._load(directory)
            # Traversing to the parent directory if any
            parent = os.path.dirname(directory)
            if parent != directory:
                parent_settings = self._get_directory(parent)
                # TODO: For nested structures shouldn't we do a deepcopy and update?
                merged_settings = parent_settings.copy()
                merged_settings.update(settings)
                settings = merged_settings

            self._cache[directory] = settings

        return self._cache[directory]

    def get_settings(self, fname):
        directory = os.path.abspath(os.path.dirname(fname))
        return self._get_directory(directory)

    def reset(self):
        self._cache = {'/': {}}

    def apply(self, view):
        if not view.settings().get(DIRECTORY_SETTINGS_FLAG, True):
            return

        overrides = self.get_settings(view.file_name())
        #print(overrides)
        settings = view.settings()
        for name, value in overrides.items():
            if value == ERASE_MARK:
                if settings.has(name):
                    settings.erase(name)
            else:
                settings.set(name, value)


class ReloadDirectorySettingsCommand(sublime_plugin.ApplicationCommand):
    """Clear out the cache and reload settings for all views in all windows."""
    def run(self):
        global instance
        instance.reset()
        for window in sublime.windows():
            for view in window.views():
                finder.apply(view)


class DirectorySettingsEventListener(sublime_plugin.EventListener):
    def __init__(self):
        # Make sure we reset the settings every time the plugin is loaded (development)
        global instance
        instance = DirectorySettings()

    @property
    def instance(self):
        global instance
        return instance

    def on_load(self, view):
        self.instance.apply(view)


import sublime, sublime_plugin
import os
import json
from string import Template


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

    def _placeholders(self, value, placeholders):
        """ Applies a set of placeholders to the given settings recursively
            See http://sublimetext.info/docs/en/reference/build_systems.html#variables
        """
        if isinstance(value, str) and '$' in value:
            value = Template(value).safe_substitute(placeholders)
        elif isinstance(value, dict):
            for key, val in value.items():
                value[key] = self._placeholders(val, placeholders)
        elif isinstance(value, list):
            value = [self._placeholders(x, placeholders) for x in value]

        return value

    def _load(self, directory):
        """Return settings, if any, strictly for this directory."""
        settings = {}
        fname = os.path.join(directory, SETTINGS_FILE)
        try:
            with open(fname) as fp:
                data = fp.read()
                data = self._placeholders(data, {'settings_path': directory})
                settings = json.loads(data)
        except ValueError as ex:
            print('{0}: ERROR parsing file {1}: {2}'.format(__name__, fname, ex))
        except:
            pass

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
        """ Reset the cache """
        self._cache = {'/': {}}

    def apply(self, view):
        """ Apply the current overrides to a given view """
        settings = view.settings()
        if not settings.get(DIRECTORY_SETTINGS_FLAG, True):
            return

        overrides = self.get_settings(view.file_name())
        if not overrides:
            return

        # Compute the list of placeholders 
        # see http://docs.sublimetext.info/en/sublime-text-3/reference/build_systems.html#build-system-variables
        # Note: `settings_path` is automatically injected before loading the settings
        fname = view.file_name()
        try:
            pname = view.window().project_file_name() or ''
        except: # ST2
            pname = ''

        overrides = self._placeholders(overrides, {
            'file': fname,
            'file_path': os.path.dirname(fname),
            'file_name': os.path.basename(fname),
            'file_extension': os.path.splitext(fname)[1],
            'file_base_name': os.path.splitext(fname)[0],
            'project': pname,
            'project_path': os.path.dirname(pname),
            'project_name': os.path.basename(pname),
            'project_extension': os.path.splitext(pname)[1],
            'project_base_name': os.path.splitext(pname)[0],
        })

        #print(overrides)
        for name, value in overrides.items():
            if value == ERASE_MARK:
                if settings.has(name):
                    settings.erase(name)
            else:
                settings.set(name, value)

    def reload(self):
        """ Apply the current overrides to all the loaded views """
        for window in sublime.windows():
            for view in window.views():
                if view.file_name():
                    self.apply(view)


class ReloadDirectorySettingsCommand(sublime_plugin.ApplicationCommand):
    """Clear out the cache and reload settings for all views in all windows."""
    def run(self):
        global instance
        instance.reset()
        instance.reload()


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

    def on_post_save(self, view):
        """ When editing a directory settings file force a reload of the current buffers
        """
        fname = os.path.basename(view.file_name())
        if fname == SETTINGS_FILE:
            self.instance.reset()
            self.instance.reload()

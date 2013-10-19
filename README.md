# DirectorySettings for SublimeText 2 and 3

### What it is:

Place `.sublime-settings` files in a directory and, if you open a file in that directory, the settings will get applied to the file's view. Settings can nest in directories; in the event of conflict, the deepest settings files win.

To activate the plugin, just install it. If you want to disable it you can set the following in your File user preferences:

    "directory_settings": false

This prevents the plugin from doing work when you don't want it to.

### How to use it:

To get a different color scheme for files in the `~/my/work/` directory, add a `~/my/work/.sublime-settings` file that contains:

    {
        "color_scheme": "Packages/Color Scheme - Default/DifferentTheme.tmTheme"
    }

That's it!

### Reloading settings:

When you edit your `.sublime-settings` inside Sublime, it will automatically apply the changes to every open file when saving the
changes.

Additionally you can issue a reload from the Command Palette under "Reload Directory Settings" or event assign a keyboard shortcut
to it like the following:

    { "keys": ["super+ctrl+alt+r"], "command": "reload_directory_settings"}


### Example use case:

I am currently porting an app from Python 2 to 3. I've got one directory with the old code, one directory with the new code. Lots of similarly named files! I popped a `.sublime-settings` at the top of each source tree so I could have different fonts and color schemes -- this helps me quickly distinguish which files I'm looking at when I'm editing.

### Advanced features:

If for some reason you want to modify the default settings by erasing one of its values, you can use
the value `#ERASE#` in your directory overrides.

    { 'key_i_want_remove': '#ERASE#' }

You can also use placeholders in your per directory settings files, they are the same as the ones supported
by [Sublime's build files](http://docs.sublimetext.info/en/latest/reference/build_systems.html#build-system-variables)
with the exception of `$packages`.

There is also a handy specific one that gets replaced by the directory where the `.sublime-settings` was loaded
from: `settings_path`. Allowing to reference relative paths easily.

	{ "boo.args": [
		"-r:$settings_path/build/Project.dll",
		"-r:${file_path}/bin/Debug/${file_base_name}.dll" 
	]}


### TODO:

- support reverting settings that were previously applied (for cleaner, better reloads)
- make sure it works on something other than OS X (it should)

### License:

MIT or BSD, take your pick.




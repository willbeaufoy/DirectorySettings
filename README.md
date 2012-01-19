# DirectorySettings for SublimeText 2

### What it is:

Place `.sublime-settings` files in a directory and, if you open a file in that directory, the settings will get applied to the file's view. Settings can nest in directories; in the event of conflict, the deepest settings files win.

To activate the plugin, install it and then add this setting to your File user preferences:

    "use_directory_settings": true

This prevents the plugin from doing work when you don't want it to.

### How to use it:

To get a different color scheme for files in the `~/my/work/` directory, add a `~/my/work/.sublime-settings` file that contains:

    {
        "color_scheme": "Packages/Color Scheme - Default/DifferentTheme.tmTheme"
    }

That's it!

### Reloading settings:

If you change your `.sublime-settings` often, consider mapping a key to the `reload_directory_settings` command. I use the following mapping:

    { "keys": ["super+ctrl+alt+r"], "command": "reload_directory_settings"}

Easy.

### TODO:

- support reverting settings that were previously applied (for cleaner, better reloads)
- watch filesystem for settings changes
- support erase()
- make sure it works on something other than OS X (it should)

### License:

MIT or BSD, take your pick.




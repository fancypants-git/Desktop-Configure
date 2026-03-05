# Installation

Simply download the build and [dependencies](#dependencies)<br>
You might need to initialize some dependencies and settings.

## Dependencies
The [Desktop Widgets](https://extensions.gnome.org/extension/5156/desktop-clock/) Extension >> [Homepage](https://gitlab.com/AndrewZaech/azclock)

The [Wallpaper Slideshow](https://extensions.gnome.org/extension/6281/wallpaper-slideshow/) Extension >> [Homepage](https://gitlab.com/AndrewZaech/azwallpaper)

[Optional]<br>
The [Custom Command Menu](https://extensions.gnome.org/extension/7024/custom-command-list/) Extension for easy, instant access to the GUI<br>
\>> [Homepage](https://github.com/StorageB/custom-command-menu)


## Setup

The application itself doesn't require any setup at all, the extensions however do:

For [Desktop Widgets](https://extensions.gnome.org/extension/5156/desktop-clock/), you want to initialize a 'Digital Clock Widget'
and add however many Time (or Date) Labels that you want.<br>
This setup can only be changed manually by you and is partially
(unsupported) compatible with configs paired to different setups, keep in mind updating this might cause unwanted behaviours.

For the [Wallpaper Slideshow](https://extensions.gnome.org/extension/6281/wallpaper-slideshow/) Extension, just make sure
bing wallpaper downloading is disabled (this is found in the 'Bing Wallpapers' tab in the Slideshow settings)

If you have installed the [Custom Command Menu](https://extensions.gnome.org/extension/7024/custom-command-list/) Extension
(recommended), link a command to this application's Executable.

After that you will need to compile the GLIB schemas of the Desktop Widgets and Wallpaper Slideshow extensions so the application can use them.
To do this:
1. open a terminal or file explorer
2. navigate to "~/.local/share/gnome-shell/extensions" where you will find the downloaded extensions

repeat the following steps (3 and 4) for "azclock@azclock.gitlab.com" and "azwallpaper@azwalpaper.gitlab.com"
3. open "\[EXTENSION]/schemas" and replace \[EXTENSION] with the names given above
    - if you opened this folder in a file explorer, right click and press "open in terminal"

now you must copy the schemas to the system wide schemas folder and compile them
4. type "sudo cp org.gnome.shell.extensions.\[EXTENSION].gschema.xml /usr/share/glib-2.0/schemas/" and replace \[EXTENSION]

after you have done this for both extensions you must re-compile the glib schemas
5. do this by typing "sudo glib-compile-schemas /usr/share/glib-2.0/schemas"



# Usage

## Themes

To install a theme for use, follow the next steps:

1. Select the "Themes Directory" in the GUI
2. In this directory, add a new folder with the name of your theme (e.g. "Cozy")
3. Within this new folder, there are two optional things to add:
    1. a 'clockconfig.json', containing the settings of the clock theme
       (see [Clock Tutorial](#Clock))
    2. a 'Wallpapers' folder, containing all wallpapers in this theme
4. relaunch the GUI and select your new theme :D

## Clock

To create a config for your newly themed clock, it is most recommended to follow the [EAS](#edit-and-save-method-eas)
method<br>

If you already have a config file for your clock, you can follow the next steps:

1. If not already the case: move the config file to your new theme's directory

yeah, that's about it.

### Edit-And-Save Method (EAS)

This method uses the Clock's Extension GUI to edit the clock's settings, and then<br>
upload them to the clockconfig.json file.<br>
So open up the extension manager and click on the settings for the widget extension.
In there, you can edit all your clock to your liking, but keep in mind only
the [supported settings](#supported-settings) will be affected.<br>

After you have changed the clock to your liking, go ahead and open up the GUI and select your new theme<br>
Nothing should happen, yet. After selecting the 'Desktop Theme', Press 'Update Clock' to apply the settings to a new
clockconfig.json and your clock is ready to go.

#### Supported Settings

##### Widget Settings

[Setting (Name in Json)]

- location (location-data)
- vertical layout (vertical)
- anchor point (anchor-point)
- spacing
- all border settings (show-border, border-width, border-color)
- all background settings (show-background, border-radius, background-color)

##### Element Settings

[Setting (Name in Json)]

- date/time format (date-format)
- alignment (text-align-x, text-align-y)
- padding
- margins (margin)
- all border settings (show-border, border-width, border-color)
- all background settings (show-background, border-radius, background-color)
- all font settings (font-family-override, font-weight, font-style, font-size)
- text color (foreground-color)
- all shadow settings (shadow)
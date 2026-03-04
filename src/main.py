import os
import json
from pathlib import Path

import schema_handler as schema
import clock_config as clock
import ui

WALLPAPER_XML_DIR: str = '/home/michiel/.local/share/gnome-shell/extensions/azwallpaper@azwallpaper.gitlab.com/schemas'
WALLPAPER_SCHEMA_ID: str = 'org.gnome.shell.extensions.azwallpaper'
WALLPAPER_DIRECTORY_KEY: str = 'slideshow-directory'

THEMES_DIRECTORY: str
CONFIG_PATH: str = os.path.join(os.path.dirname(__file__), '../config.json')

wallpaper_settings: schema.Gio.Settings
global_themes: list[str] = []
clock_themes: list[str] = ['default']
wallpaper_themes: list[str] = ['default']

clock_theme_dropdown: ui.Dropdown
wallpaper_theme_dropdown: ui.Dropdown

root: ui.Window


def set_theme(theme_name: str):
    set_wallpaper(theme_name)
    set_clock(theme_name)

    clock_theme_dropdown.set('default')
    wallpaper_theme_dropdown.set('default')

    write_theme_to_config(theme_name)


def set_clock(theme_name: str, update_json: bool = False):
    if theme_name == 'default':
        theme_name = get_config_key('desktop-theme')

    clock.load_json(os.path.join(THEMES_DIRECTORY, theme_name, "clockconfig.json"))

    if update_json:
        write_to_config('clock-theme', theme_name)


def update_clock():
    clock.write_json(os.path.join(THEMES_DIRECTORY, get_config_key('desktop-theme'), "clockconfig.json"))


def set_wallpaper(theme_name: str, update_json: bool = False):
    if theme_name == 'default':
        theme_name = get_config_key('desktop-theme')

    schema.set_key(wallpaper_settings, WALLPAPER_DIRECTORY_KEY,
                   os.path.join(THEMES_DIRECTORY, theme_name, "Wallpapers"))

    if update_json:
        write_to_config('wallpaper-theme', theme_name)


def update_themes_directory(new_dir: str):
    themes_directory = os.path.expanduser(new_dir)
    usr_path = str(Path.home())
    write_to_config("themes-directory", themes_directory.replace(usr_path, '~'))


def write_to_config(key: str, value: str):
    config: dict[str, str] = json.load(open(CONFIG_PATH))
    if not config.get(key):
        print('Key {} does not exist in config.json'.format(key))
        return

    config[key] = value
    json.dump(config, open(CONFIG_PATH, 'w'), indent=4)


def write_theme_to_config(theme: str):
    config: dict[str, str] = json.load(open(CONFIG_PATH))
    config["desktop-theme"] = theme
    config["wallpaper-theme"] = 'default'
    config["clock-theme"] = 'default'

    json.dump(config, open(CONFIG_PATH, 'w'), indent=4)


def get_config_key(key: str) -> str:
    config: dict[str, str] = json.load(open(CONFIG_PATH))
    if not config.get(key):
        print('Key {} does not exist in config.json'.format(key))
        return ""

    return config[key]



def initialize():
    global THEMES_DIRECTORY, global_themes, clock_themes, wallpaper_themes, wallpaper_settings

    wallpaper_settings = schema.get_settings(WALLPAPER_SCHEMA_ID)
    THEMES_DIRECTORY = os.path.expanduser(get_config_key('themes-directory'))

    for f in os.listdir(THEMES_DIRECTORY):
        theme_dir = os.path.join(THEMES_DIRECTORY, f)
        if os.path.isdir(theme_dir):
            is_wallpaper = os.path.isdir(os.path.join(theme_dir, 'Wallpapers'))
            is_clock = os.path.isfile(os.path.join(theme_dir, 'clockconfig.json'))
            if is_wallpaper:
                wallpaper_themes.append(f)
            if is_clock:
                clock_themes.append(f)
            if is_wallpaper and is_clock:
                global_themes.append(f)


    set_wallpaper(get_config_key('wallpaper-theme'))
    set_clock(get_config_key('clock-theme'))


def main():
    global root, clock_theme_dropdown, wallpaper_theme_dropdown

    root = ui.Window('Desktop Theming', (400, 400))



    theme_section = ui.Section(root, 'Desktop Theme', size='h1').pack()

    ui.Dropdown(theme_section, get_config_key('desktop-theme'), global_themes, lambda e, var: set_theme(var.get())).pack()
    ui.Label(theme_section, text='Themes Directory').pack(side='top')
    ui.Path(theme_section, default=THEMES_DIRECTORY, callback=update_themes_directory).pack()



    clock_section = ui.Section(root, 'Clock Theme', size='h2', relief='solid').pack()

    clock_callback = lambda e, var: set_clock(var.get(), True)
    clock_theme_dropdown = ui.Dropdown(clock_section, get_config_key('clock-theme'), clock_themes, clock_callback).pack()
    ui.Button(clock_section, text='Update Clock',
              command=lambda: ui.ConfirmWindow(root, name='Update Clock',
                                               text='Are you sure to update the "{}" Clock?\nThis Action can not be undone'.format(
                                                   get_config_key('desktop-theme')
                                               ),
                                               callback=update_clock)).pack()



    wallpaper_section = ui.Section(root, 'Wallpaper Theme', size='h2', relief='solid').pack()

    wallpaper_callback = lambda e, var: set_wallpaper(var.get(), True).pack()
    wallpaper_theme_dropdown = ui.Dropdown(wallpaper_section, default=get_config_key('wallpaper-theme'),
                                           options=wallpaper_themes,
                                           callback=wallpaper_callback).pack()

    root.mainloop()


if __name__ == '__main__':
    initialize()
    main()

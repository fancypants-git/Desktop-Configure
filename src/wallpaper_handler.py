import schema_handler as schema
from gi.repository import GLib

SCHEMA = 'org.gnome.shell.extensions.azwallpaper'
WALLPAPER_KEY = 'slideshow-directory'

class WallpaperConfigHandler:
    def __init__(self):
        self.settings = schema.Settings(SCHEMA)

    def set_slideshow_dir(self, path: str) -> None:
        self.settings.set_value(WALLPAPER_KEY, GLib.Variant.new_string(path))
    
    def get_slideshow_dir(self) -> str:
        return str(self.settings.get_value(WALLPAPER_KEY))



if __name__ == "__main__":
    wallpaper_config_handler = WallpaperConfigHandler()

    while True:
        print()
        print("Choose an Option:")
        print("0. Exit")
        print("1. Get Directory")
        print("2. Set Directory")

        option_str = input("Option ")
        option: int
        try:
            option = int(option_str)
        except:
            print(f"Failed to convert {option_str} to integer. Please input a number")
            continue

        if option == 0:
            break
        elif option == 1:
            print(wallpaper_config_handler.get_slideshow_dir())
        elif option == 2:
            path: str = input("Path: ")
            wallpaper_config_handler.set_slideshow_dir(path)

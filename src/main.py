### PURPOSE ###
# main.py provides the entry point to the program
# it initializes the handlers and the UI using gi.Gtk (GIMP ToolKit)

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import clock_handler as clock
import wallpaper_handler as slideshow
import json, os

class JsonConfigHandler:
    def __init__(self, path: str):
        self.config_path = path
        self.load_config()
    
    def load_config(self) -> None:
        with open(self.config_path) as f:
            json_str: str = f.read()
            self.config = json.loads(json_str)
    
    def save_config(self) -> None:
        with open(self.config_path, 'w') as f:
            json_str: str = json.dumps(self.config, indent=4)
            f.write(json_str)

    def get_current_theme(self) -> dict[str, str | None]:
        return {
            'desktop-theme': self.config['desktop-theme'],
            'wallpaper-theme': self.config['wallpaper-theme'],
            'clock-theme': self.config['clock-theme']
        }
    
    def set_desktop_theme(self, value: str) -> None:
        self.config['desktop-theme'] = value
        self.config['wallpaper-theme'] = 'default'
        self.config['clock-theme'] = 'default'
        self.save_config()
    
    def set_wallpaper_theme(self, value: str) -> None:
        self.config['wallpaper-theme'] = value
        self.save_config()
    
    def set_clock_theme(self, value: str) -> None:
        self.config['clock-theme'] = value
        self.save_config()
    
    def set_themes_directory(self, value: str) -> None:
        self.config['themes-directory'] = value
        self.save_config()
    
    def get_themes_directory(self) -> str:
        if 'themes-directory' in self.config:
            return os.path.expanduser(self.config['themes-directory'])
        return ""


class ThemeHandler:
    def __init__(self, config_handler: JsonConfigHandler):
        self.config_handler = config_handler
        self.load_themes()
    

    def load_themes(self):
        themes_dir = os.path.expanduser(self.config_handler.get_themes_directory())

        self.desktop_themes: list[str] = []
        self.wallpaper_themes: list[str] = []
        self.clock_themes: list[str] = []

        if os.path.exists(themes_dir): # if the themes_dir exists and is set
            for theme in os.listdir(themes_dir):
                theme_dir = os.path.join(themes_dir, theme)
                wallpaper_dir = os.path.join(theme_dir, 'Wallpapers')
                clock_dir = os.path.join(theme_dir, 'clockconfig.json')

                if os.path.exists(wallpaper_dir) and os.path.exists(clock_dir):
                    self.desktop_themes.append(theme)
                if os.path.exists(wallpaper_dir):
                    self.wallpaper_themes.append(theme)
                if os.path.exists(clock_dir):
                    self.clock_themes.append(theme)
                
            self.desktop_themes.sort()
            self.wallpaper_themes.sort()
            self.clock_themes.sort()
                

    
    def get_desktop_themes(self):
        return self.desktop_themes

    def get_wallpaper_themes(self, include_default: bool = True) -> list[str]:
        if include_default:
            return ['default'] + self.wallpaper_themes
        return self.wallpaper_themes

    def get_clock_themes(self, include_default: bool = True) -> list[str]:
        if include_default:
            return ['default'] + self.clock_themes
        return self.clock_themes
    
    def get_current_desktop_theme(self) -> str | None:
        return self.config_handler.get_current_theme()['desktop-theme']

    def get_current_wallpaper_theme(self, replace_default: bool = True) -> str | None:
        theme = self.config_handler.get_current_theme()['wallpaper-theme']
        if theme == 'default' and replace_default:
            return self.get_current_desktop_theme()
        return theme
    
    def get_current_clock_theme(self, replace_default: bool = True) -> str | None:
        theme = self.config_handler.get_current_theme()['clock-theme']
        if theme == 'default' and replace_default:
            return self.get_current_desktop_theme()
        return theme
    

    def refresh(self):
        self.load_themes()
    


        

class Window(Gtk.Window):
    def __init__(self):
        super().__init__(title="Desktop Configure")
        self.set_border_width(10)

        self.wallpaper_handler = slideshow.WallpaperConfigHandler()
        self.clock_handler = clock.JsonConverter()
        self.theme_handler = ThemeHandler(JsonConfigHandler(os.path.join(os.path.dirname(__file__), 'config.json')))

        self.box = Gtk.Box(spacing=20, orientation=Gtk.Orientation.VERTICAL)
        self.add(self.box)

        ## DESKTOP THEME BOX
        desktop_theme_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        self.box.pack_start(desktop_theme_box, False, False, 0)

        desktop_theme_label = Gtk.Label(label="Desktop Theme", halign=Gtk.Align.START)
        desktop_theme_box.pack_start(desktop_theme_label, False, False, 0)

        # DESKTOP THEME DROPDOWN
        self.desktop_theme_combo = Gtk.ComboBoxText.new()

        for i, theme in enumerate(self.theme_handler.get_desktop_themes()):
            self.desktop_theme_combo.append_text(theme)
            if theme == self.theme_handler.get_current_desktop_theme():
                self.desktop_theme_combo.set_active(i)
            
        self.desktop_theme_changed_id = self.desktop_theme_combo.connect("changed", self.on_desktop_theme_combo_changed)
        desktop_theme_box.pack_start(self.desktop_theme_combo, False, False, 0)


        ## WALLPAPER THEME BOX
        wallpaper_theme_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        self.box.pack_start(wallpaper_theme_box, False, False, 0)

        wallpaper_theme_label = Gtk.Label(label="Wallpaper Theme", halign=Gtk.Align.START)
        wallpaper_theme_box.pack_start(wallpaper_theme_label, False, False, 0)

        # WALLPAPER THEME DROPDOWN
        self.wallpaper_theme_combo = Gtk.ComboBoxText.new()

        for i, theme in enumerate(self.theme_handler.get_wallpaper_themes()):
            self.wallpaper_theme_combo.append_text(theme)
            if theme == self.theme_handler.get_current_wallpaper_theme(False):
                self.wallpaper_theme_combo.set_active(i)
        
        self.wallpaper_theme_changed_id = self.wallpaper_theme_combo.connect('changed', self.on_wallpaper_theme_combo_changed)
        wallpaper_theme_box.pack_start(self.wallpaper_theme_combo, False, False, 0)


        ## CLOCK THEME BOX
        clock_theme_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        self.box.pack_start(clock_theme_box, False, False, 0)

        clock_theme_label = Gtk.Label(label="Clock Theme", halign=Gtk.Align.START)
        clock_theme_box.pack_start(clock_theme_label, False, False, 0)

        # CLOCK THEME DROPDOWN
        self.clock_theme_combo = Gtk.ComboBoxText.new()

        for i, theme in enumerate(self.theme_handler.get_clock_themes()):
            self.clock_theme_combo.append_text(theme)
            if theme == self.theme_handler.get_current_clock_theme(False):
                self.clock_theme_combo.set_active(i)
        
        self.clock_theme_changed_id = self.clock_theme_combo.connect('changed', self.on_clock_theme_combo_changed)
        clock_theme_box.pack_start(self.clock_theme_combo, False, False, 0)

        # UPDATE CLOCK BUTTON
        update_clock_button = Gtk.Button(label="Update Clock")
        update_clock_button.connect("clicked", self.on_update_clock_clicked)
        clock_theme_box.pack_start(update_clock_button, False, False, 0)


        ## EXTRA SETTINGS
        extra_settings_expander = Gtk.Expander(label="Extra Settings")
        extra_settings_expander.set_expanded(False)
        self.box.pack_start(extra_settings_expander, False, False, 0)

        extra_settings_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        extra_settings_expander.add(extra_settings_box)

        # THEMES DIRECTORY CHOOSER
        theme_dir_chooser_button = Gtk.Button(label="Choose Themes Directory")
        theme_dir_chooser_button.connect("clicked", self.on_select_theme_dir_clicked)
        extra_settings_box.pack_start(theme_dir_chooser_button, False, False, 0)

        # REFRESH BUTTON
        refresh_button = Gtk.Button(label="Refresh")
        refresh_button.connect("clicked", self.on_refresh_button_clicked)
        extra_settings_box.pack_start(refresh_button, False, False, 0)

        # INITIALIZE CLOCK IDS
        initialize_clock_ids_button = Gtk.Button(label="Update Clock IDs")
        initialize_clock_ids_button.connect("clicked", self.on_update_clock_widget_ids_clicked)
        extra_settings_box.pack_start(initialize_clock_ids_button, False, False, 0)


    def on_desktop_theme_combo_changed(self, combo):
        new_theme = combo.get_active_text()
        theme_dir = os.path.join(self.theme_handler.config_handler.get_themes_directory(), new_theme)
        self.theme_handler.config_handler.set_desktop_theme(new_theme)
        self.wallpaper_handler.set_slideshow_dir(os.path.join(theme_dir, 'Wallpapers'))
        self.clock_handler.load_from_json_path(os.path.join(theme_dir, 'clockconfig.json'))
        self.refresh_ui()

    def on_wallpaper_theme_combo_changed(self, combo):
        new_theme = combo.get_active_text()
        if new_theme == 'default':
            new_theme = self.theme_handler.get_current_desktop_theme()
        
        if new_theme == None:
            return

        theme_dir = os.path.join(self.theme_handler.config_handler.get_themes_directory(), new_theme, 'Wallpapers')
        self.theme_handler.config_handler.set_wallpaper_theme(new_theme)
        self.wallpaper_handler.set_slideshow_dir(theme_dir)
    
    def on_clock_theme_combo_changed(self, combo):
        new_theme = combo.get_active_text()
        if new_theme == 'default':
            new_theme = self.theme_handler.get_current_desktop_theme()
        
        if new_theme == None:
            return
        
        theme_dir = os.path.join(self.theme_handler.config_handler.get_themes_directory(), new_theme, 'clockconfig.json')
        self.theme_handler.config_handler.set_clock_theme(new_theme)
        self.clock_handler.load_from_json_path(theme_dir)
    
    def on_update_clock_clicked(self, button):
        theme = self.theme_handler.get_current_desktop_theme()
        if not theme:
            return
        print(f"updating clock of {theme}")
        theme_dir = os.path.join(self.theme_handler.config_handler.get_themes_directory(), theme, 'clockconfig.json')
        self.clock_handler.write_to_json(theme_dir)
    
    def on_update_clock_widget_ids_clicked(self, button):
        for theme in self.theme_handler.get_clock_themes(False):
            path = os.path.join(self.theme_handler.config_handler.get_themes_directory(), theme, 'clockconfig.json')
            self.clock_handler.initialize_clock_id(path)
    
    def on_select_theme_dir_clicked(self, button):
        dialog = Gtk.FileChooserDialog(title="Themes Directory", parent=self, action=Gtk.FileChooserAction.SELECT_FOLDER)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            "Select",
            Gtk.ResponseType.OK
        )
        dialog.set_default_size(600, 300)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            new_dir = dialog.get_filename()
            self.theme_handler.config_handler.set_themes_directory(new_dir)
            self.theme_handler.refresh()
            self.refresh_ui()

        dialog.destroy()

    def on_refresh_button_clicked(self, button):
        self.theme_handler.refresh()
        self.refresh_ui()

    
    def populate_combo(self, combo, values, active_value=None, *block_ids):
        for id in block_ids:
            combo.handler_block(id)
        combo.remove_all()

        active_index = -1

        for i, value in enumerate(values):
            combo.append_text(value)

            if value == active_value:
                active_index = i

        if active_index >= 0:
            combo.set_active(active_index)

        for id in block_ids:
            combo.handler_unblock(id)
    
    def refresh_ui(self):
        self.populate_combo(
            self.desktop_theme_combo,
            self.theme_handler.get_desktop_themes(),
            self.theme_handler.get_current_desktop_theme(),
            self.desktop_theme_changed_id
        )

        self.populate_combo(
            self.wallpaper_theme_combo,
            self.theme_handler.get_wallpaper_themes(),
            self.theme_handler.get_current_wallpaper_theme(False),
            self.wallpaper_theme_changed_id
        )

        self.populate_combo(
            self.clock_theme_combo,
            self.theme_handler.get_clock_themes(),
            self.theme_handler.get_current_clock_theme(False),
            self.clock_theme_changed_id
        )



# start and run the application window
def run():
    win = Window()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    run()
import schema_handler as schema
import json, os
from gi.repository import GLib

SCHEMAS = {
    'general': 'org.gnome.shell.extensions.azclock',
    'widget': 'org.gnome.shell.extensions.azclock.widget-data',
    'element': 'org.gnome.shell.extensions.azclock.element-data'
}

PATHS = {
    'general': '',
    'widget': '/org/gnome/shell/extensions/azclock/widget-data/{}/',
    'element': '/org/gnome/shell/extensions/azclock/widget-data/{}/element-data/{}/'
}

GLOBAL_KEYS: list[str] = [
    'widgets' # whether enabled or not
]

WIDGET_KEYS: list[str] = [
    'location-data',
    'vertical',
    'anchor-point',
    'spacing',
    'show-background',
    'background-color',
    'border-radius',
    'show-border',
    'border-color',
    'border-width',
]

ELEMENT_KEYS: list[str] = [
    'date-format',
    'padding',
    'margin',
    'shadow',
    'font-family-override',
    'font-weight',
    'font-style',
    'font-size',
    'foreground-color',
    'show-background',
    'background-color',
    'border-radius',
    'show-border',
    'border-width',
    'border-color',
    'text-align-x',
    'text-align-y',
]

class GeneralConfigHandler:
    def __init__(self):
        self.settings = schema.Settings(SCHEMAS['general'], PATHS['general'])
        self.schema = schema.Schema(SCHEMAS['general'])
    
    def set_value(self, key: str, value: GLib.Variant):
        self.settings.set_value(key, value)
    
    def get_value(self, key: str) -> GLib.Variant:
        return self.settings.get_value(key)

    def get_key_type(self, key: str) -> str:
        gio_key = self.schema.get_key(key)
        if gio_key:
            return gio_key.get_type_str()
        return ""

class WidgetConfigHandler:
    def __init__(self, widget):
        self.settings = schema.Settings(SCHEMAS['widget'], PATHS['widget'].format(widget))
        self.schema = schema.Schema(SCHEMAS['widget'])

    def set_value(self, key: str, value: GLib.Variant):
        self.settings.set_value(key, value)
    
    def get_value(self, key: str) -> GLib.Variant:
        return self.settings.get_value(key)

    def get_key_type(self, key: str) -> str:
        gio_key = self.schema.get_key(key)
        if gio_key:
            return gio_key.get_type_str()
        return ""
    
class ElementConfigHandler:
    def __init__(self, widget, element):
        self.settings = schema.Settings(SCHEMAS['element'], PATHS['element'].format(widget, element))
        self.schema = schema.Schema(SCHEMAS['element'])

    def set_value(self, key: str, value: GLib.Variant):
        self.settings.set_value(key, value)
    
    def get_value(self, key: str) -> GLib.Variant:
        return self.settings.get_value(key)

    def get_key_type(self, key: str) -> str:
        gio_key = self.schema.get_key(key)
        if gio_key:
            return gio_key.get_type_str()
        return ""
    

class JsonConverter:
    def decode_to_json(self) -> str:
        result: dict = {'widgets': {}}
        widgets: list[dict]
        elements: list[dict]

        general_config_handler = GeneralConfigHandler()
        widgets = general_config_handler.get_value('widgets')
        
        for widget in widgets:
            widget_id = list(widget.keys())[0]
            widget_config_handler = WidgetConfigHandler(widget_id)

            result['widgets'][widget_id] = {}
            
            for key in WIDGET_KEYS:
                value = str(widget_config_handler.get_value(key))

                result['widgets'][widget_id][key] = {
                    'type': widget_config_handler.get_key_type(key),
                    'value': str(value)
                }


            result['widgets'][widget_id]['elements'] = {}
            elements = widget_config_handler.get_value('elements')
            for element in elements:
                element_id = list(element.keys())[0]
                element_config_handler = ElementConfigHandler(widget_id, element_id)
                
                result['widgets'][widget_id]['elements'][element_id] = {}

                for key in ELEMENT_KEYS:
                    value = str(element_config_handler.get_value(key))

                    result['widgets'][widget_id]['elements'][element_id][key] = {
                        'type': element_config_handler.get_key_type(key),
                        'value': str(value)
                    }
        
        return json.dumps(result, indent=4)

    def write_to_json(self, path: str) -> None:
        if not os.path.exists(path):
            return
        text = self.decode_to_json()
        with open(path, 'w') as f:
            f.write(text)


    def load_from_json_text(self, text: str):
        result: dict = json.loads(text)
        
        for widget in result['widgets']:
            widget_config_handler = WidgetConfigHandler(widget)

            for key in result['widgets'][widget]:
                if key == 'enabled': continue
                if key == 'elements':
                    if key == 'enabled': continue
                    for element in result['widgets'][widget]['elements']:
                        element_config_handler = ElementConfigHandler(widget, element)
                        for key in result['widgets'][widget]['elements'][element]:
                            value: str = result['widgets'][widget]['elements'][element][key]['value']
                            type: str = result['widgets'][widget]['elements'][element][key]['type']
                            variant = GLib.Variant.parse(GLib.VariantType(type), value, None, None)
                            element_config_handler.set_value(key, variant)
                    continue

                value: str = result['widgets'][widget][key]['value']
                type: str = result['widgets'][widget][key]['type']
                variant = GLib.Variant.parse(GLib.VariantType(type), value, None, None)
                widget_config_handler.set_value(key, variant)
    
    def load_from_json_path(self, path: str):
        if not os.path.exists(path):
            return
        
        with open(path, "r") as f:
            text = f.read()
        self.load_from_json_text(text)
    

    def initialize_clock_id(self, path):
        settings = schema.Settings(SCHEMAS['general'])
        widgets_schema = settings.get_value('widgets')

        if not os.path.isfile(path):
            print(f"Failed to load json: {path}")
            return

        with open(path) as f:
            result = json.load(f)

        widgets_dict = result.get("widgets", {})
        new_widgets = {}

        for w_index, (old_widget_id, widget_data) in enumerate(widgets_dict.items()):

            new_widget_id = list(settings.get_value('widgets')[w_index].keys())[0]

            elements = widget_data.get("elements", {})
            new_elements = {}

            for e_index, (old_element_id, element_data) in enumerate(elements.items()):
                widget_settings = schema.Settings(SCHEMAS['widget'], PATHS['widget'].format(new_widget_id))
                new_element_id = list(widget_settings.get_value('elements')[e_index].keys())[0]
                new_elements[new_element_id] = element_data

            widget_data["elements"] = new_elements
            new_widgets[new_widget_id] = widget_data
        
        result["widgets"] = new_widgets

        json_text = json.dumps(result, indent=4)
        with open(path, 'w') as f:
            f.write(json_text)
        



### DEBUG ###
def debug_load_clock(path: str):
    if not os.path.exists(path):
        print(f"{path} does not exist!")
        print(f"Creating file: {path}")
        with open(path, 'x'):
            pass

    while True:
        print()
        print("Choose an Option:")
        print("0. Back")
        print("1. Print JSON File")
        print("2. Print Clock as JSON")
        print("3. Load Clock from JSON")
        print("4. Save Clock as JSON")
        print("5. Initialize Clock ID")

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
            with open(path, "r") as f:
                print(f.read())
        elif option == 2:
            converter = JsonConverter()
            print(converter.decode_to_json())
        elif option == 3:
            converter = JsonConverter()
            converter.load_from_json_path(path)
        elif option == 4:
            converter = JsonConverter()
            text = converter.decode_to_json()
            with open(path, "w") as f:
                f.write(text)
        elif option == 5:
            converter = JsonConverter()
            converter.initialize_clock_id(path)




if __name__ == "__main__":
    while True:
        print()
        print("Choose an Option:")
        print("0. Exit")
        print("1. Load Clock JSON Config")

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
            path: str = input("JSON Path: ")
            debug_load_clock(path)
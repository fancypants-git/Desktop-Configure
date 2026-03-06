import json
import os

import schema_handler as schema


# all schemaIDs for the azclock
SCHEMAS = [
    'org.gnome.shell.extensions.azclock',
    'org.gnome.shell.extensions.azclock.widget-data',
    'org.gnome.shell.extensions.azclock.element-data'
]

# the paths for the relocatable schemas, paired with the schemaID
RELOCATABLE_SCHEMAS = {
    'org.gnome.shell.extensions.azclock.widget-data': '/org/gnome/shell/extensions/azclock/widget-data/{widget-id}/',
    'org.gnome.shell.extensions.azclock.element-data': '/org/gnome/shell/extensions/azclock/widget-data/{widget-id}/element-data/{element-id}/',
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


def get_widget_id(widget: dict[str, dict]) -> str:
    return list(widget.keys())[0]

def get_element_id(index: int, widget_id: str) -> str:
    widget_settings = get_widget_settings(widget_id)
    elements = widget_settings.get_value('elements')
    return list(elements[index].keys())[0]


def get_widget_settings(widget_id: str) -> schema.Gio.Settings:
    widget_schema_id = SCHEMAS[1]
    widget_path = RELOCATABLE_SCHEMAS[widget_schema_id].replace('{widget-id}', widget_id)
    return schema.get_settings(widget_schema_id, widget_path)

def get_element_settings(element_id: str, widget_id: str):
    element_schema_id = SCHEMAS[2]
    element_path = RELOCATABLE_SCHEMAS[element_schema_id].replace('{widget-id}', widget_id).replace('{element-id}', element_id)
    return schema.get_settings(element_schema_id, element_path)





def list_keys():
    widgets: list[dict]

    print("Settings:")
    for key in GLOBAL_KEYS:
        settings = schema.get_settings(SCHEMAS[0])
        widgets = settings.get_value(key)
        print(f'\t{key}:'.ljust(40) + str(widgets))


    elements: list[dict]
    for i, widget in enumerate(widgets):

        widget_id = get_widget_id(widget)
        elements = get_widget_settings(widget_id).get_value('elements')
        print('\n\tindex:{}\tid:{}'.format(i, widget_id))
        print(('\t\tenabled:'.ljust(40) + str(widget[widget_id]['enabled'])))

        for key in WIDGET_KEYS:
            value = get_widget_settings(widget_id).get_value(key)
            print(f'\t\t{key}:'.ljust(40) + str(value))

        for j, element in enumerate(elements):

            element_id = get_element_id(j, widget_id)
            print('\n\t\tindex:{}\tid:{}'.format(j, element_id))

            for key in ELEMENT_KEYS:
                value = get_element_settings(element_id, widget_id).get_value(key)
                print(f'\t\t\t{key}:'.ljust(40) + str(value))



def validate_schemas():
    for schema_id in SCHEMAS:
        # see if there is a path
        path = RELOCATABLE_SCHEMAS.get(schema_id)

        settings = schema.get_settings(schema_id, path)

        if settings:
            print(f"Loaded schema: {schema_id}")
        else:
            print(f"Failed to load schema: {schema_id} {path}")

def encode() -> dict:
    result: dict = {}

    widgets: list[dict]

    settings = schema.get_settings(SCHEMAS[0])

    widgets = settings.get_value('widgets')

    elements: list[dict]

    result['widgets'] = {}
    for i, widget in enumerate(widgets):

        widget_id = get_widget_id(widget)
        widget_settings = get_widget_settings(widget_id)
        widget_schema = schema.initialize_schema(SCHEMAS[1])
        elements = get_widget_settings(widget_id).get_value('elements')
        result['widgets'][widget_id] = {}
        result['widgets'][widget_id]['enabled'] = {"type": 'b', "value": widget[widget_id]['enabled']}

        for key in WIDGET_KEYS:
            value = widget_settings.get_value(key)
            if value.get_type_string() == 's':
                value = value.get_string()

                if value.startswith("'") and value.endswith("'"):
                    # Unwrap outer single quotes
                    value = value[1:-1]

            result['widgets'][widget_id][key] = {"type": widget_schema.get_key(key).get_value_type().dup_string(),
                                                 "value": str(value)}

        result['widgets'][widget_id]['elements'] = {}
        for j, element in enumerate(elements):

            element_id = get_element_id(j, widget_id)
            element_settings = get_element_settings(element_id, widget_id)
            element_schema = schema.initialize_schema(SCHEMAS[2])
            result['widgets'][widget_id]['elements'][element_id] = {}
            result['widgets'][widget_id]['elements'][element_id]['enabled'] = {"type": "b",
                                                                               "value": element[element_id]['enabled']}

            for key in ELEMENT_KEYS:
                value = element_settings.get_value(key)
                if isinstance(value, str) and value.startswith("'") and value.endswith("'"):
                    # Unwrap outer single quotes
                    value = value[1:-1]

                result['widgets'][widget_id]['elements'][element_id][key] = {
                    "type": element_schema.get_key(key).get_value_type().dup_string(), "value": str(value)}

    return result


def write_json(file: str):
    with open(file, 'w') as f:
        json.dump(encode(), f, indent=4)

def write_json_manual(file: str, output: dict):
    with open(file, 'w') as f:
        json.dump(output, f, indent=4)


def load_json(path: str):
    result: dict = {}
    if os.path.isfile(path):
        result = json.load(open(path))
    else:
        print(f"Failed to load json: {path}")
        return

    for widget_id in result['widgets']:
        widget_settings = get_widget_settings(widget_id)
        for key in result['widgets'][widget_id]:
            if key == 'enabled': continue # skip the 'enabled' key, no method of setting that yet
            if key != 'elements':
                setting = result['widgets'][widget_id][key]
                schema.set_value(widget_settings, key, setting['value'], setting['type'])
            else:
                for element_id in result['widgets'][widget_id]['elements']:
                    element_settings = get_element_settings(element_id, widget_id)
                    for ekey in result['widgets'][widget_id]['elements'][element_id]:
                        if ekey == 'enabled': continue

                        setting = result['widgets'][widget_id]['elements'][element_id][ekey]
                        schema.set_value(element_settings, ekey, setting['value'], setting['type'])


def initialize_clock_IDs(json_path: str):
    # TODO:
    # Get the widget ID from the schema
    # Get the element IDs of the widget from the schema
    # Load the JSON from the path and replace all IDs with the read IDs

    settings = schema.get_settings(SCHEMAS[0])
    widgets = settings.get_value('widgets') # gets all the widgets
    widget_id = get_widget_id(widgets[0])
    element_ids = [get_element_id(i, widget_id) for i in range(3)]

    result: dict = {}
    if os.path.isfile(json_path):
        result = json.load(open(json_path))
    else:
        print(f"Failed to load json: {json_path}")
        return

    result['widgets'][0] = widget_id

    print(result)

    for i in range(3):
        result['widgets'][widget_id]['elements'][i] = element_ids[i]

    write_json_manual(json_path, result)





if __name__ == '__main__':
    validate_schemas()
    encode()
    while True:
        print("1. List keys")
        print("2. Print Json")
        print("3. Write Json")
        print("4. Load Json")
        print("5. Initialize Clock IDs")
        print("0. Exit")
        option = input("Select an option: ")
        print()
        if option == "1":
            list_keys()
        elif option == "2":
            print(json.dumps(encode(), indent=4))
        elif option == "3":
            write_json(input("Output file: "))
        elif option == "4":
            load_json(input("Path: "))
        elif option == "5":
            initialize_clock_IDs(input("Path: "))
        elif option == "0":
            break

        print()
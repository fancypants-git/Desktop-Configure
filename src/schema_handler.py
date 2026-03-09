from __future__ import annotations
from typing import Any

import gi
gi.require_version("Gio", "2.0")
from gi.repository import Gio, GLib


class SchemaKey:
    def __init__(self, key: Gio.SettingsSchemaKey):
        self.gio_key = key

    def get_default_value(self) -> Gio.Variant:
        return self.gio_key.get_default_value()
    
    def get_description(self) -> str:
        return self.gio_key.get_description()
    
    def get_name(self) -> str:
        return self.gio_key.get_name()
    
    def get_summary(self) -> str:
        return self.gio_key.get_summary()
    
    def get_type(self) -> Gio.VariantType:
        return self.gio_key.get_value_type()
    
    def get_type_str(self) -> str:
        return self.get_type().dup_string()


class Schema:
    def __init__(self, schema_id: str):
        self.schema = Gio.SettingsSchemaSource.get_default().lookup(schema_id, False)
    
    def is_null(self) -> bool:
        return self.schema == None

    def get_path(self) -> str:
        if self.is_null():
            return ""
        return self.schema.get_path()
    
    def has_key(self, key: str) -> bool:
        if self.is_null():
            return False
        return self.schema.has_key(key)

    def get_key(self, key: str) -> SchemaKey | None:
        if not self.has_key(key):
            return None
        return SchemaKey(self.schema.get_key(key))

class Settings:
    def __init__(self, schema_id: str, path: str | None = None):
        if path:
            self.settings = Gio.Settings.new_with_path(schema_id, path)
        else:
            self.settings = Gio.Settings.new(schema_id)

    def set_value(self, key: str, value: GLib.Variant) -> None:
        self.settings.set_value(key, value)
        self.settings.sync()
    
    def get_value(self, key: str) -> Gio.Variant:
        return self.settings.get_value(key)



def debug_load_schema(id: str):
    schema = Schema(id)
    if schema.is_null():
        print(f"Schema '{id}' does not exist.")
        return
    
    print(f"Schema '{id}' loaded at path {schema.get_path()}.")

    while True:
        print()
        print("Choose an Option:")
        print("0. Back")
        print("1. Has Key")
        print("2. Print Key")

        option = int(input("Option "))

        if option == 0:
            return
        elif option == 1:
            print(schema.has_key(input("Key Name: ")))
        elif option == 2:
            key_name = input("Key Name: ")
            key = schema.get_key(key_name)
            if key != None:
                print(f"Values for Key '{key.get_name()}'")
                print(f"Description: {key.get_description()}")
                print(f"Default Value: {key.get_default_value()}")
                print(f"Summary: {key.get_summary()}")
                print(f"Type: {key.get_type()}")

def debug_load_settings(id: str, path: str):
    schema = Schema(id)
    if schema.is_null():
        print(f"Schema '{id}' does not exist.")
        return

    settings = Settings(id, path)
    print(f"Schema Settings '{id}' loaded at {path if path else "None"}.")

    while True:
        print()
        print("Choose an Option:")
        print("0. Back")
        print("1. Set Value")
        print("2. Get Value")

        option = int(input("Option "))

        if option == 0:
            return
        elif option == 1:
            key = input("Key Name: ")
            value = input("Value: ")
            if not schema.has_key(key):
                print(f"Key {key} does not exist.")
                return
            
            format_key = schema.get_key(key)
            if not format_key:
                return
            format = format_key.get_type()
            variant = GLib.Variant.parse(format, value, None, None)
            settings.set_value(key, variant)
        elif option == 2:
            key = input("Key Name: ")
            print(settings.get_value(key))



if __name__ == "__main__":
    while True:
        print()
        print("Choose an Option:")
        print("0. Exit")
        print("1. Load Schema")
        print("2. Load Settings")

        option = int(input("Option "))

        if option == 0:
            break
        elif option == 1:
            id = input("Schema ID: ")
            debug_load_schema(id)
        elif option == 2:
            id = input("Schema ID: ")
            path = input("Schema Path: ")
            debug_load_settings(id, path)
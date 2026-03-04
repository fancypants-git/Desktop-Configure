# https://api.pygobject.gnome.org/Gio-2.0/
from json import JSONDecodeError
import gi
gi.require_version("Gio", "2.0")
from gi.repository import Gio, GLib
import json

def initialize_schema(directory: str, schema_id: str) -> Gio.SettingsSchema | None:
    """Load a settings schema by ID from a directory."""
    return Gio.SettingsSchemaSource.new_from_directory(directory, None, True).lookup(schema_id, False)

def initialize_schema(schema_id: str) -> Gio.SettingsSchema | None:
    return Gio.SettingsSchemaSource.get_default().lookup(schema_id, False)

def get_settings(schema_id: str, path: str | None = None) -> Gio.Settings | None:
    if path:
        return Gio.Settings.new_with_path(schema_id, path)
    return Gio.Settings.new(schema_id)

def set_key(settings: Gio.Settings, key: str, value: str) -> None:
    """Set a string value and sync."""
    settings.set_string(key, value)
    settings.sync()

def set_value(settings: Gio.Settings, key: str, value: str, value_type: str) -> None:
    # Clean up accidentally quoted JSON strings
    if isinstance(value, str) and value.startswith("'") and value.endswith("'"):
        # Unwrap outer single quotes
        value = value[1:-1]

    if value_type == 'b':
        # Boolean
        parsed_value = str(value).lower() in ['true', '1']
        settings.set_boolean(key, parsed_value)

    elif value_type == 's':
        # String — store directly
        settings.set_string(key, value)

    elif value_type == 'i':
        # Integer
        parsed_value = int(value)
        settings.set_int(key, parsed_value)

    else:
        # Complex GLib.Variant types (like tuples)
        try:
            # Parse as GLib.Variant, then set
            variant = GLib.Variant(value_type, GLib.Variant.parse(None, value, None, None))
            settings.set_value(key, variant)
        except Exception as e:
            raise ValueError(f"Failed to set key '{key}' with value {value} and type {value_type}: {e}")

    settings.sync()

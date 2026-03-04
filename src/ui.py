import subprocess, shutil
import tkinter as tk
from tkinter import ttk, filedialog, font
from typing import Literal, Any, Mapping


class Window(tk.Tk):
    """window"""

    def __init__(self, name: str = 'Tkinter Window', size: tuple[int, int] | None = None):
        """Creates a new window with the given name NAME and size SIZE

        :arg name: str -> the name of the window
        :arg size: tuple[int, int] | None -> the size of the window, if None the size is not set and automatically calculated by tkinter"""
        super().__init__()
        if size:
            super().geometry('{}x{}'.format(size[0], size[1]))
        super().title(name)


class Toplevel(tk.Toplevel):
    """toplevel"""

    def __init__(self, master: Window, name: str = 'Tkinter Toplevel', size: tuple[int, int] | None = None):
        """Creates a Toplevel with parent MASTER, name NAME and size SIZE

        :arg master: Window -> the parent of the toplevel
        :arg name: str -> the name of the toplevel
        :arg size: tuple[int, int] | None -> the size of the toplevel, if None the size is not set and automatically calculated by tkinter"""
        super().__init__(master)
        if size:
            super().geometry('{}x{}'.format(size[0], size[1]))
        super().title(name)


class ConfirmWindow(Toplevel):
    """confirm window that prompts the user to confirm their action or cancel it"""

    def __init__(self, master: Window, callback, name='Confirm Action', text='Confirm Action'):
        """Creates a confirm window with parent MASTER and name NAME

        :arg master: Window -> the parent of the toplevel
        :arg name: str -> the name of the toplevel
        :arg callback: callable -> the callback to call when user confirms
        :arg text: str -> the text displayed within the confirm window to prompt the user what to do"""
        super().__init__(master, name=name, size=None)
        self.callback = callback

        label = tk.Label(self, text=text, anchor='center')
        confirm_btn = tk.Button(self, text='Confirm', command=self.confirm)
        cancel = tk.Button(self, text='Cancel', command=self.destroy)

        label.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW, padx=5, pady=5)
        confirm_btn.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        cancel.grid(row=1, column=1, sticky=tk.NSEW, padx=5, pady=5)

    def confirm(self):
        """Confirms the action intended by the user, calls the user callback and destroys itself"""
        self.callback()
        self.destroy()


class Section(tk.Frame):
    """section"""

    def __init__(self, master,
                 text: str = "Section",
                 relief: Literal['sunken', 'solid', 'groove', 'raised', 'flat'] = 'flat',
                 bd: int = 1,
                 header_size: Literal['h1', 'h2', 'h3'] | int = 'h1',
                 header_relief: Literal['solid', 'raised', 'flat'] = 'raised'):
        """Creates a section with a header

        :arg master: Widget -> the master of the section
        :arg text: str -> the text displayed on the header
        :arg relief: Literal['sunken', 'solid', 'groove', 'raised', 'flat'] -> the relief of the section
        :arg bd: int -> the border depth of the section
        :arg header_size: Literal['h1', 'h2', 'h3'] | int -> the size of the header font
        :arg header_relief: Literal['solid', 'raised', 'flat'] -> the relief of the header"""
        super().__init__(master, relief=relief, bd=bd)

        self.isinner = isinstance(master, Section)

        self.header = SectionHeader(self, text=text, size=header_size, relief=header_relief)

    def pack(self):
        if self.isinner:
            super().pack(fill='both', padx=20, pady=(5, 15))
        else:
            super().pack(fill='both', padx=5, pady=(5, 15))

        self.header.pack()
        return self


class SectionHeader(tk.Label):
    """header for sections"""

    def __init__(self, master,
                 text: str = "Section",
                 size: Literal['h1', 'h2', 'h3'] | int = 'h1',
                 relief: Literal['solid', 'raised', 'flat'] = 'raised'):
        """Creates a header for a section

        :arg master: Section -> the master of the header
        :arg text: str -> the text displayed on the header
        :arg size: Literal['h1', 'h2', 'h3'] | int -> the size of the header font
        :arg relief: Literal['solid', 'raised', 'flat'] -> the relief of the header"""
        header_font = font.nametofont("TkDefaultFont").copy()
        if size in ('h1', 1):
            header_font.configure(weight='bold', size=14)
        elif size in ('h2', 2):
            header_font.configure(weight='bold', size=12)
        else:
            header_font.configure(size=12)

        super().__init__(master, text=text, relief=relief, font=header_font)

    def pack(self):
        super().pack(fill='both')
        return self


class Label(tk.Label):
    def __init__(self, master, text, relief: Literal["raised", "sunken", "flat", "ridge", "solid", "groove"] = "flat"):
        super().__init__(master, text=text, relief=relief, anchor='w')

    def pack(self, side: Literal['left', 'right', 'top', 'bottom'] = 'left', **kwargs):
        fill = 'y' if side in ('top', 'bottom') else 'x'
        super().pack(fill=fill, pady=5, side=side, **kwargs)
        return self


class Button(tk.Button):
    def __init__(self, master, text, command,
                 relief: Literal["raised", "sunken", "flat", "ridge", "solid", "groove"] = "raised"):
        super().__init__(master, text=text, relief=relief, command=command)

    def pack(self):
        super().pack(fill='both', padx=5, pady=5)
        return self


class ConfirmButton(tk.Button):
    def __init__(self, master, root, text, command,
                 relief: Literal["raised", "sunken", "flat", "ridge", "solid"] = "raised"):
        super().__init__(master, text=text, relief=relief,
                         command=lambda: ConfirmWindow(root, command))

    def pack(self):
        super().pack(fill='both', padx=5, pady=5)


class Dropdown(ttk.Combobox):
    def __init__(self, master, default: str, options: list[str] | tuple[str], callback):
        self.variable = tk.StringVar(value=default)
        super().__init__(master, values=options, textvariable=self.variable, state='readonly')

        super().set(default)
        super().bind('<<ComboboxSelected>>', lambda e, value=self.variable: callback(e, value))
        super().bind('<Return>', lambda e, var=self.variable: callback(e, var))

    def pack(self):
        super().pack(fill='both', pady=5)
        return self


class Path(tk.Frame):
    def __init__(self, master, default: str = "~/", callback=None):
        super().__init__(master)
        self.callback = callback
        self.directory = default
        self.entry = tk.Entry(self)
        self.entry.insert(0, self.directory)
        self.entry.bind('<Return>', lambda e: self.callback(self.entry.get()))

        button_font = font.nametofont('TkDefaultFont').copy()
        button_font.configure(size=8)
        self.button = tk.Button(self, text='📁', font=button_font, command=self.open_folder, relief='flat')

    def open_folder(self):
        def select_directory():
            if shutil.which('zenity'):
                result = subprocess.run(
                    ['zenity', '--file-selection', '--directory'],
                    capture_output=True, text=True,  # makes sure the output is captured as text
                )

                if result.returncode == 0:
                    return result.stdout.strip()
                elif result.returncode == 1:  # when the 'Cancel' button is clicked
                    return self.directory

            return filedialog.askdirectory(title='Select directory (fallback)', initialdir=self.directory)

        self.directory = select_directory()
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.directory)

        if self.callback:
            self.callback(self.directory)

    def pack(self):
        super().pack(fill='both', pady=5)
        self.button.pack(fill='y', side='right')
        self.entry.pack(fill='both', pady=(2, 0))
        return self


def _test():
    root = Window(name='test')

    info = {
        "version": "0.1.2",
        "credits": [
            "fancypants (Michiel Eding)",
            "no one"
        ]
    }

    info_sect = Section(root, text='Info', relief='solid', bd=2).pack()

    version_frm = tk.Frame(info_sect)
    Label(version_frm, text='Version').pack()
    Label(version_frm, text=info["version"]).pack(side='right')
    version_frm.pack(fill='x')

    credits_sect = Section(info_sect, text="Credits", relief="flat", header_size='h3', header_relief='flat').pack()
    for name in info["credits"]:
        Label(credits_sect, text=name).pack(side='top')

    misc_sect = Section(root, text='Miscellaneous', header_size='h2').pack()

    Path(misc_sect, callback=lambda path: print("path selected:", path)).pack()

    root.mainloop()


if __name__ == '__main__':
    _test()

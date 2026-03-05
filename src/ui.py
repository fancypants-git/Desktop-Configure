import subprocess, shutil
import tkinter as tk
from tkinter import ttk, filedialog, font
from typing import Literal

from tkinter.ttk import Entry


class Window(tk.Tk):
    def __init__(self, name: str = 'Tkinter Window', size: tuple[int, int] | None = (800, 600)):
        super().__init__()
        if size:
            super().geometry('{}x{}'.format(size[0], size[1]))
        super().title(name)

class Toplevel(tk.Toplevel):
    def __init__(self, master: Window, name: str = 'Tkinter Toplevel', size: tuple[int, int] | None = None):
        super().__init__(master)
        if size:
            super().geometry('{}x{}'.format(size[0], size[1]))
        super().title(name)

class ConfirmWindow(Toplevel):
    def __init__(self, master: Window, callback, name='Confirm Action', text='Confirm Action'):
        super().__init__(master, name=name, size=None)
        self.callback = callback

        label = tk.Label(self, text=text, anchor='center')
        confirm_btn = tk.Button(self, text='Confirm', command=self.confirm)
        cancel = tk.Button(self, text='Cancel', command=self.destroy)

        label.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW, padx=5, pady=5)
        confirm_btn.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        cancel.grid(row=1, column=1, sticky=tk.NSEW, padx=5, pady=5)

    def confirm(self):
        self.callback()
        self.destroy()


class Section(tk.Frame):
    def __init__(self, master, header: str | None, size: Literal['h1', 'h2', 'h3'] | Literal[1, 2, 3] = 'h1',
                 relief: Literal['raised', 'solid'] = 'raised'):
        super().__init__(master)
        self.header = SectionHeader(self, text=header, size=size, relief=relief)

        self.is_inner_section = isinstance(master, (Section | CollapsableSection))

    def pack(self):
        if self.is_inner_section:
            super().pack(fill='both', padx=20, pady=(5, 15))
        else:
            super().pack(fill='both', padx=5, pady=(5, 15))

        self.header.pack()
        return self

class CollapsableSection(tk.Frame):
    def __init__(self, master, header: str | None, size: Literal['h1', 'h2', 'h3'] | Literal[1, 2, 3] = 'h1',
                 relief: Literal['raised', 'solid'] = 'raised',
                 collapsed: bool = False,
                 on_collapse = None,):
        super().__init__(master)

        arrow_font = font.nametofont('TkDefaultFont')
        arrow_font.configure(weight='bold')

        self.header = SectionHeaderButton(self, text=header, command=self.collapse, size=size, relief=relief)
        self.arrow = tk.Label(self, text='v', relief='flat', font=arrow_font, height=1)

        self.frame = tk.Frame(self) # frame for all the contents of the section

        self.is_inner_section = isinstance(master, (Section, CollapsableSection))
        self.collapsed = collapsed
        self.callback_on_collapse = on_collapse

    def collapse(self):
        if self.collapsed: # not collapsed
            self.collapsed = False
            self.arrow.configure(text='v')
            self.pack_inner()
        else: # collapsed
            self.collapsed = True
            self.arrow.configure(text='>')
            self.frame.pack_forget()

        if self.callback_on_collapse:
            self.callback_on_collapse(self.collapsed)

    def pack_inner(self):
        self.frame.pack(fill='both')
        return self.frame

    def pack(self):
        if self.is_inner_section:
            super().pack(fill='both', padx=20, pady=(5, 15))
        else:
            super().pack(fill='both', padx=5, pady=(5, 15))

        self.arrow.pack(fill='both', padx=(0,5), pady=3, side='right')
        self.header.pack()

        if not self.collapsed:
            self.pack_inner()

        return self


class SectionHeader(tk.Label):
    def __init__(self, master, text, size: Literal['h1', 'h2', 'h3'] | Literal[1, 2, 3] = 'h1',
                 relief: Literal['raised', 'solid'] = tk.RAISED):
        text_font = font.nametofont('TkDefaultFont').copy()
        if size in ('h1', 1):
            text_font.configure(weight='bold', size=14)
        elif size in ('h2', 2):
            text_font.configure(weight='bold', size=12)
        elif size in ('h3', 3):
            text_font.configure(size=12)

        super().__init__(master, text=text, relief=relief, anchor='center', font=text_font)

    def pack(self):
        super().pack(fill='both', pady=5)
        return self

class SectionHeaderButton(tk.Button):
    def __init__(self, master, text, command, size: Literal['h1', 'h2', 'h3'] | Literal[1, 2, 3] = 'h1',
                 relief: Literal['raised', 'solid'] = tk.RAISED):
        text_font = font.nametofont('TkDefaultFont').copy()
        if size in ('h1', 1):
            text_font.configure(weight='bold', size=14)
        elif size in ('h2', 2):
            text_font.configure(weight='bold', size=12)
        elif size in ('h3', 3):
            text_font.configure(size=12)

        super().__init__(master, text=text, relief=relief, anchor='center', font=text_font, command=command)

    def pack(self):
        super().pack(fill='both', pady=5)
        return self


class Label(tk.Label):
    def __init__(self, master, text, relief: Literal["raised", "sunken", "flat", "ridge", "solid", "groove"] = "flat"):
        super().__init__(master, text=text, relief=relief, anchor='w')

    def pack(self, side: Literal['left', 'right', 'top', 'bottom']='left'):
        super().pack(fill='both', pady=5, side=side)
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


if __name__ == '__main__':
    def method(collapsed: bool):
        print('is collapsed?', collapsed)

    root = Window()

    Section(root, 'Normal Section').pack()

    collapse_frame = CollapsableSection(root, 'Collapsable Section', on_collapse=method).pack().frame
    Label(collapse_frame, text='THIS frame is COLLAPSABLE!!!').pack()


    root.mainloop()
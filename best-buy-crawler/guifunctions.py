from tkinter import Button, Variable, Entry, IntVar, StringVar
from typing import Callable, Dict


def display_default_text(var: Variable, default_text: str,
                         widget: Entry, secure: bool) -> None:
    def clear_default(*args) -> None:
        if widget.get() == default_text:
            widget.config(textvariable=var)
            widget.delete(0, 'end')
            widget.insert(0, '')
            widget.config(fg='black')
            if secure:
                widget.config(show='*')
        return None

    def display_default(*args) -> None:
        if widget.get() == '':
            widget.config(textvariable='')
            widget.insert(0, default_text)
            widget.config(fg='grey')
            if secure:
                widget.config(show='')
        return None

    def on_window_open(*args) -> None:
        if var.get():
            widget.config(textvariable=var)
            if secure:
                widget.configure(show='*')
        elif widget.get() == '':
            widget.config(textvariable='')
            widget.insert(0, default_text)
            widget.config(fg='grey')
        return None

    on_window_open()
    widget.bind('<FocusIn>', clear_default)
    widget.bind('<FocusOut>', display_default)
    return None


def set_character_limit(var: Variable, limit: int) -> None:
    def character_limit(*args) -> None:
        value = var.get()
        if len(value) > limit:
            var.set(value[: limit])
        return None
    var.trace_add('write', character_limit)
    return None


def button_state(input_type: Dict, button: Button, *args) -> None:
    for key in input_type:
        for value in input_type[key].values():
            if isinstance(value, (IntVar, StringVar)):
                if not value.get():
                    button.configure(state='disabled')
                    return
            elif isinstance(value, Callable):
                if not value():
                    button.configure(state='disabled')
                    return
    button.configure(state='normal')
    return

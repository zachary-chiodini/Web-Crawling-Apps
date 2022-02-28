from json import load
from re import search
from tkinter import Entry, Frame, Label, Scrollbar, StringVar, Text, Tk
from typing import Tuple, Union

COOL_ROBOT_EMOJI = 'icon/cool_robot_emoji.ico'
COOL_GLASSES_EMOJI = 'icon/cool_glasses.png'


class App:
    
    def __init__(self, root_window_: Tk):
        self._user_input = {}
        self._private_input = {}
        self._assign_instance_vars(self._user_input, self._private_input)
        self._search_started = False
        self._search_stopped = True
        self._root_frame = Frame(root_window_)
        self._root_frame.pack(expand=True)
        self._user_form(0, 0, 10, 10)
        # self._log_box = Text(self._root_frame, height=10, width=100)
        # self._setup_log_box(10, 0, 10, 10)

    @staticmethod
    def _display_default_text(
            var: StringVar, default_text: str, widget: Entry, secure: bool
            ) -> None:
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

    @staticmethod
    def _set_force_regex(var: StringVar, regex: str) -> None:
        def force_regex(*args) -> None:
            value = var.get()
            if not search(regex, value):
                var.set(value[:-1])
            return None
        var.trace_add('write', force_regex)
        return None

    def _set_force_format(
            self, var: StringVar, default_text: str, widget: Entry,
            regex: str, message: str, secure=False) -> None:
        value = var.get()
        widget.unbind('<FocusOut>')
        if not search(regex, value):
            var.set('')  # FUUUUUUUUU
        else:
            self._display_default_text(var, default_text, widget, secure)
        return None

    def _entry_box(
            self, default_text: str, regex: str, width: int,
            row: Union[int, Tuple[int, int]], col: int,
            padx: int, pady: int, secure=False
            ) -> Entry:
        widget = Entry(self._root_frame, width=width)
        widget.grid(row=row, column=col, sticky='w', padx=padx, pady=pady)
        var = self._user_input[default_text]
        self._display_default_text(var, default_text, widget, secure)
        self._set_force_regex(var, regex)
        return widget

    def _user_form(self, row: int, col: int, padx: int, pady: int) -> None:
        Label(self._root_frame, text='Personal Information').grid(
            row=row, column=col, sticky='w',
            padx=padx, pady=pady
            )
        self._entry_box('First Name', '^[A-Z]{0,1}[a-z]*$', 30, row + 1, col, padx, pady)
        self._entry_box('Last Name', '^[A-Z]{0,1}[a-z]*$', 30, row + 1, col + 1, padx, pady)
        email_widget = self._entry_box(
            'Email Address',
            '^[0-9a-z](?!.*?\.\.)(?!.*?@\.)[0-9a-z\.]*[0-9a-z]*@{0,1}[a-z]*\.{0,1}[a-z]*$',
            30, row + 2, col, padx, pady)
        self._set_force_format(
            self._user_input['Email Address'], 'Email Address', email_widget,
            '^[a-z0-9]+@[a-z]+\.[a-z]$', 'Email must be of the form "username@domain.extension."')
        self._entry_box('Phone Number', '^[0-9]{0,10}$', 30, row + 2, col + 1, padx, pady)
        return None

    @staticmethod
    def _assign_instance_vars(user_input_ref, private_input_ref) -> None:
        with open('default_q_and_a.json') as json:
            q_and_a = load(json)
        private_input_ref = q_and_a['Private']
        del q_and_a['Private']
        for question in q_and_a:
            user_input_ref[question] = StringVar()
        return None

    def _setup_log_box(self, row: int, col: int, padx: int, pady: int) -> None:
        Label(self._root_frame, text='Crawler Log:') \
            .grid(row=row, column=col, sticky='w', padx=padx, pady=(pady, 0))
        scroll_bar = Scrollbar(self._root_frame, command=self._log_box.yview)
        self._log_box.config(yscrollcommand=scroll_bar.set)
        scroll_bar.grid(column=col, sticky='nse', pady=(0, pady))
        self._log_box.grid(row=row + 1, column=col, padx=padx, pady=(0, pady))
        self._log_box.insert('end', 'Please fill out the above information.')
        self._log_box.configure(state='disabled')
        return None


if __name__ == '__main__':
    root_window = Tk()
    root_window.geometry('')
    root_window.title('Indeed Crawler')
    root_window.iconbitmap(COOL_ROBOT_EMOJI)
    App(root_window)
    root_window.mainloop()

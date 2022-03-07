from json import load
from re import search
from tkinter import BooleanVar, Button, Entry, Frame, IntVar, Label, Scrollbar, StringVar, Text, Tk
from typing import Dict, List, Tuple, Union

from run_crawler2 import RunCrawler

COOL_ROBOT_EMOJI = 'icon/cool_robot_emoji.ico'
COOL_GLASSES_EMOJI = 'icon/cool_glasses.png'


class App:
    
    def __init__(self, root_window_: Tk):
        self._user_input = {}
        self._q_and_a = {}
        self._assign_instance_vars(self._user_input, self._q_and_a)
        self._required_input = {
            'First Name': StringVar(), 'Last Name': StringVar(),
            'Email Address': StringVar(), 'Phone Number': StringVar(),
            'City': StringVar(), 'State': StringVar(), 'Country': StringVar(),
            'Education': StringVar(), 'Indeed Login': StringVar(), 'Indeed Password': StringVar(),
            'Job Search': StringVar(), 'Job Location': StringVar(),
            'Number of Job Applications': IntVar()
        }
        self._dict_difference(self._user_input, self._required_input)
        self._invalid_input = False
        self._crawler_instance_args = {
            'number_of_jobs': IntVar(),
            'auto_answer_questions': BooleanVar(),
            'manually_fill_out_questions': BooleanVar(),
            'default_q_and_a': {},
            'debug': BooleanVar()
            }
        self._crawler_search_args = {
            'query': StringVar(),
            'enforce_query': BooleanVar(),
            'job_title_negate_lst': [StringVar()],
            'company_name_negate_lst': [StringVar()],
            'job_type': StringVar(),
            'min_salary': IntVar(),
            'enforce_salary': BooleanVar(),
            'exp_lvl': StringVar(),
            'country': StringVar(),
            'location': StringVar()
        }
        self._error_label_dict: Dict[str, Label] = {}
        self._skill_entry_list: List[List[Entry]] = []
        self._cert_entry_list: List[List[Entry]] = []
        self._lang_entry_list: List[List[Entry]] = []
        self._root_frame = Frame(root_window_)
        self._root_frame.pack(expand=True)
        self._user_form(0, 0, 10, 10, 20)
        # self._log_box = Text(self._root_frame, height=10, width=100)
        # self._setup_log_box(10, 0, 10, 10)

    @staticmethod
    def _assign_instance_vars(user_input_ref: Dict, q_and_a_ref: Dict) -> None:
        with open('default_q_and_a.json') as json:
            q_and_a_ref = load(json)
        q_and_a_copy = q_and_a_ref.copy()
        del q_and_a_copy['Private']
        for input_ in q_and_a_copy:
            user_input_ref[input_] = StringVar()
        return None

    @staticmethod
    def _dict_difference(ref1: Dict, ref2: Dict) -> None:
        for key in ref1.copy():
            if key in ref2:
                del ref1[key]
        return None

    def _error_label(self, message: str, row: int, col: int, padx: int) -> None:
        widget = Label(self._root_frame, text=message, fg='red')
        widget.grid(row=row + 1, column=col, sticky='w', padx=padx)
        self._error_label_dict[message] = widget
        return None

    def _display_default_text_or_check_format(
            self, var: StringVar, default_text: str, widget: Entry, secure: bool,
            row: int, col: int, padx: int, format_regex='', format_message=''
            ) -> None:
        def clear_default(*args) -> None:
            if (widget.get() == default_text
                    or format_message and widget.get() == format_message):
                widget.config(textvariable=var)
                widget.config(fg='black')
                if secure:
                    widget.config(show='*')
            if var.get() and format_regex and not search(format_regex, var.get()):
                if format_message not in self._error_label_dict:
                    self._error_label(format_message, row, col, padx)
            return None

        def display_default_or_check_format(*args) -> None:
            if widget.get() == '':
                widget.config(textvariable='', fg='grey')
                widget.insert(0, default_text)
                if secure:
                    widget.config(show='')
            elif format_regex and not search(format_regex, widget.get()):
                if format_message in self._error_label_dict:
                    error_widget = self._error_label_dict[format_message]
                    error_widget.destroy()
                    del self._error_label_dict[format_message]
                widget.config(textvariable='', fg='red')
                widget.delete(0, 'end')
                widget.insert(0, format_message)
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
        widget.bind('<FocusOut>', display_default_or_check_format)
        return None

    def _set_force_regex(
            self, var: StringVar, regex: str, message: str,
            row: int, col: int, padx: int
            ) -> None:
        def force_regex(*args) -> None:
            value = var.get()
            if not search(regex, value):
                if message not in self._error_label_dict:
                    self._error_label(message, row, col, padx)
            else:
                if message in self._error_label_dict:
                    widget = self._error_label_dict[message]
                    widget.destroy()
                    del self._error_label_dict[message]
            return None
        var.trace_add('write', force_regex)
        return None

    def _entry_box(
            self, default_text: str, regex: str, width: int,
            row: int, col: int, padx: int, pady: int, secure=False,
            format_regex='', format_message=''
            ) -> Entry:
        widget = Entry(self._root_frame, width=width)
        widget.grid(row=row, column=col, sticky='w', padx=padx, pady=pady)
        if default_text in self._required_input:
            var = self._required_input[default_text]
        else:
            var = self._user_input[default_text]
        self._display_default_text_or_check_format(
            var, default_text, widget, secure, row, col, padx, format_regex, format_message)
        self._set_force_regex(var, regex, format_message, row, col, padx)
        return widget

    def _add_entry(
            self, entry_titles: List[str], entry_list: List[List[Entry]],
            width: int, row: int, col: int, padx: int, pady: int, max_entries: int) -> None:
        if len(entry_list) < max_entries:
            entry_n = len(entry_list) + 1
            entry_widgets = []
            for i, title in enumerate(entry_titles):
                self._required_input.update({f'{title} {entry_n}': StringVar()})
                entry_widget = self._entry_box(
                    f'{title} {entry_n}', '',
                    width, row + 2*len(entry_list), col + 1 + i, padx, pady,)
                entry_widgets.append(entry_widget)
            entry_list.append(entry_widgets)
        return None

    @staticmethod
    def _remove_entry(entry_list: List[List[Entry]]) -> None:
        if len(entry_list) > 1:
            for entry_widget in entry_list.pop(-1):
                entry_widget.destroy()
        return None

    def _add_and_remove_buttons(
            self, add_and_remove_frame: Frame,
            entry_titles: List[str], entry_list: List[List[Entry]],
            width: int, row: int, col: int, padx: int, pady: int, max_entries: int) -> None:
        Button(
            add_and_remove_frame, text='+', width=2,
            command=lambda *args:
                self._add_entry(entry_titles, entry_list, width, row + 1, col, padx, pady, max_entries)
            ).grid(row=row, column=col + 1, sticky='w', padx=0, pady=pady)
        Button(add_and_remove_frame, text='-', width=2,
               command=lambda *args: self._remove_entry(entry_list)
               ).grid(row=row, column=col + 2, sticky='w', padx=0, pady=pady)
        self._add_entry(entry_titles, entry_list, width, row + 1, col, padx, pady, max_entries)
        return None

    def _add_and_remove_widget(
            self, text: str, entry_titles: List[str], entry_list: List[List[Entry]],
            width: int, row: int, col: int, padx: int, pady: int, max_entries: int) -> None:
        add_and_remove_frame = Frame(self._root_frame)
        add_and_remove_frame.grid(row=row, column=col, columnspan=3, sticky='w')
        Label(add_and_remove_frame, text=text) \
            .grid(row=row, column=col, sticky='w', padx=padx, pady=pady)
        self._add_and_remove_buttons(
            add_and_remove_frame, entry_titles, entry_list,
            width, row, col, padx, pady, max_entries)
        return None

    def _user_form(self, row: int, col: int, padx: int, pady: int, width: int) -> None:
        Label(self._root_frame, text='Personal Information')\
            .grid(row=row, column=col, sticky='w', padx=padx, pady=pady)
        self._entry_box(
            'First Name', '^[A-Z]{0,1}[a-z]*$',
            width, row + 1, col, padx, pady,
            format_regex='^[A-Za-z][a-z]+$',
            format_message='First name is invalid.')
        self._entry_box(
            'Last Name', '^[A-Z]{0,1}[a-z]*$',
            width, row + 1, col + 1, padx, pady,
            format_regex='^[A-Za-z][a-z]+$',
            format_message='Last name is invalid.')
        self._entry_box(
            'Current Company',
            '(?!.*?  )^[0-9A-Za-z ]*$',
            width, row + 3, col, padx, pady,
            format_regex='(?!.*?  )^[0-9A-Za-z ]+$',
            format_message='Company name is invalid.')
        self._entry_box(
            'Current Job Title',
            '(?!.*?  )^[A-Za-z]{0,1}[A-Za-z ]*$',
            width, row + 3, col + 1, padx, pady,
            format_regex='(?!.*?  )^[A-Za-z]{0,1}[A-Za-z ]+$',
            format_message='Job title is invalid.')
        self._entry_box(
            'Email Address',
            '(?!.*?\.\.)(?!.*?@\.)(?!.*?\.@)^[0-9a-z]{0,1}[0-9a-z\.]*[0-9a-z]*@{0,1}[a-z]*\.{0,1}[a-z]*$',
            width, row + 5, col, padx, pady,
            format_regex='^[a-z0-9]+@[a-z]+\.[a-z]$',
            format_message='Invalid email address.')
        self._entry_box(
            'Phone Number', '^[0-9]{0,10}$',
            width, row + 5, col + 1, padx, pady,
            format_regex='^[0-9]{10}$',
            format_message='Phone number must be 10 digits.')
        self._entry_box('LinkedIn', '', width, row + 7, col, padx, pady)
        self._entry_box('Website', '', width, row + 7, col + 1, padx, pady)
        self._entry_box(
            'Street Address',
            '(?!.*?  )(?!.*?,,)(?!.*? ,)^[0-9]*[0-9A-Za-z ,]*$',
            width, row + 9, col, padx, pady,
            format_regex='(?!.*?  )^[0-9]+ [0-9A-Za-z ]+$',
            format_message='Invalid street address.')
        self._entry_box(
            'City',
            '^[A-Z]{0,1}[a-z]*$',
            width, row + 9, col + 1, padx, pady,
            format_regex='^[A-Za-z][a-z]+$',
            format_message='City name is invalid.')
        self._entry_box(
            'State',
            '^[A-Z]{0,1}[a-z]* {0,1}[A-Z]{0-1}[a-z]*$',
            width, row + 11, col, padx, pady,
            format_regex='(?!.*?  )^[A-Za-z ]+$',
            format_message='State name is invalid.')
        self._entry_box(
            'Postal Code',
            '^[0-9]*$',
            width, row + 11, col + 1, padx, pady,
            format_regex='^[0-9]+$',
            format_message='Invalid postal code.')
        self._entry_box(
            'Country',
            '(?!.*?  )^[A-Za-z]{0,1}[A-Za-z ]*$',
            width, row + 13, col, padx, pady,
            format_regex='(?!.*?  )^[A-Za-z]{0,1}[A-Za-z ]+$',
            format_message='Invalid country name.')
        self._entry_box(
            'Country Code',
            '^[0-9]*$',
            width, row + 13, col + 1, padx, pady,
            format_regex='^[0-9]+$',
            format_message='Invalid country code.')
        self._entry_box(
            'Highest Education',
            "(?!.*?  )(?!.*?'')^[A-Za-z]{0,1}[A-Za-z ']*$",
            width, row + 15, col, padx, pady,
            format_regex="(?!.*?  )(?!.*?'')^[A-Za-z]{0,1}[A-Za-z ']+$",
            format_message='Invalid country code.')
        self._entry_box(
            'Clearance',
            '(?!.*?  )^[A-Za-z]{0,1}[A-Za-z ]*$',
            width, row + 15, col + 1, padx, pady,
            format_regex='(?!.*?  )^[A-Za-z]{0,1}[A-Za-z ]+$',
            format_message='Invalid country code.')
        self._add_and_remove_widget(
            'Skills/Experience', ['Skill', 'Experience'], self._skill_entry_list,
            width, row, col + 2, padx, pady, 8)
        self._add_and_remove_widget(
            'Languages', ['Language'], self._lang_entry_list,
            width, row, col + 5, padx, pady, 8)
        self._add_and_remove_widget(
            'Cert/Lic', ['Cert/License'], self._cert_entry_list,
            width, row, col + 8, padx, pady, 8)
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
    root_window.bind_all("<Button-1>", lambda event: event.widget.focus_set())
    root_window.iconbitmap(COOL_ROBOT_EMOJI)
    App(root_window)
    root_window.mainloop()

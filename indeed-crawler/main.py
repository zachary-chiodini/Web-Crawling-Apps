from json import load
from re import search
from tkinter import BooleanVar, Entry, Frame, IntVar, Label, Scrollbar, StringVar, Text, Tk
from typing import Dict, Tuple, Union

COOL_ROBOT_EMOJI = 'icon/cool_robot_emoji.ico'
COOL_GLASSES_EMOJI = 'icon/cool_glasses.png'


class App:
    
    def __init__(self, root_window_: Tk):
        self._user_input = {}
        self._q_and_a = {}
        self._assign_instance_vars(self._user_input, self._q_and_a)
        self._required_input = {
            'First Name': '', 'Last Name': '',
            'Email Address': '', 'Phone Number': '',
            'City': '', 'State': '', 'Country': '',
            'Education': '', 'Login': '', 'Password': '',
            'Job Search': '', 'Job Location': '',
            'Skills': [], 'Experience': []
        }
        self._user_input_ref.update(self._required_input)
        self._crawler_login_args = {'email': StringVar(), 'password': StringVar()}
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
        self._search_started = False
        self._search_stopped = True
        self._root_frame = Frame(root_window_)
        self._root_frame.pack(expand=True)
        self._user_form(0, 0, 10, 10, 50)
        # self._log_box = Text(self._root_frame, height=10, width=100)
        # self._setup_log_box(10, 0, 10, 10)

    @staticmethod
    def _assign_instance_vars(user_input_ref: Dict, q_and_a_ref: Dict) -> None:
        with open('default_q_and_a.json') as json:
            q_and_a_ref = load(json)
        q_and_a_copy = q_and_a_ref.copy()
        del q_and_a_copy['Private']
        for input_ in q_and_a_copy:a
            user_input_ref[input_] = StringVar()
        return None

    def _display_default_text(
            self, var: StringVar, default_text: str, widget: Entry, secure: bool,
            force_format=False, format_regex='', format_message=''
            ) -> None:
        def clear_default(*args) -> None:
            if (widget.get() == default_text
                    or force_format and widget.get() == format_message):
                widget.config(textvariable=var)
                widget.config(fg='black')
                if secure:
                    widget.config(show='*')
            return None

        def display_default_or_check_input(*args) -> None:
            if widget.get() == '':
                widget.config(textvariable='')
                widget.insert(0, default_text)
                widget.config(fg='grey')
                if secure:
                    widget.config(show='')
                if default_text in self._required_input:
                    self._required_input[default_text] = ''
            elif force_format and not search(format_regex, widget.get()):
                widget.config(textvariable='')
                widget.delete(0, 'end')
                widget.insert(0, format_message)
                widget.config(fg='red')
                if default_text in self._required_input:
                    self._required_input[default_text] = ''
            else:
                if default_text in self._required_input:
                    self._required_input[default_text] = var.get()
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
        widget.bind('<FocusOut>', display_default_or_check_input)
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

    def _entry_box(
            self, default_text: str, regex: str, width: int,
            row: Union[int, Tuple[int, int]], col: int,
            padx: int, pady: int, secure=False,
            force_format=False, format_regex='', format_message=''
            ) -> Entry:
        widget = Entry(self._root_frame, width=width)
        widget.grid(row=row, column=col, sticky='w', padx=padx, pady=pady)
        var = self._user_input[default_text]
        self._display_default_text(
            var, default_text, widget, secure, force_format, format_regex, format_message)
        self._set_force_regex(var, regex)
        return widget

    def _user_form(self, row: int, col: int, padx: int, pady: int, width: int) -> None:
        Label(self._root_frame, text='Personal Information').grid(
            row=row, column=col, sticky='w',
            padx=padx, pady=pady
            )
        self._entry_box('First Name', '^[A-Z]{0,1}[a-z]*$', width, row + 1, col, padx, pady)
        self._entry_box('Last Name', '^[A-Z]{0,1}[a-z]*$', width, row + 1, col + 1, padx, pady)
        self._entry_box(
            'Email Address',
            '^[0-9a-z](?!.*?\.\.)(?!.*?@\.)(?!.*?\.@)[0-9a-z\.]*[0-9a-z]*@{0,1}[a-z]*\.{0,1}[a-z]*$',
            width, row + 2, col, padx, pady,
            force_format=True, format_regex='^[a-z0-9]+@[a-z]+\.[a-z]$',
            format_message='Email format must be "username@domain.extension."')
        self._entry_box(
            'Phone Number', '^[0-9]{0,10}$',
            width, row + 2, col + 1, padx, pady,
            force_format=True, format_regex='^[0-9]{10}$',
            format_message='Phone number must be 10 digits.')
        self._entry_box(
            'Street Address',
            '(?!.*?  )(?!.*?,,)(?!.*? ,)^[0-9A-Za-z][0-9A-Za-z ,]*$',
            width, row + 3, col, padx, pady)
        self._entry_box('City', '^[A-Z]{0,1}[a-z]*$', width, row + 3, col + 1, padx, pady)
        self._entry_box('State', '^[A-Z]{0,1}[a-z]*$', width, row + 4, col, padx, pady)
        self._entry_box('Postal Code', '^[0-9]+$', width, row + 4, col + 1, padx, pady)
        self._entry_box('Country', '(?!.*?  )^[A-Za-z][A-Za-z ]*$', width, row + 5, col, padx, pady)
        self._entry_box('Country Code', '^[0-9]+$', width, row + 5, col + 1, padx, pady)
        Label(self._root_frame, text='Portfolio').grid(
            row=row + 6, column=col, sticky='w',
            padx=padx, pady=pady
            )
        self._entry_box('LinkedIn', '', width, row + 7, col, padx, pady)
        self._entry_box('Website', '', width, row + 7, col + 1, padx, pady)
        # skills
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

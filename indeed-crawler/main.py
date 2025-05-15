from collections import OrderedDict
from datetime import date
from json import dump, load
from os import environ, path
from PIL import ImageTk, Image
from re import search
from threading import Thread
from tkinter import (Button, Checkbutton, Entry, Frame,
    IntVar, Label, OptionMenu, Scrollbar, StringVar, Text, Tk)

from helper_funs import center
from run_crawler import RunCrawler
from self_destruct import SelfDestruct


class App:
    version = '2.0-Beta'
    _save_file = 'saved_input.txt'
    _save_file2 = 'saved_input2.txt'
    _required_input = {
        'First Name', 'Last Name', 'Email Address', 'Phone Number',
        'City', 'State', 'Country', 'Highest Education',
        'Indeed Login', 'Indeed Password', 'Search Job(s) (Comma Separated)',
        'Search Country', 'Number of Jobs', 'Skill 1', 'Experience 1'
    }
    _widget_entries = {
        'Skills/Experience': {'Skill': [], 'Experience': []},
        'Certs/Licenses': {'Cert/License': []},
        'Languages': {'Language': []}
    }
    def __init__(self, root_window_: Tk):
        self._start = True
        self._default_input = {
            'Clearance': 'No Clearance',
            'Country Code': '1',
            'LinkedIn': 'No Website',
            'Website': 'No Website',
            'Salary Type': 'Annual',
            'Currency': 'USD',
            'Employment Type': 'Fulltime',
            'Hours per Week': '40',
            'Start Date': date.today().strftime('%m/%d/%y'),
            'Interview Date & Time': 'Anytime',
        }
        self._user_input = OrderedDict({
            'First Name': {'Variable': StringVar(), 'Entity': Entry},
            'Email Address': {'Variable': StringVar(), 'Entity': Entry},
            'Current Job Title': {'Variable': StringVar(), 'Entity': Entry},
            'Current Company': {'Variable': StringVar(), 'Entity': Entry},
            'City': {'Variable': StringVar(), 'Entity': Entry},
            'State': {'Variable': StringVar(), 'Entity': Entry},
            'Country': {'Variable': StringVar(), 'Entity': Entry},
            'Search Country': {'Variable': StringVar(value='United States'), 'Entity': ['United States']},
            'Last Name': {'Variable': StringVar(), 'Entity': Entry},
            'Phone Number': {'Variable': StringVar(), 'Entity': Entry},
            'Highest Education': {'Variable': StringVar(), 'Entity': Entry},
            'Country Code': {'Variable': StringVar(), 'Entity': Entry},
            'Street Address': {'Variable': StringVar(), 'Entity': Entry},
            'Postal Code': {'Variable': StringVar(), 'Entity': Entry},
            'Clearance': {'Variable': StringVar(), 'Entity': Entry},
            'Languages': {'Variable': StringVar(), 'Entity': Button},
            'Indeed Login': {'Variable': StringVar(), 'Entity': Entry},
            'Website': {'Variable': StringVar(), 'Entity': Entry},
            'Employment Type': {'Variable': StringVar(), 'Entity': Entry},
            'Hours per Week': {'Variable': StringVar(), 'Entity': Entry},
            'Search State(s)/Region(s) (Comma Separated)': {'Variable': StringVar(), 'Entity': Entry},
            'Word(s) or Phrase(s) to Avoid (Comma Separated)': {'Variable': StringVar(), 'Entity': Entry},
            'Companies to Avoid (Comma Separated)': {'Variable': StringVar(), 'Entity': Entry},
            'Certs/Licenses': {'Variable': StringVar(), 'Entity': Button},
            'Indeed Password': {'Variable': StringVar(), 'Entity': Entry},
            'LinkedIn': {'Variable': StringVar(), 'Entity': Entry},
            'Desired Salary': {'Variable': StringVar(), 'Entity': Entry},
            'Salary Type': {'Variable': StringVar(), 'Entity': Entry},
            'Currency': {'Variable': StringVar(), 'Entity': Entry},
            'Number of Jobs': {'Variable': StringVar(), 'Entity': Entry},
            'Search Job(s) (Comma Separated)': {'Variable': StringVar(), 'Entity': Entry},
            'Skills/Experience': {'Variable': StringVar(), 'Entity': Button},
            'Start Date': {'Variable': StringVar(), 'Entity': Entry},
            'Interview Date & Time': {'Variable': StringVar(), 'Entity': Entry},
            '18 Years or Older': {'Variable': IntVar(value=1), 'Entity': Checkbutton},
            'Req. Sponsorship': {'Variable': IntVar(value=0), 'Entity': Checkbutton},
            'Eligible to Work': {'Variable': IntVar(value=1), 'Entity': Checkbutton},
            'Remote': {'Variable': IntVar(value=0), 'Entity': Checkbutton}
        })
        with open('q_and_a.json') as f:
            self._q_and_a = load(f)
        if path.exists(self._save_file):
            with open(self._save_file) as f:
                for field, dict_ in load(f).items():
                    for label, entry_list in dict_.items():
                        self._widget_entries[field][label] = entry_list
            with open(self._save_file2) as f:
                for field, value in load(f).items():
                    self._user_input[field]['Variable'].set(value)
        self._log_box: Text
        self._root_frame = Frame(root_window_)
        self._root_frame.pack(expand=True)
        self._start_button = Button(self._root_frame, command=self._start_crawling)
        self._user_form(0, 0, 13, 7, 25, 'nesw')

    def _entry_box(
            self, root_frame: Frame, default_text: str, width: int, row: int, col: int,
            padx: int, pady: int, sticky: str, colspan=1, regex = '', secure=False, value='') -> Entry:
        def bind_clear_default(*args) -> None:
            if (entry.get() == default_text) or (entry.get() == 'INVALID'):
                entry.config(textvariable=var)
                entry.config(fg='black')
                if secure:
                    entry.config(show='*')
            return None
        def bind_show_default(*args) -> None:
            if not entry.get():
                entry.config(textvariable='', fg='grey')
                entry.insert(0, default_text)
                if secure:
                    entry.config(show='')
            elif regex and not search(regex, entry.get()):
                entry.config(textvariable='', fg='red')
                entry.delete(0, 'end')
                entry.insert(0, 'INVALID')
            return None
        if default_text in self._user_input:
            var = self._user_input[default_text]['Variable']
        else:
            var = StringVar(value=value)
            self._user_input[default_text] = {'Variable': var, 'Entity': Entry}
        var.trace_add("write", bind_show_default)
        entry = Entry(root_frame, textvariable=var, width=width)
        entry.grid(row=row, column=col, columnspan=colspan, padx=padx, pady=pady, sticky=sticky)
        entry.bind('<FocusIn>', bind_clear_default)
        entry.bind('<FocusOut>', bind_show_default)
        if not var.get():
            entry.config(textvariable='')
            entry.insert(0, default_text)
            entry.config(fg='grey')
        if default_text in self._required_input:
            var.trace_add('write', self._toggle_start_button)
            entry.config({'background': 'yellow'})
        return entry

    def _add_entry(self, root_frame: Frame, field: str, width: int,
            row: int, col: int, padx: int, pady: int, sticky: str) -> None:
        # Detects and processes saved user input.
        if self._start and any(self._widget_entries[field].values()):
            for i, (label, entry_list) in enumerate(self._widget_entries[field].items()):
                for j, value in enumerate(entry_list.copy()):
                    entry = self._entry_box(root_frame, f"{label} {j + 1}",
                        width, row + j, col + i, padx, pady, sticky, value=value)
                    entry_list[j] = entry
            self._start = False
        else:
            for i, (label, entry_list) in enumerate(self._widget_entries[field].items()):
                entry = self._entry_box(root_frame, f"{label} {len(entry_list) + 1}",
                    width, row + len(entry_list), col + i, padx, pady, sticky)
                entry_list.append(entry)
        return None

    def _remove_entry(self, field: str) -> None:
        for label, list_ in self._widget_entries[field].items():
            if len(list_) > 1:
                del self._user_input[f"{label} {len(list_)}"]
                list_.pop(-1).destroy()
        return None

    def _widget(self, root_frame: Frame, field: str, width: int,
            row: int, col: int, padx: int, pady: int, sticky) -> None:
        add_frame = Frame(root_frame)
        add_frame.grid(row=row, column=col, padx=padx, pady=pady, sticky=sticky)
        Label(add_frame, text=field).grid(row=0, column=0, sticky='w')
        Button(add_frame, text='+', width=2,
            command=lambda *args: self._add_entry(root_frame, field, width, row + 1, col, padx, pady, sticky))\
            .grid(row=0, column=1, sticky='e')
        Button(add_frame, text='-', width=2,
            command=lambda *args: self._remove_entry(field)).grid(row=0, column=2, sticky='e')
        self._add_entry(root_frame, field, width, row + 1, col, padx, pady, sticky)
        return None

    def _user_form(self, row: int, col: int, padx: int, pady: int, width: int, sticky) -> None:
        add_frame = Frame(self._root_frame)
        add_frame.grid(row=row, column=col, padx=padx, pady=pady, sticky=sticky)
        Label(add_frame, text='Requirements Document').grid(row=0, column=0, sticky='w')
        no_rows = 8
        for i, field in enumerate(self._user_input.copy()):
            col_i, row_i = i // no_rows, i % no_rows + 1
            if self._user_input[field]['Entity'] is Entry: 
                self._entry_box(add_frame, field, width, row_i, col_i, padx, pady, sticky)
            elif self._user_input[field]['Entity'] is Button:
                self._widget(add_frame, field, width, row_i, col_i, padx, pady, sticky)
            elif self._user_input[field]['Entity'] is Checkbutton:
                Checkbutton(add_frame, text=field, variable=self._user_input[field]['Variable'])\
                .grid(row=row_i, column=col_i, sticky='w', padx=padx, pady=pady)
            elif type(self._user_input[field]['Entity']) is list:
                OptionMenu(add_frame, self._user_input[field]['Variable'], *self._user_input[field]['Entity'])\
                .grid(row=row_i, column=col + col_i, sticky=sticky, padx=padx, pady=pady)
        self._setup_log_box(row + 2, col, padx, 0, width, col_i + 1)
        image = ImageTk.PhotoImage(Image.open('icon/cool_glasses.png'))
        self._start_button.image = image
        self._start_button.configure(image=image)
        self._start_button.grid(row=row + 3, column=col, sticky='e', padx=padx, pady=pady)
        add_frame = Frame(self._root_frame)
        add_frame.grid(row=row + 3, column=col, padx=padx, pady=pady, sticky='w')
        Button(add_frame, text='Reset Cache', command=self._reset_cache).grid(row=0, column=0, padx=(0, padx))
        Button(add_frame, text='Save Input', command=self._save_user_input).grid(row=0, column=1, padx=(0, padx))
        Button(add_frame, text='Clear Input', command=self._clear_user_input).grid(row=0, column=2)
        self._toggle_start_button()
        return None

    def _save_user_input(self) -> None:
        user_input = self._user_input.copy()
        save_input = {}
        for field, dict_ in self._widget_entries.items():
            label_dict = {}
            for i, (label, entry_list) in enumerate(dict_.items()):
                label_dict[label] = []
                for j in range(len(entry_list)):
                    val_label = f"{label} {j + 1}"
                    value = user_input[val_label]['Variable'].get()
                    if value:
                        label_dict[label].append(value)
                    del user_input[val_label]
            # All labels within a widget field must have a value.
            if len(label_dict) == i + 1:
                save_input[field] = label_dict
        with open(path.join(path.dirname(__file__), self._save_file), 'w') as f:
            dump(save_input, f)
        with open(path.join(path.dirname(__file__), self._save_file2), 'w') as f:
            dump({field: dict_['Variable'].get() for field, dict_ in user_input.items()}, f)
        return None

    def _clear_user_input(self) -> None:
        for dict_ in self._user_input.values():
            if dict_['Entity'] is Checkbutton:
                dict_['Variable'].set(0)
            else:
                dict_['Variable'].set('')
        for dict_ in self._widget_entries.values():
            for label, entry_list in dict_.items():
                n = len(entry_list)
                for i in range(n - 1, -1):
                    entry_list[i].destroy()
                    del self._user_input[f"{label} {i + 1}"]
                entry_list = entry_list[0]
                self._user_input[f"{label} {n}"]['Variable'].set('')
        return None

    def _setup_log_box(self, row: int, col: int, padx: int, pady: int, width: str, colspan: int) -> None:
        add_frame = Frame(self._root_frame)
        add_frame.grid(row=row, column=col, columnspan=colspan, padx=padx, pady=pady, sticky='nsew')
        self._log_box = Text(add_frame, height=10, width=colspan*width - padx)
        Label(add_frame, text='Crawler Log:').grid(row=0, column=0, sticky='w')
        scroll_bar = Scrollbar(add_frame, command=self._log_box.yview)
        self._log_box.config(yscrollcommand=scroll_bar.set)
        scroll_bar.grid(row=1, column=0, sticky='nse')
        self._log_box.grid(row=1, column=0, sticky='w')
        self._log_box.insert('end', 'Please fill out the above information. Required input is highlighted.')
        self._log_box.configure(state='disabled')
        return None

    def _toggle_start_button(self, *args) -> None:
        if all(self._user_input[field]['Variable'].get() for field in self._required_input if field in self._user_input)\
            & all(entry_list[0].get() for entry_list in self._widget_entries['Skills/Experience'].values()):
            self._start_button.configure(state='normal')
        else:
            self._start_button.configure(state='disable')
        return None

    @staticmethod
    def _reset_cache(*args) -> None:
        if path.exists('cache.txt'):
            with open('cache.txt', 'w') as cache:
                cache.truncate()
        return None

    def _start_crawling(self) -> None:
        """Processes data from user input before crawling."""
        input_q_and_a = {}
        for skill, experience in zip(self._widget_entries['Skills/Experience']['Skill'],
                self._widget_entries['Skills/Experience']['Experience']):
            for question in self._q_and_a['Skills']:
                input_q_and_a[question.replace('[BLANK]', skill.get())] = experience.get()
            for question in self._q_and_a['Skills Other']:
                input_q_and_a[question.replace('[BLANK]', skill.get())] = 'yes'

        for _, entry_list in self._widget_entries['Languages'].items():
            for question in self._input_q_and_a['Languages']:
                if not entry_list:
                    input_q_and_a[question.replace('[BLANK]', 'English')] = 'yes'
                for entry in entry_list:
                    input_q_and_a[question.replace('[BLANK]', entry.get())] = 'yes'

        for _, entry_list in self._widget_entries['Certs/Licenses'].items():
            for question in self._input_q_and_a['Certs/Licenses']:
                if not entry_list:
                    input_q_and_a[question] = 'no'
                for entry in entry_list:
                    input_q_and_a[question.replace('[BLANK]', entry.get())] = 'yes'

        for field in ['Req. Sponsorship', 'Eligible to Work', '18 Years or Older']:
            if self._user_input[field].get():
                answer = 'yes'
            else:
                answer = 'no'
            for question in self._q_and_a[field]:
                input_q_and_a[question.replace('[BLANK]', self._user_input['Search Country'].get())] = answer

        for label, tuple_ in {'Full Name': ('First Name', 'Last Name'), 'Full Address': ('City', 'State')}:
            answer = ' '.join([self._user_input[tuple_[0]].get(), self._user_input[tuple_[1]].get()])
            for question in self._q_and_a[label]:
                input_q_and_a[question] = answer

        for question, answer in self._q_and_a['Private'].items():
            input_q_and_a[question] = answer

        for field in self._q_and_a:
            if field in input_q_and_a:
                continue
            answer = self._user_input[field].get()
            if (not answer) and (field in self._default_input):
                answer = self._default_input[field]
            else:
                answer = 'Prefer not to say'
            for question in self._q_and_a[field]:
                input_q_and_a[question] = answer

        run_crawler = RunCrawler(
            email=self._user_input['Indeed Login'].get(),
            password=self._user_input['Indeed Password'].get(),
            total_number_of_jobs=self._user_input['Number of Jobs'].get(),
            queries=[query.strip() for query in self._user_input['Search Job(s) (Comma Separated)'].get().split(',')],
            places=[(location.strip(), self._user_input['Search Country'].get().lower())
                    for location in self._user_input['Search State(s)/Region(s) (Comma Separated)'].get().split(',')],
            negate_jobs_list=[
                word.strip() for word in self._user_input['Word(s) or Phrase(s) to Avoid (Comma Separated)'].get().split(',')],
            negate_companies_list=[
                word.strip() for word in self._user_input['Companies to Avoid (Comma Separated)'].get().split(',')],
            min_salary=self._user_input['Desired Salary'].get(),
            default_q_and_a=input_q_and_a,
            log_box=self._log_box)
        new_thread = Thread(target=run_crawler.start)
        new_thread.start()
        return None


if __name__ == '__main__':
    current_date = date.today()
    PROGRAM_EXPIRATION_DATE = date(2030, 1, 1)
    if current_date >= PROGRAM_EXPIRATION_DATE:
        self_destruct = SelfDestruct('Indeed Crawler')
        self_destruct.open_window('EXPIRATION DATE EXCEEDED')
    else:
        root_window = Tk()
        root_window.geometry('960x600')
        root_window.title('Indeed Crawler')
        root_window.bind_all("<Button-1>", lambda event: event.widget.focus_set())
        center(root_window)
        root_window.iconbitmap('icon/cool_robot_emoji.ico')
        App(root_window)
        root_window.mainloop()

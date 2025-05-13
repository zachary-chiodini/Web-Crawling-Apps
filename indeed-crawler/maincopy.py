from collections import OrderedDict
from datetime import date
from json import dump, load
from os import environ, path
from PIL import ImageTk, Image
from re import search
from threading import Thread
from tkinter import (
    BooleanVar, Button, Checkbutton, Entry, Frame,
    IntVar, Label, OptionMenu, Scrollbar, StringVar, Text, Tk)
from typing import Dict, List

from helper_funs import center
from indeed_crawler import IndeedCrawler
from run_crawler import RunCrawler
from self_destruct import SelfDestruct


class App:
    version = '2.0-Beta'
    _input_file = 'saved_input.txt'
    _required_input = {
        'First Name', 'Last Name', 'Email Address', 'Phone Number',
        'City', 'State', 'Country', 'Highest Education',
        'Indeed Login', 'Indeed Password', 'Search Job(s) (Comma Separated)',
        'Search Country', 'Number of Jobs', 'Skill 1', 'Experience 1'
    }
    def __init__(self, root_window_: Tk):
        self._widget_entries = {
            'Skills/Experience': {'Skill': [], 'Experience': []},
            'Certs/Licenses': {'Cert/License': []},
            'Languages': {'Language': []}
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
        if path.exists(self._input_file):
            with open(self._input_file) as f:
                for field, value in load(f).items():
                    self._user_input[field]['Variable'].set(value)
        self._crawler_instance_args = {
            'number_of_jobs': 0,
            'auto_answer_questions': True,
            'manually_fill_out_questions': False,
            'default_q_and_a': {},
            'debug': False
            }
        self._crawler_search_args = {
            'query': '',
            'enforce_query': False,
            'job_title_negate_lst': [],
            'company_name_negate_lst': [],
            'job_type': '',
            'min_salary': '',
            'enforce_salary': False,
            'exp_lvl': '',
            'country': '',
            'location': ''
        }
        self._log_box: Text
        self._root_frame = Frame(root_window_)
        self._root_frame.pack(expand=True)
        self._start_button = Button(self._root_frame, command=self._start_crawling)
        self._start_button.configure(state='disable')
        self._user_form(0, 0, 13, 7, 25, 'nesw')
        for field in self._required_input:
            self._user_input[field]['Variable'].trace_add('write', self._toggle_start_button)

    def _entry_box(
            self, root_frame: Frame, default_text: str, width: int, row: int, col: int,
            padx: int, pady: int, sticky: str, colspan=1, secure=False, regex = '') -> Entry:
        def bind_clear_default(*args) -> None:
            if (entry.get() == default_text) or (entry.get() == 'INVALID'):
                entry.config(textvariable=var)
                entry.config(fg='black')
                if secure:
                    entry.config(show='*')
            return None
        def bind_on_focus_out(*args) -> None:
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
            var = StringVar()
        entry = Entry(root_frame, textvariable=var, width=width)
        entry.grid(row=row, column=col, columnspan=colspan, padx=padx, pady=pady, sticky=sticky)
        entry.config(textvariable='')
        entry.insert(0, default_text)
        entry.config(fg='grey')
        entry.bind('<FocusIn>', bind_clear_default)
        entry.bind('<FocusOut>', bind_on_focus_out)
        if default_text in self._required_input:
            var.trace_add('write', self._toggle_start_button)
            entry.config({'background': 'yellow'})
        return entry

    def _add_entry(self, root_frame: Frame, field: str, width: int,
            row: int, col: int, padx: int, pady: int, sticky: str) -> None:
        for i, (label, list_) in enumerate(self._widget_entries[field].items()):
            entry = self._entry_box(root_frame, f"{label} {len(list_) + 1}",
                width, row + len(list_), col + i, padx, pady, sticky)
            list_.append(entry)
        return None

    def _remove_entry(self, field: str) -> None:
        for _, list_ in self._widget_entries[field].items():
            if len(list_) > 1:
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
        for i, field in enumerate(self._user_input):
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
        Button(add_frame, text='Save Input', command=self._save_user_input).grid(row=0, column=1)
        return None

    def _save_user_input(self) -> None:
        with open(path.join(path.dirname(__file__), self._input_file), 'w') as f:
            dump({field: dict_['Variable'].get() for field, dict_ in self._user_input.items()}, f)
        return None

    def _setup_log_box(self, row: int, col: int, padx: int, pady: int, width: str, colspan: int) -> None:
        add_frame = Frame(self._root_frame)
        add_frame.grid(row=row, column=col, columnspan=colspan, padx=padx, pady=pady, sticky='nsew')
        self._log_box = Text(add_frame, height=10, width=colspan*width - padx)
        Label(add_frame, text='Crawler Log:').grid(row=0, column=0, sticky='w')
        scroll_bar = Scrollbar(add_frame, command=self._log_box.yview)
        self._log_box.config(yscrollcommand=scroll_bar.set)
        scroll_bar.grid(row=1, column=0, sticky='nse')
        self._log_box.grid(row=1, column=0, sticky="w")
        self._log_box.insert('end', 'Please fill out the above information. Required input is highlighted.')
        self._log_box.configure(state='disabled')
        return None

    def _toggle_start_button(self, *args) -> None:
        if all(self._user_input[field]['Variable'].get() for field in self._required_input):
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
        input_q_and_a = {}
        for field, dict_ in self._widget_entries.items():
            for label, list_ in dict_.items():
                for widget in list_:
                    for question in self._q_and_a[field]:
                        question = question.replace('[BLANK]', skill_name)
        
        q_and_a_copy = self._q_and_a.copy()
        for i in range(1, 4):
            if f'Skill {i}' in self._required_input:
                skill_name = self._required_input[f'Skill {i}'].get()
                for question in self._q_and_a['Skills']:
                    question = question.replace('[BLANK]', skill_name)
                    answer = self._required_input[f'Experience {i}'].get()
                    input_q_and_a[question] = answer
                for question in self._q_and_a['Skills Other']:
                    question = question.replace('[BLANK]', skill_name)
                    input_q_and_a[question] = 'Yes'
                if 'Skills' in q_and_a_copy:
                    del q_and_a_copy['Skills']
            if f'Language {i}' in self._required_input:
                language_name = self._required_input[f'Language {i}'].get()
                if not language_name:
                    language_name = 'English'
                for question in self._q_and_a['Language']:
                    question = question.replace('[BLANK]', language_name)
                    input_q_and_a[question] = 'Yes'
                if 'Language' in q_and_a_copy:
                    del q_and_a_copy['Language']
            if f'Cert/Lic {i}' in self._required_input:
                cert_name = self._required_input[f'Cert/Lic {i}'].get()
                for question in self._q_and_a['Certifications/Licenses']:
                    question = question.replace('[BLANK]', cert_name)
                    answer = self._required_input[f'Cert/Lic {i}'].get()
                    if not answer:
                        answer = 'No'
                    input_q_and_a[question] = answer
                if 'Certifications/Licenses' in q_and_a_copy:
                    del q_and_a_copy['Certifications/Licenses']
        search_country = self._required_input['Search Country'].get()
        if self._user_input['Req. Sponsorship'].get():
            answer = 'Yes'
        else:
            answer = 'No'
        for question in self._q_and_a['Req. Sponsorship']:
            question = question.replace('[BLANK]', search_country)
            input_q_and_a[question] = answer
        del q_and_a_copy['Req. Sponsorship']
        if self._user_input['Eligible to Work'].get():
            answer = 'Yes'
        else:
            answer = 'No'
        for question in self._q_and_a['Eligible to Work']:
            question = question.replace('[BLANK]', search_country)
            input_q_and_a[question] = answer
        del q_and_a_copy['Eligible to Work']
        answer = self._user_input['Clearance'].get()
        if not answer:
            answer = 'No clearance'
        for question in self._q_and_a['Clearance']:
            input_q_and_a[question] = answer
        del q_and_a_copy['Clearance']
        answer = ' '.join([self._required_input['First Name'].get(), self._required_input['Last Name'].get()])
        for question in self._q_and_a['Full Name']:
            input_q_and_a[question] = answer
        del q_and_a_copy['Full Name']
        answer = ', '.join(
            [self._required_input['City'].get(), self._required_input['State'].get()]
        )
        for question in self._q_and_a['Full Address']:
            input_q_and_a[question] = answer
        del q_and_a_copy['Full Address']
        answer = self._user_input['Country Code'].get()
        if not answer:
            answer = '1'
        for question in self._q_and_a['Country Code']:
            input_q_and_a[question] = answer
        del q_and_a_copy['Country Code']
        answer = self._user_input['LinkedIn'].get()
        if not answer:
            answer = 'No website'
        for question in self._q_and_a['LinkedIn']:
            input_q_and_a[question] = answer
        del q_and_a_copy['LinkedIn']
        answer = self._user_input['Website'].get()
        if not answer:
            answer = 'No website'
        for question in self._q_and_a['Website']:
            input_q_and_a[question] = answer
        del q_and_a_copy['Website']
        answer = self._user_input['Salary Type'].get()
        if not answer:
            answer = 'annual'
        for question in self._q_and_a['Salary Type']:
            input_q_and_a[question] = answer
        del q_and_a_copy['Salary Type']
        answer = self._user_input['Currency'].get()
        if not answer:
            answer = 'USD'
        for question in self._q_and_a['Currency']:
            input_q_and_a[question] = answer
        del q_and_a_copy['Currency']
        answer = self._user_input['Employment Type'].get()
        if not answer:
            answer = 'Fulltime'
        for question in self._q_and_a['Employment Type']:
            input_q_and_a[question] = answer
        del q_and_a_copy['Employment Type']
        answer = self._user_input['Hours per Week'].get()
        if not answer:
            answer = '40'
        for question in self._q_and_a['Hours per Week']:
            input_q_and_a[question] = answer
        del q_and_a_copy['Hours per Week']
        answer = self._user_input['Start Date'].get()
        if not answer:
            answer = date.today().strftime('%m/%d/%y')
        for question in self._q_and_a['Start Date']:
            input_q_and_a[question] = answer
        del q_and_a_copy['Start Date']
        answer = self._user_input['Interview Date & Time'].get()
        if not answer:
            answer = 'Anytime'
        for question in self._q_and_a['Interview Date & Time']:
            input_q_and_a[question] = answer
        del q_and_a_copy['Interview Date & Time']
        answer = self._user_input['18 Years or Older'].get()
        if answer:
            answer = 'Yes'
        else:
            answer = 'No'
        for question in self._q_and_a['18 Years or Older']:
            input_q_and_a[question] = answer
        del q_and_a_copy['18 Years or Older']
        for question, answer in self._q_and_a['Private'].items():
            input_q_and_a[question] = answer
        del q_and_a_copy['Private']
        for question_key in q_and_a_copy:
            if question_key in self._required_input:
                answer = self._required_input[question_key].get()
            else:
                answer = self._user_input[question_key].get()
            if not answer:
                answer = 'Prefer not to say'
            for question in q_and_a_copy[question_key]:
                input_q_and_a[question] = answer
        run_crawler = RunCrawler(
            email=self._required_input['Indeed Login'].get(),
            password=self._required_input['Indeed Password'].get(),
            total_number_of_jobs=self._required_input['Number of Jobs'].get(),
            queries=[
                query.strip()
                for query in self._required_input['Search Job(s) (Comma Separated)'].get().split(',')
            ],
            places=[
                (location.strip(), self._required_input['Search Country'].get().lower())
                for location in self._user_input['Search State(s)/Region(s) (Comma Separated)'].get().split(',')
            ],
            negate_jobs_list=[
                negate_job.strip() for negate_job in self._user_input['Word(s) or Phrase(s) to Avoid (Comma Separated)'].get().split(',')
            ],
            negate_companies_list=[
                negate_comp.strip() for negate_comp in self._user_input['Companies to Avoid (Comma Separated)'].get().split(',')
            ],
            min_salary=self._user_input['Desired Salary'].get(),
            default_q_and_a=input_q_and_a,
            log_box=self._log_box
        )
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

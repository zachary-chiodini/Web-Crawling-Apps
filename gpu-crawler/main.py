import tkinter as tk
from form import Form
from threading import Thread
from PIL import ImageTk, Image
from bestbuycrawler import BestBuyCrawler
from typing import Callable, Dict, List

COOL_ROBOT_EMOJI = 'gpu-crawler//icon//cool_robot_emoji.ico'
COOL_GLASSES_EMOJI = 'gpu-crawler//icon//cool_glasses.png'


class App:

    def __init__(self, main_window: tk.Tk):
        self.started = False
        self.terminated = True
        self.threads = []
        self.form = Form()
        self.bestbuycrawler = BestBuyCrawler(self.form.bestbuy, self.log)
        self.amd_window = tk.Toplevel()
        self.amd_window.destroy()
        self.bestbuy_window = tk.Toplevel()
        self.bestbuy_window.destroy()
        self.main_window = main_window
        main_frame = tk.Frame(main_window)
        main_frame.pack(expand=True)
        tk.Label(main_frame, text='Welcome to the GPU Crawler.')\
            .grid(row=0, column=0, padx=10, pady=10)
        selection = tk.Frame(main_frame)
        selection.grid(row=1, column=0)
        self.amd_btn = tk.Checkbutton
        self.amazon_btn = tk.Checkbutton
        self.bestbuy_btn = tk.Checkbutton
        self.website_selection(selection, 0, 0, 10, 10)
        tk.Label(main_frame, text='Crawler Log:')\
            .grid(row=2, column=0, sticky='w', padx=10, pady=(10, 0))
        self.log_box = tk.Text(main_frame, height=5, width=60)
        self.log_display(main_frame, 3, 0, 10, 10)
        start_stop = tk.Frame(main_frame)
        start_stop.grid(row=4, column=0, sticky='e')
        self.strt_btn = tk.Button(
            start_stop, text='Start Crawling', state='disable',
            command=self.start)
        self.strt_btn.grid(row=1, column=1, padx=10, pady=10)
        self.stop_btn = tk.Button(
            start_stop, text='Terminate', state='disable',
            command=self.stop)
        self.stop_btn.grid(row=1, column=2, padx=10, pady=10)

    def disable_strt_btn(self, *args) -> None:
        if any(map(
                lambda var: var.get() == 'complete',
                [self.form.amd['filled out']['status'],
                 self.form.amazon['filled out']['status'],
                 self.form.bestbuy['filled out']['status']]
        )):
            self.strt_btn.configure(state='normal')
        else:
            self.strt_btn.configure(state='disable')
        return None

    def website_selection(self, frame: tk.Frame, row, col, padx, pady) -> None:
        tk.Label(
            frame, text='Select Website'
        ).grid(row=row, column=col, columnspan=3, sticky='w',
               padx=padx, pady=pady)
        self.amd_btn = tk.Checkbutton(
            frame, text='AMD', state='disable',
            variable=self.form.amd['select']['checked'],
            command=self.website_selection_actions
        )
        self.amd_btn.grid(row=row + 1, column=col + 1, sticky='w',
                          padx=padx, pady=pady)
        self.amazon_btn = tk.Checkbutton(
            frame, text='Amazon', state='disable',
            variable=self.form.amazon['select']['checked'],
            command=self.website_selection_actions
        )
        self.amazon_btn.grid(row=row + 1, column=col + 2,
                             sticky='w', padx=padx, pady=pady)
        self.bestbuy_btn = tk.Checkbutton(
            frame, text='Best Buy',
            variable=self.form.bestbuy['select']['checked'],
            command=self.website_selection_actions
        )
        self.bestbuy_btn.grid(row=row + 1, column=col + 3,
                              sticky='w', padx=padx, pady=pady)
        return None

    def log_display(self, frame: tk.Frame, row, col, padx, pady) -> None:
        scroll_bar = tk.Scrollbar(frame, command=self.log_box.yview)
        self.log_box.config(yscrollcommand=scroll_bar.set)
        scroll_bar.grid(column=col, sticky='nse', pady=(0, pady))
        self.log_box.grid(row=row, column=col,
                          padx=padx, pady=(0, pady))
        self.log_box.insert('end', 'Please select which website(s) to crawl.')
        self.log_box.configure(state='disabled')
        return None

    def log(self, string) -> None:
        self.log_box.configure(state='normal')
        self.log_box.delete(1.0, 'end')
        self.log_box.insert('end', string)
        self.log_box.configure(state='disabled')
        return None

    def address_form(self, frame: tk.Frame, form_type: Dict,
                     title: str, key: str, col: int,
                     padx=0, pady=0) -> None:
        tk.Label(frame, text=title).grid(
            row=1, column=col, sticky='w',
            padx=padx, pady=pady
        )
        tk.Label(frame, text='Street Address').grid(
            row=2, column=col, sticky='w',
            padx=padx, pady=pady
        )
        tk.Entry(
            frame,
            textvariable=form_type[key]['street1']
        ).grid(row=3, column=col, sticky='w',
               padx=padx, pady=pady)
        tk.Entry(
            frame,
            textvariable=form_type[key]['street2']
        ).grid(row=4, column=col, sticky='w',
               padx=padx, pady=pady)
        tk.Label(frame, text='City').grid(
            row=5, column=col, sticky='w',
            padx=padx, pady=pady
        )
        tk.Entry(
            frame,
            textvariable=form_type[key]['city']
        ).grid(row=6, column=col, sticky='w',
               padx=padx, pady=pady)
        tk.Label(frame, text='State').grid(
            row=7, column=col, sticky='w',
            padx=padx, pady=pady
        )
        tk.Entry(
            frame,
            textvariable=form_type[key]['state']
        ).grid(row=8, column=col, sticky='w',
               padx=padx, pady=pady)
        tk.Label(frame, text='Zip Code').grid(
            row=9, column=col, sticky='w',
            padx=padx, pady=pady
        )
        tk.Entry(
            frame,
            textvariable=form_type[key]['zip code']
        ).grid(row=10, column=col, sticky='w',
               padx=padx, pady=pady)
        return None

    def set_character_limit(self, var, limit) -> None:
        def character_limit(*args) -> None:
            value = var.get()
            if len(value) > limit:
                var.set(value[: limit])
            return None

        var.trace_add('write', character_limit)
        return None

    def set_force_int(self, var, commas=False) -> None:
        def force_int(*args) -> None:
            value = var.get()
            for indx, char in enumerate(value):
                if char and not char.isdigit():
                    if commas:
                        if char != ',':
                            var.set(value[: indx])
                            break
                    else:
                        var.set(value[: indx])
                        break
            return None

        var.trace_add('write', force_int)
        return None

    def security_code(self, frame: tk.Frame, form_type: Dict,
                      row: int, col: int, padx=0, pady=0) -> None:
        tk.Label(frame, text='CC Security Code').grid(
            row=row, column=col, padx=padx, pady=pady
        )
        self.set_character_limit(
            form_type['credit card']['security code'], 3
        )
        self.set_force_int(
            form_type['credit card']['security code']
        )
        code_var = form_type['credit card']['security code']
        code_wdgt = tk.Entry(frame, width=3)
        code_wdgt.grid(row=row + 1, column=col,
                       padx=padx, pady=pady)
        self.display_default_text(code_var, '000', code_wdgt, True)
        return None

    def credit_card_form(self, frame: tk.Frame, form_type: Dict,
                         title: str, col: int, padx=0, pady=0) -> None:
        tk.Label(frame, text=title).grid(
            row=1, column=col, columnspan=5, sticky='w',
            padx=padx, pady=pady
        )
        tk.Label(frame, text='Name on Card').grid(
            row=2, column=col, columnspan=5, sticky='w',
            padx=padx, pady=pady
        )
        tk.Entry(
            frame,
            textvariable=form_type['credit card']['name']
        ).grid(row=3, column=col, columnspan=5, sticky='w',
               padx=padx, pady=pady)
        tk.Label(frame, text='Card Number').grid(
            row=4, column=col, columnspan=5, sticky='w',
            padx=padx, pady=pady
        )
        tk.Entry(
            frame,
            textvariable=form_type['credit card']['number'],
            show='*'
        ).grid(row=5, column=col, columnspan=5, sticky='w',
               padx=padx, pady=pady)
        tk.Label(frame, text='Expiration Date').grid(
            row=6, column=col, columnspan=5, sticky='w',
            padx=padx, pady=pady
        )
        tk.Label(frame, text='MM').grid(
            row=7, column=col, columnspan=2, sticky='w',
            padx=(padx, 0), pady=pady
        )
        tk.Label(frame, text='DD').grid(
            row=7, column=col + 2, columnspan=2, sticky='w',
            pady=pady
        )
        tk.Label(frame, text='YYYY').grid(
            row=7, column=col + 4, sticky='w',
            pady=pady
        )
        tk.Label(frame, text='/').grid(
            row=8, column=col + 1, sticky='w',
            pady=pady
        )
        tk.Label(frame, text='/').grid(
            row=8, column=col + 3, sticky='w',
            pady=pady
        )
        self.set_character_limit(
            form_type['credit card']['month'], 2
        )
        tk.Entry(
            frame,
            textvariable=form_type['credit card']['month'],
            width=2
        ).grid(row=8, column=col, sticky='w',
               padx=(padx, 0), pady=pady)
        self.set_character_limit(
            form_type['credit card']['day'], 2
        )
        tk.Entry(
            frame,
            textvariable=form_type['credit card']['day'],
            width=2
        ).grid(row=8, column=col + 2, sticky='w',
               pady=pady)
        self.set_character_limit(
            form_type['credit card']['year'], 4
        )
        tk.Entry(
            frame,
            textvariable=form_type['credit card']['year'],
            width=4
        ).grid(row=8, column=col + 4, sticky='w',
               pady=pady)
        tk.Label(frame, text='Security Code').grid(
            row=9, column=col, columnspan=5, sticky='w',
            padx=padx, pady=pady
        )
        self.set_character_limit(
            form_type['credit card']['security code'], 3
        )
        tk.Entry(
            frame,
            textvariable=form_type['credit card']['security code'],
            show='*',
            width=3
        ).grid(row=10, column=col, columnspan=5, sticky='w',
               padx=padx, pady=pady)
        return None

    def form_trace_remove(self, form_type: Dict) -> None:
        for key in form_type:
            for value in form_type[key].values():
                if isinstance(value, (tk.IntVar, tk.StringVar)):
                    for trace in value.trace_info():
                        value.trace_remove(*trace)
                elif isinstance(value, Callable):
                    continue
                else:
                    for nested_value in value.values():
                        for trace in nested_value.trace_info():
                            nested_value.trace_remove(*trace)
        return None

    def on_exit(self, window: tk.Toplevel, form_type: Dict,
                canceled: bool, *args) -> None:
        self.form_trace_remove(form_type)
        window.destroy()
        if canceled:
            form_type['select']['checked'].set(0)
            self.website_selection_log()
        else:
            form_type['filled out']['status'].set('complete')
            self.strt_btn.configure(state='normal')
        return None

    def button_state(self, form_type: Dict,
                     button: tk.Button, *args) -> None:
        for key in form_type:
            for value in form_type[key].values():
                if isinstance(value, (tk.IntVar, tk.StringVar)):
                    if not value.get():
                        button.configure(state='disabled')
                        return
                elif isinstance(value, Callable):
                    if not value():
                        button.configure(state='disabled')
                        return
        button.configure(state='normal')
        return

    def ok_or_cancel_buttons(
            self, frame: tk.Frame, window: tk.Toplevel, form_type: Dict,
            row: int, colspan: int, padx: int, pady: int
            ) -> None:
        def form_trace_callback(*args) -> None:
            self.button_state(form_type, cool_glasses)
            return None

        frame = tk.Frame(frame)
        frame.grid(row=row, column=1,
                   columnspan=colspan, sticky='e')
        cool_glasses = tk.Button(
            frame,
            command=(
                lambda *args, win=window, form=form_type, can=False:
                self.on_exit(win, form, can, *args)
            )
        )
        image = ImageTk.PhotoImage(Image.open(COOL_GLASSES_EMOJI))
        cool_glasses.image = image
        cool_glasses.configure(image=image)
        cool_glasses.grid(row=row, column=1,
                          padx=padx, pady=pady)
        self.button_state(form_type, cool_glasses)
        for key in form_type:
            for value in form_type[key].values():
                if isinstance(value, (tk.IntVar, tk.StringVar)):
                    value.trace_add('write', form_trace_callback)
                elif isinstance(value, Callable):
                    continue
                else:
                    for nested_value in value.values():
                        nested_value.trace_add('write', form_trace_callback)
        tk.Button(
            frame, text='Cancel', command=(
                lambda *args, win=window, form=form_type, can=True:
                self.on_exit(win, form, can, *args)
            )
        ).grid(row=row, column=2, sticky='nesw',
               padx=padx, pady=pady)
        return None

    def display_default_text(self, var, default_text,
                             widget, secure) -> None:
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

    def login_form(self, frame, form_type, key,
                   row, col, padx, pady) -> None:
        tk.Label(frame, text='Email').grid(
            row=row, column=col, sticky='w',
            padx=padx, pady=pady
        )
        usr_var = form_type[key]['username']
        usr_wdgt = tk.Entry(frame, width=30)
        usr_wdgt.grid(row=row + 1, column=col, sticky='w',
                      padx=padx, pady=pady)
        self.display_default_text(usr_var, 'username@domain.com',
                                  usr_wdgt, False)
        tk.Label(frame, text='Password').grid(
            row=row, column=col + 1, sticky='w',
            padx=padx, pady=pady
        )
        pas_var = form_type[key]['password']
        pas_wdgt = tk.Entry(frame, width=30)
        pas_wdgt.grid(row=row + 1, column=col + 1, sticky='w',
                      padx=padx, pady=pady)
        self.display_default_text(pas_var, 'password', pas_wdgt, True)
        self.security_code(frame, form_type, row, col + 2, padx, pady)
        return None

    def on_delete(self, window: tk.Toplevel, form_type: Dict) -> None:
        def on_exit(*args) -> None:
            self.on_exit(window, form_type, True, *args)
            return None

        window.protocol('WM_DELETE_WINDOW', on_exit)
        return None

    def open_amd_form(self) -> None:
        self.amd_window = tk.Toplevel(self.main_window)
        self.amd_window.geometry('450x300')
        self.amd_window.title('AMD Login Form')
        self.amd_window.iconbitmap(COOL_ROBOT_EMOJI)
        frame = tk.Frame(self.amd_window)
        frame.pack(expand='True')
        self.address_form(
            frame, self.form.amd,
            'Shipping Information', 'shipping', 1, 10, 1
        )
        self.address_form(
            frame, self.form.amd,
            'Billing Information', 'billing', 2, 10, 1
        )
        self.credit_card_form(
            frame, self.form.amd,
            'Credit Card Information', 3, 10, 1
        )
        self.ok_or_cancel_buttons(
            frame, self.amd_window, self.form.amd, 11, 7, 10, 17
        )
        self.on_delete(self.amd_window, self.form.amd)
        return None

    def model_selection(self, frame: tk.Frame, row, col, padx, pady) -> None:
        def set_display_default_text_on_click(
                check_var, str_var, default_text, widget, secure
        ) -> None:
            def display_default_text_on_click(*args) -> None:
                if check_var.get():
                    widget.config(state='normal')
                    self.display_default_text(str_var, default_text,
                                              widget, secure)
                else:
                    widget.config(textvariable='')
                    widget.delete(0, 'end')
                    widget.insert(0, '')
                    widget.config(state='disable')
                return None

            check_var.trace_add('write', display_default_text_on_click)
            return None

        tk.Label(
            frame, text='Model Selection'
        ).grid(row=row, column=col, sticky='w',
               padx=padx, pady=pady)
        # ids widget is to the right of check button
        ids_var = self.form.bestbuy['search by'] \
            ['sku id']['ids']
        ids_wdgt = tk.Entry(frame, width=25)
        ids_wdgt.grid(row=row + 1, column=col + 1, columnspan=5,
                      padx=padx, pady=pady)
        ids_checked = self.form.bestbuy['search by'] \
            ['sku id']['checked']
        # checkbutton enables ids widget
        ids_btn = tk.Checkbutton(frame, text='By SKU ID',
                                 variable=ids_checked)
        ids_btn.grid(row=row + 1, column=col, sticky='w',
                     padx=padx, pady=pady)
        self.set_force_int(ids_var, commas=True)
        if ids_checked.get():
            self.display_default_text(ids_var, 'Comma-separated SKU IDs',
                                      ids_wdgt, False)
        else:
            ids_wdgt.configure(state='disable')
        set_display_default_text_on_click(
            ids_checked, ids_var, 'Comma-separated SKU IDs',
            ids_wdgt, False
        )
        # price widgets are to the right of check button
        tk.Label(
            frame, text='$'
        ).grid(row=row + 2, column=col + 1,
               padx=(padx, 0), pady=pady
               )
        min_var = self.form.bestbuy['search by'] \
            ['price range']['min']
        min_wdgt = tk.Entry(frame, width=6)
        min_wdgt.grid(row=row + 2, column=col + 2,
                      padx=0, pady=pady)
        tk.Label(frame, text='-').grid(
            row=row + 2, column=col + 3, padx=0, pady=pady
        )
        tk.Label(frame, text='$').grid(
            row=row + 2, column=col + 4, padx=0, pady=pady
        )
        max_var = self.form.bestbuy['search by'] \
            ['price range']['max']
        max_wdgt = tk.Entry(frame, width=6)
        max_wdgt.grid(row=row + 2, column=col + 5,
                      padx=(0, padx), pady=pady)
        prc_checked = self.form.bestbuy['search by'] \
            ['price range']['checked']
        # checkbutton enables price widgets
        prc_btn = tk.Checkbutton(frame, text='By Price Range',
                                 variable=prc_checked)
        prc_btn.grid(row=row + 2, column=col, sticky='w',
                     padx=padx, pady=pady)
        self.set_force_int(min_var)
        self.set_force_int(max_var)
        if prc_checked.get():
            self.display_default_text(min_var, '000000', min_wdgt, False)
            self.display_default_text(max_var, '000000', max_wdgt, False)
        else:
            min_wdgt.configure(state='disable')
            max_wdgt.configure(state='disable')
        set_display_default_text_on_click(prc_checked, min_var,
                                          '000000', min_wdgt, False)
        set_display_default_text_on_click(prc_checked, max_var,
                                          '000000', max_wdgt, False)
        # sku id and price widget is to the right of check button
        pps_ids_var = self.form.bestbuy['search by'] \
            ['price per sku id']['ids']
        pps_ids_wdgt = tk.Entry(frame, width=25)
        pps_ids_wdgt.grid(row=row + 3, column=col + 1, columnspan=5,
                          padx=padx, pady=(pady, 0))
        pps_prc_var = self.form.bestbuy['search by'] \
            ['price per sku id']['prices']
        pps_prc_wdgt = tk.Entry(frame, width=25)
        pps_prc_wdgt.grid(row=row + 4, column=col + 1, columnspan=5,
                          padx=padx, pady=(0, pady))
        pps_checked = self.form.bestbuy['search by'] \
            ['price per sku id']['checked']
        # checkbutton enables sku id and price widget
        pps_btn = tk.Checkbutton(frame, text='By Price Per Sku ID',
                                 variable=pps_checked)
        pps_btn.grid(row=row + 3, rowspan=2, column=col, sticky='w',
                     padx=padx, pady=pady)
        self.set_force_int(pps_ids_var, commas=True)
        self.set_force_int(pps_prc_var, commas=True)
        if pps_checked.get():
            self.display_default_text(
                pps_ids_var, 'Comma-separated SKU IDs', pps_ids_wdgt, False
            )
            self.display_default_text(
                pps_prc_var, 'Comma-separated prices', pps_prc_wdgt, False
            )
        else:
            pps_ids_wdgt.configure(state='disable')
            pps_prc_wdgt.configure(state='disable')
        set_display_default_text_on_click(
            pps_checked, pps_ids_var, 'Comma-separated SKU IDs',
            pps_ids_wdgt, False
        )
        set_display_default_text_on_click(
            pps_checked, pps_prc_var, 'Comma-separated prices',
            pps_prc_wdgt, False
        )
        return None

    def page_selection(self, frame: tk.Frame, form_type: Dict,
                       row, col, padx, pady) -> None:
        tk.Label(frame, text='Crawl Pages').grid(
            row=row, column=col, columnspan=3, sticky='w',
            padx=padx, pady=pady
        )
        strt_var = form_type['settings']['page start']
        strt_wdgt = tk.Entry(frame, width=2)
        strt_wdgt.grid(row=row + 1, column=col,
                       padx=(padx, 0), pady=pady)
        self.set_character_limit(strt_var, 2)
        self.set_force_int(strt_var)
        self.display_default_text(strt_var, '00', strt_wdgt, False)
        tk.Label(frame, text='-').grid(
            row=row + 1, column=col + 1, padx=0, pady=pady
        )
        stop_var = form_type['settings']['page stop']
        stop_wdgt = tk.Entry(frame, width=2)
        stop_wdgt.grid(row=row + 1, column=col + 2,
                       padx=(0, padx), pady=pady)
        self.set_character_limit(stop_var, 2)
        self.set_force_int(stop_var)
        self.display_default_text(stop_var, '00', stop_wdgt, False)
        return None

    def budget(self, frame: tk.Frame, form_type: Dict,
               row, col, padx, pady) -> None:
        tk.Label(frame, text='Budget').grid(
            row=row, column=col, columnspan=2, sticky='w',
            padx=padx, pady=pady
        )
        tk.Label(frame, text='$').grid(
            row=row + 1, column=col,
            padx=(padx, 0), pady=pady
        )
        bgt_var = form_type['settings']['budget']
        bgt_wdgt = tk.Entry(frame, width=8)
        bgt_wdgt.grid(row=row + 1, column=col + 1,
                      padx=(0, padx), pady=pady)
        self.display_default_text(bgt_var, '00000000', bgt_wdgt, False)
        self.set_force_int(bgt_var)
        return None

    def open_bestbuy_form(self) -> None:
        self.bestbuy_window = tk.Toplevel(self.main_window)
        self.bestbuy_window.geometry('570x425')
        self.bestbuy_window.title('Best Buy Login Form')
        self.bestbuy_window.iconbitmap(COOL_ROBOT_EMOJI)
        frame = tk.Frame(self.bestbuy_window)
        frame.pack(expand=True)
        self.login_form(frame, self.form.bestbuy, 'login', 0, 0, 10, 10)
        subframe = tk.Frame(frame)
        subframe.grid(row=2, column=0, columnspan=3, sticky='w')
        self.page_selection(subframe, self.form.bestbuy, 0, 0, 10, 10)
        tk.Label(
            subframe,
            text='|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|'
        ).grid(
            row=0, column=4, rowspan=5, padx=10, pady=10
        )
        self.model_selection(subframe, 0, 5, 10, 10)
        tk.Label(
            subframe,
            text='|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|'
        ).grid(
            row=0, column=11, rowspan=5, padx=10, pady=10
        )
        self.budget(subframe, self.form.bestbuy, 0, 12, 10, 10)
        self.ok_or_cancel_buttons(frame, self.bestbuy_window,
                                  self.form.bestbuy, 3, 3, 10, 17)
        self.on_delete(self.bestbuy_window, self.form.bestbuy)
        return None

    def form_actions(self, form_type: Dict, window: tk.Toplevel,
                     call_window: Callable) -> None:
        # makes form incomplete when selection is unchecked
        if not form_type['select']['checked'].get():
            form_type['filled out']['status'].set('incomplete')
        # prevents form from opening repeatedly
        if (form_type['select']['checked'].get() and
                not window.winfo_exists() and
                form_type['filled out']['status'].get() == 'incomplete'):
            call_window()
        # makes form close when selection is unchecked
        elif not form_type['select']['checked'].get() and window.winfo_exists():
            self.form_trace_remove(form_type)
            window.destroy()
            form_type['select']['checked'].set(0)
        return None

    def website_selection_actions(self) -> None:
        self.form_actions(self.form.amd, self.amd_window,
                          self.open_amd_form)
        self.form_actions(self.form.bestbuy, self.bestbuy_window,
                          self.open_bestbuy_form)
        if self.started:
            return
        self.disable_strt_btn()
        self.website_selection_log()
        return None

    def website_selection_log(self) -> None:
        any_selected = (
                self.form.amd['select']['checked'].get() or
                self.form.amazon['select']['checked'].get() or
                self.form.bestbuy['select']['checked'].get()
        )
        all_selected = (
                self.form.amd['select']['checked'].get() and
                self.form.amazon['select']['checked'].get() and
                self.form.bestbuy['select']['checked'].get()
        )
        amd_and_amazon_not_bestbuy = (
                self.form.amd['select']['checked'].get() and
                self.form.amazon['select']['checked'].get() and
                not self.form.bestbuy['select']['checked'].get()
        )
        amd_or_amazon_and_bestbuy = (
                (self.form.amd['select']['checked'].get() or
                 self.form.amazon['select']['checked'].get())
                and self.form.bestbuy['select']['checked'].get()
        )
        selection = (
            any_selected * (
                'You have selected to crawl '
                + self.form.amd['select']['checked'].get() * 'AMD'
                + amd_and_amazon_not_bestbuy * ' and '
                + all_selected * ', '
                + self.form.amazon['select']['checked'].get() * 'Amazon'
                + amd_or_amazon_and_bestbuy * ' and '
                + self.form.bestbuy['select']['checked'].get() * 'Best Buy'
                + '.'
                )
            + (not any_selected)
            * 'Please select which website(s) to crawl.'
            )
        self.log(selection)
        return None

    def start_bestbuy_crawler(self) -> None:
        try:
            self.bestbuycrawler.setup_crawler()
            self.bestbuycrawler.login_crawler()
            while self.started:
                page_start = int(self.form.bestbuy['settings']['page start'])
                page_stop = int(self.form.bestbuy['settings']['page stop'])
                for page in range(page_start, page_stop + 1):
                    if self.terminated:
                        break
                    html = self.bestbuycrawler.search_gpus(page)
                    self.bestbuycrawler.scrape_page(html)
        except Exception as e:
            self.log(str(e))
            self.stop(exception=True)
        return None

    def start(self) -> None:
        self.started = True
        self.terminated = False
        self.stop_btn.configure(state='normal')
        self.strt_btn.configure(state='disable')
        self.amd_btn.configure(state='disable')
        self.amazon_btn.configure(state='disable')
        self.bestbuy_btn.configure(state='disable')
        self.log('GPU Crawler has started.')
        if self.form.bestbuy['filled out']['status'] == 'complete':
            separate_thread = Thread(target=self.start_bestbuy_crawler)
            self.threads.append(separate_thread)
            separate_thread.start()
        return None

    def stop(self, exception=False) -> None:
        self.started = False
        self.terminated = True
        self.stop_btn.configure(state='disable')
        if not exception:
            self.log('Waiting for threads to close ...')
            for separate_thread in self.threads:
                separate_thread.join()
            self.log('GPU Crawler has terminated.')
        self.bestbuycrawler.close()
        self.strt_btn.configure(state='normal')
        self.amd_btn.configure(state='normal')
        self.amazon_btn.configure(state='normal')
        self.bestbuy_btn.configure(state='normal')
        return None


if __name__ == '__main__':
    main = tk.Tk()
    main.geometry('550x300')
    main.title('GPU Crawler')
    main.iconbitmap(COOL_ROBOT_EMOJI)
    App(main)
    main.mainloop()

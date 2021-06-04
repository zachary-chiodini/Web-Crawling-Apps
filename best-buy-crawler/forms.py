import tkinter as tk
import guifunctions as gui
from typing import Dict


def address(
        frame: tk.Frame, input_type: Dict,
        title: str, key: str, col: int, padx=0, pady=0
        ) -> None:
    tk.Label(frame, text=title) \
        .grid(row=1, column=col, sticky='w', padx=padx, pady=pady)
    tk.Label(frame, text='Street Address') \
        .grid(row=2, column=col, sticky='w', padx=padx, pady=pady)
    tk.Entry(frame, textvariable=input_type[key]['street1']) \
        .grid(row=3, column=col, sticky='w', padx=padx, pady=pady)
    tk.Entry(frame, textvariable=input_type[key]['street2']) \
        .grid(row=4, column=col, sticky='w', padx=padx, pady=pady)
    tk.Label(frame, text='City') \
        .grid(row=5, column=col, sticky='w', padx=padx, pady=pady)
    tk.Entry(frame, textvariable=input_type[key]['city']) \
        .grid(row=6, column=col, sticky='w', padx=padx, pady=pady)
    tk.Label(frame, text='State') \
        .grid(row=7, column=col, sticky='w', padx=padx, pady=pady)
    tk.Entry(frame, textvariable=input_type[key]['state']) \
        .grid(row=8, column=col, sticky='w', padx=padx, pady=pady)
    tk.Label(frame, text='Zip Code').grid(
        row=9, column=col, sticky='w', padx=padx, pady=pady)
    tk.Entry(frame, textvariable=input_type[key]['zip code']) \
        .grid(row=10, column=col, sticky='w', padx=padx, pady=pady)
    return None


def credit_card(frame: tk.Frame, form_type: Dict,
                title: str, col: int, padx=0, pady=0) -> None:
    tk.Label(frame, text=title)\
        .grid(row=1, column=col, columnspan=5, sticky='w',
              padx=padx, pady=pady)
    tk.Label(frame, text='Name on Card')\
        .grid(row=2, column=col, columnspan=5, sticky='w',
              padx=padx, pady=pady)
    tk.Entry(frame, textvariable=form_type['credit card']['name'])\
        .grid(row=3, column=col, columnspan=5, sticky='w',
              padx=padx, pady=pady)
    tk.Label(frame, text='Card Number')\
        .grid(row=4, column=col, columnspan=5, sticky='w',
              padx=padx, pady=pady)
    tk.Entry(frame, textvariable=form_type['credit card']['number'],
             show='*')\
        .grid(row=5, column=col, columnspan=5, sticky='w',
              padx=padx, pady=pady)
    tk.Label(frame, text='Expiration Date')\
        .grid(row=6, column=col, columnspan=5, sticky='w',
              padx=padx, pady=pady)
    tk.Label(frame, text='MM')\
        .grid(row=7, column=col, columnspan=2, sticky='w',
              padx=(padx, 0), pady=pady)
    tk.Label(frame, text='DD')\
        .grid(row=7, column=col + 2, columnspan=2, sticky='w',
              pady=pady)
    tk.Label(frame, text='YYYY')\
        .grid(row=7, column=col + 4, sticky='w', pady=pady)
    tk.Label(frame, text='/')\
        .grid(row=8, column=col + 1, sticky='w', pady=pady)
    tk.Label(frame, text='/')\
        .grid(row=8, column=col + 3, sticky='w', pady=pady)
    gui.set_character_limit(form_type['credit card']['month'], 2)
    tk.Entry(frame, textvariable=form_type['credit card']['month'],
             width=2)\
        .grid(row=8, column=col, sticky='w', padx=(padx, 0),
              pady=pady)
    gui.set_character_limit(form_type['credit card']['day'], 2)
    tk.Entry(frame, textvariable=form_type['credit card']['day'],
             width=2).\
        grid(row=8, column=col + 2, sticky='w', pady=pady)
    gui.set_character_limit(form_type['credit card']['year'], 4)
    tk.Entry(frame, textvariable=form_type['credit card']['year'],
             width=4)\
        .grid(row=8, column=col + 4, sticky='w', pady=pady)
    tk.Label(frame, text='Security Code')\
        .grid(row=9, column=col, columnspan=5, sticky='w',
              padx=padx, pady=pady)
    gui.set_character_limit(form_type['credit card']['security code'], 3)
    tk.Entry(frame, textvariable=form_type['credit card']['security code'],
             show='*', width=3)\
        .grid(row=10, column=col, columnspan=5, sticky='w',
              padx=padx, pady=pady)
    return None

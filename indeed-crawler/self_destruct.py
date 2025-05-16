from tkinter import Button, Frame, Label, Tk
from webbrowser import open_new

from helper_funs import center

COOL_ROBOT_EMOJI = 'icon/cool_robot_emoji.ico'


class SelfDestruct:

    def __init__(self, program_title: str):
        self.program_title = program_title

    def open_window(self, message: str) -> None:
        window = Tk()
        window.geometry('250x100')
        window.title(self.program_title)
        window.iconbitmap(COOL_ROBOT_EMOJI)
        center(window)
        frame = Frame(window)
        frame.pack(expand=True)
        label = Label(frame, text=message, fg='red')
        label.pack()
        label = Label(frame, text='This robot has become obsolete.')
        label.pack()
        label = Label(frame, text='Visit Bionic Person Ent. for an updated copy.')
        label.pack()
        button = Button(frame, text='Request Copy',
                        command=lambda *args: open_new('https://www.fiverr.com/bionicperson'))
        button.pack()
        window.mainloop()

from json import load
from tkinter import StringVar, Tk

COOL_ROBOT_EMOJI = 'icon/cool_robot_emoji.ico'
COOL_GLASSES_EMOJI = 'icon/cool_glasses.png'


class App:
    
    def __init__(self, root_window_: Tk):
        self._root_window = root_window_
        self._user_input = {}
        self._private = {}
        self._assign_instance_vars()

    def _assign_instance_vars(self) -> None:
        with open('default_q_and_a.json') as json:
            q_and_a = load(json)
        self._private = q_and_a['Private']
        del q_and_a['Private']
        for question in q_and_a:
            self._user_input[question] = StringVar()
        return None


if __name__ == '__main__':
    root_window = Tk()
    root_window.geometry('')
    # root_window.resizable(True, True)
    root_window.title('Indeed Crawler')
    root_window.iconbitmap(COOL_ROBOT_EMOJI)
    App(root_window)
    root_window.mainloop()

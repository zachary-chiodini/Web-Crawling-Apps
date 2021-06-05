from tkinter import StringVar, IntVar


class Form:

    def __init__(self):
        self.amd = {
            'shipping': {
                'street1': StringVar(),
                'street2': StringVar(),
                'city': StringVar(),
                'state': StringVar(),
                'zip code': StringVar(),
                },
            'billing': {
                'street1': StringVar(),
                'street2': StringVar(),
                'city': StringVar(),
                'state': StringVar(),
                'zip code': StringVar(),
                },
            'credit card': {
                'name': StringVar(),
                'number': StringVar(),
                'month': StringVar(),
                'day': StringVar(),
                'year': StringVar(),
                'security code': StringVar()
                },
            'select': {
                'checked': IntVar()
                },
            'filled out': {
                'status': StringVar()
                }
            }
        self.amazon = {
            'login': {
                'username': StringVar(),
                'password': StringVar()
                },
            'select': {
                'checked': IntVar()
                },
            'filled out': {
                'status': StringVar()
                }
            }
        self.bestbuy = {
            'login': {
                'username': StringVar(),
                'password': StringVar()
                },
            'credit card': {
                'security code': StringVar()
                },
            'select': {
                'checked': IntVar()
                },
            'settings': {
                'page start': StringVar(),
                'page stop': StringVar(),
                'budget': StringVar(),
                'spent': StringVar(),
                },
            'search by': {
                'sku id': {
                    'checked': IntVar(),
                    'ids': StringVar()
                    },
                'price range': {
                    'checked': IntVar(),
                    'min': StringVar(),
                    'max': StringVar()
                    },
                'price per sku id': {
                    'checked': IntVar(),
                    'ids': StringVar(),
                    'prices': StringVar()
                    }
                },
            'filled out': {
                'status': StringVar()
                }
            }
        self.bestbuy['settings']['spent'].set('0')
        self.bestbuy['settings']['search'] = \
            self.bestbuy_search_selection
        self.amd['filled out']['status'].set('incomplete')
        self.amazon['filled out']['status'].set('incomplete')
        self.bestbuy['filled out']['status'].set('incomplete')

    def bestbuy_search_selection(self) -> int:
        sku_id = (self.bestbuy['search by']
                  ['sku id']['checked'].get())
        prices = (self.bestbuy['search by']
                  ['price range']['checked'].get())
        price_per_id = (self.bestbuy['search by']
                        ['price per sku id']['checked'].get())
        selection = sku_id or prices or price_per_id
        if sku_id:
            selection *= \
                bool(self.bestbuy['search by']
                     ['sku id']['ids'].get())
        if prices:
            selection *= \
                bool(self.bestbuy['search by']
                     ['price range']['min'].get())
            selection *= \
                bool(self.bestbuy['search by']
                     ['price range']['max'].get())
        if price_per_id:
            selection *= \
                bool(self.bestbuy['search by']
                     ['price per sku id']['ids'].get())
            selection *= \
                bool(self.bestbuy['search by']
                     ['price per sku id']['prices'].get())
        return selection

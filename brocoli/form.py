from six import print_
from six.moves import tkinter as tk
from six.moves import tkinter_ttk as ttk

import re

class FormField(object):
    def __init__(self, text = ''):
        self.text = text

    def from_string(self, s):
        raise NotImplementedError

    def to_string(self):
        raise NotImplementedError

    def get_widget(self, master):
        raise NotImplementedError

    def get_widgets(self, master):
        return tk.Label(master, text=self.text), self.get_widget(master)


class TextField(FormField):
    def __init__(self, text, default_value='', validate_command=None,
                 password_mode=False):
        super(TextField, self).__init__(text)
        self.var = tk.StringVar()
        self.var.set(default_value)
        self.validate_command = validate_command
        self.password_mode = password_mode

    def from_string(self, s):
        self.var.set(s)

    def to_string(self):
        return self.var.get()

    def get_widget(self, master):
        show=''
        if self.password_mode:
            show='*'

        entry = tk.Entry(master, textvariable=self.var, show=show)

        if self.validate_command is not None:
            vcmd = (master.register(self.validate_command), '%P')
            entry.config(validate='key', validatecommand=vcmd)

        return entry


class HostnameField(TextField):
    __hostname_re = re.compile('^([_\-\d\w]+(\.)?)*$')

    def __init__(self, text, default_value=''):
        super(HostnameField, self).__init__(text, default_value, self.validate)

    def validate(self, v):
        ok = self.__hostname_re.match(v) != None

        return ok


class PasswordField(TextField):
    def __init__(self, text, encode=lambda s: s, decode=lambda s: s):
        super(PasswordField, self).__init__(text, password_mode=True)

        self.encode = encode
        self.decode = decode

    def from_string(self, s):
        self.var.set(self.decode(s))

    def to_string(self):
        return self.encode(self.var.get())



class IntegerField(TextField):
    def validate(self, v):
        try:
            iv=int(v)
            return True
        except:
            pass

        return False

    def __init__(self, text, default_value=0):
        super(IntegerField, self).__init__(text, default_value, self.validate)


class BooleanField(FormField):
    def __init__(self, text, default_value=False):
        self.text = text
        self.var = tk.BooleanVar()
        self.var.set(default_value)

    def from_string(self, s):
        self.var.set(s)

    def to_string(self):
        return str(self.var.get())

    def get_widget(self, master):
        return tk.Checkbutton(master, text=self.text, variable=self.var,
                              onvalue=True, offvalue=False)

    def get_widgets(self, master):
        return (self.get_widget(master), )

class RadioChoiceField(FormField):
    def __init__(self, text, values, default_value = None, vertical=True):
        super(RadioChoiceField, self).__init__(text)

        self.values = values
        self.var = tk.StringVar()
        if default_value is None:
            default_value = values[0]

        self.var.set(default_value)

        self.side = tk.TOP
        if not vertical:
            self.side = tk.LEFT

    def from_string(self, s):
        self.var.set(s)

    def to_string(self):
        return self.var.get()

    def get_widget(self, master):
        frame = tk.Frame(master)

        for v in self.values:
            rb = tk.Radiobutton(frame, text=v, value=v, variable=self.var)
            rb.pack(side=self.side)

        return frame


class ComboboxChoiceField(FormField):
    def __init__(self, text, values, default_value=None):
        super(ComboboxChoiceField, self).__init__(text)

        self.values = values
        self.var = tk.StringVar()
        if default_value is None:
            default_value = values[0]

        self.var.set(default_value)

    def from_string(self, s):
        self.var.set(s)

    def to_string(self):
        return self.var.get()

    def get_widget(self, master):
        return ttk.Combobox(master, values=self.values, textvariable=self.var)

class FormFrame(tk.Frame):
    def grid_fields(self, fieldlist):
        i = 0
        for field in fieldlist:
            widgets = field.get_widgets(self)
            j = 0
            for w in widgets:
                w.grid(row=i, column=j)
                j += 1
            i += 1

if __name__ == '__main__':
    master = tk.Tk()

    hf = HostnameField('host:')

    e = hf.get_widget(master)
    e.pack()

    e.focus_set()

    bf = BooleanField('toto')
    b = bf.get_widget(master)
    b.pack()

    pf = PasswordField('pwd:')
    pe = pf.get_widget(master)
    pe.pack()

    if_ = IntegerField('integer:', 12)
    ie = if_.get_widget(master)
    ie.pack()

    rbc = RadioChoiceField('radiochoic:', ['one', 'two', 'three'], vertical=False)
    rb = rbc.get_widget(master)
    rb.pack()

    cbcf = ComboboxChoiceField('comboboxchoice:', ['yi', 'er', 'san'])
    cb = cbcf.get_widget(master)
    cb.pack()


    ff = FormFrame(master)
    ff.grid_fields([hf, bf, pf, if_, rbc, cbcf])
    ff.pack()
    master.mainloop()
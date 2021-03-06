"""
Preferences handling widgets
"""

from six import print_
from six.moves import tkinter as tk
from six.moves import tkinter_tksimpledialog as tksimpledialog
from six.moves import tkinter_ttk as ttk

import tempfile
import copy
import collections

from . import config
from . import form

class ConnectionConfigDialog(tksimpledialog.Dialog, object):
    """
    A dialog to configure connections
    """
    def __init__(self, master, connection_name='new-connection',
                 catalog_type=config.catalog_types[0],
                 root_path=tempfile.gettempdir(), isdefault=False,
                 catalog_config=None, **kwargs):
        self.connection_name = connection_name
        self.catalog_type = catalog_type
        self.root_path = root_path
        self.isdefault = isdefault
        self.catalog_config = catalog_config

        super(ConnectionConfigDialog, self).__init__(master, **kwargs)

    def body(self, master):
        tk.Label(master, text='Connection name:').grid(row=0)
        tk.Label(master, text='Catalog type:').grid(row=1)
        tk.Label(master, text='Root path:').grid(row=2)

        self.name = ttk.Entry(master)
        self.name.grid(row=0, column=1, sticky='ew')
        self.name.insert(0, self.connection_name)

        self.catalog_cbox = ttk.Combobox(master, values=config.catalog_types)
        self.catalog_cbox.grid(row=1, column=1, sticky='ew')
        self.catalog_cbox.set(self.catalog_type)

        self.root_path_entry = tk.Entry(master)
        self.root_path_entry.grid(row=2, column=1, sticky='ew')
        self.root_path_entry.insert(0, self.root_path)

        self.isdefault_var = tk.IntVar()
        self.isdefault_var.set(self.isdefault)
        self.set_default = tk.Checkbutton(master,
                                          text='make default connection',
                                          variable = self.isdefault_var)
        self.set_default.grid(row=3, column=1)

        self.catalog_config_frame = tk.Frame(master)
        self.catalog_config_frame.grid(row=4, sticky='nsew')

        self.catalog_type_changed(catalog_config=self.catalog_config)
        self.catalog_cbox.bind('<<ComboboxSelected>>', self.catalog_type_changed)

        self.result = None

    def apply(self):
        self.result = collections.OrderedDict([
            ('name', self.name.get()),
            ('catalog_type', self.catalog_cbox.get()),
            ('root_path', self.root_path_entry.get()),
            ('set_default', self.isdefault_var.get() != 0),
        ])

        config = collections.OrderedDict()
        for k, ff in self.config_fields.items():
            config[k] = ff.to_string()

        self.result.update(config)

    def to_config_dict(self):
        config = collections.OrderedDict()
        if self.result is None:
            return config

        new_conn = self.result
        name = new_conn['name']
        del new_conn['name']

        if new_conn['set_default']:
            config['SETTINGS'] = {'default_connection': name}
        del new_conn['set_default']

        config['connection:' + name] = new_conn

        return config

    def catalog_type_changed(self, event=None, catalog_config=None):
        catalog_type = self.catalog_cbox.get()
        self.config_fields = config.catalog_dict[catalog_type].config_fields()

        if catalog_config is not None:
            for k, ff in self.config_fields.items():
                if k in catalog_config:
                    ff.from_string(catalog_config[k])

        master = self.catalog_config_frame.master
        self.catalog_config_frame.grid_remove()
        self.catalog_config_frame = form.FormFrame(master)
        self.catalog_config_frame.grid_fields(self.config_fields.values())
        self.catalog_config_frame.grid(row=4, columnspan=2, sticky='nsew')


class ConnectionManager(tk.Frame):
    """
    Displays connections and allows to add, remove and edit them
    """
    def __init__(self, master, config_filename):
        tk.Frame.__init__(self, master)

        self.master = master
        self.config_filename = config_filename

        self.cfg = config.load_config(self.config_filename)
        self.old_cfg = copy.deepcopy(self.cfg)

        columns = ('catalog type', 'path', 'default connection')
        self.tree = ttk.Treeview(self, columns=columns,  selectmode='browse')

        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)

        self.tree.heading('#0', text='name', anchor='w')
        self.tree.heading('catalog type', text='catalog type', anchor='w')
        self.tree.heading('path', text='path', anchor='w')
        self.tree.heading('default connection', text='default connection',
                          anchor='w')

        self.insert_connections()

        self.tree.grid(row=0, column=0, sticky='nsew')
        ysb.grid(row=0, column=1, sticky='ns')
        xsb.grid(row=1, column=0, sticky='ew')

        butbox = tk.Frame(self)
        butbox.grid(row=0, column=2, sticky='ns')
        self.newbut = tk.Button(butbox, text='Add', command=self.add)
        self.newbut.grid(row=0, column=0, sticky='ew')
        self.removebut = tk.Button(butbox, text='Remove', command=self.remove,
                                   state=tk.DISABLED)
        self.removebut.grid(row=1, column=0, sticky='ew')
        self.editbut = tk.Button(butbox, text='Edit', command=self.edit,
                                 state=tk.DISABLED)
        self.editbut.grid(row=2, column=0, sticky='ew')

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.grid(sticky='nsew')

        self.tree.bind('<<TreeviewSelect>>', self.selchanged)

    def insert_connections(self):
        default = self.cfg['SETTINGS']['default_connection']

        for child in self.tree.get_children():
            self.tree.delete(child)

        for section in [s for s in self.cfg if s.startswith('connection:')]:
            conn = self.cfg[section]
            name = section.rsplit(':', 1)[1]
            isdefault = ''
            if name == default:
                isdefault = 'true'
            values = [conn['catalog_type'], conn['root_path'], isdefault]
            root_node = self.tree.insert('', 'end', iid=section, text=name,
                                         open=True, values=values)


    def add(self):
        n = ConnectionConfigDialog(self)
        new = n.result
        if new is None:
            return

        name = new['name']
        del new['name']

        if new['set_default']:
            self.cfg['SETTINGS']['default_connection'] = name
        del new['set_default']

        self.cfg['connection:' + name] = new

        self.insert_connections()

    def remove(self):
        selected = self.tree.selection()[0]

        del self.cfg[selected]

        if selected == ('connection:' +
                        self.cfg['SETTINGS']['default_connection']):
            connections = [c.rsplit(':', 1)[1] for c in self.cfg
                           if c.startswith('connection:')]
            new_default = None
            if connections:
                new_default = connections[0]

            self.cfg['SETTINGS']['default_connection'] = new_default

        self.insert_connections()

    def edit(self):
        selected = self.tree.selection()[0]
        item = self.tree.item(selected)
        name = item['text']
        catalog_type, root_path, isdefault = item['values']
        if isdefault is '':
            isdefault = 0
        else:
            isdefault = 1
        print_(name, catalog_type, root_path, isdefault)

        n = ConnectionConfigDialog(self, name, catalog_type, root_path, isdefault,
                                catalog_config=self.cfg['connection:' + name])
        new = n.result
        if new is None:
            return

        new_name = new['name']
        del new['name']
        if new_name != name:
            del self.cfg['connection:' + name]

        if new['set_default']:
            self.cfg['SETTINGS']['default_connection'] = new_name
        elif self.cfg['SETTINGS']['default_connection'] == name:
            connections = [c.rsplit(':', 1)[1] for c in self.cfg
                           if c.startswith('connection:')]
            new_default = None
            if connections:
                new_default = connections[0]

        del new['set_default']

        self.cfg['connection:' + new_name] = new

        self.tree.selection_set('')
        self.insert_connections()

    def selchanged(self, event):
        buts = (self.editbut, self.removebut)
        if self.tree.selection():
            for b in buts:
                b.config(state=tk.NORMAL)
        else:
            for b in buts:
                b.config(state=tk.DISABLED)

class Preferences(tksimpledialog.Dialog):
    """
    Preferences dialog
    """
    def body(self, master):
        self.connection_manager = ConnectionManager(master, None)
        self.connection_manager.grid(row=0)

        self.changed = False

    def apply(self):
        if self.connection_manager.cfg != self.connection_manager.old_cfg:
            config.save_config(self.connection_manager.cfg, update=False)
            self.changed = True

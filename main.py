import tkinter as tk
from tkinter import ttk
import progress_grid
import vk_api as vk
import json
import os

def l10n(string_name: str) -> str:
  if os.path.isfile("l10n.json"):
    l10n_dict=json.load(open("l10n.json","r+",encoding="utf-8"))
    return l10n_dict.get(string_name,string_name)
  else:
    return string_name

log:list
log_var:tk.Variable

token_url:str
token_url_var:tk.Variable

chat_id:str
chat_id_var:tk.Variable

offset:str
offset_var:tk.Variable

batch_size:str
batch_size_var:tk.Variable

progress_table_data:dict

class GUI:
  root: tk.Tk
  ui_table: dict
  def root_config(self):
    self.root.title(l10n("root.title"))
    self.root.geometry("800x350")
    self.root.grid_columnconfigure(0,weight=2000)
    self.root.grid_columnconfigure(1,weight=1)
    self.root.grid_columnconfigure(2,weight=20000)
    self.root.grid_rowconfigure(0, weight=1)
  def variable_init(self):
    global log,token_url,chat_id,offset,batch_size,progress_table_data
    global log_var,token_url_var,chat_id_var,offset_var,batch_size_var
    log=["Variables initialized"]
    progress_table_data={}
    token_url=chat_id=offset=batch_size=""
    log_var=tk.Variable(value=log)
    token_url_var=tk.Variable(value=token_url)
    chat_id_var=tk.Variable(value=chat_id)
    offset_var=tk.Variable(value=chat_id)
    batch_size_var=tk.Variable(value=chat_id)
  def config_panel_init(self):
    def auth_panel_init(parent):
      panel=tk.PanedWindow(master=parent)
      panel.grid(row=0,column=0,sticky="nesw")
      panel.grid_columnconfigure(0,weight=1)
      panel.grid_columnconfigure(1,weight=1)
      panel.grid_rowconfigure(0, weight=1)
      panel.grid_rowconfigure(1, weight=1)

      token_link_entry=tk.Entry(master=panel)
      token_link_entry.grid(row=0,column=0,columnspan=2,sticky="nesw")

      get_token_button=tk.Button(master=panel,text=l10n("get_token_button"))
      get_token_button.grid(row=1,column=0,sticky="nesw")

      auth_button=tk.Button(master=panel,text=l10n("auth_button"))
      auth_button.grid(row=1,column=1,sticky="nesw")
    def separator_init(parent):
      separator = ttk.Separator(master=parent, orient="horizontal")
      separator.grid(row=1,column=0,sticky="nesw")
      separator = ttk.Separator(master=parent, orient="horizontal")
      separator.grid(row=3,column=0,sticky="nesw")
    def settings_panel_init(parent):
      panel=tk.PanedWindow(master=parent)
      panel.grid(row=2,column=0,sticky="nesw")
      panel.grid_columnconfigure(0,weight=1)
      panel.grid_columnconfigure(1,weight=9)
      panel.grid_columnconfigure(3,weight=1)
      panel.grid_rowconfigure(0, weight=1)
      panel.grid_rowconfigure(1, weight=1)
      panel.grid_rowconfigure(2, weight=1)
      panel.grid_rowconfigure(3, weight=1)

      chat_id_entry=tk.Entry(master=panel)
      chat_id_entry_desc=tk.Label(master=panel, justify="right", anchor="e")
      chat_id_entry_desc.config(text=l10n("chat_id_entry_desc"))
      chat_id_entry.grid(row=0,column=1,sticky="new")
      chat_id_entry_desc.grid(row=0,column=0,sticky="new")

      offset_entry=tk.Entry(master=panel)
      offset_entry_desc=tk.Label(master=panel, justify="right", anchor="e")
      offset_entry_desc.config(text=l10n("offset_entry_desc"))
      offset_entry.grid(row=1,column=1,sticky="new")
      offset_entry_desc.grid(row=1,column=0,sticky="new")

      batch_size_entry=tk.Entry(master=panel)
      batch_size_desc=tk.Label(master=panel, justify="right", anchor="e")
      batch_size_desc.config(text=l10n("batch_size_desc"))
      batch_size_entry.grid(row=2,column=1,sticky="new")
      batch_size_desc.grid(row=2,column=0,sticky="new")

      start_button=tk.Button(master=panel,text=l10n("start_button"))
      start_button.grid(row=3,column=0,columnspan=4,sticky="new")
    def log_panel_init(parent):
      global log_var
      panel=tk.PanedWindow(master=parent)
      panel.grid(row=4,column=0,sticky="nesw")
      panel.grid_columnconfigure(0,weight=1)
      panel.grid_rowconfigure(0, weight=1)

      log_listbox=tk.Listbox(master=panel,bg="black",fg="white")
      log_listbox.config(listvariable=log_var, activestyle="none")
      log_listbox.config(selectbackground="black", selectforeground="white")
      log_listbox.grid(row=0,column=0,sticky="news")
    panel=tk.PanedWindow()
    panel.grid(row=0,column=0,sticky="nesw")
    panel.grid_columnconfigure(0,weight=1)
    panel.grid_rowconfigure(0, weight=1)
    panel.grid_rowconfigure(1,weight=1)
    panel.grid_rowconfigure(2, weight=21)
    panel.grid_rowconfigure(3, weight=1)
    panel.grid_rowconfigure(4, weight=60)
    auth_panel_init(panel)
    separator_init(panel)
    settings_panel_init(panel)
    log_panel_init(panel)

  def progress_panel_init(self):
    global progress_table_model
    panel=tk.PanedWindow()
    panel.grid(row=0,column=2,sticky="nesw")
    panel.grid_columnconfigure(0,weight=1)
    panel.grid_rowconfigure(0, weight=1)
    pgrid=progress_grid.ProgressGrid(panel)
  def separator_init(self):
    separator = ttk.Separator(master=self.root, orient="vertical")
    separator.grid(row=0,column=1,sticky="nesw")

  def __init__(self):
    self.root=tk.Tk()
    self.variable_init()
    self.root_config()
    self.config_panel_init()
    self.separator_init()
    self.progress_panel_init()
    self.root.mainloop()

GUI()

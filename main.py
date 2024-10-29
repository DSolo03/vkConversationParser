#Tkinter modules
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename

#Custom modules
import progress_grid
import messages_parser
import merger

#Net modules
import vk_api as vk
import webbrowser

#Storage modules
import json
import sqlite_utils
import pickle

#System modules
import os
import threading
import time

#Get localization string from file or return string id
def l10n(string_name: str,value="") -> str:
  if os.path.isfile("l10n.json"):
    l10n_dict=json.load(open("l10n.json","r+",encoding="utf-8"))
    return l10n_dict.get(string_name,string_name).replace("<value>",str(value))
  else:
    return string_name

log:list
log_var:tk.Variable
log_listbox:tk.Listbox

token_url:str
token_url_var:tk.Variable

chat_id:str
chat_id_var:tk.Variable

offset:str
offset_var:tk.Variable

batch_size:str
batch_size_var:tk.Variable

pgrid:progress_grid.ProgressGrid

profiles={}

auth_request="https://oauth.vk.com/authorize?client_id=6121396&scope=69632&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1" # pylint: disable=line-too-long

def logger(text: str):
  log.append(text)
  log_var.set(log)
  log_listbox.yview("end")

class Auth:
  api: vk.VkApi.get_api
  token = ""

  def load(self):
    if os.path.isfile("auth.pickle"):
      self.token=pickle.load(open("auth.pickle","rb"))
      return True
    else:
      return False

  def save(self):
    pickle.dump(self.token,open("auth.pickle","wb"))
    logger(l10n("token_save_success"))
    return True

  def silent_load(self):
    self.load()
    self.api=vk.VkApi(token=self.token).get_api()

  def extract_token_from_url(self,url:  str):
    if url or (not self.load()):
      try:
        self.token=url.split("access_token=")[1].split("&expires_in")[0]
        return True
      except IndexError:
        logger(l10n("token_extract_fail"))
        return False
    elif (not url) and (self.load()):
      logger(l10n("token_load_success"))
      self.api=vk.VkApi(token=self.token).get_api()
    else:
      logger(l10n("enter_token_error"))
  def auth_button_handler(self):
    if self.extract_token_from_url(token_url_var.get()):
      try:
        vk.VkApi(token=self.token).get_api().messages.getHistory(peer_id=1)
        logger(l10n("token_valid_success"))
        self.api=vk.VkApi(token=self.token).get_api()
        self.save()
      except vk.exceptions.ApiError:
        token_url_var.set("")
        self.token=""
        logger(l10n("token_invalid_fail"))

  def get_token_button_handler(self):
    webbrowser.open(auth_request)

auth=Auth()

def clampmin(intval,intmin):
  return intval if intval>intmin else intmin

def process(n,maximum):
  logger(l10n("thread_work_start",n+1))
  database=sqlite_utils.Database(f"messages-{n}.db")
  perf_start=perf_finish=0
  row_id=0
  column_id=n
  internal_offset=int(batch_size_var.get())*n
  items=[1]
  current_auth=Auth()
  current_auth.silent_load()
  time.sleep(0.5) #Calm down, rate limit
  if current_auth.token:
    while items:
      pgrid.update(column_id,row_id,"pending") #Set cell as pending
      while True: #Make sure that batch is downloaded
        try:
          perf_start = time.perf_counter() #Time perfomance for messages retrieving and parsing

          messages=current_auth.api.messages.getHistory(
            peer_id=2000000000+int(chat_id_var.get()),
            rev=1,
            count=int(batch_size_var.get()),
            extended=1,
            offset=clampmin(int(offset_var.get())+internal_offset-1,0)
            )
          items=messages.get("items",[])
          messages_parser.parse_profiles(messages.get("profiles",[])) #Populating profiles dictionary
          database["messages"].upsert_all(list(map(messages_parser.parse_messages,items)),pk="id")

          perf_finish=time.perf_counter() #Finish timing perfomance

          #If all operations taken less than second - force to wait rest of the time to avoid rate limit
          if (perf_finish-perf_start)<=1:
            time.sleep(1-(perf_finish-perf_start))

          pgrid.update(column_id,row_id,"done") #Set cell as done
          break
        except Exception as exception:
          pgrid.update(column_id,row_id,"error") #Set cell as error

          #Logging error to file with debug information
          with open(f"logs\\{time.time()}-{n}.log","w+",encoding="UTF-8") as log_file:
            log_file.write(str(exception)+"\n")
            log_file.write(f"offset={int(offset_var.get())+internal_offset}\n")
            log_file.write(str(list(map(messages_parser.parse_messages,items)))+"\n")

      internal_offset+=int(batch_size_var.get())*(maximum+1)

      #Ensure that new line created and exist and then scroll screen to it
      if row_id>=15 or pgrid.max_row==int((internal_offset/int(batch_size_var.get()))//10):
        pgrid.ensure_line(row_id+6)
        pgrid.move()

      row_id=int((internal_offset/int(batch_size_var.get()))//10)
      column_id=int((internal_offset/int(batch_size_var.get()))%10)

  logger(l10n("thread_work_done",n+1))
  database.close()

processing_thread_0=threading.Thread(target=process,args=(int(0),2),daemon=True)
processing_thread_1=threading.Thread(target=process,args=(int(1),2),daemon=True)
processing_thread_2=threading.Thread(target=process,args=(int(2),2),daemon=True)

def start_processing():
  global processing_thread_0,processing_thread_1,processing_thread_2

  #Check whether user is authentificated
  if not auth.token:
    logger(l10n("auth_first_error"))
    return False

  #Input validation
  if not (
    str(chat_id_var.get()).isdigit() and
    str(offset_var.get()).isdigit() and
    str(batch_size_var.get()).isdigit() and
    int(batch_size_var.get())>=1
  ):
    logger(l10n("wrong_inputs_error"))
    return False

  #Check if parsing already begin
  if not (processing_thread_0.is_alive() or processing_thread_1.is_alive() or processing_thread_2.is_alive()):
    processing_thread_0=threading.Thread(target=process,args=(int(0),2),daemon=True)
    processing_thread_1=threading.Thread(target=process,args=(int(1),2),daemon=True)
    processing_thread_2=threading.Thread(target=process,args=(int(2),2),daemon=True)
    processing_thread_0.start()
    processing_thread_1.start()
    processing_thread_2.start()
  else:
    logger(l10n("threads_already_work"))

class GUI:
  root: tk.Tk

  def root_config(self):
    self.root.title(l10n("root.title"))
    self.root.geometry("600x400")
    self.root.resizable(width=False, height=False)
    self.root.grid_columnconfigure(0,weight=2000)
    self.root.grid_columnconfigure(1,weight=1)
    self.root.grid_columnconfigure(2,weight=20000)
    self.root.grid_rowconfigure(0, weight=1)

  def variable_init(self):
    global log,token_url,chat_id,offset,batch_size
    global log_var,token_url_var,chat_id_var,offset_var,batch_size_var

    log=[]
    token_url=chat_id=offset=batch_size=""
    offset=0
    batch_size=200
    log_var=tk.Variable(value=log)
    token_url_var=tk.Variable(value=token_url)
    chat_id_var=tk.Variable(value=chat_id)
    offset_var=tk.Variable(value=offset)
    batch_size_var=tk.Variable(value=batch_size)

  def config_panel_init(self):
    def auth_panel_init(parent):
      panel=tk.PanedWindow(master=parent)
      panel.grid(row=0,column=0,sticky="nesw")
      panel.grid_columnconfigure(0,weight=1)
      panel.grid_columnconfigure(1,weight=1)
      panel.grid_rowconfigure(0, weight=1)
      panel.grid_rowconfigure(1, weight=1)

      token_link_entry=tk.Entry(master=panel,textvariable=token_url_var)
      token_link_entry.grid(row=0,column=0,columnspan=2,sticky="nesw")

      get_token_button=tk.Button(
        master=panel,text=l10n("get_token_button"),
        command=auth.get_token_button_handler
        )
      get_token_button.grid(row=1,column=0,sticky="nesw")

      auth_button=tk.Button(master=panel,text=l10n("auth_button"),command=auth.auth_button_handler)
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

      chat_id_entry=tk.Entry(master=panel,textvariable=chat_id_var)
      chat_id_entry_desc=tk.Label(master=panel, justify="right", anchor="e")
      chat_id_entry_desc.config(text=l10n("chat_id_entry_desc"))
      chat_id_entry.grid(row=0,column=1,sticky="new")
      chat_id_entry_desc.grid(row=0,column=0,sticky="new")

      offset_entry=tk.Entry(master=panel,textvariable=offset_var)
      offset_entry_desc=tk.Label(master=panel, justify="right", anchor="e")
      offset_entry_desc.config(text=l10n("offset_entry_desc"))
      offset_entry.grid(row=1,column=1,sticky="new")
      offset_entry_desc.grid(row=1,column=0,sticky="new")

      batch_size_entry=tk.Entry(master=panel,textvariable=batch_size_var)
      batch_size_desc=tk.Label(master=panel, justify="right", anchor="e")
      batch_size_desc.config(text=l10n("batch_size_desc"))
      batch_size_entry.grid(row=2,column=1,sticky="new")
      batch_size_desc.grid(row=2,column=0,sticky="new")

      start_button=tk.Button(master=panel,text=l10n("start_button"),command=start_processing)
      start_button.grid(row=3,column=0,columnspan=4,sticky="new")

    def log_panel_init(parent):
      global log_var, log_listbox
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
    global pgrid
    panel=tk.PanedWindow()
    panel.grid(row=0,column=2,sticky="nesw")
    panel.grid_columnconfigure(0,weight=1)
    panel.grid_rowconfigure(0, weight=1)
    pgrid=progress_grid.ProgressGrid(panel,200)
    pgrid.re_init(200)

  def main_menu_init(self):
    main_menu = tk.Menu()
    main_menu.add_command(
      label=f"{l10n("merge_button")}",
      command=lambda:merger.merge(
        asksaveasfilename(
          filetypes = [(f"{l10n("database_file_type")}","*.db")],
          defaultextension = [(f"{l10n("database_file_type")}","*.db")]
          )
        )
      )
    self.root.config(menu=main_menu)

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
    self.main_menu_init()
    self.root.mainloop()

gui=GUI()

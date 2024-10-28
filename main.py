import tkinter as tk
import vk_api as vk

class GUI:
  root: tk.Tk
  def root_config(self):
    self.root.title("VK Conversation Parser")
    self.root.geometry("600x350")
    self.root.grid_columnconfigure(0,weight=1)
    self.root.grid_columnconfigure(1,weight=2)
    self.root.grid_rowconfigure(0, weight=1)

  def config_panel_init(self):
    def auth_panel_init(parent):
      panel=tk.PanedWindow(master=parent,background="green")
      panel.grid(row=0,column=0,sticky="nesw")         
    def settings_panel_init(parent):
      panel=tk.PanedWindow(master=parent,background="gray")
      panel.grid(row=1,column=0,sticky="nesw")      
    panel=tk.PanedWindow(background="red")
    panel.grid(row=0,column=0,sticky="nesw")
    panel.grid_columnconfigure(0,weight=1)
    panel.grid_rowconfigure(0, weight=3)
    panel.grid_rowconfigure(1, weight=16)
    auth_panel_init(panel)
    settings_panel_init(panel)

  def progress_panel_init(self):
    panel=tk.PanedWindow(background="blue")
    panel.grid(row=0,column=1,sticky="nesw")

  def __init__(self):
    self.root=tk.Tk()
    self.root_config()
    self.config_panel_init()
    self.progress_panel_init()
    self.root.mainloop()

GUI()

import tkinter as tk
from tkinter import ttk

class ProgressGrid():
  tree_views:list[ttk.Treeview]
  master: tk.PanedWindow
  max_row: int
  def noop(self,_):
    return "break"
  def __init__(self,master: tk.PanedWindow,count=0):
    self.max_row=0
    self.master=master
    self.tree_views=[]
    master.grid_rowconfigure(0,weight=1)
    for i in range(0,10):
      master.grid_columnconfigure(i,weight=1)
      tree_view=ttk.Treeview(master=master,show="tree",columns=(""),selectmode="none")
      tree_view.column("#0",width=5,anchor="w")
      tree_view.bind("<MouseWheel>",self.noop)
      tree_view.grid(row=0,column=i,sticky="nswe")
      self.tree_views.append(tree_view)
    for i in range(0,count//10):
      for j in range(0,10):
        self.tree_views[j].insert("",i,values=(""),tags="undefined")
        self.tree_views[j].tag_configure("undefined",background="white")
        self.tree_views[j].tag_configure("pending",background="yellow")
        self.tree_views[j].tag_configure("done",background="green")
        self.tree_views[j].tag_configure("error",background="red")
  def re_init(self,count=0):
    self.max_row=0
    for i in range(0,10):
      self.tree_views[i].delete(*self.tree_views[i].get_children())
    for i in range(0,count//10):
      self.max_row=i
      for j in range(0,10):
        self.tree_views[j].insert("",i,values=(""),tags="undefined")
        self.tree_views[j].tag_configure("undefined",background="white")
        self.tree_views[j].tag_configure("pending",background="yellow")
        self.tree_views[j].tag_configure("done",background="green")
        self.tree_views[j].tag_configure("error",background="red")
  def create_line(self,i):
    for j in range(0,10):
      self.tree_views[j].insert("",i,values=(""),tags="undefined")
      self.tree_views[j].tag_configure("undefined",background="white")
      self.tree_views[j].tag_configure("pending",background="yellow")
      self.tree_views[j].tag_configure("done",background="green")
      self.tree_views[j].tag_configure("error",background="red")
  def update(self,x,y,status):
    self.max_row = y if self.max_row<y else self.max_row
    self.tree_views[x].item(self.tree_views[x].get_children()[y],tag=status)
  def ensure_line(self,i):
    if len(self.tree_views[9].get_children())<i+1:
      self.create_line(i)
  def move(self):
    for i in range(0,10):
      self.tree_views[i].yview_scroll(1, "units")

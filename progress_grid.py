import tkinter as tk
from tkinter import ttk

class ProgressGrid():
  tree_views:list[ttk.Treeview]
  def noop(self,_):
    return "break"
  def __init__(self,master: tk.PanedWindow,count=0):
    self.tree_views=[]
    master.grid_rowconfigure(0,weight=1)
    for i in range(0,10):
      master.grid_columnconfigure(i,weight=1)
      tree_view=ttk.Treeview(master=master,show='tree',columns=(""),selectmode="none")
      tree_view.column("#0",width=5)
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
  def update(self,x,y,status):
    self.tree_views[x].item(self.tree_views[x].get_children()[y],tag=status)
  def see(self,y):
    for i in range(0,10):
      self.tree_views[i].see(self.tree_views[i].get_children()[y])
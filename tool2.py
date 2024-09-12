from tkinter import *
from tkinter.ttk import *
from PIL import Image, ImageTk
from main import main

def open_advanced_options():
    win = Toplevel()
    win.title('Advanced Options')
    win.geometry('1200x600')
    # adding a window frame with padding
    win_frm =  Frame(win)
    win_frm.pack(fill='both', expand='True', padx=20, pady=10)


    # add change variabels label
    change_var_lbl = Label(win_frm, text='Change variables:')
    change_var_lbl.grid(row=0, column=0)


    # add change variables frame with values
    var_frm = Frame(win_frm, relief='groove', borderwidth=6, padding=10)
    var_frm.grid(row=1,column=0)

    # add varables to the frame for low voltage
    var1_lbl = Label(var_frm, text='Low voltage Station Costs: ').grid(row=1, column=0)
    var1_ent = Entry(var_frm).grid(row=1, column=1)
    var2_lbl = Label(var_frm, text='Low voltage Cables Costs: ').grid(row=2, column=0)
    var2_ent = Entry(var_frm).grid(row=2, column=1)
    var3_lbl = Label(var_frm, text='Low voltage Cables Material: ').grid(row=3, column=0)
    material1 = IntVar()
    var4_rdb1 = Radiobutton(var_frm, text='Coper', value=1, variable=material1).grid(row=4, column=0)
    var4_rdb2 = Radiobutton(var_frm, text='Aluminium', value=2, variable=material1).grid(row=4, column=1)

    # medium voltage 
    var4_lbl = Label(var_frm, text='Medium voltage Station Costs: ').grid(row=5, column=0)
    var4_ent = Entry(var_frm).grid(row=5, column=1)
    var5_lbl = Label(var_frm, text='Medium voltage Cables Costs: ').grid(row=6, column=0)
    var5_ent = Entry(var_frm).grid(row=6, column=1)
    var6_lbl = Label(var_frm, text='Medium voltage Cables Material: ').grid(row=7, column=0)
    material2 = IntVar()
    var7_rdb1 = Radiobutton(var_frm, text='Coper', value=1, variable=material2).grid(row=8, column=0)
    var7_rdb2 = Radiobutton(var_frm, text='Aluminium', value=2, variable=material2).grid(row=8, column=1)

    # high voltage
    var8_lbl = Label(var_frm, text='High voltage Station Costs: ').grid(row=9, column=0)
    var8_ent = Entry(var_frm).grid(row=9, column=1)
    var9_lbl = Label(var_frm, text='High voltage Cables Costs: ').grid(row=10, column=0)
    var9_ent = Entry(var_frm).grid(row=10, column=1)
    var10_lbl = Label(var_frm, text='High voltage Cables Material: ').grid(row=11, column=0)
    material3 = IntVar()
    var11_rdb1 = Radiobutton(var_frm, text='Coper', value=1, variable=material3).grid(row=12, column=0)
    var11_rdb2 = Radiobutton(var_frm, text='Aluminium', value=2, variable=material3).grid(row=12, column=1)
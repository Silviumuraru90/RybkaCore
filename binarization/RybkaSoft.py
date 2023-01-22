#!usr/bin/env python3

import os
import subprocess
import webbrowser

from datetime import datetime
from sys import platform
from tkinter import messagebox
from tkinter import *
from tkinter.ttk import *



# ===============================================
#	ENV VAR
# ===============================================

PYTHON_PATH = os.environ.get("RYBKA_PYTHON_PATH")

if not PYTHON_PATH:
    messagebox.showerror("RybkaSoft Error Module", "Please provide [RYBKA_PYTHON_PATH] ENV VAR in order for GUI to boot up")
    exit(1)



# ===============================================
#	Generic architecture
# ===============================================

top = Tk()
top.resizable(False, False)
top.geometry("650x550")  
top.title('RybkaSoft')
top.config(cursor="pirate")
top['bg'] = 'black'

if platform == "linux" or platform == "linux2":
    try:
        build_id = f'Release\n{str(open("../project_version", "r").read())}'.strip("\n")
    except:
        build_id = f'Release\n{str(open("project_version", "r").read())}'.strip("\n")
elif platform == "win32":
    if os.path.exists("rybka.ico"):
        top.iconbitmap("rybka.ico")
        build_id = f'Release\n{str(open("../project_version", "r").read())}'.strip("\n")
    else:
        top.iconbitmap("binarization/rybka.ico")
        build_id = f'Release\n{str(open("project_version", "r").read())}'.strip("\n")

top.columnconfigure(0, weight=1)
top.columnconfigure(1, weight=1)
top.columnconfigure(2, weight=1)

top.rowconfigure(0, weight=1)
top.rowconfigure(1, weight=2)
top.rowconfigure(2, weight=2)
top.rowconfigure(3, weight=2)
top.rowconfigure(4, weight=2)
top.rowconfigure(5, weight=2)
top.rowconfigure(6, weight=2)
top.rowconfigure(7, weight=2)
top.rowconfigure(8, weight=3)
top.rowconfigure(9, weight=2)

style = Style(top)
Font_tuple = ("Courier", 15, "bold")
style.configure('.', font=Font_tuple)



# ===============================================
#	Core functions
# ===============================================

def click(text):
    if text == "stopped":
        A.config(text="LIVE")
        B.config(text="DEMO")
        C.config(text="LIVE")
        D.config(text="DEMO")
    else:
        if text == "rybka_live":
            message = f'LIVE (previously started at: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")})'
            A.config(text=message)
        elif text == "rybka_demo":
            message = f'DEMO (previously started at: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")})'
            B.config(text=message)
        elif text == "restarter_live":
            message = f'LIVE (previously started at: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")})'
            C.config(text=message)
        elif text == "restarter_demo":
            message = f'DEMO (previously started at: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")})'
            D.config(text=message)


def software_start(text):
    if text == "rybka_live":
        click("stopped")
        subprocess.Popen([PYTHON_PATH, f"{text.split('_')[0]}.py", "-m", f"{text.split('_')[1]}"])
        click(text)
    elif text == "rybka_demo":
        click("stopped")
        subprocess.Popen([PYTHON_PATH, f"{text.split('_')[0]}.py", "-m", f"{text.split('_')[1]}"])
        click(text)
    elif text == "restarter_live":
        click("stopped")
        subprocess.Popen([PYTHON_PATH, f"{text.split('_')[0]}.py", "-m", f"{text.split('_')[1]}"])
        click(text)
    elif text == "restarter_demo":
        click("stopped")
        subprocess.Popen([PYTHON_PATH, f"{text.split('_')[0]}.py", "-m", f"{text.split('_')[1]}"])
        click(text)


def callback(url):
   webbrowser.open_new_tab(url)



# ===============================================
#	Generic Headings
# ===============================================

heading_welcome = Label(text='RYBKA SOFTWARE', background='black', foreground="DarkOrange4", style='Heading.TLabel')
heading_welcome.grid(column=0, columnspan=3, row=0, pady=(15,0))



# ===============================================
#	Header Grid
# ===============================================

header_grid = Label(text='-----------------------------', style='Heading.TLabel', foreground="DarkOrange4", background="black")
header_grid.grid(column=0, columnspan=3, row=1, pady=(0,30))



# ===============================================
#	Button configuration
# ===============================================

style_rybka = Style()
style_rybka.configure("BW.TLabel", background="grey", activebackground='#78d6ff')

A = Button(top, text="LIVE", command=lambda input="rybka_live": software_start(input), cursor="hand1", style="BW.TLabel")
B = Button(top, text="DEMO", command=lambda input="rybka_demo": software_start(input), cursor="hand1", style="BW.TLabel")
C = Button(top, text="LIVE", command=lambda input="restarter_live": software_start(input), cursor="hand1", style="BW.TLabel")
D = Button(top, text="DEMO", command=lambda input="restarter_demo": software_start(input), cursor="hand1", style="BW.TLabel")



# ===============================================
#	RYBKA section configuration
# ===============================================

heading_rybka = Label(text='Launch RYBKA:', background='black', foreground="DarkGoldenrod4", style='Heading.TLabel')
heading_rybka.grid(column=0, columnspan=3, row=2, pady=(10,10))

A.grid(column=0, columnspan=3, row=3, padx=5, pady=5)
B.grid(column=0, columnspan=3, row=4, padx=5, pady=5)



# ===============================================
#	RESTARTER section configuration
# ===============================================

heading_restarter = Label(text='Launch RESTARTER:', background='black', foreground="DarkGoldenrod4", style='Heading.TLabel')
heading_restarter.grid(column=0, columnspan=3, row=5, pady=(30,10))

C.grid(column=0, columnspan=3, row=6, padx=5, pady=5)
D.grid(column=0, columnspan=3, row=7, padx=5, pady=(5,15))



# ===============================================
#	Footer Grid
# ===============================================

footer_grid = Label(text='_______________________________________________________________________', style='Heading.TLabel', foreground="DarkOrange4", background="black")
footer_grid.grid(column=0, columnspan=3, row=8, pady=5)



# ===============================================
#	Footer notes
# ===============================================

# Website
link = Label(top, text="Open Source on Gitlab", cursor="hand2", foreground="gray", background="black", font=("Courier", 11, "bold"), relief="solid", borderwidth=15)
link.grid(column=0, row=9, pady=5, padx=(5,10))
link.bind("<Button-1>", lambda e:
callback("https://silviu_space.gitlab.io/rybka"))

# Copyright + Email
footer_email = Label(text='Contact:\nsilviumuraru90@yahoo.com', style='Heading.TLabel', foreground="DarkOrange4", background="black", font=("Courier", 11, "bold"))
footer_email.grid(column=1, row=9, pady=5, padx=15)

# Build ID
strvar = IntVar(top, name=build_id)
footer_release = Label(text=strvar, style='Heading.TLabel', foreground="DarkOrange4", background="black", font=("Courier", 11, "bold"))
footer_release.grid(column=2, row=9, padx=(10,5), pady=5)



# ===============================================
top.mainloop()

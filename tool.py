from tkinter import *
from tkinter.ttk import *
from PIL import Image, ImageTk
from main import main
from tool2 import open_advanced_options

def show_data():
    update_image(f"{city_cmb.get().lower()}.png")

def calc_routing():
    solution_data = main(city_cmb.get().lower(), algo_cmb2.get().lower(), algo_cmb1.get().lower())
    update_solution_data(solution_data)
    update_image(f"tool_images/{city_cmb.get().lower()}.png")   

def update_image(path):
    image = Image.open(path)
    # resize the image
    width_ratio = 750 / image.width
    height_ratio = 500 / image.height
    resize_ratio = min(width_ratio, height_ratio)
    new_width = int(image.width * resize_ratio)
    new_height = int(image.height * resize_ratio)
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    photoimage = ImageTk.PhotoImage(resized_image)
    # Create a label and display the image
    img_lbl.config(image=photoimage)
    img_lbl.image = photoimage

def update_solution_data(solution_data):
    var1_lbl.config(text=f'Total target: {round(solution_data[-1])}')
    var2_lbl.config(text=f'Routing costs: {round(solution_data[0])}')
    var3_lbl.config(text=f'Building costs: {round(solution_data[1])}')
    var4_lbl.config(text=f'Voltage drop: {round(solution_data[2])}')
    var5_lbl.config(text=f'Stability: {round(solution_data[3], 2)}')

# defining the window
win = Tk()
win.title('Energy network showcase tool')
win.geometry('1200x600')
# adding a window frame with padding
win_frm =  Frame(win)
win_frm.pack(fill='both', expand='True', padx=20, pady=10)

# city selection
city_cmb = Combobox(win_frm, state='readonly')
city_cmb['values'] = ['Krommenie', 'Leiden', 'Eindhoven', 'Amsterdam']
city_cmb.current(0)
city_cmb.grid(row=0, column=0, pady=10)

# button to calculate the routing
route_btn = Button(win_frm, command = show_data) 
route_lbl = Label(win_frm, text = 'Show data')
route_btn.grid(row=1, column=0, pady=10)
route_lbl.grid(row=1, column=1)

# button to calculate starting solution
algo_cmb1 = Combobox(win_frm, state='readonly')
algo_cmb1['values'] = ['Greedy', 'ALA', 'KAL']
algo_lbl1 = Label(win_frm, text = 'Locating algorithm:')
algo_cmb1.current(0)
algo_lbl1.grid(row=2, column=0, pady=4)
algo_cmb1.grid(row=2, column=1, pady=4)

# button to calculate starting solution
algo_cmb2 = Combobox(win_frm, state='readonly')
algo_cmb2['values'] = ['Greedy', 'Prim']
algo_lbl2 = Label(win_frm, text = 'Routing algorithm:')
algo_cmb2.current(0)
algo_lbl2.grid(row=3, column=0, pady=4)
algo_cmb2.grid(row=3, column=1, pady=4)


# button to calculate the routing
route_btn = Button(win_frm, command = calc_routing) 
route_lbl = Label(win_frm, text = 'Calculate routing')
route_btn.grid(row=4, column=0, pady=10)
route_lbl.grid(row=4, column=1)

# variable display
# create frame for the labels
var_frm = Frame(win_frm, relief='groove', borderwidth=6, padding=10)
var_frm.grid(row=5,column=0, pady=10)
var1_lbl = Label(var_frm, text='Total Target: ')
var2_lbl = Label(var_frm, text='Routing Costs: ')
var3_lbl = Label(var_frm, text='Building Costs: ')
var4_lbl = Label(var_frm, text='Voltage drop: ')
var5_lbl = Label(var_frm, text='Stability: ')
var1_lbl.grid(row=1, column=0)
var2_lbl.grid(row=2, column=0)
var3_lbl.grid(row=3, column=0)
var4_lbl.grid(row=4, column=0)
var5_lbl.grid(row=5, column=0)


# adding image
image = Image.open(f"{city_cmb.get().lower()}.png")
# resize the image
width_ratio = 750 / image.width
height_ratio = 500 / image.height
resize_ratio = min(width_ratio, height_ratio)
new_width = int(image.width * resize_ratio)
new_height = int(image.height * resize_ratio)
resized_image = image.resize((new_width, new_height), Image.LANCZOS)
photoimage = ImageTk.PhotoImage(resized_image)
# Create a label and display the image
img_lbl = Label(win_frm, image=photoimage)
img_lbl.grid(row=0, column=3, rowspan=6, padx=50, pady=30)

# add advanced options button
adv_btn = Button(win_frm, command = open_advanced_options) 
adv_lbl = Label(win_frm, text = 'Advanced Options')
adv_btn.grid(row=0, column=4, pady=10)
adv_lbl.grid(row=0, column=5, padx=30)


# running the tool
win.mainloop()
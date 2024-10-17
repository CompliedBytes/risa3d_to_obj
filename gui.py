from tkinter import ttk
from tkinter import *
from tkinter import filedialog


def on_select():
    selected_file = filedialog.askopenfilename()
    if selected_file:
        file.set(selected_file)
        file_label.config(text=selected_file)

def convert():
    print(file.get())

bg_color = 'lightblue'


root = Tk()
root.title("RISA-3D to OBJ Converter")
style = ttk.Style(root)
style.configure('UFrame', background=bg_color, foreground='black')
style.configure('TFrame', background=bg_color, foreground='black')
style.configure('TLabel', background=bg_color, foreground='black')
style.configure('TCheckbutton', background=bg_color)

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

ttk.Label(mainframe, text="UAA 3D File Conversion Tool", font=("Arial", 15)).grid(column=0, row = 0, padx=(25,25), pady=(5,10))

file = StringVar()
file_frame = ttk.Frame(mainframe)
file_button = ttk.Button(file_frame, text="Select File", command=on_select)
file_label = ttk.Label(file_frame, text="                                                         ", background="white", relief='sunken')
file_button.grid(column=0, row=0, sticky = 'W')# side='left')
file_label.grid(column=1, row=0, padx=(5,0), pady=(0,0))
file_frame.grid(column=0, row=1, padx=(25,25), pady=(10,10))

dimvar = StringVar()
dim_frame = ttk.Frame(mainframe)
dim_label = ttk.Label(dim_frame, text="2D/3D:", foreground="black").grid(column=0, row=0, padx=(0,5), pady=(0,0))
dim_box = ttk.Combobox(dim_frame, textvariable=dimvar)
# Add the values to the combobox
dim_box['values'] = ('2D', '3D','Both')
# Do not allow the user to edit the values
dim_box.state(["readonly"])
# Set the default value to Both
dim_box.set('Both')
# Place the combobox
dim_box.grid(column=1, row=0, padx=(5,0), pady=(0,0))
dim_frame.grid(column=0, row=2, padx=(0,0), pady=(10,10))



side = IntVar()
top = IntVar()
bottom = IntVar()
options_label = ttk.Label(mainframe, text="Advanced 2D Options", foreground="black").grid(column=0, row=3, padx=(0,0), pady=(10,0))
options_frame = ttk.Frame(mainframe)
side_button = ttk.Checkbutton(options_frame, text="Side", variable=side, onvalue=1, offvalue=0).grid(column=0, row=0, padx=(0,10))
top_button = ttk.Checkbutton(options_frame, text="Top", variable=side, onvalue=1, offvalue=0).grid(column=1, row=0, padx=(10,10))
bottom_button = ttk.Checkbutton(options_frame, text="Bottom", variable=side, onvalue=1, offvalue=0).grid(column=2, row=0, padx=(10,0))
options_frame.grid(column=0, row=4, padx=(0,0), pady=(10,10))

bottom_frame = ttk.Frame(mainframe)
convert_button = ttk.Button(bottom_frame, text="Convert", command=convert).grid(column=0, row=0, padx=(0,25), pady=(0,0))
exit_button = ttk.Button(bottom_frame, text="Exit", command=root.destroy).grid(column=1, row=0, padx=(25,0), pady=(0,0))
bottom_frame.grid(column=0, row=5, padx=(0,0), pady=(10,5))

root.mainloop()


from tkinter import *
from tkinter import ttk
from tkinter import filedialog


def on_select():
    selected_file = filedialog.askopenfilename()
    if selected_file:
        file.set(selected_file)
        file_label.config(text=selected_file)

root = Tk()
root.title("RISA-3D to OBJ Converter")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

ttk.Label(mainframe, text="UAA 3D File Conversion Tool",font=("Arial", 15)).grid(column=1, row=0, sticky=(N))


file = StringVar()
file_button = ttk.Button(mainframe, text="Select File", command=on_select)
file_button.grid(column=1, row=1, sticky=(W))


file_label = ttk.Label(mainframe, text="", relief='sunken')
file_label.grid(column=22, row=1, sticky=(E))


dimensionvar = StringVar()
dimension = ttk.Combobox(mainframe, textvariable=dimensionvar)

# Add the values to the combobox
dimension['values'] = ('2D', '3D','Both')
# Do not allow the user to edit the values
dimension.state(["readonly"])
# Set the default value to Both
dimension.set('Both')
# Place the combobox
dimension.grid(column=1, row=2, sticky=(N))




for child in mainframe.winfo_children(): 
    child.grid_configure(padx=5, pady=5)



root.mainloop()
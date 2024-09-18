import os
import math
import tkinter
from tkinter import filedialog

def GetUnits(lines):
    units_num = []
    units_text = []
    num_lines = len(lines)
    curr_line = 0
    for line in lines:
        if '[UNITS]' in lines[curr_line]:
            units_num = lines[curr_line + 1].split(' ')
            break
        curr_line += 1
    
    #Check length_units and translate into text-based flags.
    if units_num[1] == '0':
        units_text.append('ft')
    elif units_num[1] == '1':
        units_text.append('in')
    elif units_num[1] == '2':
        units_text.append('m')
    elif units_num[1] == '3':
        units_text.append('cm')
    elif units_num[1] == '4':
        units_text.append('mm')
    
    #Check dim_units and translate into text-based flags.
    if units_num[1] == '0':
        units_text.append('in')
    elif units_num[1] == '1':
        units_text.append('cm')
    elif units_num[1] == '2':
        units_text.append('mm')
    
    return units_text

with open("2024 SB V4.5.r3d") as file:
    data=file.read().split('\n')
    print(GetUnits(data))
    #print(data)
# -*- coding: utf-8 -*-
"""
Created on Wed May 10 10:53:36 2023

@author: Mircea
"""

import traceback
import sympy
import numpy as np
from scipy.integrate import odeint,solve_ivp
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk,messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from tkinter.filedialog import askopenfilename
import re,random,os

global solution,y0

solution = None

def parse_ode(equation):
        y, t = sympy.symbols('y t')
        f = sympy.sympify(equation)
        f_func = sympy.lambdify((y, t), f)
    
        def ode_func(y, t):
            return f_func(y, t)
    
        return ode_func
    
def replace_y(string):
    pattern = r'(\d+)y'
    match = re.search(pattern, string)
    if match:
        num = match.group(1)
        new_string = re.sub(pattern, num + ' * y', string)
        return new_string
    else:
        return string
    
def contains_illegal_chars(string):
    pattern = r"[^y0-9+\-*/ ]"
    match = re.search(pattern, string)
    return match is not None



def submit():
    try:
        global solution,solve_method
        solution = None
        equation = y_prime_entry.get()
        if(contains_illegal_chars(equation)):
            messagebox.showerror("Invalid Equation","The equation variable must be y!")
            return
        ode_func = parse_ode(replace_y(equation))
        y0 = np.array([float(y0_entry.get())])
        t_start = float(time_start_entry.get())
        t_end = float(time_end_entry.get())
        print(y_prime_entry.get(),y0_entry.get(),time_start_entry.get(),time_end_entry.get())
        if(t_start == t_end):
            messagebox.showerror("Invalid Time","The start time cannot be the same as the end time!")
            return
        if(t_start > t_end):
            messagebox.showerror("Invalid Time", "The start time cannot be bigger than the end time!")
            return
        
        solution = solve_ivp(ode_func, [t_start,t_end], y0,method=solve_method.get(),t_eval = np.linspace(t_start, t_end))    
    

        ax.clear()
        ax.plot(solution.t, solution.y[0])
        ax.set_xlabel('time')
        ax.set_ylabel('y(t)')
        canvas.draw()
        
       
    except ValueError:
        messagebox.showerror("Null values","One or more entries are null")
        traceback.print_exc()
    except TypeError:
        messagebox.showerror("Equation","The equation is not valid!")
        traceback.print_exc()
        

def animate(i):
    global solution
    ax.plot(solution.t[:i], solution.y[0][:i])
    ax.scatter(solution.t[:i], solution.y[0][:i])
    ax.set_xlabel('time')
    ax.set_ylabel('y(t)') 

def save_as_animation():
    global solution
    if(solution is None):
        messagebox.showerror("SolutionError","You must first calculate the equation!")
        return
    ani = FuncAnimation(fig, animate, frames=len(solution.t), interval=100)
    
    filename = tk.filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 file", "*.mp4")])
    if filename:
        ani.save(filename)
    ax.clear()
    ax.plot(solution.t, solution.y[0])
    ax.set_xlabel('time')
    ax.set_ylabel('y(t)')
        
    
def read_equation():
    global y_prime_entry,y0_entry,time_end_entry,time_start_entry
    filename = askopenfilename()
    file = open(filename, 'r')
    try:
        equation = file.readline()
        y0 = int(file.readline())
        time_start = int(file.readline())
        time_end = int(file.readline())
        if(not equation or not y0 or not time_start or not time_end ):
            print("One or more entries are null")
            return
        y_prime_entry.insert(0,equation)
        y0_entry.insert(0,y0)
        time_start_entry.insert(0, time_start)
        time_end_entry.insert(0, time_end)
        
    except:
        print("Y0,start time and end time must be an integer!")
    
def generate_random_equation():
    a = random.randint(1, 100)   
    b = random.randint(1, 100)   
    operator = random.choice(['+', '-','/','*'])  
    equation = f"{a}*y {operator} {b}"  
    return equation

    
def input_random():
    global y_prime_entry,y0_entry,time_end_entry,time_start_entry
    y_prime_entry.delete(0, 'end')
    y0_entry.delete(0, 'end')
    time_start_entry.delete(0, 'end')
    time_end_entry.delete(0, 'end')
    y_prime_entry.insert(0,generate_random_equation())
    y0_entry.insert(0, random.randint(1,100))
    time_start_entry.insert(0, random.randint(0, 100))
    time_end_entry.insert(0, random.randint(int(time_start_entry.get())+1, 101))
    
def input_txt():
    global y_prime_entry,y0_entry,time_end_entry,time_start_entry
    y_prime_entry.delete(0, 'end')
    y0_entry.delete(0, 'end')
    time_start_entry.delete(0, 'end')
    time_end_entry.delete(0, 'end')
    read_equation()
    y_prime_entry.config(state = "disabled")
    y0_entry.config(state = "disabled")
    time_end_entry.config(state = "disabled")
    time_start_entry.config(state = "disabled")
    

    
def input_manual():
    global y_prime_entry,y0_entry,time_end_entry,time_start_entry
    y_prime_entry.config(state = "enabled")
    y_prime_entry.delete(0, 'end')
    y0_entry.config(state = "enabled")
    y0_entry.delete(0, 'end')
    time_start_entry.config(state = "enabled")
    time_start_entry.delete(0, 'end')
    time_end_entry.config(state = "enabled")
    time_end_entry.delete(0, 'end')
    
def show_table():
    
    global solution
    if(solution is None):
        messagebox.showerror("SolutionError","You must first calculate the equation!")
        return
    table = tk.Tk()

    tree = ttk.Treeview(table)

    tree["columns"] = ("time", "y")

    tree.heading("time", text="Time")
    tree.heading("y", text="Y")

    for i, (t, y) in enumerate(zip(solution.t, solution.y.T)):
        t_str = "{:.4f}".format(t)
        y_str = " ".join(["{:.4f}".format(y_elem) for y_elem in y])
        tree.insert("", i, text=str(i), values=(t_str, y_str))

    tree.pack()


    table.mainloop()


root = tk.Tk()
root.title("My GUI")
root.geometry("800x500")

# Create a frame for the radio buttons
radio_frame = ttk.Frame(root)
radio_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)

# Create the radio buttons
input_method = tk.StringVar(value="Manual Input")
manual_rb = ttk.Radiobutton(radio_frame, text="Manual Input", variable=input_method, value="manualOption",command=input_manual)
txt_file_rb = ttk.Radiobutton(radio_frame, text="Input from .txt file", variable=input_method, value="txtOption",command=input_txt)
auto_rb = ttk.Radiobutton(radio_frame, text="Auto-generated input", variable=input_method, value="autoOption",command=input_random)
manual_rb.grid(row=0, column=0, sticky=tk.W)
txt_file_rb.grid(row=0, column=1, sticky=tk.W)
auto_rb.grid(row=0, column=2, sticky=tk.W)





# Create a frame for the labels and entries
label_frame = ttk.Frame(root)
label_frame.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)


method_frame=ttk.Frame(label_frame)
method_frame.grid(row=0,column=0,columnspan=2,padx=0,pady=0,sticky=tk.W)

solve_method = tk.StringVar(value="RK45")

methodRK45_rb = ttk.Radiobutton(method_frame, text="RK45",variable=solve_method,value="RK45")
methodRK45_rb.grid(row=1, column=0, sticky=tk.W)
methodRK23_rb = ttk.Radiobutton(method_frame, text="RK23",variable=solve_method,value="RK23")
methodRK23_rb.grid(row=2, column=0, sticky=tk.W)
methodDOP853_rb = ttk.Radiobutton(method_frame,variable=solve_method, text="DOP853",value="DOP853")
methodDOP853_rb.grid(row=3, column=0, sticky=tk.W)
methodLSODA_rb = ttk.Radiobutton(method_frame,variable=solve_method, text="LSODA",value="LSODA")
methodLSODA_rb.grid(row=4,column=0,sticky=tk.W)


y_prime = tk.StringVar()
t_start = float()
t_end = float()



# Create the labels and entries
y_prime_label = ttk.Label(label_frame, text="y'=")
y_prime_label.grid(row=4, column=0, sticky=tk.E)
y_prime_entry = ttk.Entry(label_frame)
y_prime_entry.grid(row=4, column=1, sticky=tk.W)

y0_label = ttk.Label(label_frame, text="y(0)=")
y0_label.grid(row=5, column=0, sticky=tk.E)
y0_entry = ttk.Entry(label_frame)
y0_entry.grid(row=5, column=1, sticky=tk.W)

time_start_label = ttk.Label(label_frame, text="Time start=")
time_start_label.grid(row=6, column=0, sticky=tk.E)
time_start_entry = ttk.Entry(label_frame)
time_start_entry.grid(row=6, column=1, sticky=tk.W)

time_end_label = ttk.Label(label_frame, text="Time end=")
time_end_label.grid(row=7, column=0, sticky=tk.E)
time_end_entry = ttk.Entry(label_frame)
time_end_entry.grid(row=7, column=1, sticky=tk.W)

table_button = ttk.Button(label_frame,text="Value Table",command=show_table)
table_button.grid(row=8,column=1,sticky=tk.E)

# Create a frame for the plot
plot_frame = ttk.Frame(root)
plot_frame.grid(row=1, column=1, padx=10, pady=10, sticky=tk.NSEW)

# Create the plot
fig = plt.Figure()

ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, plot_frame)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Create a frame for the buttons
button_frame = ttk.Frame(root)
button_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=tk.E)

# Create the buttons
calculate_button = ttk.Button(button_frame, text="Calculate", command=submit)
calculate_button.pack(side=tk.LEFT, padx=10)

save_animation_button = ttk.Button(button_frame, text="Save as Animation",command=save_as_animation)
save_animation_button.pack(side=tk.LEFT, padx=10)

# Set the grid weights
root.columnconfigure(1, weight=1)
root.rowconfigure(1, weight=1)

input_method.set("manualOption")
input_manual()


root.mainloop()




import tkinter as tk
import time
import numpy as np
import pandas as pd

from simulasi_antrean import avg_distribution, count_cumulative, distribute_random
from simulasi_antrean import Server, Customer, Simulation


# Create a Tkinter window
root = tk.Tk()
root.geometry('1080x720')
root.title("Program Simulasi Antrean")

label0 = tk.Label(root, text="Program Simulasi Antrean", justify='center', font=20)
label0.place(x=0, y=50, width=720)

# Create a Text widget
text_widget = tk.Text(root, wrap=tk.WORD, width=200, height=200)
text_widget.place(x=10, y=100, width=800, height=500)

# Create a Scrollbar

scrollbar = tk.Scrollbar(text_widget)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Attach the Text widget and Scrollbar
text_widget.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=text_widget.yview)

def insert_texts(text):
    text_widget.insert(tk.END, f"{text}\n")
    text_widget.update_idletasks()
    text_widget.see(tk.END)
    time.sleep(0.001)

simulator = Simulation(function=insert_texts)

# Button untuk mulai simulasi
start_button = tk.Button(root, text="Start Simulation", command=simulator.single_server_simulation, width=25, bg='#00ff00')
start_button.place(x=650, y=650)

def create_input(root, label, x, y, width, button_name,key, simulator:Simulation=simulator):
    label = tk.Label(root, text=label)
    label.place(x=x, y=y, width=width)

    entry = tk.Entry(root)
    entry.place(x=x, y=y + 20, width=width)

    def command():
        val = entry.get()
        vars(simulator)[key] = eval(val)

    btn = tk.Button(root, text=button_name,bg='#aaa', fg='blue', command=command)
    btn.place(x=x, y=y + 40, width=width)

create_input(root, label="Total Waktu Simulasi", x=850, y=100, width=200, button_name="submit", key='max_minute')
create_input(root, label="Distribusi Service Time Server", x=850, y=200, width=200, button_name="submit", key='distribution')

reset = lambda : text_widget.delete("1.0", "end")
reset_button = tk.Button(root, text="Reset", command=reset, width=25, bg='#ff0000')
reset_button.place(x=850, y=650)
# Run the Tkinter main loop
root.mainloop()

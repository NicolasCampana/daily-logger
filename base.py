import tkinter as tk
import tkinter.messagebox as tkmsg
import datetime
import threading
import time
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CountingTime(threading.Thread):
    def __init__(self, master, start_time, end_time):
        super().__init__()
        self.master = master
        self.start_time = start_time
        self.end_time = end_time

        self.end_now = False
        self.paused = False
        self.forced_quit = False

    def run(self):
        while(1):
            if not self.paused and not self.end_now and not self.forced_quit:
                self.main_loop()
                if datetime.datetime.now() >= self.end_time:
                    # Add force quit
                    self.master.finish()
                    break
            elif self.forced_quit:
                del self.master.worker
                break
            time.sleep(1)
        
    def main_loop(self):
        now = datetime.datetime.now()
        if now < self.end_time:
            exc = self.end_time - now
            self.master.update_time_remaining(str(exc))

                
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Daily Logger")
        self.maxsize(800,600)
        self.create_control_buttons()
        self.create_list_box_time()
        self.register_widgets()
        self.protocol("WM_DELETE_WINDOW", self.safe_destroy)

    def create_control_buttons(self):
        self.start_button = tk.Button(self, text="Start!", command=self.start)
        self.time_remaining_var = tk.StringVar(self, value="25:00") 
        self.label_remaining = tk.Label(self, textvar=self.time_remaining_var)
        self.label_remaining.pack(side = tk.BOTTOM)
        self.start_button.pack(side = tk.TOP)
        self.pause_button = tk.Button(self, text="Pause!", command=self.pause, state="disabled")
        self.pause_button.pack(side= tk.TOP)
    
    def create_list_box_time(self):
        self.choose_time = tk.Listbox(self, selectmode=tk.SINGLE)
        self.choose_time.bind("<<ListboxSelect>>", self.update_start_time)
        for index, i in enumerate(range(5,30, 5)):
            self.choose_time.insert(index, f"{i}:00")
        self.choose_time.pack()
    
    def create_list_box_tasks(self):
        self.tasks = tk.Listbox(self, selectmode=tk.SINGLE, highlightcolor="red", height=5)
        self.tasks.insert(0, "Estudo")
        self.tasks.insert(0, "Estágio")
        self.tasks.insert(0, "Treino")
        self.tasks.insert(0, "Almoço")
        self.tasks.insert(0, "Duolingo")
        self.tasks.pack(side=tk.LEFT)


    def update_start_time(self, event):
        self.time_remaining_var.set(self.choose_time.get(self.choose_time.curselection()))

    def register_widgets(self):
        self.label = tk.Label(self, text="O que cê ta arrumando?")
        self.create_list_box_tasks()
        self.send_button = tk.Button(self, text="Registrar!", command=self.write_activity)
        self.label.pack()
        self.send_button.pack()
    
    def finish(self):
        del self.worker
        tkmsg.showinfo("Parabens carai", "Vai tomar no cu!")
    
    

    def setup_worker(self):
        choosed_minutes = int(self.time_remaining_var.get().split(":")[0])
        end_time = datetime.datetime.now() + datetime.timedelta(minutes=choosed_minutes)
        worker = CountingTime(self, datetime.datetime.now, end_time)
        self.worker = worker
        self.worker.setDaemon(True)

    def pause(self):
        self.worker.paused = not self.worker.paused
        if(self.worker.paused):
            self.pause_button.configure(text="Resume")
            self.worker.start_time = datetime.datetime.now()
        else:
            self.pause_button.configure(text="Pause")
            end_time = datetime.datetime.now() - self.worker.start_time
            self.worker.end_time = self.worker.end_time + datetime.timedelta(end_time)


    def start(self):
        if not hasattr(self, "worker"):
            self.setup_worker()
        self.worker.start()
        self.pause_button.configure(text="Pause")
        self.start_button.configure(state="disabled")
        self.choose_time.configure(state="disabled")
        self.pause_button.configure(state="active")

    def update_time_remaining(self, new_value):
        self.time_remaining_var.set(new_value)
        print(self.time_remaining_var.get())
        self.update_idletasks()

    def write_activity(self):
        with open("db.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')},{self.tasks.get(self.tasks.curselection())}\n")
        #self.input_field.delete(0, tk.END)
        #self.input_field.configure(state="disabled")
        #self.send_button.configure(state="disabled")
    
    def safe_destroy(self):
        if hasattr(self, "worker"):
            self.worker.forced_quit = True
            self.after(100, self.safe_destroy)
        else:
            self.destroy()


class MainFrame(tk.Tk):
    zip_dict = {}
    def __init__(self):
        super().__init__()
        self.title("Daily Logger")
        self.maxsize(800,600)
        self.geometry("800x600")
        self.figure = plt.Figure()
        self.ax1 = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack()
        self.read_file()
    
    def read_file(self):
        self.data = pd.read_csv("db.txt")
        for index, row in self.data.iterrows():
            if not row[1] in self.zip_dict:
                self.zip_dict[row[1]] = max(self.zip_dict.values())+1 if len(self.zip_dict) != 0 else 0
        
        self.data["label"] = self.data["activity"].apply(lambda x: self.zip_dict[x])
        self.create_graph()
        
    
    def create_graph(self):
        self.ax1.clear()
        #labels = [i for i in self.zip_dict]
        labels = []
        values = []
        for i, k in self.data.groupby(by="activity"):
            labels.append(i)
            values.append(len(k))
            
        #ax1.plot(k['activity'], k['time'], label=i)
        #self.data.groupby(by="activity").plot(kind="bar",, ax = ax1)
        self.ax1.pie(values, labels=labels)
        self.canvas.draw()
        self.after(2000, self.read_file)


app2 = Application()
app = MainFrame()
#app.mainloop()
app2.mainloop()
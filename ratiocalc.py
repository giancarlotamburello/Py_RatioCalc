import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr
import contextily as ctx
import pandastable as pt
from scipy import stats

class RatioCalcApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RatioCalc Python")

        self.file_path = None
        self.df = None # Data frame
        self.fc = None # First column
        filtered_num = None
        filtered_den = None
        self.scatter_fig = None
        self.scatter_ax = None
        self.results_list = []

        # Create widgets for the GUI

        # Create a frame to hold the buttons
        # self.label_frame = tk.Frame(root, bd=2, relief=tk.SUNKEN)
        # self.label_frame.pack(pady=5, padx=5, fill=tk.X)

        self.file_var = tk.StringVar()
        self.file_dropdown = tk.ttk.Combobox(root, textvariable=self.file_var)
        self.file_var.set("No file selected")
        self.file_dropdown.bind("<<ComboboxSelected>>", self.dropdown_changed)
        self.file_dropdown.config(width=50)
        self.file_dropdown.config(font=("Helvetica", 10, "italic"))
        self.file_dropdown.pack(pady=5, padx=5)

        self.button_frame1 = tk.Frame(root)
        self.button_frame1.pack(pady=15)

        self.info_frame3 = tk.Frame(self.button_frame1)
        self.info_frame3.pack(side=tk.LEFT,pady=5, padx=5, fill=tk.X)

        self.info_frame = tk.Frame(self.info_frame3, bd=2, relief=tk.SUNKEN)
        self.info_frame.pack(side=tk.LEFT,pady=5, padx=5, fill=tk.X)

        self.info_data = tk.Label(self.info_frame, text="No data selected", font=("Helvetica", 10),justify=tk.LEFT)
        self.info_data.pack(pady=5, padx=5)

        self.info_frame2 = tk.Frame(self.button_frame1, bd=2, relief=tk.SUNKEN)
        self.info_frame2.pack(side=tk.LEFT,pady=5, padx=5, fill=tk.X)

        self.info_fit = tk.Label(self.info_frame2, text="No data selected", font=("Helvetica", 10),justify=tk.LEFT)
        self.info_fit.pack(pady=5, padx=5)

        self.shift_value = "-"
        self.do_shift = tk.BooleanVar()
        self.do_shift_checkbutton = tk.Checkbutton(self.info_frame3, text="Shift", variable=self.do_shift,command=self.shift_flag)
        self.do_shift_checkbutton.pack(side=tk.TOP,pady=5)

        self.append_button = tk.Button(self.info_frame3, text="Remove", command=self.append_fit_parameters)
        self.append_button.pack(side=tk.BOTTOM, pady=5)

        self.append_button = tk.Button(self.info_frame3, text="Add", command=self.append_fit_parameters)
        self.append_button.pack(side=tk.BOTTOM, pady=5)
        
        
        # Create a menu bar
        self.menu_bar = tk.Menu(self.root)

        # Create a File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open...", command=self.browse_file)
        self.file_menu.add_command(label="Open and split...", command=self.browse_file_to_split)
        self.file_menu.add_command(label="Save")#, command=save_file)
        self.file_menu.add_separator()  # Add separator
        #  Separator
        self.sep_var = tk.StringVar()
        self.separator_menu = tk.Menu(self.file_menu, tearoff=0)
        self.separator_menu.add_radiobutton(label=";", variable=self.sep_var, value=";")
        self.separator_menu.invoke(0)
        self.separator_menu.add_radiobutton(label=",",variable=self.sep_var, value=",")
        self.separator_menu.add_radiobutton(label="Tab",variable=self.sep_var, value="\t")
        self.file_menu.add_cascade(label="Separator", menu=self.separator_menu)  # Add Options menu under Edit
        self.file_menu.add_separator()  # Add separator 
        self.file_menu.add_command(label="Exit", command=self.exit_app)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        
        # Create a Results menu
        self.results_menu = tk.Menu(self.menu_bar, tearoff=0)  
        self.results_menu.add_command(label="Loaded data",command=self.show_raw_data_table)
        self.results_menu.add_command(label="Manual results",command=self.show_fit_parameters_table)
        self.results_menu.add_command(label="Processing results ",command=self.show_proc_results_table)
        self.menu_bar.add_cascade(label="Tables", menu=self.results_menu)

        # Create a Selection menu
        self.selection_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Selection", menu=self.selection_menu)

        #  Col names
        self.col_names = ""

        #  Numerator
        self.y2_var = tk.StringVar()
        self.numerator_menu = tk.Menu(self.selection_menu, tearoff=0)
        self.numerator_menu.add_radiobutton(label="--",variable=self.y2_var)  # Default selected
        self.selection_menu.add_cascade(label="Numerator", menu=self.numerator_menu)  # Add Options menu under Edit

        #  Denominator
        self.y1_var = tk.StringVar()
        self.denominator_menu = tk.Menu(self.selection_menu, tearoff=0)
        self.denominator_menu.add_radiobutton(label="--",variable=self.y1_var)  # Default selected
        self.selection_menu.add_cascade(label="Denominator", menu=self.denominator_menu)  # Add Options menu under Edit

        #  Plume marker
        self.mark_var = tk.StringVar()
        self.marker_menu = tk.Menu(self.selection_menu, tearoff=0)
        self.marker_menu.add_radiobutton(label="--",variable=self.mark_var)  # Default selected
        self.selection_menu.add_cascade(label="Plume marker", menu=self.marker_menu)  # Add Options menu under Edit

        #  Longitude
        self.lon_var = tk.StringVar()
        self.lon_menu = tk.Menu(self.selection_menu, tearoff=0)
        self.lon_menu.add_radiobutton(label="--",variable=self.lon_var)  # Default selected
        self.selection_menu.add_cascade(label="Longitude", menu=self.lon_menu)  # Add Options menu under Edit

        #  Longitude
        self.lat_var = tk.StringVar()
        self.lat_menu = tk.Menu(self.selection_menu, tearoff=0)
        self.lat_menu.add_radiobutton(label="--",variable=self.lat_var)  # Default selected
        self.selection_menu.add_cascade(label="Latitude", menu=self.lat_menu)  # Add Options menu under Edit

        # Create a Plot menu
        self.plot_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.plot_menu.add_command(label="Scatter and time-series",command=self.generate_dual_y_plot)
        self.plot_menu.add_command(label="Coordinates",command=self.generate_lonlat_plot)
        self.menu_bar.add_cascade(label="Plot", menu=self.plot_menu)

        # Create a Processing menu 
        self.proc_menu = tk.Menu(self.menu_bar, tearoff=0)  
        self.proc_menu.add_command(label="Parameters",command=self.open_settings_window)
        self.proc_menu.add_separator()  # Add separator
        self.proc_menu.add_command(label="Current dataset",command=self.ratio_proc)
        self.proc_menu.add_command(label="Multiple dataset",command=self.show_fit_parameters_table)
        self.menu_bar.add_cascade(label="Processing", menu=self.proc_menu)

        # Add the menu bar to the window
        self.root.config(menu=self.menu_bar)

        # Table
        self.table_window = tk.Toplevel(self.root)
        #self.table_window.withdraw()  # Hide the window initially
        self.table_window.title("Results")
        self.table_frame = tk.Frame(self.table_window)
        self.table_frame.pack(fill=tk.BOTH, expand=True)
        self.table_window.destroy()

    def open_file_to_sep(self):
        plt.close('all')
        self.new_window = tk.Toplevel(self.root)
        self.new_window.title("Open file to split")

        description_label = tk.Label(self.new_window, text="Enter the time format of the first column. Here Some examples:\n"+
                      "%Y-%m-%d %H:%M:%S for 2024-02-12 12:00:00\n" + 
                      "%d/%m/%Y %H:%M:%S for 12/02/2024 12:00:00\n" +
                      "%d-%m-%y %H:%M for 12-02-24 12:00", justify=tk.LEFT)
        description_label.pack(pady=5,padx=5)
   
        self.time_fmt = '%Y-%m-%d %H:%M:%S'
        description_entry = tk.Entry(self.new_window, width=25)
        description_entry.insert(0, self.time_fmt)
        description_entry.pack(pady=5)

        spinbox_label = tk.Label(self.new_window, text="Split if next sample is taken after seconds:")
        spinbox_label.pack(pady=5)

        self.sep_time = tk.DoubleVar(value=60)  # initial value
        spinbox = tk.Spinbox(self.new_window, from_=1, to=10000, textvariable=self.sep_time, width=10)
        spinbox.pack(pady=5)

        submit_button = tk.Button(self.new_window, text="Open file", command=self.load_and_split_data)
        submit_button.pack(pady=10)

    def load_and_split_data(self):
        self.new_window.destroy()
        if not self.file_path:
            messagebox.showerror("Error", "Please select a text file.")
            return

        self.separator = self.sep_var.get()  # Get the separator from the entry
        try:
            #self.df = pd.read_csv(self.file_path, sep=self.separator, parse_dates=[0], date_parser=lambda x: pd.to_datetime(x, format='%Y-%m-%d %H:%M:%S'))
            self.df = pd.read_csv(self.file_path, sep=self.separator)
            self.df.iloc[:, 1:] = self.df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
            self.df.iloc[:, 0] = pd.to_datetime(self.df.iloc[:, 0], format=self.time_fmt)

            if self.df.shape[1] < 3:
                messagebox.showerror("Error", "The data must have at least three columns.")
                return

            self.df.iloc[:, 1:] = self.df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
            #self.fc = self.df.pop(self.df.columns[0])
            self.fc = self.df.iloc[:, 0]
            self.update_column_menus()
            self.info_data.config(text=f"Data loaded: {self.df.shape[0]} rows x {self.df.shape[1]} columns")

            # Split the dataset if the difference between dates is greater than N seconds
            self.split_datasets = []
            current_split = [self.df.iloc[0]]

            deltat = np.int64(np.abs(np.diff(self.fc).astype('timedelta64[s]')))
            deltat = np.append(0,deltat)
            split_indices = np.where(deltat > self.sep_time.get())
            split_indices = np.array(split_indices)[0,:]
            self.file_dropdown['values'] = []
            for i in range(len(split_indices)):
                if i == 0:
                    self.split_datasets.append(self.df.iloc[:split_indices[i]])
                    time_start = self.fc.iloc[:split_indices[i]]
                else:
                    self.split_datasets.append(self.df.iloc[split_indices[i-1]:split_indices[i]])
                    time_start = self.fc.iloc[split_indices[i-1]:split_indices[i]]
   
                len_df = len(time_start)
                time_start = time_start.iloc[0]
                values = list(self.file_dropdown["values"])
                self.file_dropdown["values"] = values + [str(time_start) + " (" + str(len_df)  + " samples)"]

            if split_indices[-1] < len(self.df):
                self.split_datasets.append(self.df.iloc[split_indices[-1]:])

            self.file_dropdown.current(0)
            self.dropdown_changed(None)

            messagebox.showinfo("Message", f"Data split into {len(self.split_datasets)} segments.")
            
        except Exception as e:
            #messagebox.showerror("Error", f"Failed to load data: {e}")
            messagebox.showerror("Error", "Failed to load data.\nCheck the column separator and/or time format.")

        

        plt.close('all')


    def dropdown_changed(self,event):
        selection = self.file_dropdown.get()
        self.df = pd.DataFrame.copy(self.split_datasets[self.file_dropdown.current()],deep=True)
        self.df.reset_index(drop=True, inplace=True)
        self.fc = self.df.pop(self.df.columns[0])
        self.update_column_menus()

        if hasattr(self, 'table_data') and self.table_data.winfo_exists():
            self.dTDaPT2.updateModel(pt.TableModel(self.df))
            self.dTDaPT2.redraw()

        self.info_data.config(text=f"Data loaded: {self.df.shape[0]} rows x {self.df.shape[1]} columns")

        if plt.fignum_exists(1):
            xlim = [self.click_start[0],self.click_end[0]]

            if xlim[1] > self.fc.size:
                xlim[1] = self.fc.size - 1
            
            if xlim[0] > self.fc.size:
                xlim[0] = self.fc.size - 10

            self.simulate_click_event(xlim[0],xlim[1])
            self.fig_dual.canvas.draw_idle()
            self.generate_dual_y_plot()


    def exit_app(self):
        plt.close('all')
        self.root.quit()
        self.root.destroy()

    def browse_file(self):
        if hasattr(self, 'table_window') and self.table_window.winfo_exists():
            self.table_window.destroy()
        if hasattr(self, 'table_data') and self.table_data.winfo_exists():
            self.table_data.destroy()
        plt.close('all')
        self.file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.*")])
        if self.file_path:
            #self.label_file.config(text=self.file_path)
            self.file_var.set(os.path.basename(self.file_path))

            self.file_dropdown['values'] = [os.path.basename(self.file_path)]
            self.load_data()
    
    def browse_file_to_split(self):
        if hasattr(self, 'table_window') and self.table_window.winfo_exists():
            self.table_window.destroy()
        if hasattr(self, 'table_data') and self.table_data.winfo_exists():
            self.table_data.destroy()
        plt.close('all')
        self.file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.*")])
        if self.file_path:
            #self.label_file.config(text=self.file_path)
            self.file_var.set(self.file_path)
            #self.new_window.destroy()
            self.open_file_to_sep()

    def load_data(self):
        if not self.file_path:
            messagebox.showerror("Error", "Please select a text file.")
            return

        self.separator = self.sep_var.get() # Get the separator from the entry
        try:
            self.df = pd.read_csv(self.file_path, sep=self.separator)
            self.df.iloc[:, 1:] = self.df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
            self.fc = self.df.pop(self.df.columns[0])
            self.update_column_menus()
            self.info_data.config(text=f"Data loaded: {self.df.shape[0]} rows x {self.df.shape[1]} columns")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")

        plt.close('all')

    def update_column_menus(self):
        columns = list(self.df.columns)

        if columns == self.col_names:
            return
        else:
            self.col_names = columns

        # Update y menu selection   
        self.numerator_menu.delete(0, 'end')
        self.numerator_menu.invoke(0)
        self.y2_var.set(columns[0])
        new_options = columns

        for option in new_options:
            self.numerator_menu.add_radiobutton(label=option, variable=self.y2_var,command=self.menu_click)
             
        # Update y menu selection   
        self.denominator_menu.delete(0, 'end')
        self.denominator_menu.invoke(0)
        self.y1_var.set(columns[1])
        new_options = columns
        for option in new_options:
            self.denominator_menu.add_radiobutton(label=option, variable=self.y1_var,command=self.menu_click)
        
        # Update y menu selection   
        self.marker_menu.delete(0, 'end')
        self.marker_menu.invoke(0)
        self.mark_var.set(columns[0])
        new_options = columns
        for option in new_options:
            self.marker_menu.add_radiobutton(label=option, variable=self.mark_var,command=self.menu_click)
        
        # Update y menu selection   
        self.lon_menu.delete(0, 'end')
        self.lon_menu.invoke(0)
        self.lon_var.set(columns[0])
        new_options = columns
        for option in new_options:
            self.lon_menu.add_radiobutton(label=option, variable=self.lon_var,command=self.menu_click)
        
        # Update y menu selection   
        self.lat_menu.delete(0, 'end')
        self.lat_menu.invoke(0)
        self.lat_var.set(columns[0])
        new_options = columns
        for option in new_options:
            self.lat_menu.add_radiobutton(label=option, variable=self.lat_var,command=self.menu_click)

    def menu_click(self):
        self.generate_dual_y_plot()

    def generate_scatter_plot(self):

        if self.df is None:
            messagebox.showerror("Error", "No data loaded.")
            return

        y1 = self.y1_var.get()
        y2 = self.y2_var.get()

        self.info_data.config(text=f"Num.:\t{y2} \n\n"
                              f"Den.:\t{y1} \n\n"
                              f"Marker:\t{self.mark_var.get()} \n\n"
                              f"Lon:\t{self.lon_var.get()} \n\n"
                              f"Lat:\t{self.lat_var.get()}")

        try:
            xlim = [self.click_start[0],self.click_end[0]]

            if xlim[0] > xlim[1]:
                xlim = xlim[::-1]

            if self.do_shift.get():
                best_shift = self.best_correlation(np.array(self.df.iloc[:][y1]),np.array(self.df.iloc[:][y2]), np.int32(xlim[0]),np.int32(xlim[1]))
                self.shift_value = str(best_shift)

            else:
                best_shift = 0
                self.shift_value = "-"
            
            filtered_num = np.array(self.df.iloc[(self.df.index >= xlim[0]) & (self.df.index <= xlim[1])][y2])
            filtered_den = np.array(self.df.iloc[(self.df.index >= (xlim[0]-best_shift) ) & (self.df.index <= (xlim[1]-best_shift))][y1])
            
            filtered_fc = self.fc.iloc[(self.fc.index >= xlim[0]) & (self.fc.index <= xlim[1])] # First column
        except:
            xlim = [0,10]
            self.click_start = (0,0)
            self.click_end = (10,0)
            filtered_num = np.array(self.df[y2])
            filtered_den = np.array(self.df[y1])
            filtered_fc = self.fc # First column

        if plt.fignum_exists(3):
            self.generate_lonlat_plot(update=True)

        plt.figure(num=2, figsize=(10,4)) #figsize=(6,7)
        plt.clf()  # Clear the figure to avoid overlapping plots
        mngr = plt.get_current_fig_manager()

        # Create a figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2,num=2)


        # First plot: Scatter plot of X1 vs X2
        ax1.scatter(filtered_den, filtered_num, color='blue')
        ax1.set_xlabel(y1)
        ax1.set_ylabel(y2)
        #ax1.set_title(f"{filtered_fc.iloc[0]} - {filtered_fc.iloc[-1]}")

        try:
            slope, intercept, r_value, p_value, std_err = stats.linregress(filtered_den, filtered_num)
        except:
            slope = np.NaN
            intercept = np.NaN
            r_value = np.NaN
            p_value = np.NaN
            std_err = np.NaN

        fit = [slope,intercept]
        r_squared = r_value**2

        # Add the best fit line to the scatter plot
        ax1.plot(filtered_den, filtered_den*fit[0]+fit[1], color='red', label='Best Fit Line')
        ci = 1.959964*std_err

        # Create equation text
        #equation_text = f"y = {fit[0]:.2f} x (±{ci:.2f}) + {fit[1]:.2f}\nR² = {r_squared:.2f}"
        #ax1.text(0.05, 0.95, equation_text, transform=ax1.transAxes,
        #                     fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', edgecolor='black', facecolor='lightgray'))

        self.info_fit.config(text=(
            f"{filtered_fc.iloc[0]} - {filtered_fc.iloc[-1]}\n\n"
            f"Num. samples = {len(filtered_num)}\n\n"
            f"{y2} = {fit[0]:.2f} {y1} (±{ci:.2f}) + {fit[1]:.2f}\n\n"
            f"R² = {r_squared:.2f}\n\n"
            f"Max {y2} = {filtered_num.max():.2f}\n\n"
            f"Max {y1} = {filtered_den.max():.2f}\n\n"
            f"Shift = {self.shift_value}"
        ))


        # Second plot: Line plot of X1 and X2 against indexes
        index = np.arange(len(filtered_num))  # Create an index array for X1 and X2
        ax3 = ax2.twinx()  # Create a second y-axis for the second plot

        # Plot X1 and X2 against their indices
        ax2.plot(index, filtered_num, color='g')
        ax3.plot(index, filtered_den, color='b')

        ax2.set_xlabel('Index')
        ax2.set_ylabel(y2, color='g')
        ax3.set_ylabel(y1, color='b')


        plt.tight_layout()  # Adjust layout for better spacing
        plt.show(block=False) # Display the plots


    def generate_dual_y_plot(self):
        if self.df is None:
            messagebox.showerror("Error", "No data loaded.")
            return


        # Close all plot windows if plot 1 is already open
        if plt.fignum_exists(1):
            #plt.close('all')
            plt.figure(num=1)
            plt.clf() 

        y1 = self.y1_var.get()
        y2 = self.y2_var.get()


        self.fig_dual, ax1 = plt.subplots(num=1, figsize=(10, 4))  # Create a new figure and axis

        # Plot the first y-axis
        ax1.plot(self.df.index, self.df[y2], 'g-', label=y2)
        ax1.set_xlabel('Sample Number')
        ax1.set_ylabel(y2, color='g')
        ax1.tick_params(axis='y', labelcolor='g')

        # Create a second y-axis
        ax2 = ax1.twinx()
        ax2.plot(self.df.index, self.df[y1], 'b-', label=y1)
        ax2.set_ylabel(y1, color='b')
        ax2.tick_params(axis='y', labelcolor='b')


        try:
            xlim = [self.click_start[0],self.click_end[0]]
        except:
            xlim = [0,10]
            self.click_start = (0,0)
            self.click_end = (10,0)
            
            
        if xlim[0] > xlim[1]:
            xlim = xlim[::-1]

        self.line_start = ax1.axvline(xlim[0],color='g')
        self.line_end = ax2.axvline(xlim[1],color='r')

        # Click
        cid = self.fig_dual.canvas.mpl_connect('button_press_event', self.onclick)
        cid3 = self.fig_dual.canvas.mpl_connect('key_press_event', self.on_key_press)

        self.fig_dual.tight_layout() 

        #ax1.callbacks.connect('xlim_changed', self.update_scatter_plot)

        if not plt.fignum_exists(2):
            if plt.fignum_exists(1):
                try:
                    self.simulate_click_event(xlim[0],xlim[1])
                except:
                    pass
        else:
            self.generate_scatter_plot()

        plt.show(block=False)

    def on_key_press(self, event):
        if event.key == 'left':
            delta1 = delta2 = -1
        elif event.key == 'right':
            delta1 = delta2 = 1
        elif event.key == 'shift+left':
            delta1 = delta2 = -10
        elif event.key == 'shift+right':
            delta1 = delta2 = 10
        elif event.key == 'up':
            delta1 = -1
            delta2 = 1
        elif event.key == 'down':
            delta1 = 1
            delta2 = -1
        elif event.key == 'shift+up':
            delta1 = -10
            delta2 = 10
        elif event.key == 'shift+down':
            delta1 = 10
            delta2 = -10
        elif event.key == 'pageup':
            if self.file_dropdown.current() != 0:
                self.file_dropdown.current(self.file_dropdown.current() - 1)
                self.dropdown_changed(None)
            return
        elif event.key == 'pagedown':
            if self.file_dropdown.current() < (len(self.file_dropdown.cget("values")) -1):
                self.file_dropdown.current(self.file_dropdown.current() + 1)
                self.dropdown_changed(None)        
            return
        else:
            return

        xlim = [self.click_start[0], self.click_end[0]]
        self.simulate_click_event(xlim[0] + delta1, xlim[1] + delta2)
        self.fig_dual.canvas.draw_idle()

    def onclick(self, event_click):
        
        toolbar = plt.get_current_fig_manager().toolbar
        if toolbar.mode == 'zoom rect':
            return

        if event_click.button == 1:
            if event_click.xdata > self.click_end[0]:
                self.click_start = (self.click_end[0],event_click.ydata)
                self.click_end = (event_click.xdata,0)
            else:
                self.click_start = (event_click.xdata, event_click.ydata)
            
            self.line_start.set_xdata([self.click_start[0]])
            self.line_end.set_xdata([self.click_end[0]])
            self.generate_scatter_plot()
        

        elif event_click.button == 3:


            if event_click.xdata < self.click_start[0]:
                self.click_end = (self.click_start[0],event_click.ydata)
                self.click_start = (event_click.xdata,0)
            else:
                self.click_end = (event_click.xdata, event_click.ydata)

            self.line_start.set_xdata([self.click_start[0]])
            self.line_end.set_xdata([self.click_end[0]])
            self.generate_scatter_plot()


    def simulate_click_event(self, x_start, x_end):
        """Simulate click events on the graph to set start and end lines."""
        # Simulate middle click for start line
        self.onclick(type('Event', (object,), {'button': 1, 'xdata': x_start, 'ydata': 0}))
        # Simulate right click for end line
        self.onclick(type('Event', (object,), {'button': 3, 'xdata': x_end, 'ydata': 0}))

    def update_scatter_plot(self, event_ax):
        """Update the scatter plot based on the dual plot's x-limits."""
        self.xlim = event_ax.get_xlim()  # Update the stored x-limits
        self.generate_scatter_plot()  # Refresh the scatter plot


    def shift_flag(self):
        self.simulate_click_event(self.click_start[0],self.click_end[0])

    def generate_lonlat_plot(self,update=False):
        lon = self.lon_var.get()
        lat = self.lat_var.get()
        marker = self.mark_var.get()

        try:
            xlim = [self.click_start[0],self.click_end[0]]
            filtered_df = self.df.iloc[(self.df.index >= xlim[0]) & (self.df.index <= xlim[1])]
            filtered_fc = self.fc.iloc[(self.fc.index >= xlim[0]) & (self.fc.index <= xlim[1])]
        except:
            filtered_df = self.df
            filtered_fc = self.fc
        

        if plt.fignum_exists(3) and not update:
            plt.close(3)

        plt.figure(num=3)
        plt.clf()  # Clear the figure to avoid overlapping plots
        
        # Scatter plot

        mark_index = filtered_df[marker].sort_values().index

        ax = plt.gca()  # Get the current axes
        scatter = ax.scatter(self.df[:][lon], self.df[:][lat], c='gray', s=15)
        ax.scatter(filtered_df[lon].reindex(mark_index), filtered_df[lat].reindex(mark_index), c=filtered_df[marker].reindex(mark_index),
               vmin=np.array(filtered_df[marker]).min(), vmax=np.array(filtered_df[marker]).max(), cmap='viridis')
        ax.set_aspect('equal', 'box')

        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")

        # Add OpenStreetMap basemap
        ctx.add_basemap(ax, crs='EPSG:4326', source=ctx.providers.OpenStreetMap.Mapnik)

        # Add color bar
        cbar = plt.colorbar(scatter)
        # cbar.clim = (np.array(filtered_df[marker]).min(), np.array(filtered_df[marker]).max())
        cbar.set_label(marker)
        # cbar.set_ticks(np.linspace(np.array(filtered_df[marker]).min(),np.array(filtered_df[marker]).max(), num=10))
        ticklabels = np.linspace(np.array(filtered_df[marker]).min(),np.array(filtered_df[marker]).max(), num=10)
        #cbar.set_ticks(ticklabels)
        cbar.set_ticklabels([f"{tick:.2f}" for tick in ticklabels])
        plt.show(block=False)


    def append_fit_parameters(self):

        y1 = self.y1_var.get()
        y2 = self.y2_var.get()
        lon = self.lon_var.get()
        lat = self.lat_var.get()
        marker = self.mark_var.get()
        shift = self.shift_value

        if self.df is None:
            messagebox.showerror("Error", "No data loaded.")
            return

        try:
            xlim = [self.click_start[0],self.click_end[0]]
            filtered_df = self.df.iloc[(self.df.index >= xlim[0]) & (self.df.index <= xlim[1])]
            filtered_fc = self.fc.iloc[(self.fc.index >= xlim[0]) & (self.fc.index <= xlim[1])]
        except:
            filtered_df = self.df
            filtered_fc = self.fc

        start = filtered_fc.iloc[0]
        slope, intercept, r_value, p_value, std_err = stats.linregress(filtered_df[y1], filtered_df[y2])
        fit = [slope,intercept]
        r_squared = r_value**2
        ci = 1.959964*std_err
        y2_max = filtered_df[y2].max()
        y1_max = filtered_df[y1].max()
        mark_max = filtered_df[marker].max()

        if plt.fignum_exists(3):
            lon_mean = filtered_df[lon].mean()
            lat_mean = filtered_df[lat].mean()
        else:
            lon_mean = "-"
            lat_mean = "-"

        if not hasattr(self, 'results_list'):
            self.results_list = []
        self.results_list.append([start, y2, y1, fit[0], fit[1], r_squared, y2_max, y1_max, mark_max, shift,lon_mean, lat_mean])

        results_df = pd.DataFrame(self.results_list)
        results_df.columns = ["Time","Numerator", "Denominator", "Slope", "Intercept", "R²", "Max num.", "Max den.", "Max marker","Shift", "Longitude", "Latitude"]

        if (hasattr(self, 'table_window') or self.table_window.winfo_exists()) and hasattr(self, 'dTDaPT') :
            try:
                self.dTDaPT.updateModel(pt.TableModel(results_df))
                self.dTDaPT.redraw()
            except:
                pass


    def show_raw_data_table(self):

        if self.df is None:
            return

        table_was_closed = False

        if not hasattr(self, 'table_data') or not self.table_data.winfo_exists():
            self.table_data = tk.Toplevel(self.root)
            self.table_data.withdraw()  # Hide the window initially
            self.table_data.title("Loaded data")
            self.table_frame = tk.Frame(self.table_data)
            self.table_frame.pack(fill=tk.BOTH, expand=True)
            table_was_closed = True
        
        self.table_data.deiconify()  # Show the window

        if table_was_closed:
            self.dTDaPT2 = pt.Table(self.table_frame, dataframe=self.df, showstatusbar=True)
            self.dTDaPT2.show()
        else:
            self.dTDaPT2.updateModel(pt.TableModel(self.df))
            self.dTDaPT2.redraw()

    def show_fit_parameters_table(self):

        if not self.results_list:
            return

        results_df = pd.DataFrame(self.results_list)
        results_df.columns = ["Time","Numerator", "Denominator", "Slope", "Intercept", "R²", "Max num.", "Max den.", "Max marker","Shift", "Longitude", "Latitude"]

        table_was_closed = False

        if not hasattr(self, 'table_window') or not self.table_window.winfo_exists():
            self.table_window = tk.Toplevel(self.root)
            self.table_window.withdraw()  # Hide the window initially
            self.table_window.title("Results")
            self.table_frame = tk.Frame(self.table_window)
            self.table_frame.pack(fill=tk.BOTH, expand=True)
            table_was_closed = True
        
        self.table_window.deiconify()  # Show the window

        if table_was_closed:
            self.dTDaPT = pt.Table(self.table_frame, dataframe=results_df,showstatusbar=True )
            self.dTDaPT.show()
        else:
            self.dTDaPT.updateModel(pt.TableModel(results_df))
            self.dTDaPT.redraw()
    
    def show_proc_results_table(self):

        if not hasattr(self, 'proc_results'):
            return

        results_df = self.proc_results
        results_df.columns = ["Index","Time", "Ratio", "∆ den.", "∆ num.","Max den.","Max num.","Max marker","R²","Shift","Longitude","Latitude","Num. samples"]

        table_was_closed = False

        if not hasattr(self, 'table_window') or not self.table_window.winfo_exists():
            self.table_window = tk.Toplevel(self.root)
            self.table_window.withdraw()  # Hide the window initially
            self.table_window.title("Processing results")
            self.table_frame = tk.Frame(self.table_window)
            self.table_frame.pack(fill=tk.BOTH, expand=True)
            table_was_closed = True
        
        self.table_window.deiconify()  # Show the window

        if table_was_closed:
            self.dTDaPT3 = pt.Table(self.table_frame, dataframe=results_df,showstatusbar=True )
            self.dTDaPT3.show()
        else:
            self.dTDaPT3.updateModel(pt.TableModel(results_df))
            self.dTDaPT3.redraw()
          
    def best_correlation(self, X1, X2, start_idx, end_idx):
        X1 = np.array(X1)
        X2 = np.array(X2)

        if len(X1) != len(X2):
            raise ValueError("Input vectors must have the same length.")

        segment_X1 = X1[start_idx:end_idx]
        best_corr = -1
        best_shift = 0

        for shift in range(-5, 6):
            if shift < 0:
                # Shift left
                shifted_X2 = X2[start_idx + shift:end_idx + shift]  # Adjusted indexing
            else:
                # Shift right
                shifted_X2 = X2[start_idx + shift:end_idx + shift]

            # Check if lengths match
            if len(shifted_X2) == len(segment_X1):
                corr, _ = pearsonr(segment_X1, shifted_X2)
                if corr > best_corr:
                    best_corr = corr
                    best_shift = shift

        return best_shift
    
    def open_settings_window(self):
        settings_file = "settings.npy"
        if os.path.exists(settings_file):
            settings = np.load(settings_file, allow_pickle=True).item()
        else:
            settings = {
                "mrk_lim": 10,
                "cor_lim": 0.7,
                "win_width": 120,
                "max_shift": 5,
                "num_ratios": 0
            }

        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")

        labels = ["Marker Limit", "Correlation Limit", "Window Width", "Max Shift"]
        keys = ["mrk_lim", "cor_lim", "win_width", "max_shift"]
        entries = {}

        for i, label in enumerate(labels):
            tk.Label(settings_window, text=label).grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
            entry = tk.Entry(settings_window)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entry.insert(0, str(settings[keys[i]]))
            entry.config(width=10)
            entries[keys[i]] = entry

        def save_settings():
            for key in keys:
                settings[key] = type(settings[key])(entries[key].get())
            np.save(settings_file, settings)
            settings_window.destroy()

        save_button = tk.Button(settings_window, text="Save", command=save_settings)
        save_button.grid(row=len(labels), column=0, columnspan=2, pady=10)

    def ratio_proc(self):
        if self.df is None:
            messagebox.showerror("Error", "No data loaded.")
            return

        df1=self.df

        settings_file = "settings.npy"
        if not os.path.exists(settings_file):
            settings = {
                "mrk_lim": 10,
                "cor_lim": 0.7,
                "win_width": 120,
                "max_shift": 5,
                "num_ratios": 0
            }
            np.save(settings_file, settings)
        else:
            settings = np.load(settings_file, allow_pickle=True).item()

        num = self.df.columns.get_loc(self.y2_var.get())
        den = self.df.columns.get_loc(self.y1_var.get())
        mrk = self.df.columns.get_loc(self.mark_var.get())
        lat = self.df.columns.get_loc(self.lat_var.get())
        lon = self.df.columns.get_loc(self.lon_var.get())
        lat_sel = self.lat_var.get()
        lon_sel = self.lon_var.get()

        if self.lat_var.get() == self.lon_var.get():
            lat, lon = np.NAN, np.NAN
            lat_sel, lon_sel = "-", "-"

        mrk_lim = settings["mrk_lim"]
        cor_lim = settings["cor_lim"]
        win_width = settings["win_width"]
        max_shift = settings["max_shift"]
        num_ratios = settings["num_ratios"]
        
        df1 = df1.dropna(subset=[df1.columns[num], df1.columns[den], df1.columns[mrk]])

        if df1[df1.columns[mrk]].max(skipna=True) < mrk_lim:
            return None
        
        if len(df1) <= (win_width + 1):
            return None

        results = []

        settings_text = (
            f"Numerator: {self.y2_var.get()}\n"
            f"Denominator: {self.y1_var.get()}\n"
            f"Latitude: {lat_sel}\n"
            f"Longitude: {lon_sel}\n"
            f"Marker: {self.mark_var.get()}\n"
            f"Marker Limit: {mrk_lim}\n"
            f"Correlation Limit: {cor_lim}\n"
            f"Window Width: {win_width}\n"
            f"Max Shift: {max_shift}\n"
        )
        

        progress = tk.Toplevel(self.root)
        progress.title("Processing")
        progress.geometry("300x300")
        progress_label = tk.Label(progress, text=f"Processing data, please wait...\n\n{settings_text}",justify=tk.LEFT)
        progress_label.pack(pady=10)
        progress_bar = tk.ttk.Progressbar(progress, orient="horizontal", length=200, mode="determinate")
        progress_bar.pack(pady=10)
        progress_bar["maximum"] = len(df1) - 1 - max_shift - win_width
        

        for ii in range(1 + max_shift, len(df1) - 1 - max_shift - win_width):

            progress_bar["value"] = ii
            progress.update_idletasks()

            
            if df1[df1.columns[mrk]].max(skipna=True) < mrk_lim:
                continue

            # Calculate cross-correlation
            cor2 = []
            for jj in range(-max_shift, max_shift + 1):
                segment_den = df1.iloc[ii + jj:ii + win_width + jj][df1.columns[den]]
                segment_num = df1.iloc[ii:ii + win_width][df1.columns[num]]
                correlation, _ = pearsonr(segment_den, segment_num)  # Get correlation
                cor2.append(correlation)

            ccf1 = np.argmax(cor2) - max_shift
            
            cor1, _ = pearsonr(df1.iloc[ii + ccf1:ii + win_width + ccf1][df1.columns[den]], 
                            df1.iloc[ii:ii + win_width][df1.columns[num]])

            if pd.isna(cor1):
                continue

            if cor1 >= cor_lim:
                # Perform linear regression using stats.linregress
                X = df1.iloc[ii + ccf1:ii + win_width + ccf1][df1.columns[den]]
                y = df1.iloc[ii:ii + win_width][df1.columns[num]]

                slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)
                ratio = slope
                
                dDen = df1.iloc[ii + ccf1 - 1:ii + win_width + ccf1 - 1][df1.columns[den]].max() - df1.iloc[ii + ccf1 - 1:ii + win_width + ccf1 - 1][df1.columns[den]].min()
                dNum = df1.iloc[ii:ii + win_width][df1.columns[num]].max() - df1.iloc[ii:ii + win_width][df1.columns[num]].min()
                maxDen = df1.iloc[ii + ccf1 - 1:ii + win_width + ccf1 - 1][df1.columns[den]].max()
                maxNum = df1.iloc[ii + ccf1 - 1:ii + win_width + ccf1 - 1][df1.columns[num]].max()
                maxMrk = df1.iloc[ii + ccf1 - 1:ii + win_width + ccf1 - 1][df1.columns[mrk]].max()

                if self.lat_var.get() == self.lon_var.get():
                    lat_mean, lon_mean = np.NAN, np.NAN
                else:
                    lat_mean = df1.iloc[ii + ccf1 - 1:ii + win_width + ccf1 - 1][df1.columns[lat]].mean()
                    lon_mean = df1.iloc[ii + ccf1 - 1:ii + win_width + ccf1 - 1][df1.columns[lon]].mean()

                result = {
                    'index': ii,
                    'time': self.fc.iloc[ii],
                    'ratio': ratio,
                    'dDen': dDen,
                    'dNum': dNum,
                    'maxDen': maxDen,
                    'maxNum': maxNum,
                    'maxMrk': maxMrk,
                    'cor': cor1**2,
                    'shift': ccf1,
                    "latMean": lat_mean,
                    "lonMean": lon_mean,
                    'numSamples' : win_width
                }
                results.append(result)
                num_ratios += 1

        progress.destroy()

        
        results = pd.DataFrame(results)
        self.proc_results = results.copy()


if __name__ == "__main__":
    root = tk.Tk()
    app = RatioCalcApp(root)
    root.mainloop()

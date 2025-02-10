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
        self.results_menu.add_command(label="Results",command=self.show_fit_parameters_table)
        self.menu_bar.add_cascade(label="Tables", menu=self.results_menu)

        # Create a Selection menu
        self.selection_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Selection", menu=self.selection_menu)

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

            messagebox.showinfo("Info", f"Data split into {len(self.split_datasets)} segments.")
            
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

        self.info_data.config(text=f" Num.:\t{y2} \n Den.:\t{y1} \n Marker:\t{self.mark_var.get()} \n Lon:\t{self.lon_var.get()} \n Lat:\t{self.lat_var.get()}")

        try:
            xlim = [self.click_start[0],self.click_end[0]]

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
            filtered_num = np.array(self.df[y2])
            filtered_den = np.array(self.df[y1])
            filtered_fc = self.fc # First column

        if xlim[0] > xlim[1]:
            xlim = xlim[::-1]

        if plt.fignum_exists(3):
            self.generate_lonlat_plot(update=True)

        plt.figure(num=2, figsize=(6,7))
        plt.clf()  # Clear the figure to avoid overlapping plots
        mngr = plt.get_current_fig_manager()

        # Create a figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1,num=2)


        # First plot: Scatter plot of X1 vs X2
        ax1.scatter(filtered_den, filtered_num, color='blue')
        ax1.set_xlabel(y1)
        ax1.set_ylabel(y2)
        ax1.set_title(f"{filtered_fc.iloc[0]} - {filtered_fc.iloc[-1]}")

        slope, intercept, r_value, p_value, std_err = stats.linregress(filtered_den, filtered_num)
        fit = [slope,intercept]
        r_squared = r_value**2

        # Add the best fit line to the scatter plot
        ax1.plot(filtered_den, filtered_den*fit[0]+fit[1], color='red', label='Best Fit Line')
        ci = 1.959964*std_err

        # Create equation text
        equation_text = f"y = {fit[0]:.2f} x (±{ci:.2f}) + {fit[1]:.2f}\nR² = {r_squared:.2f}"
        ax1.text(0.05, 0.95, equation_text, transform=ax1.transAxes,
                             fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', edgecolor='black', facecolor='lightgray'))

        self.info_fit.config(text=(
            f"{filtered_fc.iloc[0]} - {filtered_fc.iloc[-1]}\n"
            f"Num. samples = {len(filtered_num)}\n"
            f"{y2} = {fit[0]:.2f} {y1} (±{ci:.2f}) + {fit[1]:.2f}\n"
            f"R² = {r_squared:.2f}\n"
            f"Max {y2} = {filtered_num.max():.2f}\n"
            f"Max {y1} = {filtered_den.max():.2f}\n"
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
            # Write to figure
            self.click_start = (event_click.xdata, event_click.ydata)
            self.line_start.set_xdata(self.click_start[0])
            self.generate_scatter_plot()
        

        elif event_click.button == 3:
            # Write to figure
            self.click_end = (event_click.xdata, event_click.ydata)
            self.line_end.set_xdata(self.click_end[0])
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
        ax.scatter(filtered_df[lon].reindex(mark_index), filtered_df[lat].reindex(mark_index),c=filtered_df[marker].reindex(mark_index),
                   vmin=np.array(filtered_df[marker]).min(), vmax=np.array(filtered_df[marker]).max(), cmap='viridis')

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


if __name__ == "__main__":
    root = tk.Tk()
    app = RatioCalcApp(root)
    root.mainloop()

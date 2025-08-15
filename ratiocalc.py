import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr
import pandastable as pt
from scipy import stats
from scipy import signal


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
        self.file_menu.add_command(label="Save", command=self.save_results_to_csv)
        self.file_menu.add_command(label="Save processing", command=self.save_processing_results)
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

        # Create a Filter menu
        self.filter_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Filter", menu=self.filter_menu)

        self.y2_filt = tk.StringVar()
        self.num_filt_menu = tk.Menu(self.filter_menu, tearoff=0)
        self.num_filt_menu.add_radiobutton(label="None", variable=self.y2_filt,command=self.filter_menu_changed)
        self.num_filt_menu.invoke(0)
        self.num_filt_menu.add_radiobutton(label="Exponential",variable=self.y2_filt,command=self.filter_menu_changed)
        self.num_filt_menu.add_radiobutton(label="Savitzky Golay",variable=self.y2_filt,command=self.filter_menu_changed)
        self.num_filt_menu.add_radiobutton(label="Centered moving average",variable=self.y2_filt,command=self.filter_menu_changed)
        self.filter_menu.add_cascade(label="Numerator", menu=self.num_filt_menu)

        self.y1_filt = tk.StringVar()
        self.y1_filt.set("None")
        self.den_filt_menu = tk.Menu(self.filter_menu, tearoff=0)
        self.den_filt_menu.add_radiobutton(label="None",variable=self.y1_filt,command=self.filter_menu_changed)
        self.den_filt_menu.invoke(0)
        self.den_filt_menu.add_radiobutton(label="Exponential",variable=self.y1_filt,command=self.filter_menu_changed)
        self.den_filt_menu.add_radiobutton(label="Savitzky Golay",variable=self.y1_filt,command=self.filter_menu_changed)
        self.den_filt_menu.add_radiobutton(label="Centered moving average",variable=self.y1_filt,command=self.filter_menu_changed)
        self.filter_menu.add_cascade(label="Denominator", menu=self.den_filt_menu)  

        self.filter_menu.add_separator() 
        self.filter_menu.add_command(label="Settings",command=self.open_filter_settings_window)

        # Create a Plot menu
        self.plot_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.plot_menu.add_command(label="Scatter and time-series",command=self.generate_combined_plot)
        self.plot_menu.add_command(label="Coordinates",command=self.generate_lonlat_plot)
        self.plot_menu.add_command(label="Processing results",command=self.plot_proc)
        self.plot_menu.add_separator()  # Add separator
        self.plot_menu.add_command(label="Settings",command=self.open_plot_settings_window)
        self.menu_bar.add_cascade(label="Plot", menu=self.plot_menu)

        # Create a Processing menu 
        self.proc_menu = tk.Menu(self.menu_bar, tearoff=0)  
        self.proc_menu.add_command(label="Current dataset",command=self.ratio_proc_single)
        self.proc_menu.add_command(label="Multiple dataset",command=self.ratio_proc_multiple)
        self.proc_menu.add_separator()  # Add separator
        self.proc_menu.add_command(label="Settings",command=self.open_settings_window)
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

        if os.path.exists("plots.npy"):
            self.plot_params = np.load("plots.npy", allow_pickle=True).item()
        else:
            self.plot_params = {
            "Numerator color": {"num_col": 'green'},
            "Denominator color": {"den_col": 'blue'},
            "Line width": {"line_width": 1.5},
            "Scatter color": {"scatter_col": 'black'},
            "Scatter size": {"scatter_size": 2}
            }
            np.save("plots.npy", self.plot_params)

        self.y1_color = tk.StringVar(value=self.plot_params["Denominator color"]["den_col"])
        self.y2_color = tk.StringVar(value=self.plot_params["Numerator color"]["num_col"]) 
        self.line_width = tk.DoubleVar(value=self.plot_params["Line width"]["line_width"]) 
        self.scatter_color = tk.StringVar(value=self.plot_params["Scatter color"]["scatter_col"])
        self.scatter_size = tk.DoubleVar(value=self.plot_params["Scatter size"]["scatter_size"])


        if os.path.exists("filters.npy"):
            self.filter_params = np.load("filters.npy", allow_pickle=True).item()
        else:
            self.filter_params = {
            "Exponential": {"alpha": 0.3},
            "Savitzky Golay": {"window_length": 5, "polyorder": 2},
            "Centered moving average": {"window_size": 5}
            }
            np.save("filters.npy", self.filter_params)

        if os.path.exists("settings.npy"):
            self.settings = np.load("settings.npy", allow_pickle=True).item()
        else:
            self.settings = {
                "mrk_lim": 10,
                "cor_lim": 0.7,
                "win_width": 120,
                "max_shift": 5,
                "num_ratios": 0
            }
            np.save("settings.npy", self.settings)


    def open_plot_settings_window(self):
        plot_settings_window = tk.Toplevel(self.root)
        plot_settings_window.title("Plot Settings")

        self.plots_params = np.load("plots.npy", allow_pickle=True).item()

        # Variables to store settings
        self.y1_color = tk.StringVar(value=self.plots_params["Denominator color"]["den_col"])
        self.y2_color = tk.StringVar(value=self.plots_params["Numerator color"]["num_col"]) 
        self.line_width = tk.DoubleVar(value=self.plots_params["Line width"]["line_width"]) 
        self.scatter_color = tk.StringVar(value=self.plots_params["Scatter color"]["scatter_col"])

        # Y1 color
        tk.Label(plot_settings_window, text="Num. Line Color:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        tk.Entry(plot_settings_window, textvariable=self.y2_color).grid(row=0, column=1, padx=10, pady=5)

        # Y2 color
        tk.Label(plot_settings_window, text="Den. Line Color:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        tk.Entry(plot_settings_window, textvariable=self.y1_color).grid(row=1, column=1, padx=10, pady=5)

        # Line width
        tk.Label(plot_settings_window, text="Line Width:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        tk.Entry(plot_settings_window, textvariable=self.line_width).grid(row=2, column=1, padx=10, pady=5)

        # Scatter plot color
        tk.Label(plot_settings_window, text="Scatter Plot Color:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        tk.Entry(plot_settings_window, textvariable=self.scatter_color).grid(row=3, column=1, padx=10, pady=5)

        tk.Label(plot_settings_window, text="Scatter Plot Size:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        tk.Entry(plot_settings_window, textvariable=self.scatter_size).grid(row=4, column=1, padx=10, pady=5)

        def save_plot_settings():
            # Save settings and close the window
            self.plot_params = {
            "Numerator color": {"num_col": self.y2_color.get()},
            "Denominator color": {"den_col": self.y1_color.get()},
            "Line width": {"line_width": self.line_width.get()},
            "Scatter color": {"scatter_col": self.scatter_color.get()},
            "Scatter size": {"scatter_size": self.scatter_size.get()}
            }
            np.save("plots.npy", self.plot_params)
            self.generate_combined_plot()
            plot_settings_window.destroy()

        save_button = tk.Button(plot_settings_window, text="Save", command=save_plot_settings)
        save_button.grid(row=5, column=0, columnspan=2, pady=10)

    def save_results_to_csv(self):
        if not self.results_list:
            messagebox.showerror("Error", "No results to save.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if save_path:
            try:
                results_df = pd.DataFrame(self.results_list)
                results_df.columns = ["Time","Numerator", "Denominator", "Slope", "Intercept", "R²", "Max num.", "Max den.", "Max marker","Shift", "Longitude", "Latitude"]
                results_df.to_csv(save_path, index=False)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save results: {e}")

    def save_processing_results(self):
        if not hasattr(self, 'proc_results'):
            messagebox.showerror("Error", "No processing results to save.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if save_path:
            try:
                self.proc_results.to_csv(save_path, index=False)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save processing results: {e}")

    def filter_menu_changed(self):
        if self.df is not None:
            self.generate_combined_plot()

    def open_filter_settings_window(self):
        filter_settings_window = tk.Toplevel(self.root)
        filter_settings_window.title("Filter Settings")

        self.filter_params = np.load("filters.npy", allow_pickle=True).item()
        
        # Default filter parameters
        
        row = 0

        # Exponential filter settings
        tk.Label(filter_settings_window, text="Exponential Alpha").grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)
        self.exp_alpha = tk.DoubleVar(value=self.filter_params["Exponential"]["alpha"])
        tk.Entry(filter_settings_window, textvariable=self.exp_alpha).grid(row=row, column=1, padx=10, pady=5)
        row += 1

        # Savitzky Golay filter settings
        tk.Label(filter_settings_window, text="Savitzky Golay Window Length").grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)
        self.sg_window_length = tk.IntVar(value=self.filter_params["Savitzky Golay"]["window_length"])
        tk.Entry(filter_settings_window, textvariable=self.sg_window_length).grid(row=row, column=1, padx=10, pady=5)
        row += 1

        tk.Label(filter_settings_window, text="Savitzky Golay Polyorder").grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)
        self.sg_polyorder = tk.IntVar(value=self.filter_params["Savitzky Golay"]["polyorder"])
        tk.Entry(filter_settings_window, textvariable=self.sg_polyorder).grid(row=row, column=1, padx=10, pady=5)
        row += 1

        # Centered moving average settings
        tk.Label(filter_settings_window, text="Centered Moving Average Window Size").grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)
        self.cma_window_size = tk.IntVar(value=self.filter_params["Centered moving average"]["window_size"])
        tk.Entry(filter_settings_window, textvariable=self.cma_window_size).grid(row=row, column=1, padx=10, pady=5)
        row += 1

        def save_filter_settings():
            self.filter_params["Exponential"]["alpha"] = self.exp_alpha.get()
            self.filter_params["Savitzky Golay"]["window_length"] = self.sg_window_length.get()
            self.filter_params["Savitzky Golay"]["polyorder"] = self.sg_polyorder.get()
            self.filter_params["Centered moving average"]["window_size"] = self.cma_window_size.get()
            self.filter_menu_changed()
            np.save("filters.npy", self.filter_params)
            filter_settings_window.destroy()

        save_button = tk.Button(filter_settings_window, text="Save", command=save_filter_settings)
        save_button.grid(row=row, column=0, columnspan=2, pady=10)

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
            self.generate_combined_plot()


    def exit_app(self):
        plt.close('all')
        self.root.quit()
        self.root.destroy()

    def browse_file(self):

        self.proc_multi_results = pd.DataFrame()

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

        self.proc_multi_results = pd.DataFrame()

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

        # Update num menu selection   
        self.numerator_menu.delete(0, 'end')
        self.numerator_menu.invoke(0)
        self.y2_var.set(columns[0])
        new_options = columns

        for option in new_options:
            self.numerator_menu.add_radiobutton(label=option, variable=self.y2_var,command=self.menu_click)
             
        # Update den menu selection   
        self.denominator_menu.delete(0, 'end')
        self.denominator_menu.invoke(0)
        self.y1_var.set(columns[1])
        new_options = columns
        for option in new_options:
            self.denominator_menu.add_radiobutton(label=option, variable=self.y1_var,command=self.menu_click)
        
        # Update marker menu selection   
        self.marker_menu.delete(0, 'end')
        self.marker_menu.invoke(0)
        self.mark_var.set(columns[1])
        new_options = columns
        for option in new_options:
            self.marker_menu.add_radiobutton(label=option, variable=self.mark_var,command=self.menu_click)
        
        # Update lon menu selection

        lon_index = next((i for i, col in enumerate(columns) if "lon" in col.lower()), None)
        if lon_index is None:
            lon_index = 0

        self.lon_menu.delete(0, 'end')
        self.lon_menu.invoke(0)
        self.lon_var.set(columns[lon_index])
        new_options = columns
        for option in new_options:
            self.lon_menu.add_radiobutton(label=option, variable=self.lon_var,command=self.menu_click)
        
        # Update lat menu selection   

        lat_index = next((i for i, col in enumerate(columns) if "lat" in col.lower()), None)
        if lat_index is None:
            lat_index = 0

        self.lat_menu.delete(0, 'end')
        self.lat_menu.invoke(0)
        self.lat_var.set(columns[lat_index])
        new_options = columns
        for option in new_options:
            self.lat_menu.add_radiobutton(label=option, variable=self.lat_var,command=self.menu_click)

    def menu_click(self):
        #self.generate_dual_y_plot()
        self.generate_combined_plot()

    def generate_combined_plot(self):
        if self.df is None:
            messagebox.showerror("Error", "No data loaded.")
            return
        
        if plt.fignum_exists(3):
            self.generate_lonlat_plot(update=True)

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


        if self.y2_filt.get() == "Exponential":
            alpha = self.filter_params["Exponential"]["alpha"]  # Smoothing factor
            filtered_num = pd.Series(filtered_num).ewm(alpha=alpha).mean().to_numpy()
        elif self.y2_filt.get() == "Savitzky Golay":
            window_length = self.filter_params["Savitzky Golay"]["window_length"]
            polyorder = self.filter_params["Savitzky Golay"]["polyorder"]
            filtered_num = signal.savgol_filter(filtered_num, window_length, polyorder)
        elif self.y2_filt.get() == "Centered moving average":
            window_length = self.filter_params["Centered moving average"]["window_size"]
            filtered_num = np.convolve(filtered_num, np.ones(window_length)/window_length, mode='same')
        
        if self.y1_filt.get() == "Exponential":
            alpha = self.filter_params["Exponential"]["alpha"]  # Smoothing factor
            filtered_den = pd.Series(filtered_den).ewm(alpha=alpha).mean().to_numpy()
        elif self.y1_filt.get() == "Savitzky Golay":
            window_length = self.filter_params["Savitzky Golay"]["window_length"]
            polyorder = self.filter_params["Savitzky Golay"]["polyorder"]
            filtered_den = signal.savgol_filter(filtered_den, window_length, polyorder)
        elif self.y1_filt.get() == "Centered moving average":
            window_length = self.filter_params["Centered moving average"]["window_size"]
            filtered_den = np.convolve(filtered_den, np.ones(window_length)/window_length, mode='same') 


        self.fig_main = plt.figure(figsize=(12, 8), num=1,)
        self.fig_main.clf()  # Clear the figure to avoid overlapping plots
        
        plt.get_current_fig_manager().set_window_title('Scatter and time-series')

        ax1 = plt.subplot(211)

        # First plot: Scatter plot of X1 vs X2
        ax1.plot(self.df.index, self.df[y2], color=self.y2_color.get(), linestyle='-', label=y2,linewidth=self.line_width.get())
        ax1.set_title( f"{filtered_fc.iloc[0]} - {filtered_fc.iloc[-1]}")
        ax1.set_xlabel('Sample Number')
        ax1.set_ylabel(y2, color=self.y2_color.get())
        ax1.tick_params(axis='y', labelcolor=self.y2_color.get())

        # Create a second y-axis
        ax1b = ax1.twinx()
        ax1b.plot(self.df.index, self.df[y1], color=self.y1_color.get(), linestyle='-', label=y1,linewidth=self.line_width.get())
        ax1b.set_ylabel(y1, color=self.y1_color.get())
        ax1b.tick_params(axis='y', labelcolor=self.y1_color.get())

        try:
            xlim = [self.click_start[0],self.click_end[0]]
        except:
            xlim = [0,10]
            self.click_start = (0,0)
            self.click_end = (10,0)
            
            
        if xlim[0] > xlim[1]:
            xlim = xlim[::-1]

        self.line_start = ax1.axvline(xlim[0],color='darkgreen')
        self.line_end = ax1b.axvline(xlim[1],color='red')

        # Click
        cid4 = self.fig_main.canvas.mpl_connect('button_press_event', self.onclick)
        cid5 = self.fig_main.canvas.mpl_connect('key_press_event', self.on_key_press)


        ax2 = plt.subplot(223)


        # First plot: Scatter plot of X1 vs X2
        ax2.scatter(filtered_den, filtered_num, color=self.scatter_color.get(), s=self.scatter_size.get())
        ax2.set_xlabel(y1)
        ax2.set_ylabel(y2)

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

        ax3 = plt.subplot(224)

        # Add the best fit line to the scatter plot
        ax2.plot(filtered_den, filtered_den*fit[0]+fit[1], color='red', label='Best Fit Line')
        ci = 1.959964*std_err

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
        index = np.arange(xlim[0],xlim[0]+len(filtered_num))  # Create an index array for X1 and X2
        ax3b = ax3.twinx()  # Create a second y-axis for the second plot

        # Plot X1 and X2 against their indices
        ax3.plot(index, filtered_num, color=self.y2_color.get(),linewidth=self.line_width.get())
        ax3b.plot(index, filtered_den, color=self.y1_color.get(),linewidth=self.line_width.get())   

        ax3.set_xlabel('Sample Number')
        ax3.set_ylabel(y2, color=self.y2_color.get())   
        ax3b.set_ylabel(y1, color=self.y2_color.get())

        plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust layout to make room for the title
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
        #self.fig_dual.canvas.draw_idle()
        self.fig_main.canvas.draw_idle()

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
            #self.generate_scatter_plot()
            self.generate_combined_plot()
        

        elif event_click.button == 3:


            if event_click.xdata < self.click_start[0]:
                self.click_end = (self.click_start[0],event_click.ydata)
                self.click_start = (event_click.xdata,0)
            else:
                self.click_end = (event_click.xdata, event_click.ydata)

            self.line_start.set_xdata([self.click_start[0]])
            self.line_end.set_xdata([self.click_end[0]])
            #self.generate_scatter_plot()
            self.generate_combined_plot()


    def simulate_click_event(self, x_start, x_end):
        """Simulate click events on the graph to set start and end lines."""
        # Simulate middle click for start line
        self.onclick(type('Event', (object,), {'button': 1, 'xdata': x_start, 'ydata': 0}))
        # Simulate right click for end line
        self.onclick(type('Event', (object,), {'button': 3, 'xdata': x_end, 'ydata': 0}))

    def update_scatter_plot(self, event_ax):
        """Update the scatter plot based on the dual plot's x-limits."""
        self.xlim = event_ax.get_xlim()  # Update the stored x-limits
        #self.generate_scatter_plot()  # Refresh the scatter plot
        self.generate_combined_plot()

    def shift_flag(self):
        self.simulate_click_event(self.click_start[0],self.click_end[0])

    def generate_lonlat_plot(self,update=False):
        lon = self.lon_var.get()
        lat = self.lat_var.get()

        if lon == lat:
            return

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
        plt.get_current_fig_manager().set_window_title('Coordinates')
        plt.clf()  # Clear the figure to avoid overlapping plots
        
        # Scatter plot

        mark_index = filtered_df[marker].sort_values().index

        ax = plt.gca()  # Get the current axes
        scatter = ax.scatter(self.df[:][lon], self.df[:][lat], c='gray', s=15)
        ax.scatter(filtered_df[lon].reindex(mark_index), filtered_df[lat].reindex(mark_index), c=filtered_df[marker].reindex(mark_index),
               vmin=np.array(filtered_df[marker]).min(), vmax=np.array(filtered_df[marker]).max(), cmap='viridis')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect('equal', 'box')

        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")

        # Add OpenStreetMap basemap
        #ctx.add_basemap(ax, crs='EPSG:4326', source=ctx.providers.OpenStreetMap.Mapnik)

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

        df_table = self.df.copy(deep=True)

        df_table.insert(0, self.fc.name, self.fc)

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

            self.dTDaPT2 = pt.Table(self.table_frame, dataframe=df_table, showstatusbar=True,)
            self.dTDaPT2.show()
        else:
            self.dTDaPT2.updateModel(pt.TableModel(df_table))
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

        if not hasattr(self, 'proc_multi_results') or self.proc_multi_results is None:
            return

        results_df = self.proc_multi_results.copy()
        results_df.columns = ["Index","Time","Num.","Den.","Marker","Ratio", "∆ den.", "∆ num.","Max den.","Max num.","Max marker","R²","Shift","Longitude","Latitude","Num. samples"]

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

        #self.settings = np.load("settings.npy", allow_pickle=True).item()
        
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")

        labels = ["Marker Limit", "R² limit", "Window Width", "Max Shift"]
        keys = ["mrk_lim", "cor_lim", "win_width", "max_shift"]
        entries = {}

        for i, label in enumerate(labels):
            tk.Label(settings_window, text=label).grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
            entry = tk.Entry(settings_window)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entry.insert(0, str(self.settings[keys[i]]))
            entry.config(width=10)
            entries[keys[i]] = entry

        def save_settings():
            for key in keys:
                self.settings[key] = type(self.settings[key])(entries[key].get())
            np.save("settings.npy", self.settings)
            settings_window.destroy()

        save_button = tk.Button(settings_window, text="Save", command=save_settings)
        save_button.grid(row=len(labels), column=0, columnspan=2, pady=10)

    def ratio_proc(self):
        if self.df is None:
            messagebox.showerror("Error", "No data loaded.")
            return

        df1=self.df.copy()

        self.settings = np.load("settings.npy", allow_pickle=True).item()

        num = df1.columns.get_loc(self.y2_var.get())
        den = df1.columns.get_loc(self.y1_var.get())
        mrk = df1.columns.get_loc(self.mark_var.get())
        lat = df1.columns.get_loc(self.lat_var.get())
        lon = df1.columns.get_loc(self.lon_var.get())
        lat_sel = self.lat_var.get()
        lon_sel = self.lon_var.get()

        if self.lat_var.get() == self.lon_var.get():
            lat, lon = np.NAN, np.NAN
            lat_sel, lon_sel = "-", "-"

        mrk_lim = self.settings["mrk_lim"]
        cor_lim = self.settings["cor_lim"]
        win_width = self.settings["win_width"]
        max_shift = self.settings["max_shift"]
        num_ratios = self.settings["num_ratios"]
        
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
        
        self.filter_params = np.load("filters.npy", allow_pickle=True).item()

        if self.y2_filt.get() == "Exponential":
            alpha = self.filter_params["Exponential"]["alpha"]  # Smoothing factor
            df1[df1.columns[num]] = pd.Series(df1[df1.columns[num]]).ewm(alpha=alpha).mean().to_numpy()
        elif self.y2_filt.get() == "Savitzky Golay":
            window_length = self.filter_params["Savitzky Golay"]["window_length"]
            polyorder = self.filter_params["Savitzky Golay"]["polyorder"]
            df1[df1.columns[num]] = signal.savgol_filter(df1[df1.columns[num]], window_length, polyorder)
        elif self.y2_filt.get() == "Centered moving average":
            window_length = self.filter_params["Centered moving average"]["window_size"]
            df1[df1.columns[num]] = np.convolve(df1[df1.columns[num]], np.ones(window_length)/window_length, mode='same')
        
        if self.y1_filt.get() == "Exponential":
            alpha = self.filter_params["Exponential"]["alpha"]  # Smoothing factor
            df1[df1.columns[den]] = pd.Series(df1[df1.columns[den]]).ewm(alpha=alpha).mean().to_numpy()
        elif self.y1_filt.get() == "Savitzky Golay":
            window_length = self.filter_params["Savitzky Golay"]["window_length"]
            polyorder = self.filter_params["Savitzky Golay"]["polyorder"]
            df1[df1.columns[den]] = signal.savgol_filter(df1[df1.columns[den]], window_length, polyorder)
        elif self.y1_filt.get() == "Centered moving average":
            window_length = self.filter_params["Centered moving average"]["window_size"]
            df1[df1.columns[den]] = np.convolve(df1[df1.columns[den]], np.ones(window_length)/window_length, mode='same') 


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
            cor1 = cor1**2

            if pd.isna(cor1):
                continue

            if cor1 >= cor_lim:
                # Perform linear regression using stats.linregress
                X = df1.iloc[ii + ccf1:ii + win_width + ccf1][df1.columns[den]]
                y = df1.iloc[ii:ii + win_width][df1.columns[num]]

                slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)
                ratio = slope

                if df1.iloc[ii + ccf1 - 1:ii + win_width + ccf1 - 1][df1.columns[mrk]].max() < mrk_lim:
                    continue

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
                    'index': ii+np.int32(win_width/2),
                    'time': self.fc.iloc[ii+np.int32(win_width/2)],
                    'num' : self.y2_var.get(),
                    'den' : self.y1_var.get(),
                    'mrk' : self.mark_var.get(),
                    'ratio': ratio,
                    'dDen': dDen,
                    'dNum': dNum,
                    'maxDen': maxDen,
                    'maxNum': maxNum,
                    'maxMrk': maxMrk,
                    'cor': cor1,
                    'shift': ccf1,
                    "latMean": lat_mean,
                    "lonMean": lon_mean,
                    'numSamples' : win_width
                }
                results.append(result)
                num_ratios += 1

        progress.destroy()

        results = pd.DataFrame(results)

        # if results.empty:
        #     messagebox.showinfo("Info", "No valid ratios found.")
        #     return

        self.proc_results = results.copy()

        if not hasattr(self, 'proc_multi_results'):
            self.proc_multi_results = results
        else:
            self.proc_multi_results = pd.concat([self.proc_multi_results, results], ignore_index=True)

        self.plot_proc()

    def plot_proc(self):
        if not hasattr(self, 'proc_results'):
            return
        
        results = self.proc_results
        df1=self.df.copy()
        num = df1.columns.get_loc(self.y2_var.get())
        den = df1.columns.get_loc(self.y1_var.get())

        y1 = self.y1_var.get()
        y2 = self.y2_var.get()


        plt.figure(num=4, figsize=(10, 4))
        plt.get_current_fig_manager().set_window_title('Processing results')
        plt.clf()
         
        try:
            df1[df1.columns[num]] = (df1[df1.columns[num]] - df1[df1.columns[num]].min()) / (df1[df1.columns[num]].max() - df1[df1.columns[num]].min())
            df1[df1.columns[den]] = (df1[df1.columns[den]] - df1[df1.columns[den]].min()) / (df1[df1.columns[den]].max() - df1[df1.columns[den]].min())
            df1[df1.columns[num]]  = df1[df1.columns[num]] * (results['ratio'].max()-results['ratio'].min()) + results['ratio'].min()
            df1[df1.columns[den]]  = df1[df1.columns[den]] * (results['ratio'].max()-results['ratio'].min()) + results['ratio'].min()
        except:
            return

        plt.plot(df1.index, df1[df1.columns[den]], color=self.y1_color.get(), linestyle='-', label=y1,linewidth=self.line_width.get())
        plt.plot(df1.index, df1[df1.columns[num]], color=self.y2_color.get(), linestyle='-', label=y2,linewidth=self.line_width.get())
        plt.scatter(results['index'], results['ratio'], color='black', label='Ratio', zorder=5)
        plt.xlabel('Index')
        plt.ylabel('Ratio')
        plt.tight_layout()
        plt.show(block=False)

    def ratio_proc_multiple(self):

        self.proc_multi_results = pd.DataFrame()

        for i in range(self.file_dropdown.current(),len(self.split_datasets)-1):
            self.df = pd.DataFrame.copy(self.split_datasets[i],deep=True)
            self.df.reset_index(drop=True, inplace=True)
            self.fc = self.df.pop(self.df.columns[0])

            print(f"Processing dataset {i+1}/{len(self.split_datasets)} {self.fc.iloc[0]}")

            self.ratio_proc()

    def ratio_proc_single(self):

        self.proc_multi_results = pd.DataFrame()

        self.ratio_proc()

if __name__ == "__main__":
    root = tk.Tk()
    app = RatioCalcApp(root)
    root.mainloop()

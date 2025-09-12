# Py_RatioCalc

Ratiocalc is a computational program suited for processing volcanic gas concentration time series produced from any multisensor device (aka MultiGAS analyser).
It is primarily intended for calculating gas molar ratio (e.g. CO₂ and SO₂ ) and error respectively from the slope and the correlation coefficient of the best fit line.
This Python-based RatioCalc version creates a graphical user interface for analyzing data, particularly for calculating and visualizing ratios between two selected variables.

## Key Functions

### GUI Creation:
The application is built using the tkinter library, providing a user-friendly interface with menus, buttons, and display windows. It allows users to load data, select columns, and view results interactively.

### Data Handling:
It uses pandas to read and process data from text files (like CSVs). It can also split large datasets into smaller, manageable segments based on time gaps.

### Data Analysis & Visualization:
It utilizes matplotlib to generate various plots. The main plots include a time-series graph showing selected "numerator" and "denominator" data and a scatter plot of these two variables. A linear regression is performed on the data shown in the scatter plot.

### Linear Regression:
The code calculates the linear relationship between the numerator and denominator data within a user-selected time window. It also finds the optimal time shift 🔄 between the two data series to maximize their correlation before calculating the ratio (slope of the regression).

### Filtering:
The application offers different filtering options like Exponential, Savitzky-Golay, and Centered Moving Average to smooth the data before plotting and analysis.

### Results Management:
Users can manually save the calculated fit parameters (slope, intercept, R-squared) for selected data segments or automatically process the entire dataset in windows. The results can be viewed in tables and saved to a CSV file.

### Settings Persistence:
The application saves user-defined settings for plots, filters, and processing parameters to files (.npy), ensuring the settings are retained between sessions.

# Py_RatioCalc

**Interactive gas-ratio analysis and spatial interpolation for volcanic gas datasets.**

[![Build Windows](https://github.com/giancarlotamburello/Py_RatioCalc/actions/workflows/build-windows.yml/badge.svg)](https://github.com/giancarlotamburello/Py_RatioCalc/actions/workflows/build-windows.yml)

Py_RatioCalc is a Python desktop application for processing concentration time series from MultiGAS instruments and other multichannel gas analyzers. It estimates gas ratios, such as CO₂/SO₂, from linear regressions between selected channels and provides tools for signal alignment, filtering, uncertainty estimation, and spatial visualization.

The current application, **RatioCalc Qt 2.2.0**, uses **PySide6/Qt** and **Matplotlib**, with an English interface and a light theme. The interface is designed for Linux, Windows, and macOS. The included GitHub Actions workflow packages a Windows x64 application.

## Features

- **Interactive analysis:** select an interval on the time-series plot and inspect the aligned signals, scatter plot, regression, and statistics.
- **Signal processing:** apply independent exponential, Savitzky–Golay, or centered moving-average filters and optimize the relative shift between two channels.
- **Automatic analysis:** process moving windows in the current dataset or across all loaded datasets, with correlation, marker, and valid-sample thresholds.
- **Monte Carlo results:** estimate a mean ratio and a 95% confidence interval through paired bootstrap resampling.
- **Spatial interpolation:** interpolate a selected variable inside a polygon using IDW or cubic Clough–Tocher interpolation.
- **Derived H₂O channel:** calculate water-vapor concentrations from relative humidity, temperature, pressure, and an editable expression.
- **Reproducible projects:** retain imported data, settings, results, processing history, spatial polygons, and computed grids in an `.rcproj` file.
- **Exports:** save result tables and spatial matrices as CSV with JSON metadata, and export figures as PNG, PDF, or SVG.

## Installation

Python **3.12** is recommended and is the version used by the Windows build workflow.

Clone the repository:

```bash
git clone https://github.com/giancarlotamburello/Py_RatioCalc.git
cd Py_RatioCalc
```

Create and activate a virtual environment.

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies and start the application:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python ratiocalc.py
```

The application is distributed in this repository as the standalone source file `ratiocalc.py`; the analysis engine, spatial engine, and interface are included in that file.

### Dependencies

| Package | Purpose |
| --- | --- |
| NumPy | Numerical arrays, signal calculations, and IDW weights |
| pandas | Data import, tables, and CSV export |
| SciPy | Regression, filtering, cubic interpolation, and spatial neighbor searches |
| Matplotlib | Interactive plots and polygon selection |
| PySide6 | Qt desktop interface |
| pyproj | Coordinate transformations for geographic interpolation |

All runtime dependencies are listed in [`requirements.txt`](requirements.txt). PyInstaller is only needed when building a packaged executable.

### Try the synthetic example

```bash
python ratiocalc.py --demo
```

You can also select **Help → Load synthetic example** in the application.

To open a saved project directly:

```bash
python ratiocalc.py analysis.rcproj
```

## Input data

Import a delimited text file with a header row. The **first column is reserved for time**; the remaining columns contain numeric channels. Longitude, latitude, humidity, and temperature can be included alongside the gas measurements.

Example file structure:

```csv
Time;CO2;SO2;Longitude;Latitude;RH;Temperature
2026-01-01 12:00:00;421.5;0.82;14.96210;38.78910;65.2;22.1
2026-01-01 12:00:01;426.0;1.14;14.96212;38.78912;65.4;22.2
2026-01-01 12:00:02;432.8;1.57;14.96215;38.78914;65.6;22.2
```

In the **Import** tab, configure the separator, decimal mark, and time format before opening the file. Semicolon, comma, tab, and whitespace separators are available. The default time format is `%Y-%m-%d %H:%M:%S`; leave the format field empty for automatic detection.

When date/time parsing is enabled, timestamps must be valid, strictly increasing, and unique. Disable **Read the first column as date/time** to retain another time/index representation. Column names must be unique, and a file must contain at least three rows and two numeric channels in addition to the time column. The interval required for a calculation also depends on the filter and shift settings.

Enable **Split at time gaps** to divide a file into separate datasets when consecutive timestamps exceed a chosen gap. Multiple files and their segments can be retained in the same project.

## Gas-ratio analysis

1. Configure the import settings and choose **File → Open data…**. The application switches to **Analysis** after loading data or a project.
2. Select the **Numerator** and **Denominator** channels. Optional channels provide a marker threshold and representative geographic coordinates.
3. Set the filters and shift options, then drag across the upper plot to select an interval. You can also enter the interval endpoints or click **All**.
4. Inspect the ratio, confidence interval, R², and sample count. Click **Add result** to retain the displayed fit.
5. For automatic processing, set the window, step, minimum R², optional marker threshold, and minimum valid-pair percentage. Click **Process current dataset** or **Process all datasets**.
6. Review the **Results**, **Ratios**, **Coordinates**, and **Log** tabs. Save the project or export the selected result table.

### Calculation conventions

The fitted model is:

```text
numerator = intercept + ratio × denominator
```

The reported ratio is the **ordinary least-squares slope with a fitted intercept**. It represents a molar ratio when both channels use compatible molar concentration units. The standard regression confidence interval uses a Student t distribution with `n − 2` degrees of freedom.

Filters are applied to the complete dataset segment, processing finite runs separately. Shift and moving-window sizes are expressed in **samples**. A positive shift `s` pairs `numerator[i]` with `denominator[i + s]`; shift optimization selects the highest signed correlation over common support. A shift in seconds is reported only when the timestamps have a regular sampling interval.

Automatic processing rejects negative correlations and applies the configured R² and valid-pair thresholds. If a marker is selected, the maximum marker value in each window must meet its threshold.

### Monte Carlo / paired bootstrap

Select an interval, set **N** next to **Montecarlo result**, and click that button. The default is **100 valid simulations**, with an allowed range of **10 to 1,000,000**. The application displays the mean bootstrap slope and the 2.5th–97.5th percentile confidence interval. Click **Add result** to save the displayed Monte Carlo result.

The procedure resamples the aligned finite numerator–denominator pairs with replacement and fits a regression to each resample. Filtering and the selected shift remain fixed. Simulation settings, the random seed, and the original OLS fit are retained with the result. Larger N improves the numerical stability of the confidence limits.

This procedure does not model signal autocorrelation or instrument measurement-error distributions. For Monte Carlo results, the displayed R² refers to the original OLS fit on the selected pairs.

## Spatial interpolation

Open the **Spatial** controls and the **Spatial interpolation** plot to create a gridded surface from three channels:

- **X coordinate:** easting or longitude.
- **Y coordinate:** northing or latitude.
- **Z value:** the measured variable to interpolate.

Select a method and coordinate mode, then set **Cells X** and **Cells Y**. Use **Draw / edit polygon** to click the boundary vertices and click the first vertex to close it. Vertices can be dragged to edit the boundary. Alternatively, **Polygon around points** creates the convex hull of the available locations.

Click **Interpolate** to calculate the grid and **Export matrix CSV…** to save it.

### Spatial settings

| Setting | Behavior |
| --- | --- |
| Grid dimensions | Default: 100 × 100 cells; each dimension can range from 1 to 2,000, with at most 1,000,000 total cells |
| IDW | Inverse-distance weighting with configurable power, nearest-neighbor count, and maximum search radius |
| IDW defaults | Power 2, up to 12 nearest neighbors, and radius 0 for an unlimited search radius |
| Cubic | Piecewise cubic Clough–Tocher interpolation on a triangulation of scattered points |
| Duplicate locations | Combine repeated X/Y locations using their mean or median Z value |
| Analysis selection | Optionally use only the samples in the current Analysis interval |

The grid divides the polygon's bounding rectangle into rectangular cells and evaluates their centers. Only cell centers inside or on the polygon are retained, and only finite input points inside the polygon contribute to interpolation.

Cubic interpolation requires at least three non-collinear locations and leaves cells outside the support points' convex hull as `NaN`. IDW also leaves cells as `NaN` when no supporting neighbors are found within the chosen radius. Increasing the cell count produces a finer output grid; it does not increase the number of observations.

### Coordinates

- **Cartesian:** X and Y must already share the same units. The optional units/CRS field is descriptive and does not reproject the input.
- **Longitude / latitude (WGS84):** X must be longitude and Y latitude in decimal degrees. Interpolation calculations use an automatically selected metric projection; exported X/Y coordinates remain in degrees. The IDW radius is expressed in meters.

### Spatial CSV format

The exported matrix has **ascending X cell-center coordinates as column headers** and **descending Y cell-center coordinates as row labels**. The first header is `Y / X`. Cells outside the polygon or without a valid estimate are written as `NaN`.

A companion `.metadata.json` file records the selected channels, method, parameters, polygon, coordinate system, grid dimensions, source identifiers, software environment, and CSV checksum.

## Derived H₂O channel

In the **H₂O** tab, select relative humidity in **%**, temperature in **°C**, and pressure in **mbar**, then click **Add H₂O channel**. You can apply the calculation to the current dataset or all loaded datasets.

The editable expression uses `RH`, `T`, and `P` and supports arithmetic and functions such as `exp`, `log`, `log10`, `sqrt`, `abs`, and `clip`. The initial expression is inherited from the original code and is intended to produce ppm; review its physical suitability for your measurements before using the derived channel. The expression and its input settings are retained in the project.

## Projects and exports

| Output | Contents |
| --- | --- |
| `.rcproj` | Imported data, derived channels, analysis settings, saved results, run history, interface state, and spatial settings, polygons, and computed grids |
| Results `.csv` | Saved fit results, including ratio, confidence limits, regression statistics, shifts, and processing metadata |
| Results `.metadata.json` | Detailed result records, run history, source hashes, import settings, and software versions |
| Spatial `.csv` | Interpolated matrix with X/Y cell-center coordinates |
| Spatial `.metadata.json` | Grid parameters, polygon, projection, source information, and export checksum |
| `.png`, `.pdf`, `.svg` | Exported figures |

Use **File → Save project** to retain the embedded data as well as the settings needed to revisit an analysis. Export metadata identifies the source data but does not embed the complete raw dataset.

## Windows executable

The repository includes a manual [**Build Windows** workflow](https://github.com/giancarlotamburello/Py_RatioCalc/actions/workflows/build-windows.yml). It runs on a Windows runner, so you can initiate a Windows build while working on Ubuntu or another operating system.

1. Open the repository's **Actions** tab.
2. Select **Build Windows** and click **Run workflow**.
3. Select the branch to build and start the workflow.
4. After a successful run, download the **RatioCalc-Windows** artifact.
5. Extract the entire archive and run `RatioCalc.exe`.

The build uses PyInstaller in `--onedir` mode. Keep the executable together with all supporting files and folders from the extracted artifact.

## Scientific reference

The original RatioCalc software is described in:

> Tamburello, G. (2015). Ratiocalc: Software for processing data from multicomponent volcanic gas analyzers. *Computers & Geosciences*, **82**, 63–67. [https://doi.org/10.1016/j.cageo.2015.05.004](https://doi.org/10.1016/j.cageo.2015.05.004)

When reporting results from this Python version, also identify the application version and analysis settings, including filters, shift options, uncertainty method, and spatial parameters where applicable.

## Author

[Giancarlo Tamburello](https://github.com/giancarlotamburello)

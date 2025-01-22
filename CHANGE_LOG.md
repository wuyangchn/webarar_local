# Change Log

The version number of WebArAr is updated simultaneously with ArArPy.

## to do

* local scripts

* Error type selection
* Add York-2004 method comparing to IsoplotR

## v0.1.13 2024-10-08
* Export PDF.

## v0.1.12 2024-10-05
* Add gain calibration.

## v0.1.11 2024-09-27
* Add multi-domain diffusion calculation

# v0.0.42 2024-08-05
* Fix issues and some changes.

# v0.0.42 2024-07-30
* Some changes. PDF preview to be finished.

# v0.0.41 2024-05-12
* Fixed bugs (linest function empty inputs)

# v0.0.40 2024-05-01
* Fixed 12-hour or 24-hour clock issues in opening Qtegra exported files 

# v0.0.40 2024-04-23
* Add furnace heating log analysis

# v0.0.40 2024-04-12
* Add calculation function in javascript
* 注意：散点点击之后的响应函数被改写到了js，因此不再需要传回后台python处理，为了加快响应速度，
一般只有set1和set2进行拟合计算，但三维图set1/set2/set3三个组分都进行了拟合。

# v0.0.38 2024-03-04
* Fix errors in asynchronous ajax function
* Fix errors in the right side text

# v0.0.37 2024-03-01
* Fix message dialog
* Add zoom out feature of tutorial documentation
* Edit documentation

# v0.0.36 2024-02-28
* Add OLST as isochron regression methods

# v0.0.35 2024-02-28
* Fix issues in editing texts in figures
* Add weighted mean ages and initial air corrected ages to the right side information

# v0.0.34 2024-02-27
* Add supports to open Seq files as raw data

# v0.0.33 2024-02-23
* Fix bug of display checkboxes of setting parameters

# v0.0.32 2024-02-23
* Test api 

# v0.0.31 2024-02-20
* Optimized the speed of clicking scatter points

# v0.0.30 2024-02-20
* Add a information dialogue for using Monte Carlo simulation

# v0.0.29 2024-02-15
* Update readme and tutorial
* Fix age spectra y-axis ticks issue
* Fix async error of clicking isochron points

# v0.0.28 2024-02-15
* Delete options of exporting to origin.
* Change the style of information div.

# v0.0.27 2024-02-14
* Add exporting degas plot and age distribution plot.
* Fix issue about degas pattern plot. Now the x-axis and y-axis scale will be sent back.

# v0.0.26 2024-02-13
* Add line caps for exporting age spectra plot.

# v0.0.25 2024-02-13
* Fix error of axises label display in exporting to pdf, using decimal number now.

# v0.0.24 2024-02-12
* Fix error of error propagation in multiplying factors (function mul_factor in arr.py)
* Fix the step attribute for number inputs in parameter setting dialogs
* Add selection of whether conducting Monte Carlo simulation for calculation errors of 40Arr/39ArK

# v0.0.23 2024-02-11
* Fix error of exporting to excel, index error in getting data of set2

# v0.0.22 2024-02-11
* Add age spectra export

# v0.0.21 2024-02-10
* Export to pdf

# v0.0.1a4 (2023.12.17-2024-01-19)

* Fix typos in the readme document.
* Break down the request function for clicking data points into two steps to decrease response time.
* Fix bugs in column text types.
* Add raw data input filter.
* Add sequence export and import.

# v0.0.1a1 (-2023.12.17)

* First release

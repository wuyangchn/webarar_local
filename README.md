
# WebArAr

[简体中文](README_zh_CN.md)

### Content

1. [Introduction](#introduction)
2. [Background](#background)
3. [Usage](#usage)
4. [Features](#features)
5. [Update Log](#update-log)
6. [Citing WebArAr or ArArPy](#citing-webarar-or-ararpy)
7. [Reference](#reference)

## Introduction

WebArAr is a web-based application based on [Django](https://www.djangoproject.com/) 
designed to reduce <sup>40</sup>Ar/<sup>39</sup>Ar geochronologic data.

* The backend algorithms are packaged into a module called [ArArPy](https://github.com/wuyangchn/ararpy.git). 
Access through [PyPi](https://pypi.org/project/ararpy/).
* Django framework, Bootstrap, Echarts, Bootstrap-table, etc. provide an intuitive and interactive interface.

Visit [WebArAr](https://www.webarar.net)

## Background

This project originated from the necessity to update and enhance existing software tools for 
<sup>40</sup>Ar/<sup>39</sup>Ar dating. In general, ArArCALC and Isoplot/Isoplot R have been 
widely utilized within this field. However, several factors have rendered these tools inadequate 
for meeting the evolving requirements: (1) ArArCALC and Isoplot were developed as macro tools for 
outdated Excel versions, such as Excel 2003. Isoplot is no longer maintained, and ArArCALC is 
closed-source. (2) The increasing importance of chlorine correction in crushing experiments 
requires software with new features. (3) IsoplotR is great for plotting but lacks support 
for correction and newer calculations in <sup>40</sup>Ar/<sup>39</sup>Ar community such as 
age calibration. Additionally, its regression methods differ from commonly used York regression.

Therefore, the main purpose of WebArAr is to balance the functionality of ArArCALC and 
IsoplotR and it will be continuously updated with more research needs in order to serve 
the community.


## Usage

* Access the application at http://www.webarar.net.
See [Tutorial](/static/readme/Tutorial.md) for step-by-step instructions
* (Optional) Deploy and launch WebArAr on your computer for offline usage. 
See [Deploy on your own caomputer](/static/readme/Deployment.md).
* (Optional) Use ArArPy with a Python terminal. See [ArArPy](#ararpy).
<!-- * [Video examples]() -->


## Features
- [x] Import
    - [x] Raw files from mass spec
    - [x] Age files from ArArCALC
    - [x] Xls files from ArArCALC
    - [x] Manually enter
- [x] Raw Data Reduction
    - [x] Blank correction
    - [x] Mass discrimination correction
    - [x] Decay correlation
    - [x] Degas argon isotopes
- [ ] Calculation
    - [x] Age Calculation
        - [x] Regular equation
        - [x] Min equation
        - [x] Renne calibration
    - [ ] Isochron regression
        - [x] Normal and inverse isochron
        - [x] Chlorine related isochrons
        - [x] York error weighted regression
        - [ ] Robust regression
        - [ ] Other regression methods
    - [x] Three-dimensional regression
    - [x] Age spectra
        - [x] Re-correction with initial ratio derived from isochrons
        - [x] Plateau ages
    - [x] Chi-squared and P values
    - [x] MSWD 
- [x] Interfaces, tables and plots
    - [x] Interactive multi tables and plots 
- [x] Export
    - [x] Xls
    - [x] PDF
    - [x] SVG

## Update Log

The log is [here](/../CHANGE_LOG.md)

## Citing WebArAr or ArArPy


## Reference


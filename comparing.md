# To do
* Improve database, store parameter settings



# Comparing to other software

## ArArCALC

* Authors: Anthony Koppers
* Language: VBA
* Access: Free usage
* Target User: Researchers, Labs
* Tag: add-in to Microsoft Excel
* Last version: v2.5.2
* Link: https://earthref.org/ArArCALC/

### Description 

The data reduction program ArArCALC includes four different utilities 
that are executed within Microsoft Excel 2000-XP-2003-2007-2011: (1) 
curved or linear data regression, (2) blank evolution analysis, (3) 
age calculation, (4) J-value calculation, (5) air shot calculation and 
(6) age recalibration.

These utilities fully interact with each other providing a high level 
of automation. Besides ArArCALC allows for editing of all the input data, 
parameters and constants used in the calculations at every level of the 
program and at all times. This provides the needed flexibility when using 
ArArCALC online during mass spectrometry and when not all input data are 
available or final (J-values, blank intensities, and so forth). The new 
File Watch functionality will allow you to auto-calculate data files that 
just have been acquired on your mass spectrometer. The same experiments 
can also be recalculated offline after editing the changed input data. 
ArArCALC never requires you to "recalculate" your 40Ar/39Ar ages from 
scratch. ArArCALC now also supports data files acquired on the 
state-of-the-art multicollector mass spectrometers.

### Advantages
* Has many useful properties and functions.
* Has multiple data tables containing all the necessary input and output data.
* Export to Microsoft Excel for publication.

### Disadvantages
* An earlier versions of Excel is required. Excel 2003 is best suitable within 
Excel 2000-XP-2003-2007-2011.
*

# ArArSUITE

* Authors: Anthony Koppers
* Language: VBA(?)
* Access: Free usage
* Target User: Labs
* Tag: Microsoft Excel
* Link: http://geochronology.ceoas.oregonstate.edu/software/

ArArSUITE seems to be designed to allow the 24/7 automated operation of the 
CO2 laser, the extraction line valves, and the ARGUS VI multi-collector mass 
spectrometer.

Currently, I don't know if the software is already in use.

# Pychron

* Authors: Jake Ross, New Mexico Geochronology Research Laboratory
* Language: Python
* Access: Open source
* Target User: Labs (mainly), researchers
* Link: https://pychron.readthedocs.io/en/latest/
* Github: https://github.com/NMGRL/pychron

Pychron aims to augment and replace the current widely used program Mass Spec 
by Alan Deino of Berkeley Geochronology Center

## Mass Spec - Pychron Differences As of 2017/5/24
* Mass Spec does not propogate baseline error
* Mass Spec does not correct Ca/K for 37ArK
* Mass Spec does not propogate IC error correctly?
* Pychron estimates J error ~an order of magnitude greater than Mass Spec.

## Description

### pyExperiment
Write and run a set of automated analyses. Allows NMGRL to operate continuously. 
only limited by size of analysis chamber.

### pyCrunch
Display, process and publish Ar-Ar geochronology and thermochonology data. Export 
publication ready PDF tables and figures. Export Excel, CSV, and XML data tables. 
Store and search for figures in database.  

### pyValve
Used to control and monitor a noble gas extraction line a.k.a prep system. Displays 
a graphical interface for user to interact with. A RPC interface is also provided 
enabling control of the prep system by other applications.

### pyLaser
Configure for multiple types of lasers. Currently compatible with Photon machines 
Fusions CO2, 810 diode and ATLEX UV lasers. Watlow or Eurotherm interface for PID 
control. Machine vision
for laser auto targeting and modulated degassing.

## Disadvantages
* Installation required

## Advantages
* It is a complete and comprehensive laboratory management software. 
* It has a script, Remote Control Server, as a interface third-party software with 
Thermo Scientific's Mass Spectrometer control software.


# Isoplot R

* Authors: Pieter Vermeesch
* Language: R, Javascript and HTML
* Access: GPL license, open source
* Target User: Researchers
* Tag: add-in to Microsoft Excel
* Link: https://isoplotr.es.ucl.ac.uk/home/index.html
* Github: https://github.com/pvermees/IsoplotR

## Description
* An alternative to Isoplot written in R

## Advantages
* Easily access
* 

## Disadvantages 
* Comprehensive but not specialized in Ar-Ar


## IsoplotR - WebArAr Differences:

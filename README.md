Climate programs
================

These programs are for manipulating the climate data found at http://climatemodels.uchicago.edu

defs.py
-------

This module defines the datasets of interest (by variable, model, level, year, etc.).

dl.py
-----

This program downloads datasets into the current directory.

compress.py
-----------

This program moves dataset files into zip archives.

compare.py
----------

This program runs a variance analysis across datasets within a time range.  The output is a map of variance (in standard devation form) and a text file with CSV data (similar to that downloaded from the source).

Usage: `compare.py [START_YEAR STOP_YEAR]

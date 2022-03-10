# Change of Spatial Support (CoSS)

Python tools for spatial interpolation

## Introduction

Change of Spatial Support (CoSS) is a package that adds support for `spatial interpolation`.
Spatial interpolation is often referred in the literature as the process of using points with known values to estimate values of the same variable at other points.
However, spatial vector data (points, lines and polygons) is not limited to just points and several methods exist for making interpolations between these different vector types.

Several packages exist that allow different areal interpolation methods to be applied but they are often written in multiple languages and are not standardised - making them inaccessible and comparisons between methods challenging.
This package aims to make "spatial interpolation" more accessible by using a standardised classes.

## Areal interpolation
The `areal_interpolation` class supports several areal interpolation, which includes;
1. Areal weighting
2. Dasymetric mapping
	- Binary
3. Pycnophylactic interpolation (from [tobler](https://github.com/pysal/tobler))
4. Model (regression)
	- General Linear Model
	- Ordinary Least Square
5. Areal geobootstrap - 

Areal [geobootstrap](https://github.com/tastatham/geobootstrap) is a novel simulation based method, which pools neighbouring observations based on a distance decay funcion.

Further spatial interpolation methods will be supported, including those between different vector types, with raster support.

This repository is an alpha release and **will** contain errors - if you spot anything, file an issue or submit a PR.
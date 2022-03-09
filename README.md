# Change of Spatial Support (CoSS)

Python tools for spatial interpolation

## Introduction

Change of Spatial Support (CoSS) is a package that adds support for `spatial interpolation`.
Spatial interpolation is often referred to in the literature as the process of using points with known values to estimate values at other points.
However, spatial vector data is not limited to just points and interpolating values between these types is important in different applications.
Therefore, we reference spatial interpolation as a technique for interpolating values from sources to targets, irrespective of vector types (points, lines and polygons).
Interpolating raster data fis outside of the scope of this package.

Although there already exist several spatial interpolation packages, they are not easily accessible because they exist in several languages, each containing their own API.
These packages are often created for an intended purpose and several of these do not follow the language written in the literature.
This makes applying spatial interpolation challenging to an end user, especially when making comparisons between different methods.
This package aims to make spatial interpolation more accessible by creating a consistent API.

## Spatial interpolation support
This package is in the first stages of active development and I plan to first implement common areal interpolation methods first.
We will later add support for interpolating values for both point and line types, as well as mixed types e.g. polygons-points/points-polygons.

The areal interpolation methods that are currently in active development, include;
1. Areal weighting 
2. Dasymetric mapping
	- Binary
3. Model 
	- General Linear Model
	- Geographically Weighted Regression* (TBA)
    - Other* ;)
4. Pycnophylactic interpolation (from tobler)
5. Geobootstrap

Note: this package is an alpha release and **will** contain errors - if you spot anything, file an issue or submit a PR.
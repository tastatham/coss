import warnings
import numpy as np
import dask.array as da
import pandas as pd
import geopandas as gpd
from pyproj import Transformer

def _crs(sources, targets):

    _check_crs_exists(sources), _check_crs_exists(targets)
    _check_crs_match(sources, targets)


def _check_crs_match(sources, targets):
    """Check crs of GeoDataFrame match"""

    try:
        assert sources.crs == targets.crs
    except AssertionError:
        print(
            "Source and target coordinate reference systems \
         must match"
        )


def _check_crs_exists(gdf):
    """Check crs exists in GeoDataFrame"""

    if gdf.crs is None:
        raise KeyError("GeoDataFrame must contain a crs")


def _uid(df, uid=None, uid_type="sources"):
    """Checks unique identifier exists and if valid"""

    if uid is None:
        df, uid = _create_uid(df, uid_type)
    else:
        _check_uid(df[uid])

    return df, uid


def create_uid(df, uid):
    """Create fast uid"""
    import random
    from fastuuid import UUID

    df[uid] = [UUID(int=random.getrandbits(128), version=4) for x in range(len(df))]

    return df


def _create_uid(df, uid_type="sources"):
    """Creates a unique identifer for areal interpolation methods"""

    if uid_type == "sources":
        uid = "sid"
    elif uid_type == "targets":
        uid = "tid"

    df = create_uid(df, uid)

    return df, uid


def _check_uid(uids):
    """Checks whether a unique identifier is valid"""
    if uids.is_unique is False:
        raise ValueError(
            "uids are not unique. Use an alternative unique identifier"
            "or allow coss to create a valid uid"
        )


def _poly(total_bounds):
    """Return polygon box based on total bounds"""

    from shapely.geometry import box

    return box(*total_bounds)


def _get_bbox(gdf):
    """Get tuple bounding box (total bounds) from GeoDataFrame"""

    xmin, ymin, xmax, ymax = gdf.total_bounds
    return (xmin, ymin, xmax, ymax)


def reproject_array(coords, s_crs, t_crs):
    """Function reprojects numpy array (xy)
    coordinate pairs from one projection to another"""
    
    assert coords.shape[1] == 2  # x,y

    transformer = Transformer.from_crs(s_crs, t_crs)
    x, y = transformer.transform(coords[:, 0], coords[:, 1])

    return np.array([x, y]).T


def rio2gdf(
    rioxarray_obj,
    method="points",
    factor=2,
    mask=None,
    crs=None,
    name="pop",
    include_xy=True,
    dask=True,
):
    """
    Transform raster to GeoDataFrame as points or polygons
    Parameters
    ----------
    rioxarray_obj: rioxarray object
    methods: str
        whether to return points (mid points) or polygons
    factor: int
        factor to multiply cell resolution by for polygons
    mask: int
        what cell values to not include
    crs: int
        epsg code for coordinate reference system
    name: str
        Column name to return with rioxarray values
    include_xy: bool
        whether to include x,y coords (mid point)
    dask: bool
        whether to use dask
    Returns
    -------
    type: gpd.GeoDataFrame
        GeoDataFrame containing cell geometries and values
    """

    if crs is None:
        # Get crs
        crs = rioxarray_obj.rio.crs.to_epsg()
        if crs is None:
            raise ValueError(f"{crs} is invalid, please specify a valid crs")

    # Get cell values and coords
    vals = _get_rio_vals(rioxarray_obj)
    coords = _get_rio_coords(rioxarray_obj, dask)

    # Filter vals using mask
    if mask is not None:
        ind = _mask(vals, mask, dask)
        vals = vals[ind]
        coords = coords[ind]

    methods = ["points", "polygons"]

    if method == methods[0]:
        geoms = rio2points(coords)
    elif method == methods[1]:
        geoms = rio2polygons(coords, rioxarray_obj, factor)
    else:
        raise ValueError(f"Only '{methods}' are supported")


    gdf = gpd.GeoDataFrame(
        data=pd.DataFrame({name: vals.ravel()}),
        geometry=geoms,
        crs=crs,
    )
    
    if include_xy:
        gdf["x"] = coords[:, 0]
        gdf["y"] = coords[:, 1]

    return gdf
    

def st_make_grid(
    gdf=None,
    total_bounds=None,
    res=100,
    crs=None,
    include_xy=True,
    index=True,
    index_name="tid",
    dask=True,
):

    """
    Creates grids (square) covering the bounding box of a GeoDataFrame
    Assumes projected coords e.g. res in metres

    Parameters
    ----------
    gdf: gpd.GeoDataFrame (optional)
        GeoDataFrame containing nation boundaries
    total_bounds: list
        total bounds of GeoDataFrame (optional)
    res: int
        cell resolution in m
    crs: int
        epsg code for coordinate reference system
    include_xy: bool
        whether to include x,y coords (mid point)
    index: bool
        whether to include a unique index
    index_name: str
        name of index
    dask: bool
        whether to use dask

    Returns
    -------
    type: gpd.GeoDataFrame
        GeoDataFrame containing cell geometries
    """

    if total_bounds is None:
        total_bounds = gdf.total_bounds

    x, y = _grid_centroids(total_bounds, res)
    coords = _cartesian_prod(x, y, dask)
    geoms = _create_grid_geoms(coords, xres=res, yres=res)

    if crs:
        print(f"Using the following crs: {crs} for gridded GeoDataFrame")
    elif gdf is not None and crs is None:
        crs = gdf.crs
        warnings.warn("Using crs set in GeoDataFrame")
    elif crs is None:
        warnings.warn(
            "No crs or GeoDataFrame passed, so no crs is set for the resultant GeoDataFrame"
        )

    if include_xy:
        if dask:
            coords = coords.compute()
            geoms = geoms.compute()
        df = pd.DataFrame({"x": coords[:, 0], "y": coords[:, 1]})
        gdf = gpd.GeoDataFrame(df, geometry=geoms, crs=crs)
    else:
        if dask:
            geoms = geoms.compute()
        gdf = gpd.GeoDataFrame(geometry=geoms, crs=crs)

    if index:
        gdf = create_uid(gdf, uid=index_name).set_index(index_name)

    return gdf


def _get_rio_vals(rioxarray_obj):
    """Get rio cell values"""
    return np.array(rioxarray_obj).reshape(-1, 1)


def _get_rio_coords(rioxarray_obj, dask):
    """Get rio corodinates"""
    x, y = _get_xy_coords(rioxarray_obj)
    
    prod, elem = _cartesian_prod(x, y, dask)
    
    if dask:
        prod = prod.compute()
    
    return np.reshape(prod, (2, elem)).T


def _get_xy_coords(rioxarray_obj):
    """Get xy coords from rasterio object"""
    return np.array(rioxarray_obj.x), np.array(rioxarray_obj.y)


def _cartesian_prod(x, y, dask=True):
    """Calculate the cartesian product of x and y coords"""

    if dask:
        x_dask = da.from_array(x, chunks=len(x) // 5)
        y_dask = da.from_array(y, chunks=len(y) // 5)

        mesh = da.meshgrid(x_dask, y_dask)
        elem = mesh[0].size
        prod = da.concatenate(mesh).ravel()
     
    else:
        mesh = np.meshgrid(x, y)
        elem = mesh[0].size
        prod = np.concatenate(mesh).ravel()
    
    return prod, elem


def _mask(vals, mask, dask=True):
    """mask array"""

    if dask:
        ind = da.where(vals > mask)[0]
    else:
        ind = np.where(vals > mask)[0]

    return ind


def rio2points(coords):
    """A function that returns point geoms for a rioxarray object"""

    return gpd.points_from_xy(coords[:, 0], coords[:, 1])


def rio2polygons(coords, rioxarray_obj, factor):
    """A function that returns polygon geoms for a rioxarray object"""

    # Juggle around x, y values
    af = rioxarray_obj.rio.transform()
    xres, yres = abs(af[0]), abs(af[4])

    return _create_grid_geoms(coords, xres, yres, factor)


def _create_grid_geoms(coords, xres, yres, factor=2):

    """Create polygon grids based on x,y projected coords and res"""
    from pygeos import box

    xmins = coords[:, 0] - (xres / factor)
    xmaxs = coords[:, 0] + (xres / factor)
    ymins = coords[:, 1] + (yres / factor)
    ymaxs = coords[:, 1] - (yres / factor)

    # Create polygons
    return box(xmins, ymins, xmaxs, ymaxs)


def _grid_centroids(total_bounds, res):
    """Calculate centroid for all grid cells"""

    xmin, ymin, xmax, ymax = total_bounds

    x = np.arange(start=(xmin + res), stop=xmax, step=res)
    y = np.arange(start=(ymin + res), stop=ymax, step=res)

    return x, y


def _h3fy_updated(gdf, resolution):
    """
    h3_radius values calculated using;
    ```python
    import numpy as np
    import pandas as pd

    df = pd.read_html("https://h3geo.org/docs/core-library/restable/")[0]
    y = df["Average Hexagon Area (km2)"].to_numpy()
    cos_30 = np.cos(np.deg2rad(30))
    sin_30 = np.sin(np.deg2rad(30))
    radius_km = np.sqrt(y / ((cos_30 * sin_30) * 6)
    )
    radius_m = radius / 1000
    ```
    """
    from tobler.util import h3fy
    from shapely.geometry import box

    # h3 radius in m
    h3_radius = np.array(
        [
            2.79076325e05,
            4.83445409e05,
            1.82725189e05,
            6.90636300e04,
            2.61035980e04,
            9.86623300e03,
            3.72908500e03,
            1.40946200e03,
            5.32727000e02,
            2.01352000e02,
            7.61040000e01,
            2.87640000e01,
            1.08720000e01,
            4.11100000e00,
            1.55700000e00,
            5.89000000e-01,
        ]
    )

    poly = box(*gdf.total_bounds)

    aoi = gpd.GeoDataFrame()
    aoi.loc[0, "geometry"] = poly
    aoi.crs = gdf.crs
    aoi = aoi.buffer(h3_radius[resolution])

    return h3fy(aoi, resolution=resolution, clip=False, return_geoms=True)

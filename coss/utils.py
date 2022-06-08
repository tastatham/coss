import numpy as np
import pandas as pd
import geopandas as gpd


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


def _create_uid(df, uid_type="sources"):
    """Creates a unique identifer"""
    import uuid
    if uid_type == "sources":
        uid = "sid"
    elif uid_type == "targets":
        uid = "tid"
    df[uid] = df.apply(lambda _: uuid.uuid4(), axis=1)

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


def rio2gdf(rioxarray_obj, method="points", mask=None, crs=None):
    """
    A function that convert a rioxarray object to a
    GeoPandas GeoDataFrame points object
    """

    if crs is None:
        # Get crs
        crs = rioxarray_obj.rio.crs.to_epsg()
        if crs is None:
            raise ValueError(f"{crs} is invalid, please specify a valid crs")

    # Get cell values and coords
    vals = _get_rio_vals(rioxarray_obj)
    coords = _get_rio_coords(rioxarray_obj)

    # Filter vals using mask
    if mask is not None:
        attributes, coords = _mask(vals, coords, mask)

    methods = ["points", "polygons"]

    if method == methods[0]:
        geoms = rio2points(coords)
    elif method == methods[1]:
        geoms = rio2polygons(coords, rioxarray_obj)
    else:
        raise ValueError(f"Only '{methods}' are supported")

    return gpd.GeoDataFrame(
        pd.Series(attributes.ravel(), name="Value"),
        geometry=geoms,
        crs=crs,
        )


def _get_rio_vals(rioxarray_obj):
    """Get rio cell values"""
    return np.array(rioxarray_obj).reshape(-1, 1)


def _get_rio_coords(rioxarray_obj):
    """Get rio corodinates"""
    x, y = _get_xy_coords(rioxarray_obj)

    return _cartesian_prod(x, y)


def _get_xy_coords(rioxarray_obj):
    """Get xy coords from rasterio object"""
    return np.array(rioxarray_obj.x), np.array(rioxarray_obj.y)


def _cartesian_prod(x, y):
    """Calculate the cartesian product of x and y coordinates"""

    mesh = np.meshgrid(x, y)
    elem = mesh[0].size
    concat = np.concatenate(mesh).ravel()

    return np.reshape(concat, (2, elem)).T


def _mask(vals, coords, mask):
    """mask values and array"""

    ind = np.where(vals > mask)[0]

    return vals[ind], coords[ind]


def rio2points(coords):
    """
    A function that convert a rioxarray object to a
    GeoPandas GeoDataFrame points object
    """
    return gpd.points_from_xy(coords[:, 0], coords[:, 1])


def rio2polygons(coords, rioxarray_obj):
    """
    A function that convert a rioxarray object to a
    GeoPandas GeoDataFrame polygon object
    """

    from pygeos import box

    # Juggle around x, y values
    af = rioxarray_obj.rio.transform()
    xres, yres = abs(af[0]), abs(af[4])

    xmins = coords[:, 0] - (xres / 2)
    xmaxs = coords[:, 0] + (xres / 2)
    ymins = coords[:, 1] + (yres / 2)
    ymaxs = coords[:, 1] - (yres / 2)

    # Create polygons
    return box(xmins, ymins, xmaxs, ymaxs)


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

import numpy as np
from geobootstrap.sample import geobootstrap
from geobootstrap.utils import _poly_to_points


def _areal_geobootstrap(
    sources,
    targets,
    r=1000,
    kernel="gaussian",
    metric="euclidean",
    bandwidth=1000,
    col="pop_density",
    sid="sid",
    tid="tid",
    source_bounds=None,
    target_bounds=None,
    p=1000,
    method="random points",
    groupby="median",
    dropna=True,
):

    """
    Function that interpolates areal data from sources to targets

    Note: this only supports intensive variables e.g. population density but
    this will be later updated to also support extensive variables

    Parameters
    ----------
    sources : gpd.GeoDataFrame
        GeoDataFrame containing variable(s) to be interpolated
    targets : gpd.GeoDataFrame
        GeoDataFrame where variables will be assigned
        target GeoDatFrame containing unique identifier
    r : int
        how many resamples with replacement to return
    kernel : str
        kernel distance-decay function
    metric : str
        how to calculate distances between coordinates
    bandwidth : int
       bandwidth or fixed distance
    col : str
        column to interpolate from sources to targets
    sid : str
        source GeoDatFrame containing unique identifier
    tid : str
        target GeoDataFrame containing unique identifier
    source_bounds : array_like
        source GeoDataFrame bounds
    target_bounds : array_like
        target GeoDataFrame bounds
    p : int
        number of random points to generate points within bounds
    method : str
        method for generating coordinates for each polygon
    groupby : str
        how to aggregate sampled polygons

    Returns
    ---------
    stats : array_like
        computed average statistic for each target
    std : array_like
        standard deviation for each target
    """

    """
    try:
        check geometric bounds overlap
        except AssertionError:
        print(
            "Source and target geometries must overlap"
            )
    """

    groupbys = ["median"]

    if groupby not in groupbys:
        raise ValueError(f"Only {groupbys} are supported")

    if r is None:
        print("Using length of targets as the number of resamples with replacement")
        r = len(targets)

    sources = sources.copy()
    targets = targets.copy()

    if source_bounds is None:
        source_bounds = sources.bounds.to_numpy()
    if target_bounds is None:
        target_bounds = targets.bounds.to_numpy()

    source_points = _poly_to_points(
        sources,
        method,
        uid=sid,
        bounds=source_bounds,
        p=p,
        n=1,  # 1 point per polygon
        join=True,
    )

    target_points = _poly_to_points(
        targets,
        method=method,
        uid=tid,
        bounds=target_bounds,
        p=p,
        n=1,  # 1 point per polygon
        join=True,
    )

    gs = geobootstrap(
        source_points,
        target_points,
        r,
        kernel,
        metric,
        bandwidth,
    )
    # TEMP
    gs = [g[col].to_numpy() for g in gs]

    if groupby == "median":
        if dropna is True:
            stats = np.nanmedian(gs, axis=1)
            std = np.nanstd(gs, axis=1)
        else:
            stats = np.nanmedian(gs, axis=1)
            std = np.nanstd(gs, axis=1)

        return stats, std

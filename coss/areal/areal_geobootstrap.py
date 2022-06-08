import numpy as np
from geobootstrap.sample import geobootstrap


def _areal_geobootstrap(
    sources,
    targets,
    r=1000,
    kernel="gaussian",
    metric="euclidean",
    bandwidth=1000,
    fixed=True,
    col="pop_density",
    groupby="median",
):

    """
    Function that interpolates areal data from sources to targets

    Note: this only supports intensive variables e.g. population density but
    this will be later updated to also support extensive variables

    Parameters
    ----------

    sources : gpd.GeoDataFrame
        GeoDataFrame containing a variable of interest to be interpolated
    targets : gpd.GeoDataFrame
        target GeoDatFrame containing unique identifier
    r : int
        how many resamples with replacement to return
    kernel : str
        kernel distance-decay function
    metric : str
        how to calculate distances between coordinates
    bandwidth : int
       bandwidth (distance)
    fixed: bool
        whether to apply a fixed or adaptive (knn) kernel
    col : str
        column to interpolate from sources to targets
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

    gs = geobootstrap(
        gdf1=sources,
        gdf2=targets,
        r=r,
        kernel=kernel,
        metric=metric,
        bandwidth=bandwidth,
        fixed=fixed,
    )
    # TEMP
    gs = [g[col].to_numpy() for g in gs]

    if groupby == "median":
        stats = np.nanmedian(gs, axis=1)
        std = np.nanstd(gs, axis=1)

    return stats, std

from numpy import nanmean, nanmedian, nanstd, nanpercentile, nanvar, ptp
from scipy.stats import mode
from geobootstrap.sample import geobootstrap


def _areal_geobootstrap(
    sources,
    targets,
    r=1000,
    kernel="gaussian",
    metric="euclidean",
    bandwidth=1000,
    fixed=True,
    col="income",
    average="mean",
    spread="std",
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
    average : array_like
        average statistic to compute
    spread : array_like
        measure of spread to compute

    Returns
    ---------
    average : array_like
        computed average statistic for each estimate
    spread : array_like
        measure of spread for each estimate
    """

    """
    try:
        check geometric bounds overlap
        except AssertionError:
        print(
            "Source and target geometries must overlap"
            )
    """

    averages = ["mean", "median", "mode"]

    if average not in averages:
        raise ValueError(f"Only {average} are supported")

    spreads = ["std", "iqr", "var", "range"]

    if spread not in spreads:
        raise ValueError(f"Only {spread} are supported")

    if r is None:
        print("Using length of targets as the number of resamples with replacement")
        r = len(targets)

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

    if average == "mean":
        averages = nanmean(gs, axis=1)
    elif average == "median":
        averages = nanmedian(gs, axis=1)
    elif average == "mode":
        averages = mode(gs, axis=1)[0]

    if spread == "std":
        spreads = nanstd(gs, axis=1)
    if spread == "iqr":
        q75, q25 = nanpercentile(gs, [75, 25])
        spreads = q75 - q25
    elif spread == "var":
        spreads = nanvar(gs, axis=1)
    elif spread == "range":
        spreads = ptp(gs, axis=1)

    return averages, spreads

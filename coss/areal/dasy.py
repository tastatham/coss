import geopandas as gpd
from coss.areal.areal_weighting import _areal_weighting


def _dasy(
    sources,
    targets,
    mask,
    how="clip",
    extensive="TOTAL_E",
    intensive=None,
    weights="total",
    sid="GEOID",
    tid="WARD",
    geoms=True,
    all_geoms=False,
):

    """
    Binary Dasymetric mapping technique for interpolating values from sources
    to masked target geometries


    use how='clip' to keep those target geoms that overlap
    use how='difference' to drop those target geoms that overlap

    Parameters
    ----------
    sources : gpd.GeoDataFrame
        GeoDataFrame containing variable(s) to be interpolated
    targets : gpd.GeoDataFrame
        GeoDataFrame where variables will be assigned
    extensive : str or list
        str or list of extensive variables e.g population counts
    intensive : str or list
        str list of intensive variables e.g. population density
    sid : str
        Column containing unique values
    tid : str
        Column containing unique values
    weights : str
        type of weights to be computed
    geoms : bool (default False)
        whether to return target geometries
    all_geoms : bool (default False)
        whether to return all target geoms
        or only those that intersect sources

    Return
    ------
    type: pd.DataFrame or gpd.GeoDataFrame
        targets containing interpolated values
    """

    mask = mask.copy()

    if how == "clip":
        diff = gpd.clip(targets, mask)
    elif how == "difference":
        # Mask out regions that do not contain the variable of interest
        diff = gpd.overlay(targets, mask, how="difference")
    else:
        raise ValueError(
            "Only 'clip' and 'difference' are supported \
            for masking target geometries"
        )

    areal_diff = _areal_weighting(
        sources,
        targets=diff,
        extensive=extensive,
        intensive=intensive,
        weights=weights,
        sid=sid,
        tid=tid,
        geoms=True,
        all_geoms=False,
    )

    if extensive is None and intensive is not None:
        return areal_diff

    elif extensive is not None and intensive is None:

        # Rescale by ratio of loss to total as per
        # https://github.com/lexcomber/SpatInt/blob/872b30d864d20c8701c25f786e79a46f6c6e9307/SpatInt_Jan22.R#L208
        areal_diff[extensive] = areal_diff[extensive] * (
            sum(sources[extensive]) / sum(areal_diff[extensive])
        )

        targets = targets[targets[tid].isin(targets[tid])]
        targets[extensive] = areal_diff[extensive]

        return targets

    else:
        raise ValueError("Only single variables are currently supported")

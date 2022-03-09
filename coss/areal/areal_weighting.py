import pandas as pd
import geopandas as gpd


def _areal_weighting(
    sources,
    targets,
    extensive,
    intensive,
    weights,
    sid,
    tid,
    geoms=True,
    all_geoms=False,
):

    """
    A method for interpolating areal data based soley on
    the geometric overlap between sources and targets.

    For an 'extensive' variable, either the 'sum' or 'total' weight can
    be specified.
    For an 'intensive' variable, only the 'sum' weight can
    be specified.

    For mixed interpolations, this will only impact the
    calculation of the extensive variables.

    Based on :
       https://cran.r-project.org/web/packages/areal/vignettes/areal-weighted-interpolation.html

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

    if extensive is not None and intensive is None:

        if extensive is type(list):
            raise ValueError(
                "Multiple variables for areal weighting is not supported yet"
            )
        else:
            return _areal_weighting_single(
                sources,
                targets,
                extensive,
                intensive,
                weights,
                sid,
                tid,
                geoms,
                all_geoms,
            )

    elif extensive is None and intensive is not None:

        if intensive is type(list):
            raise ValueError(
                "Multiple variables for areal weighting is not supported yet"
            )
        else:
            return _areal_weighting_single(
                sources,
                targets,
                extensive,
                intensive,
                weights,
                sid,
                tid,
                geoms,
                all_geoms,
            )

    else:
        if extensive is not None and intensive is not None:
            raise ValueError("Mixed areal interpolation is not yet supported")


def _areal_weighting_single(
    sources,
    targets,
    extensive,
    intensive,
    weights,
    sid,
    tid,
    geoms=False,
    all_geoms=False,
):

    """

    A method for interpolating areal data based soley on
    the geometric overlap between sources and targets.
    This function only accepts single variables.

    For an 'extensive' variable, either the 'sum' or 'total' weight can
    be specified.
    For an 'intensive' variable, only the 'sum' weight can
    be specified.

    For mixed interpolations, this will only impact the
    calculation of the extensive variables.

    Based on :
       https://cran.r-project.org/web/packages/areal/vignettes/areal-weighted-interpolation.html

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

    if extensive is not None and intensive is not None:
        raise ValueError(
            "Use _areal_weighting_multi for mixed types - not yet supported"
        )

    if intensive is not None and weights != "sum":
        raise ValueError(
            "Areal weighting only supports 'sum' weights \
            with use of intensive variables"
        )

    area = "Aj"

    if extensive is not None:
        var = extensive
        if var in targets:
            raise ValueError(f"{var} already in target GeoDataFrame")
        sources[area] = sources.area
    else:
        var = intensive
        if var in targets:
            raise ValueError(f"{var} already in target GeoDataFrame")
        targets[area] = targets.area

    intersect = gpd.overlay(targets, sources, how="intersection")
    intersect = intersect.sort_values(by=tid)  # TO DO: remove afterwards

    # Calculate weights based on area overlap
    Ai = intersect.area
    Aj = intersect[area]
    Wij = Ai / Aj
    # Estimate values by weighted intersected values
    Vj = intersect[var].values
    Ei = Vj * Wij
    intersect[var] = Ei
    # Summarize data for each target
    Gk = intersect[[tid, var]].groupby(by=tid).sum()

    if weights == "total":
        w = sum(sources[var]) / sum(Gk[var])
        Gk[var] = Gk[var] * w

    if geoms is True:
        if all_geoms is True:
            return pd.merge(targets, Gk, on=tid, how="outer")
        else:
            return pd.merge(targets, Gk, on=tid, how="inner")
    else:
        return Gk

import statsmodels.formula.api as smf
from statsmodels.genmod.families import Poisson


def _model(
    sources,
    targets,
    df_fit,
    df_pred,
    extensive="pop_count",
    intensive=None,
    weights="sum",
    formula="pop_count ~ -1 + build_counts",
    summary=False,
):
    """
    An areal interpolation method that estimates target values
    using source target and predictor variables

    Parameters
    ----------
    sources : gpd.GeoDataFrame
        GeoDataFrame containing variable(s) to be interpolated
    targets : gpd.GeoDataFrame
        GeoDataFrame where variables will be assigned
    df_fit : pd.DataFrame
        source dataframe containing both target and predictors
    df_pred : pd.DataFrame
        target dataframe containing only predictors
    extensive : str or list
        str or list of extensive variables e.g population counts
    intensive : str or list
        str list of intensive variables e.g. population density
    weights : str
        type of weights to be computed
    formula : str
        fit model using R-style formula
    summary : bool (default: False)
        whether to also return statsmodel summary

    Returns
    -------
    gpd.GeoDataFrame & summary
    """

    fit = _model_fit(df_fit, extensive, intensive, formula)

    pred = _model_pred(
        sources,
        fit_model=fit,
        df_pred=df_pred,
        extensive=extensive,
        intensive=intensive,
        formula=formula,
    )

    if extensive is not None and intensive is None:
        var = extensive
    else:
        var = intensive
    # Assign prediction to targets
    targets[var] = pred

    if summary is True:
        return targets, fit.summary()
    else:
        return targets


def _model_fit(
    df_fit,
    extensive="pop_count",
    intensive=None,
    formula="pop_count ~ -1 + build_counts",
):

    """
    Fit a regression model for areal interpolation
    using source targets and predictors

    Parameters
    ----------
    df_fit : pd.DataFrame
        dataframe containing predictors only
    extensive : str
        single extensive variable
    intensive : str
        single intensive variable
    formula : string
        Patsy or R style regression formula

    Returns
    -------
    statsmodel object
        fitted statsmodel object
    """

    if extensive is not None and intensive is None:
        # Fit model using source data
        mod = smf.glm(formula=formula, data=df_fit, family=Poisson())

    elif extensive is None and intensive is not None:
        mod = smf.ols(formula=formula, data=df_fit)

    return mod.fit()


def _model_pred(
    sources,
    fit_model,
    df_pred,
    extensive="pop_count",
    intensive=None,
    formula="pop_count ~ -1 + build_counts",
):

    """
    Predict target values for areal interpolation
    using source fitted values

    Parameters
    ----------
    sources : gpd.GeoDataFrame
        sources to interpolate values from
    fit_model : statsmodel object
        dataframe containing predictors only
    df_pred : pd.DataFrame (default: None)
        dataframe containing variable of interest and predictors
    extensive : str or list
        extensive variables e.g. population counts
    intensive : str or list
        intensive variables e.g. population density
    formula : str
        Patsy or R style regression formula
    Returns
    -------
    targets : gpd.GeoDataFrame
        targets containing interpolated values
    """

    # Make predictions for targets using fitted model
    pred = fit_model.predict(df_pred)

    if extensive is not None and intensive is None:
        wts = sum(sources[extensive]) / sum(pred)
        pred *= wts
        return pred
    else:
        return pred

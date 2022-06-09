from coss.areal.areal_weighting import _areal_weighting
from coss.areal.dasy import _dasy
from tobler.pycno import pycno_interpolate
from coss.areal.model import _model
from coss.areal.areal_geobootstrap import _areal_geobootstrap
from coss.utils import _crs, _uid


class areal_interpolation:
    """Class for interpolating areal values from source GeoDataFrames to
    target GeoDataFrames"""

    def __init__(
        self,
        sources,
        targets,
        extensive,
        intensive,
        weights="sum",
        sid=None,
        tid=None,
        geoms=True,
        all_geoms=False,
    ):

        """
        Parameters
        ----------
        sources : gpd.GeoDataFrame
            Source GeoDataFrame containing variable to interpolate
        targets : gpd.GeoDataFrame
            Target GeoDataFrame containing variable to interpolate
        extensive : str
            single extensive variable
        intensive : str
            single intensive variable
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

        self.sources = sources
        self.targets = targets
        self.extensive = extensive
        self.intensive = intensive
        self.weights = weights
        self.sid = sid
        self.tid = tid
        self.geoms = geoms
        self.all_geoms = all_geoms

    def areal_checks(self, method):
        """A series of checks to ensure areal interpolation is valid"""

        if self.extensive is None and self.intensive is None:
            raise ValueError(
                "Areal interpolation requires either"
                "an extensive or intensive variable"
                "to interpolate values from sources to targets"
            )

        _crs(self.sources, self.targets)

        uid_methods = ["areal", "dasy"]

        if method in uid_methods:
            sources, sid = _uid(self.sources, self.sid, uid_type="sources")
            targets, tid = _uid(self.targets, self.tid, uid_type="targets")

            return sources.copy(), targets.copy(), sid, tid

    def areal_weighting(self):

        sources, targets, sid, tid = self.areal_checks(method="areal")

        return _areal_weighting(
            sources,
            targets,
            extensive=self.extensive,
            intensive=self.intensive,
            weights=self.weights,
            sid=sid,
            tid=tid,
            geoms=self.geoms,
            all_geoms=self.geoms,
        )

    def dasy(self, mask, how="clip"):

        sources, targets, sid, tid = self.areal_checks(method="dasy")

        return _dasy(
            sources,
            targets,
            mask=mask,
            extensive=self.extensive,
            intensive=self.intensive,
            weights=self.weights,
            sid=sid,
            tid=tid,
            how=how,
            geoms=self.geoms,
            all_geoms=self.all_geoms,
        )

    def pycno(
        self,
        cellsize=1000,
        r=0.2,
        handle_null=True,
        converge=3,
        verbose=False,
    ):

        if self.extensive is not None and self.intensive is None:
            variables = self.extensive
        elif self.extensive is None and self.intensive is not None:
            variables = self.intensive
        else:
            raise ValueError("Only single variables are currently supported")

        return pycno_interpolate(
            source_df=self.sources,
            target_df=self.targets,
            variables=[variables],
            cellsize=cellsize,
            r=r,
            handle_null=handle_null,
            converge=converge,
            verbose=verbose,
        )

    def model(
        self,
        df_fit,
        df_pred,
        formula="pop_density ~ -1 + building_density",
        summary=False,
    ):

        self.areal_checks(method="model")

        return _model(
            self.sources,
            self.targets,
            df_fit=df_fit,
            df_pred=df_pred,
            extensive=self.extensive,
            intensive=self.intensive,
            formula=formula,
            summary=summary,
        )

    def areal_geobootstrap(
        self,
        r=1000,
        kernel="gaussian",
        metric="euclidean",
        bandwidth=1000,
        fixed=True,
        average="mean",
        spread="std",
    ):

        """
        A resampling based technique for interpolating values in areal data

        Parameters
        ----------

        r : int
            how many resamples with replacement to return
        kernel : str
            kernel distance-decay function
        metric : str
            how to calculate distances between coordinates
        bandwidth : int
           bandwidth or fixed distance
        source_bounds : array_like
            (default None)
        target_bounds : array_like
            (default None)
        p : int
            number of random points to generate points within bounds
        method : str
            method for generating coordinates for each polygon
        average : array_like
            average statistic to compute
        spread : array_like
            measure of spread to compute
        Returns
        -------
        targets: gpd.GeoDataFrame
            targets containing interpolated values
        """

        if self.extensive is not None:
            raise ValueError(
                "Areal geobootstrap only supports intensive \
                variables"
            )
        sources = self.sources.copy()
        targets = self.targets.copy()

        averages, spreads = _areal_geobootstrap(
            sources=sources,
            targets=targets,
            r=r,
            kernel=kernel,
            metric=metric,
            bandwidth=bandwidth,
            fixed=fixed,
            col=self.intensive,
            average=average,
            spread=spread,
        )

        targets[average + "_" + self.intensive] = averages
        targets[spread] = spreads

        return targets

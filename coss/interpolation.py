from coss.areal.areal_weighting import _areal_weighting
from coss.areal.dasy import _dasy
from tobler.pycno import pycno_interpolate

from coss.utils import _check_crs_exists, _check_crs_match, _check_uid


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
        sid : string
            Column containing unique values
        tid : string
            Column containing unique values
        weights : string
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

    def areal_checks(self):
        """A series of checks to ensure areal interpolation is valid"""

        if self.extensive is None and self.intensive is None:
            raise ValueError(
                "Areal interpolation requires either"
                "an extensive or intensive variable"
                "to interpolate values from sources to targets"
            )

        _check_crs_exists(self.sources)
        _check_crs_exists(self.targets)

        _check_crs_match(self.sources, self.targets)

        sources, sid = _check_uid(self.sources, self.sid)
        targets, tid = _check_uid(self.targets, self.tid)

        return sources.copy(), targets.copy(), sid, tid

    def areal_weighting(self):

        sources, targets, sid, tid = self.areal_checks()

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

        sources, targets, sid, tid = self.areal_checks()

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

        sources, targets, sid, tid = self.areal_checks()

        if self.extensive is not None and self.intensive is None:
            variables = self.extensive
        elif self.extensive is None and self.intensive is not None:
            variables = self.intensive
        else:
            raise ValueError("Only single variables are currently supported")

        return pycno_interpolate(
            source_df=sources,
            target_df=targets,
            variables=[variables],
            cellsize=cellsize,
            r=r,
            handle_null=handle_null,
            converge=converge,
            verbose=verbose,
        )

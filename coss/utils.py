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


def _check_uid(df, uid=None, uid_type="sources"):
    """Creates a unique identifier for source or target GeoDataFrame"""

    if uid is None:
        import uuid
        if uid_type == "sources":
            uid = "sid"
        elif uid_type == "targets":
            uid = "tid"
        df[uid] = df.apply(lambda _: uuid.uuid4(), axis=1)

    return df, uid


def _poly(total_bounds):
    """Return polygon box based on total bounds"""

    from shapely.geometry import box

    return box(*total_bounds)


def _get_bbox(gdf):
    """Get tuple bounding box (total bounds) from GeoDataFrame"""

    xmin, ymin, xmax, ymax = gdf.total_bounds
    return (xmin, ymin, xmax, ymax)

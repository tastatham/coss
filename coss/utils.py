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
        df = _create_uid(df, uid_type="sources")
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

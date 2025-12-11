from fastapi import HTTPException, status


def validate_lat_lon(lat, lon):
    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lat/Lon invalidos") from exc

    if not -90 <= lat_f <= 90 or not -180 <= lon_f <= 180:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lat/Lon fora do intervalo")

    return lat_f, lon_f

import math


def calc_distance(lat1,lon1,lat2,lon2):
    R = 6371
    distance = R * math.acos(
        math.sin(math.radians(lat1))*
        math.sin(math.radians(lat2))+
        math.cos(math.radians(lat1))*
        math.cos(math.radians(lat2))*
        math.cos(math.radians(lon1)-math.radians(lon2)))
    return distance

def calculate_bearing(lat1, lon1, lat2, lon2):
    # ラジアンに変換
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lon = math.radians(lon2 - lon1)

    x = math.sin(delta_lon) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - \
        math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)

    bearing_rad = math.atan2(x, y)
    bearing_deg = (math.degrees(bearing_rad) + 360) % 360
    return bearing_deg

def move_point(lat, lon, distance_km, bearing_deg):
    R = 6371  # 地球の半径 (km)
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)
    bearing = math.radians(bearing_deg)

    lat2 = math.asin(
        math.sin(lat1) * math.cos(distance_km / R) +
        math.cos(lat1) * math.sin(distance_km / R) * math.cos(bearing)
    )

    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(distance_km / R) * math.cos(lat1),
        math.cos(distance_km / R) - math.sin(lat1) * math.sin(lat2)
    )

    return math.degrees(lat2), math.degrees(lon2)

def move_towards_target(lat1, lon1, lat2, lon2, distance_km):
    bearing = calculate_bearing(lat1, lon1, lat2, lon2)
    new_lat, new_lon = move_point(lat1, lon1, distance_km, bearing)
    return new_lat, new_lon


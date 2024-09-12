def geolocate(geocode, address):
    """
    helper function for the add coordinates function
    using geolocate api 
    (not used because it takes to much time)
    """
    location = geocode(address)
    print(location.address)
    latitude = location.latitude
    longitude = location.longitude
    return (latitude, longitude)
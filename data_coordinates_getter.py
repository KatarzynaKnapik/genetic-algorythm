# pip install geopy
# pip install Nominatim
from geopy.geocoders import Nominatim
from data import cities_data, deport_city

def fill_city_latitude_longtitude(dict_of_cities, deport_city):
    geolocator=Nominatim(user_agent='metody-metaheurystyczne')
    
    for city in dict_of_cities.keys():
        location = geolocator.geocode(city)
        try: 
            dict_of_cities[city][1] = location.latitude
            dict_of_cities[city][2] = location.longitude
        except IndexError:
            dict_of_cities[city].append(location.latitude)
            dict_of_cities[city].append(location.longitude)

    deport_city_location = geolocator.geocode(deport_city)
    deport_city_coords = (deport_city_location.latitude, deport_city_location.longitude)
    print(deport_city_coords)


fill_city_latitude_longtitude(cities_data, deport_city)
print(cities_data)    
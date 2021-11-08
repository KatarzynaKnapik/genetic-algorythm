import math
import haversine as hs
from data import cities_data, deport_city, deport_city_coordinates, num_of_vehicle, vehicle_capacity
import random
import pprint


def split_to_sublist(flat_arr, number):
    n = len(flat_arr) // number
    return [flat_arr[i:i + n] for i in range(0, len(flat_arr), n)]



class VRP():
    def __init__(self, cities_data, deport_city, deport_city_coordinates, num_of_vehicle, vehicle_capacity):
        self.cities_data = cities_data
        self.deport_city = deport_city
        self.deport_city_coordinates = deport_city_coordinates
        self.num_of_vehicles = num_of_vehicle
        self.vehicle_capacity = vehicle_capacity
        self.distance_matrix = self.calculate_distance_between_cities()


    def calculate_distance_between_cities(self):
        # używamy Haversine Distance, ponieważ ziemia nie jest płaska
        # Haversine Distance = angular distance
        distance_matrix = {}
        for first_city, value1 in self.cities_data.items():
            for next_city, value2 in self.cities_data.items():
                loc1 = (value1[1], value1[2])
                loc2 = (value2[1], value2[2])
                try:
                    distance_matrix[first_city][next_city] = hs.haversine(loc1, loc2)
                except KeyError:
                    distance_matrix[first_city] = {next_city: hs.haversine(loc1, loc2)}

        for city, value in self.cities_data.items():
            city_loc = (value[1], value[2])
            distance_matrix[city][self.deport_city] = hs.haversine(city_loc, self.deport_city_coordinates)
            try:
                distance_matrix[self.deport_city][city] = hs.haversine(self.deport_city_coordinates, city_loc)
            except KeyError:
                distance_matrix[self.deport_city] = {city: hs.haversine(self.deport_city_coordinates, city_loc)}
    
        return distance_matrix


    def sum_distance_on_track(self, cities_arr):
        if len(cities_arr) == 0:
            return 0

        deport_first_dist = self.distance_matrix[deport_city][cities_arr[0]]
        deport_last_dist = self.distance_matrix[deport_city][cities_arr[-1]]
        distance = deport_first_dist + deport_last_dist
        for i in range(len(cities_arr) - 1):
            distance += self.distance_matrix[cities_arr[i]][cities_arr[i+1]]
        return distance


    def sum_final_distance(self, arr_tracks):
        final_distance = 0
        for track in arr_tracks:
            final_distance += self.sum_distance_on_track(track)
        return final_distance


    def check_if_solution_valid(self, arr_track):
        for track in arr_track:
            sum_capacity_per_vehicle = 0
            for city in track:
                sum_capacity_per_vehicle += self.cities_data[city][0]
            
            if sum_capacity_per_vehicle > self.vehicle_capacity:
                return False
            
        return True


    def create_random_solutions(self, population_size):
        cities = list(self.cities_data.keys())
        city_permutations = []
        for pop in range(population_size):
            track = []
            shuffled_cities = cities[:]
            while True:
                random.shuffle(shuffled_cities)
                track = split_to_sublist(shuffled_cities, num_of_vehicle)
                if self.check_if_solution_valid(track) == True:
                    print('znaleziono random solution')
                    break
            city_permutations.append({'tracks': track, 'dist': self.sum_final_distance(track)})

        return city_permutations


    def cross_solutions(self, city_permutations):
        random_solutions = [] # wybierz grupy scieżek do krzyżowania
        for i in range(2):
            random_solutions.append(random.randrange(0, len(city_permutations)))
        
        # wybież ktore drogi w obrebie wybraneg rozwiązania pojda do krzyżowania
        random_track_no = random.randrange(0, len(city_permutations[0]['tracks'])-1)

        new_solution = city_permutations[random_solutions[0]]['tracks'][0:random_track_no]
        new_solution_cities = [city for row in new_solution for city in row]
        cities_remainder = []
        for track in city_permutations[random_solutions[1]]['tracks']:
            for city in track:
                if city not in new_solution_cities:
                    cities_remainder.append(city)

        new_solution_cities += cities_remainder
        new_solution = split_to_sublist(new_solution_cities, num_of_vehicle)
        new_solution_sum_distance = self.sum_final_distance(new_solution)
        solution_and_distance = {'tracks': new_solution, 'dist': new_solution_sum_distance}
        if self.check_if_solution_valid(new_solution):
            print('dodaje nowe solution')
            print('solution valid')
            city_permutations.append(solution_and_distance)
        return city_permutations


    def mutate(self, city_permutations):
        track_to_mutate_no = random.randrange(0, len(city_permutations))
        track_to_mutate = [city for row in city_permutations[track_to_mutate_no]['tracks'] for city in row]
        swap_city_1 = random.randrange(0, len(track_to_mutate))
        swap_city_2 = random.randrange(0, len(track_to_mutate))
        while swap_city_2 == swap_city_1:
            swap_city_2 = random.randrange(0, len(track_to_mutate))

        track_to_mutate[swap_city_1], track_to_mutate[swap_city_2] = track_to_mutate[swap_city_2], track_to_mutate[swap_city_1]            

        mutated_track = split_to_sublist(track_to_mutate, num_of_vehicle)
        new_distance = self.sum_final_distance(mutated_track)
        if self.check_if_solution_valid(mutated_track):
            city_permutations[track_to_mutate_no] = {'tracks': mutated_track, 'dist': new_distance}

        return city_permutations


    def reduce_solutions(self, city_permutations, population_size):
        sorted_city_permutations = sorted(city_permutations, key=lambda x: x['dist'])
        city_permutations = sorted_city_permutations[0:population_size]
        return city_permutations


    def genetic_algorithm(self, population_size, no_generations, no_cross, no_mutations):
        print('-------START----------')
        solutions = self.create_random_solutions(population_size)
        for generation in range(no_generations):
            print('Generacja: ', generation)
            for cross in range(no_cross):
                solutions = self.cross_solutions(solutions)
            for mutation in range(no_mutations):
                solutions = self.mutate(solutions)
            solutions = self.reduce_solutions(solutions, population_size)
            # pprint.pprint(solutions)
            # pprint.pprint([round(track['dist']) for track in solutions])
            pprint.pprint(solutions[0])



vrp = VRP(cities_data, deport_city, deport_city_coordinates, num_of_vehicle, vehicle_capacity)
vrp.genetic_algorithm(10, 1000, 5, 3)
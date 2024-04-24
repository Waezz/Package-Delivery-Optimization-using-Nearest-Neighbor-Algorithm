# Author: William Deutsch
# Student ID: 001406043

import csv
import datetime
import numpy as np
from truck import Truck
from hash import HashMap
from package import Package


# Function to read data from a CSV file
# Returns a list of list, where each sub-list represents a row in the file
def read_csv_data(file_path):
    with open(file_path, mode='r') as csvfile:
        reader = csv.reader(csvfile)
        return [row for row in reader]


# Function to create a distance Matrix from the CSV data
def create_distance_matrix(distance_path):
    lower_data = read_csv_data(distance_path)
    size = len(lower_data)  # Determine the size of the matrix
    full_matrix = np.zeros((size, size))  # Initialize a square matrix filled with zeros

    for i in range(size):
        for j in range(i + 1):  # Fill in the distance matrix
            distance = float(lower_data[i][j]) if lower_data[i][j] else 0.0  # Convert distance to float
            full_matrix[i, j] = full_matrix[j, i] = distance  # Mirror the distances to maintain symmetry

    return full_matrix


# Function to create mappings from address/location descriptions to its matrix index
def create_address_map(address_path):
    address_data = read_csv_data(address_path)
    # Create a map from location descriptions to their matrix indices
    location_to_index = {row[1].strip(): int(row[0]) for row in address_data}
    # Create a map from addresses to their matrix indices
    address_to_index = {row[2].strip(): int(row[0]) for row in address_data}
    return location_to_index, address_to_index


# Function to find the distance between two addresses
def get_distance(address1, address2, address_index_map, distance_matrix):
    index1 = address_index_map[address1]  # Retrieve the matrix index for the first address
    index2 = address_index_map[address2]  # Retrieve the matrix index for the second address
    if index1 is not None and index2 is not None:
        # Return the distance from the matrix if both indices are found
        return distance_matrix[index1][index2]
    else:
        return None


# File paths
distance_path = "CSV/Address_Distance_Info.csv"
address_path = "CSV/Address_Info.csv"
package_path = "CSV/Package_Info.csv"

# Load data into the Adjacency Matrix
distance_matrix = create_distance_matrix(distance_path)
# Create the address + location index maps
location_to_index, address_to_index = create_address_map(address_path)


# Function to load package data from CSV into the hash table
def load_package(package_path, package_hash_table):
    package_data = read_csv_data(package_path)
    for package in package_data:
        package_id = int(package[0])  # Extract the package ID and convert it to an integer
        # Create a new package instance with the extracted data
        new_package = Package(
            package_id,
            package[1].strip(),
            package[2].strip(),
            package[3].strip(),
            package[4].strip(),
            package[5].strip(),
            package[6].strip(),
            "At Hub"  # Initial status set to "At Hub"
        )
        # Insert the new package into the hash table with package_id as the key
        package_hash_table.insert(package_id, new_package)


# Instantiate the hash table for packages
package_hash_map = HashMap()

# Load package data into the hash table
load_package(package_path, package_hash_map)

# Create truck objects and manually load the packages
# Truck #1 Priority: Packages with the earliest deadlines not affected by the delayed flight
truck1 = Truck(16, 18, 0, "4001 South 700 East", datetime.timedelta(hours=8, minutes=0),
               [1, 13, 14, 15, 16, 17, 19, 20, 21, 22, 29, 30, 31, 34, 37, 40], "Truck 1")

# Truck #2 Priority: Packages delayed on the flight and specific truck 2 packages
truck2 = Truck(16, 18, 0, "4001 South 700 East", datetime.timedelta(hours=9, minutes=5),
               [2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 18, 25, 28, 32, 36, 38], "Truck 2")

# Truck #3 Priority: Remaining packages and package #9 after receiving updated address
truck3 = Truck(16, 18, 0, "4001 South 700 East", datetime.timedelta(hours=10, minutes=20),
               [9, 23, 24, 26, 27, 33, 35, 39], "Truck 3")


# This function applies the nearest neighbor algorithm to determine the optimal delivery route for the trucks
def nearest_algo(truck, package_hash_map, address_to_index, distance_matrix):
    departure_datetime = truck.departure_time  # Start time for the delivery route

    # Update the departure time for all packages loaded on to the trucks
    for package_id in truck.initial_packages:
        package = package_hash_map.lookup(package_id)
        package.departure_time = departure_datetime
        package.loaded_truck = truck  # Set the loaded_truck attribute

    # Initializes a dictionary of packages yet to be delivered
    not_delivered = {package_id: package_hash_map.lookup(package_id) for package_id in truck.initial_packages}
    current_location_index = address_to_index[truck.current_location]
    hours_per_mile = 1 / 18

    # Loop until all packages have been delivered
    while not_delivered:
        # Find the nearest package to the current location
        nearest_package_id, nearest_package = min(
            not_delivered.items(),
            key=lambda item: distance_matrix[current_location_index][address_to_index[item[1].delivery_address]]
        )

        # Calculate the distance to the nearest package
        nearest_package_distance = distance_matrix[current_location_index][
            address_to_index[nearest_package.delivery_address]]
        truck.total_mileage += nearest_package_distance  # Update the truck's total mileage

        # Calculate the travel time to deliver the nearest package.
        travel_time = datetime.timedelta(hours=(nearest_package_distance * hours_per_mile))
        departure_datetime += travel_time

        # Update the package's delivery time and status
        nearest_package.delivery_time = departure_datetime
        nearest_package.status = 'Delivered'

        # Remove the delivered package from the list of packages to be delivered
        not_delivered.pop(nearest_package_id)
        # Update the truck's current location to the location of the delivered package
        current_location_index = address_to_index[nearest_package.delivery_address]

    # Return the truck's total mileage and the last delivery time
    return truck.total_mileage, departure_datetime


# Applies the nearest neighbor algorithm to the trucks
total_mileage_truck1, last_delivery_time_truck1 = nearest_algo(truck1, package_hash_map, address_to_index,
                                                               distance_matrix)
total_mileage_truck2, last_delivery_time_truck2 = nearest_algo(truck2, package_hash_map, address_to_index,
                                                               distance_matrix)
total_mileage_truck3, last_delivery_time_truck3 = nearest_algo(truck3, package_hash_map, address_to_index,
                                                               distance_matrix)


# This function formats a timedelta object into a readable string
def format_timedelta(td):
    total_seconds = int(td.total_seconds())  # Convert time delta to total seconds
    hours = total_seconds // 3600  # Calculate hours
    minutes = (total_seconds % 3600) // 60  # Calculate minutes
    # Return the formatted time string
    return f"{hours % 12 if hours % 12 else 12}:{minutes:02d} {'AM' if hours < 12 else 'PM'}"


# This function validates if the given hours and minutes represent a valid time
def is_valid_time(h, m):
    if 0 <= h <= 23 and 0 <= m <= 59:
        return True
    else:
        return False


# Print route delivery results to the console
print("\nWelcome to WGUPS! The following is a summary of today's delivery routes and performance metrics:\n ")
print(f"Total mileage for truck 1 to deliver packages: {total_mileage_truck1:.2f} miles")
print(
    f"Truck 1 departed at {format_timedelta(truck1.departure_time)} and delivered its last package at {format_timedelta(last_delivery_time_truck1)}")
print("Truck 1 route completed, driver preparing to depart with Truck 3\n")

print(f"Total mileage for truck 2 to deliver packages: {total_mileage_truck2:.2f} miles")
print(
    f"Truck 2 departed at {format_timedelta(truck2.departure_time)} and delivered its last package at {format_timedelta(last_delivery_time_truck2)}\n")

print(f"Total mileage for truck 3 to deliver packages: {total_mileage_truck3:.2f} miles")
print(
    f"Truck 3 departed at {format_timedelta(truck3.departure_time)} and delivered its last package at {format_timedelta(last_delivery_time_truck3)}\n")

# Calculating and printing the total mileage for all trucks
total_mileage_all_trucks = total_mileage_truck1 + total_mileage_truck2 + total_mileage_truck3
print(f"Total mileage for all trucks to deliver packages: {total_mileage_all_trucks:.2f} miles\n")


# Function to interact with users and display package statuses
def user_interface(package_hash_map):
    while True:  # Loops to allow continuous interaction until the user decides to exit
        user_time = input("Please enter the time (HH:MM) you wish to see package statuses: ")
        try:
            # Convert user time to a timedelta object for comparison
            (h, m) = map(int, user_time.split(":"))
            if not is_valid_time(h, m):
                raise ValueError(f"Invalid time entered!")
            user_time = datetime.timedelta(hours=h, minutes=m)
        except ValueError as e:  # Catch and handle conversion errors or validation failures
            print(f"Incorrect time format or invalid time. Please use HH:MM format. Error: {e}")
            continue  # Skip the rest of the loop and prompt the user for time again

        # Ask the user if they want to view the status of a single package or all packages
        choice = input("Would you like to view the status for a single package or for all packages?\n"
                       "Please enter (s)ingle or (a)ll: ").lower()
        if choice == 's':  # Option for checking single package's status
            while True:
                package_id_str = input("Please enter a valid package ID (1-40): ")
                try:
                    package_id = int(package_id_str)  # Convert the input to an integer
                    if not 1 <= package_id <= 40:  # Validate if the ID is within a valid range
                        raise ValueError("Valid package ID's are between 1 and 40.")
                    package = package_hash_map.lookup(package_id)  # Lookup the package by its ID
                    if package is not None:  # If found display its status
                        updated_address = package.delivery_address
                        updated_city = package.delivery_city
                        updated_state = package.delivery_state
                        updated_zip = package.delivery_zip

                        if package_id == 9 and user_time < datetime.timedelta(hours=10, minutes=20):
                            # Use the incorrect address for package #9 until the correct address is received at 10:20a.m.
                            package.delivery_address = '300 State St'
                            package.delivery_city = 'Salt Lake City'
                            package.delivery_state = 'UT'
                            package.delivery_zip = '84103'
                        status_str = package.get_status_str(user_time)
                        print(status_str)

                        # Restore the correct address value after 10:20 a.m. when the system receives the updated info
                        package.delivery_address = updated_address
                        package.delivery_city = updated_city
                        package.delivery_state = updated_state
                        package.delivery_zip = updated_zip

                        break
                    else:
                        print(f"Package ID {package_id} not found.")
                except ValueError:
                    print("Invalid input. Please enter a valid package ID between 1 and 40.")

                    exit_choice = input("Press enter to try again or type 'Exit' to return: ").lower()
                    if exit_choice == 'exit':
                        break

        elif choice == 'a':  # Option for checking all  packages' status
            for package in package_hash_map.buckets:  # Iterate through all the buckets in the hash map
                if package is not None:  # If a package is found display its status
                    updated_address = package.delivery_address
                    updated_city = package.delivery_city
                    updated_state = package.delivery_state
                    updated_zip = package.delivery_zip

                    if package.package_id == 9 and user_time < datetime.timedelta(hours=10, minutes=20):
                        # Use the incorrect address for package #9 until the correct address is received at 10:20 a.m.
                        package.delivery_address = '300 State St'
                        package.delivery_city = 'Salt Lake City'
                        package.delivery_state = 'UT'
                        package.delivery_zip = '84103'
                    status_str = package.get_status_str(user_time)
                    print(status_str)

                    # Restore the correct address values after 10:20 a.m. when the system receives the updated info
                    package.delivery_address = updated_address
                    package.delivery_city = updated_city
                    package.delivery_state = updated_state
                    package.delivery_zip = updated_zip
        else:  # Handle invalid option selection
            print("Invalid option selected. Please enter 's' for single or 'a' for all.")

        # Prompt the user to either perform another search or exit the program
        search_again = input("\nWould you like to see the status of another package?\n"
                             "Please enter (y) if you would like to search again.\n"
                             "Otherwise enter (n) to end the program: ").lower()
        if search_again == 'n':  # Exit the loop and end the program if the user chooses 'n'
            break


# Main block to run the user interface
if __name__ == "__main__":
    user_interface(package_hash_map)  # Call the UI function with the package hash map

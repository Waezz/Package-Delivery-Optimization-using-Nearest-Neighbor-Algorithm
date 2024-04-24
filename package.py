class Package:
    def __init__(self, package_id, delivery_address, delivery_city, delivery_state, delivery_zip, delivery_deadline,
                 package_weight, initial_status="At Hub"):
        # Initialize a new instance of the package class with various attributes related to the
        # package delivery details.
        self.package_id = package_id
        self.delivery_address = delivery_address
        self.delivery_city = delivery_city
        self.delivery_state = delivery_state
        self.delivery_zip = delivery_zip
        self.delivery_deadline = delivery_deadline
        self.package_weight = package_weight
        self.status = initial_status
        self.departure_time = None
        self.delivery_time = None
        self.loaded_truck = None

    # Method to update the package's status based on the current time and prepare a status string
    def get_status_str(self, current_time=None):
        if self.loaded_truck is not None:
            truck_info = f"{self.loaded_truck.truck_name}"
        else:
            truck_info = ""
        if current_time is not None:
            if self.delivery_time and current_time >= self.delivery_time:
                self.status = "Delivered"  # Mark as delivered if the current time is after the delivery time
            elif self.departure_time and current_time >= self.departure_time:
                self.status = f"En Route in {truck_info}"  # Mark as En Route if the package has left the hub but not yet delivered
            else:
                self.status = f"At Hub in {truck_info}"  # Otherwise, It's still at the hub

        # Prepare the base of the status string including package details
        status_str = f"Status: {self.status}"
        if self.status == "Delivered" and self.delivery_time is not None:
            # If the package is delivered format the time into a readable string
            total_seconds = int(self.delivery_time.total_seconds())
            hours = total_seconds // 3600  # Calculate hours
            minutes = (total_seconds % 3600) // 60  # Calculate minutes
            # Adjust hours for 12-hour format and determine AM/PM
            hours_display = hours % 24
            am_pm = "AM" if hours < 12 else "PM"
            if hours_display == 0:
                hours_display = 12
            elif hours_display > 12:
                hours_display -= 12

            delivery_str = f"{hours_display:02d}:{minutes:02d} {am_pm}"  # Format the delivery time string
            status_str = f", Delivered at {delivery_str} by {truck_info}"  # Append delivery time to status string
        else:
            delivery_str = "N/A"

        # Return the full status string including all package details
        return (
            f"Package ID: {self.package_id}, Address: {self.delivery_address}, {self.delivery_city}, {self.delivery_state},"
            f" {self.delivery_zip}, Deadline: {self.delivery_deadline}, Weight: {self.package_weight}, {status_str}")

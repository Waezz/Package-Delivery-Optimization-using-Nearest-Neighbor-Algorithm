# Custom hash table implementation based on concepts from:
# -https://www.geeksforgeeks.org/implementation-of-hash-table-in-python-using-separate-chaining/
# -https://realpython.com/python-hash-table/#let-the-hash-table-resize-automatically
#
# The sources above were consulted to understand hash table Data Structures.
# However, the implementation was developed independently to meet the
# specified requirements and optimize performance for the given use case.

class HashMap:
    def __init__(self, initial_capacity=40):
        # Create a list of 'None' buckets to values to serve as the initial buckets
        self.buckets = [None] * initial_capacity
        # Initialize the size of the hash table to 0
        # The size will help keep track of the number of elements in the table
        self.size = 0
        # Define the load factor as .75 - so the hash table will resize when 75% full
        self.load = 0.75

    def custom_hash(self, key):
        # Since package IDs are sequential and start from 1
        # I directly mapped the package IDs to bucket indices by adjusting for 0-based indexing
        return (key - 1) % len(self.buckets)

    def insert(self, key, value):
        # This method checks if we need to resize before inserting and
        # doubles the size of the hashtable if the load factor becomes greater than 75%
        if self.size / len(self.buckets) >= self.load:
            self.resize(2 * len(self.buckets))

        # Directly insert or update a value based on the package ID
        bucket_index = self.custom_hash(key)
        # Increase self.size by 1 to keep track of the total number of elements stored in the hash table
        if self.buckets[bucket_index] is None:
            self.size += 1
        self.buckets[bucket_index] = value
        return True

    def lookup(self, key):
        # This method retrieves a value using the package ID, leveraging direct indexing
        bucket_index = self.custom_hash(key)  # Computes the bucket index for the given key using the hash function
        # Directly return the value from the bucket
        return self.buckets[bucket_index]

    def hash_remove(self, key):
        # This method removes an item from the hash table using its key
        bucket_index = self.custom_hash(key)
        # Checks if the bucket at the calculated index is not empty
        if self.buckets[bucket_index] is not None:
            self.buckets[bucket_index] = None  # If an item exits set its bucket to None, effectively removing it
            self.size -= 1  # Decrease the size by 1 since an item is removed
            return True
        else:
            return False

    def resize(self, new_capacity):
        # This method resizes the hash table to a new capacity
        old_buckets = self.buckets  # Store the current buckets array
        self.buckets = [None] * new_capacity  # Create a new buckets array with the new capacity
        old_size = self.size  # Temporarily hold the old size to restore it after re-insertion
        self.size = 0  # Reset the size to correctly count during re-insertion

        for i in range(len(old_buckets)):
            if old_buckets[i] is not None:
                # Re-insert each item from the old array into the new array
                self.insert(i+1, old_buckets[i])
        self.size = old_size


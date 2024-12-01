# Importing necessary Python libraries
import sqlite3  # For database interactions
import datetime  # For timestamp and date operations
from typing import Dict, Any, Optional  # For type hinting
from dataclasses import dataclass  # For creating data classes
from contextlib import contextmanager  # For context management
import logging  # For robust logging and error tracking

# Configure logging to provide informative system messages and track errors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Animal:
    """
    Represents an animal in the veterinary system.
    
    A data class provides a clean way to create objects with defined attributes.
    It automatically generates methods like __init__, __repr__, and __eq__.
    
    Attributes:
        species (str): Type of animal (e.g., Cat, Dog, Parrot)
        name (str): Name of the animal
        owner (str): Name of the animal's owner
        age (int): Age of the animal
        checkup_reason (str): Reason for the veterinary visit
        id (Optional[int]): Unique identifier in the database (optional)
    """
    species: str
    name: str
    owner: str
    age: int
    checkup_reason: str
    id: Optional[int] = None

    def validate(self) -> bool:
        """
        Validates the animal's information before database insertion.
        
        Checks that all required fields are filled.
        
        Returns:
            bool: True if all fields are populated, False otherwise
        """
        # Check if any of the required fields are empty or None
        if not all([self.species, self.name, self.owner, self.age, self.checkup_reason]):
            # Log a warning if validation fails
            logger.warning(f"Invalid animal data: {self}")
            return False
        return True

class VeterinaryDatabase:
    """
    Manages database operations for the veterinary check-in system.
    
    Provides methods for:
    - Creating database connection
    - Creating database table
    - Adding animals
    - Retrieving animal information
    - Discharging animals
    
    Uses context management for safe database connections.
    """
    def __init__(self, db_name: str = "VetBase.db"):
        """
        Initialize the database with a given database file name.
        
        Args:
            db_name (str): Name of the SQLite database file (default: VetBase.db)
        """
        self.db_name = db_name
        # Create the database table when the class is instantiated
        self._create_table()

    @contextmanager
    def _get_connection(self):
        """
        Context manager for database connections.
        
        Ensures that database connections are properly opened and closed.
        Provides error handling for database connection issues.
        
        Yields:
            sqlite3.Connection: A database connection
        
        Raises:
            sqlite3.Error: If there's an issue with the database connection
        """
        try:
            # Open a connection to the database
            conn = sqlite3.connect(self.db_name)
            yield conn
        except sqlite3.Error as e:
            # Log any database connection errors
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            # Ensure the connection is closed after use
            conn.close()

    def _create_table(self):
        """
        Create the checkups table in the database if it doesn't exist.
        
        The table stores information about animals checked into the veterinary system.
        Uses a single table with columns for all necessary animal details.
        """
        try:
            # Use context manager to handle database connection
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # SQL statement to create table with proper schema
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS checkups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        species TEXT NOT NULL,
                        name TEXT NOT NULL,
                        owner TEXT NOT NULL,
                        age INTEGER NOT NULL,
                        checkup_reason TEXT
                    )
                ''')
                conn.commit()
            logger.info("Veterinary database table initialized successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error creating database table: {e}")
            raise

    def add_animal(self, animal: Animal) -> Optional[int]:
        """
        Add an animal to the database.
        
        Validates the animal data before insertion.
        
        Args:
            animal (Animal): The animal to be added to the database
        
        Returns:
            Optional[int]: The ID of the inserted animal, or None if insertion failed
        """
        # First validate the animal data
        if not animal.validate():
            return None

        try:
            # Use context manager for database connection
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Insert animal details into the database
                cursor.execute(
                    'INSERT INTO checkups (species, name, owner, age, checkup_reason) VALUES (?, ?, ?, ?, ?)',
                    (animal.species, animal.name, animal.owner, animal.age, animal.checkup_reason)
                )
                conn.commit()
                # Set the database-generated ID
                animal.id = cursor.lastrowid
                logger.info(f"Added animal: {animal}")
                return animal.id
        except sqlite3.Error as e:
            logger.error(f"Error adding animal to database: {e}")
            return None

    def get_animal_info(self, animal_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve detailed information about an animal by its ID.
        
        Args:
            animal_id (int): The unique identifier of the animal
        
        Returns:
            Optional[Dict[str, Any]]: A dictionary of animal information, or None if not found
        """
        try:
            # Use context manager for database connection
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Retrieve all information for the specified animal ID
                cursor.execute('SELECT * FROM checkups WHERE id = ?', (animal_id,))
                result = cursor.fetchone()
                
                # Convert database result to a dictionary if found
                if result:
                    return {
                        'id': result[0],
                        'species': result[1],
                        'name': result[2],
                        'owner': result[3],
                        'age': result[4],
                        'checkup_reason': result[5]
                    }
                return None
        except sqlite3.Error as e:
            logger.error(f"Error retrieving animal information: {e}")
            return None

    def discharge_animal(self, animal_id: int) -> bool:
        """
        Remove an animal from the database (discharge).
        
        Args:
            animal_id (int): The unique identifier of the animal to discharge
        
        Returns:
            bool: True if discharge was successful, False otherwise
        """
        try:
            # Use context manager for database connection
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Delete the animal record from the database
                cursor.execute('DELETE FROM checkups WHERE id = ?', (animal_id,))
                conn.commit()
                
                # Check if any rows were affected by the deletion
                if cursor.rowcount > 0:
                    logger.info(f"Discharged animal with ID: {animal_id}")
                    return True
                
                logger.warning(f"No animal found with ID: {animal_id}")
                return False
        except sqlite3.Error as e:
            logger.error(f"Error discharging animal: {e}")
            return False

class VetCheckInSystem:
    """
    Main application class for the veterinary check-in system.
    
    Provides a user interface for:
    - Adding new animal check-ins
    - Checking animal status
    - Discharging animals
    """
    def __init__(self):
        """
        Initialize the veterinary check-in system.
        
        Sets up the database connection and defines available animal species.
        """
        # Create database instance
        self.db = VeterinaryDatabase()
        # Define supported animal species
        self.species_options = ["Cat", "Dog", "Parrot"]

    def _get_valid_input(self, prompt: str, input_type=str, options=None):
        """
        Robust input validation method.
        
        Ensures user input meets specified criteria:
        - Correct data type
        - Optional list of valid options
        
        Args:
            prompt (str): Message displayed to the user
            input_type (type): Expected type of input (default: string)
            options (list, optional): List of valid input options
        
        Returns:
            Validated user input
        """
        while True:
            try:
                # Get user input
                user_input = input(prompt)
                
                # Convert input to specified type if not a string
                if input_type != str:
                    user_input = input_type(user_input)
                
                # Validate against options if provided
                if options and user_input not in options:
                    raise ValueError
                
                return user_input
            except ValueError:
                print("Invalid input. Please try again.")

    def new_checkup(self):
        """
        Create a new animal check-up process.
        
        Guides user through entering animal details:
        1. Select animal species
        2. Enter animal details
        3. Save to database
        4. Display check-in ID
        """
        # Display species options
        print("\nSelect Animal Species:")
        for i, species in enumerate(self.species_options, 1):
            print(f"[{i}] {species}")
        
        # Get validated species selection
        species_index = self._get_valid_input(
            "YOUR CHOICE: ", 
            int, 
            list(range(1, len(self.species_options) + 1))
        )
        species = self.species_options[species_index - 1]

        # Collect animal details with input validation
        name = self._get_valid_input("Pet Name: ")
        age = self._get_valid_input("Pet Age: ", int)
        owner = self._get_valid_input("Owner Name: ")
        checkup_reason = self._get_valid_input("Checkup Reason: ")

        # Create Animal instance
        animal = Animal(
            species=species,
            name=name,
            age=age,
            owner=owner,
            checkup_reason=checkup_reason
        )
        
        # Save animal to database
        animal_id = self.db.add_animal(animal)
        
        # Display check-in confirmation
        if animal_id:
            print(f"\n\tCheck-up ID: {animal_id}\tPlease note for future processes.\t")

    def check_animal_status(self):
        """
        Retrieve and display an animal's current status by ID.
        
        Allows user to look up detailed information about a specific animal.
        """
        # Get validated animal ID
        animal_id = self._get_valid_input("Enter Animal ID: ", int)
        # Retrieve animal information
        animal_info = self.db.get_animal_info(animal_id)
        
        # Display retrieved information
        if animal_info:
            print("\nANIMAL INFORMATION:")
            for key, value in animal_info.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
        else:
            print("Animal not found.")

    def discharge_animal(self):
        """
        Process for discharging an animal from the veterinary system.
        
        Allows user to:
        1. Enter animal ID
        2. Confirm discharge
        3. Remove animal from database
        """
        # Get validated animal ID
        animal_id = self._get_valid_input("Enter Animal ID: ", int)
        
        # Confirm discharge with user
        confirm = self._get_valid_input(
            "Are you sure you want to discharge this animal? (y/n): ", 
            str.lower,
            ['y', 'n']
        )
        
        # Perform discharge if confirmed
        if confirm == 'y':
            if self.db.discharge_animal(animal_id):
                print("Animal successfully discharged.")
            else:
                print("Discharge failed. Please check the animal ID.")

    def run(self):
        """
        Main application loop.
        
        Provides a menu-driven interface for:
        - New animal check-in
        - Checking animal status
        - Discharging animals
        - Exiting the system
        """
        # Display current date
        print(f"Veterinary Check-in System - {datetime.datetime.now().strftime('%d-%m-%Y')}")
        
        # Continuous menu loop
        while True:
            # Display menu options
            print("\nMAIN MENU:")
            print("[1] New Animal Check-in")
            print("[2] Check Animal Status")
            print("[3] Discharge Animal")
            print("[4] Exit System")
            
            # Get validated menu choice
            choice = self._get_valid_input(
                "YOUR CHOICE: ", 
                int, 
                [1, 2, 3, 4]
            )
            
            # Execute corresponding action
            if choice == 1:
                self.new_checkup()
            elif choice == 2:
                self.check_animal_status()
            elif choice == 3:
                self.discharge_animal()
            else:
                # Exit message
                print("""
-----------------------------------------------------
    Thank you for using VetTech Solutions
-----------------------------------------------------
                SYSTEM EXITED""")
                break

def main():
    """
    Entry point for the application.
    
    Initializes the veterinary check-in system and handles any unexpected errors.
    """
    try:
        # Create and run the veterinary system
        vet_system = VetCheckInSystem()
        vet_system.run()
    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Unexpected error occurred: {e}")
        print("An unexpected error occurred. Please contact support.")

# Ensure the script only runs when directly executed
if __name__ == "__main__":
    main()
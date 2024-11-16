import csv
from datetime import datetime

class ConfigManager:
    """
    ConfigManager handles the loading, saving, and editing of the configuration settings for the 
    study program. The configuration is stored in a CSV file, and this class provides methods to 
    read from and write to that file, as well as to modify individual settings.

    Attributes:
        config_file (str): The path to the CSV file that stores the configuration data.
        end_date (datetime): The end date for the study program.
        weekly_hours (int): The number of hours available for study each week.
        remaining_courses (int): The number of remaining courses in the study program.
        max_courses (int): The maximum number of courses that can be taken in the study program.
        hours_per_course (float): The estimated number of hours required to complete each course.
    """

    def __init__(self, config_file='config.csv'):
        """
        Initializes the ConfigManager by loading the configuration from the specified CSV file.

        Args:
            config_file (str): The path to the configuration file. Defaults to 'config.csv'.
        """
        self.config_file = config_file
        self.end_date = None
        self.weekly_hours = None
        self.remaining_courses = None
        self.max_courses = None
        self.hours_per_course = None
        self.load_config()

    def load_config(self):
        """
        Loads the configuration from the CSV file. If the file is missing or in an invalid format,
        it prints an error message. The method reads values for the study end date, weekly study hours, 
        remaining courses, maximum courses, and hours per course.

        If the configuration file is not found or there is a format error, default values are used 
        for missing fields.
        """
        try:
            with open(self.config_file, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.end_date = datetime.strptime(row['end_date'], '%Y-%m-%d') if row['end_date'] else None
                    self.weekly_hours = int(row['weekly_hours']) if row['weekly_hours'] else None
                    self.remaining_courses = int(row['remaining_courses']) if row['remaining_courses'] else 35
                    self.max_courses = int(row['max_courses']) if row['max_courses'] else 35
                    self.hours_per_course = float(row['hours_per_course']) if row['hours_per_course'] else None
        except (FileNotFoundError, KeyError, ValueError):
            print("Configuration file not found or invalid format. Please set configuration data.")

    def save_config(self):
        """
        Saves the current configuration to the CSV file. The configuration includes the study end date,
        weekly hours, remaining courses, maximum courses, and hours per course. After saving, the configuration 
        is reloaded to update the attributes.
        """
        with open(self.config_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['end_date', 'weekly_hours', 'remaining_courses', 'max_courses', 'hours_per_course'])
            writer.writeheader()
            writer.writerow({
                'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else "",
                'weekly_hours': self.weekly_hours,
                'remaining_courses': self.remaining_courses,
                'max_courses': self.max_courses,
                'hours_per_course': self.hours_per_course
            })
        self.load_config()

    def edit_config(self, end_date, weekly_hours, max_courses, hours_per_course=None):
        """
        Edits the configuration by updating the specified values for the study program. The configuration
        is then saved to the file.

        Args:
            end_date (str): The new end date for the study program (in 'YYYY-MM-DD' format).
            weekly_hours (int): The new number of available study hours per week.
            max_courses (int): The new maximum number of courses in the study program.
            hours_per_course (float, optional): The new number of hours required for each course. 
                                                 If not provided, the existing value remains unchanged.
        """
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.weekly_hours = weekly_hours
        self.max_courses = max_courses
        if hours_per_course is not None:
            self.hours_per_course = hours_per_course
        self.save_config()

    def is_config_complete(self) -> bool:
        """
        Checks if all the required configuration fields have been set. The configuration is considered complete 
        if the end date, weekly hours, remaining courses, maximum courses, and hours per course are all defined.

        Returns:
            bool: True if all configuration fields are set; otherwise, False.
        """
        return all([self.end_date, self.weekly_hours, self.remaining_courses, self.max_courses, self.hours_per_course])

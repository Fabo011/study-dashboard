import csv
from datetime import datetime

class ConfigManager:
    def __init__(self, config_file='config.csv'):
        self.config_file = config_file
        self.end_date = None
        self.weekly_hours = None
        self.remaining_courses = None
        self.max_courses = None
        self.hours_per_course = None  # New attribute for hours per course
        self.load_config()

    def load_config(self):
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

    def edit_config(self, end_date, weekly_hours, max_courses, hours_per_course=None):
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.weekly_hours = weekly_hours
        self.max_courses = max_courses
        if hours_per_course is not None:
            self.hours_per_course = hours_per_course
        self.save_config()

    def is_config_complete(self) -> bool:
        return all([self.end_date, self.weekly_hours, self.remaining_courses, self.max_courses, self.hours_per_course])

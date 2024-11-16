from datetime import datetime, timedelta
from .config_manager_class import ConfigManager
from .course_manager_class import CourseManager

class ProgressCalculator:
    """
    ProgressCalculator calculates and evaluates the estimated study end date based on 
    available configuration settings and the number of remaining courses.

    Attributes:
        config_manager (ConfigManager): An instance that manages configuration data such as weekly hours, courses, and hours per course.
        course_manager (CourseManager): An instance that handles course data and progress.
    """

    def __init__(self, config_manager: ConfigManager, course_manager: CourseManager):
        """
        Initializes the ProgressCalculator with the given configuration and course manager instances.

        Args:
            config_manager (ConfigManager): An instance for managing the application's configuration.
            course_manager (CourseManager): An instance for managing course data.
        """
        self.config_manager = config_manager
        self.course_manager = course_manager

    def calculate_estimated_end_date(self) -> datetime:
        """
        Calculates the estimated end date of the study program based on remaining courses, 
        hours per course, and available weekly study hours.

        The estimated end date is computed by dividing the total hours remaining by the 
        weekly study hours, and adding that to the current date.

        Returns:
            datetime: The estimated end date if valid parameters are provided; otherwise, None.
        """
        if self.config_manager.weekly_hours and self.config_manager.remaining_courses and self.config_manager.hours_per_course:
            total_hours_remaining = self.config_manager.remaining_courses * self.config_manager.hours_per_course
            time_to_finish = total_hours_remaining / self.config_manager.weekly_hours
            estimated_end = datetime.now() + timedelta(weeks=time_to_finish)
            return estimated_end
        return None

    def check_schedule_status(self) -> str:
        """
        Checks the schedule status by comparing the estimated end date with the configured end date.
        
        If the estimated end date is on or before the configured end date, the status is "On Track".
        If it is after the configured end date, the status is "Not On Time".
        If any necessary configuration is missing, the status will indicate that the configuration is incomplete.

        Returns:
            str: A message indicating whether the study program is on track, not on time, or if the configuration is incomplete.
        """
        estimated_end = self.calculate_estimated_end_date()
        if estimated_end and self.config_manager.end_date:
            if estimated_end <= self.config_manager.end_date:
                return f"Auf einem Gutem Weg! Vorraussuchter Abschluss: {estimated_end.strftime('%d.%m.%Y')}"
            else:
                return f"Nicht pünktlich! Vorraussuchter Abschluss: {estimated_end.strftime('%d.%m.%Y')}"
        return "Konfiguration ist nicht komplett."


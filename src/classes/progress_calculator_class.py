from datetime import datetime, timedelta
from .config_manager_class import ConfigManager
from .course_manager_class import CourseManager

class ProgressCalculator:
    def __init__(self, config_manager: ConfigManager, course_manager: CourseManager):
        self.config_manager = config_manager
        self.course_manager = course_manager

    def calculate_estimated_end_date(self) -> datetime:
        if self.config_manager.weekly_hours and self.config_manager.remaining_courses and self.config_manager.hours_per_course:
            total_hours_remaining = self.config_manager.remaining_courses * self.config_manager.hours_per_course
            time_to_finish = total_hours_remaining / self.config_manager.weekly_hours
            estimated_end = datetime.now() + timedelta(weeks=time_to_finish)
            return estimated_end
        return None

    def check_schedule_status(self) -> str:
        estimated_end = self.calculate_estimated_end_date()
        if estimated_end and self.config_manager.end_date:
            if estimated_end <= self.config_manager.end_date:
                return f"Auf einem Gutem Weg! Vorraussuchter Abschluss: {estimated_end.strftime('%d.%m.%Y')}"
            else:
                return f"Nicht pünktlich! Vorraussuchter Abschluss: {estimated_end.strftime('%d.%m.%Y')}"
        return "Konfiguration ist nicht komplett."

from .config_manager_class import ConfigManager

class CourseManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def complete_course(self):
        if self.config_manager.remaining_courses > 0:
            self.config_manager.remaining_courses -= 1
            self.config_manager.save_config()

    def calculate_current_progress(self) -> float:
        completed_courses = self.config_manager.max_courses - self.config_manager.remaining_courses
        return (completed_courses / self.config_manager.max_courses) * 100

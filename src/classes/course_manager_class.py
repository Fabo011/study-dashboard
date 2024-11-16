from .config_manager_class import ConfigManager

class CourseManager:
    """
    CourseManager is responsible for managing the course completion process and calculating the 
    current progress of the study program. It interacts with the ConfigManager to track the 
    number of remaining courses and update the configuration accordingly.

    Attributes:
        config_manager (ConfigManager): An instance that manages configuration data related to 
                                         the number of courses and the remaining courses.
    """

    def __init__(self, config_manager: ConfigManager):
        """
        Initializes the CourseManager with the given ConfigManager instance.

        Args:
            config_manager (ConfigManager): An instance responsible for managing course-related 
                                             configuration settings such as the total number of 
                                             courses and remaining courses.
        """
        self.config_manager = config_manager

    def complete_course(self):
        """
        Marks one course as completed by reducing the number of remaining courses. 
        The configuration is updated after the completion.

        If there are remaining courses (i.e., `remaining_courses` > 0), the method 
        decrements the remaining courses and saves the updated configuration.
        """
        if self.config_manager.remaining_courses > 0:
            self.config_manager.remaining_courses -= 1
            self.config_manager.save_config()

    def calculate_current_progress(self) -> float:
        """
        Calculates the current progress of the study program as a percentage.

        The progress is computed by determining how many courses have been completed and 
        dividing that by the total number of courses (`max_courses`). The result is 
        then multiplied by 100 to obtain the percentage.

        Returns:
            float: The current progress of the study program as a percentage (0-100).
        """
        completed_courses = self.config_manager.max_courses - self.config_manager.remaining_courses
        return (completed_courses / self.config_manager.max_courses) * 100


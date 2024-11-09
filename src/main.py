import csv
from datetime import datetime, timedelta
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

# --- ConfigManager ---
class ConfigManager:
    def __init__(self, config_file='config.csv'):
        self.config_file = config_file
        self.end_date = None
        self.weekly_hours = None
        self.remaining_courses = 35  # Default remaining courses
        self.max_courses = 35  # Default maximum number of courses
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.end_date = datetime.strptime(row['end_date'], '%Y-%m-%d') if row['end_date'] else None
                    self.weekly_hours = int(row['weekly_hours']) if row['weekly_hours'] else None
                    self.remaining_courses = int(row['remaining_courses']) if row['remaining_courses'] else 35
                    self.max_courses = int(row['max_courses']) if row['max_courses'] else 35  # Default to 35 if not found
        except (FileNotFoundError, KeyError, ValueError):
            print("Configuration file not found or invalid format. Please set configuration data.")

    def save_config(self):
        # Save the config file with all relevant values including max_courses
        with open(self.config_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['end_date', 'weekly_hours', 'remaining_courses', 'max_courses'])
            writer.writeheader()
            writer.writerow({
                'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else "",
                'weekly_hours': self.weekly_hours,
                'remaining_courses': self.remaining_courses,
                'max_courses': self.max_courses
            })

    def edit_config(self, end_date, weekly_hours, max_courses):
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.weekly_hours = weekly_hours
        self.max_courses = max_courses
        self.save_config()

    def is_config_complete(self) -> bool:
        return all([self.end_date, self.weekly_hours, self.remaining_courses, self.max_courses])

# --- CourseManager ---
class CourseManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def complete_course(self):
        if self.config_manager.remaining_courses > 0:
            self.config_manager.remaining_courses -= 1  # Decrease the remaining courses
            self.config_manager.save_config()  # Save the updated remaining_courses

    def calculate_current_progress(self) -> float:
        completed_courses = self.config_manager.max_courses - self.config_manager.remaining_courses
        return (completed_courses / self.config_manager.max_courses) * 100

# --- ProgressCalculator ---
class ProgressCalculator:
    def __init__(self, config_manager: ConfigManager, course_manager: CourseManager):
        self.config_manager = config_manager
        self.course_manager = course_manager

    def calculate_estimated_end_date(self) -> datetime:
        if self.config_manager.weekly_hours and self.config_manager.remaining_courses:
            total_weeks_needed = self.config_manager.remaining_courses / self.config_manager.weekly_hours
            return datetime.now() + timedelta(weeks=total_weeks_needed)
        return None

    def check_schedule_status(self) -> str:
        estimated_end = self.calculate_estimated_end_date()
        if estimated_end and self.config_manager.end_date:
            if estimated_end <= self.config_manager.end_date:
                return "You are on track!"
            else:
                return "Adjust your weekly hours to stay on schedule."
        return "Configuration data is incomplete."

# --- DashInterface ---
class DashInterface:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.course_manager = CourseManager(self.config_manager)
        self.progress_calculator = ProgressCalculator(self.config_manager, self.course_manager)
        self.app = dash.Dash(__name__)
        self.render_dashboard()

    def open_config_editor(self):
        return html.Div([
            html.H2("Edit Configuration"),
            html.Label("End Date (YYYY-MM-DD):"),
            dcc.Input(id="end-date-input", type="text", 
                      value=self.config_manager.end_date.strftime('%Y-%m-%d') if self.config_manager.end_date else ""),
            html.Label("Weekly Study Hours:"),
            dcc.Input(id="weekly-hours-input", type="number", value=self.config_manager.weekly_hours),
            html.Label("Maximum Courses:"),
            dcc.Input(id="max-courses-input", type="number", value=self.config_manager.max_courses),
            html.Button("Save", id="save-config-button"),
            html.Div(id="config-save-output")
        ], style={'padding': '20px', 'border': '1px solid black'})

    def complete_course_button(self):
        return html.Button("Complete Course", id="complete-course-button")

    def render_dashboard(self):
        self.app.layout = html.Div([
            html.H1("Course Progress Dashboard"),
            self.complete_course_button(),
            html.Div(id="schedule-status"),
            dcc.Graph(id="circle-visualization"),
            self.open_config_editor(),
            dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0)
        ])

        # Combine all logic into a single callback to handle updates
        self.app.callback(
            Output("schedule-status", "children"),
            Output("circle-visualization", "figure"),
            Output("config-save-output", "children"),
            Input("complete-course-button", "n_clicks"),
            Input("save-config-button", "n_clicks"),
            Input("interval-component", "n_intervals"),  # To allow automatic updates
            State("end-date-input", "value"),
            State("weekly-hours-input", "value"),
            State("max-courses-input", "value"),
            prevent_initial_call=True
        )(self.update_dashboard)

    def update_dashboard(self, n_clicks_complete, n_clicks_save, n_intervals, end_date, weekly_hours, max_courses):
        ctx = dash.callback_context
        # Initialize response variables
        status = self.progress_calculator.check_schedule_status()
        figure = self.create_circle_figure()
        message = ""

        # Handle course completion
        if ctx.triggered and "complete-course-button" in ctx.triggered[0]['prop_id']:
            self.course_manager.complete_course()
            status = self.progress_calculator.check_schedule_status()  # Refresh status after completion

        # Save the config
        if ctx.triggered and "save-config-button" in ctx.triggered[0]['prop_id']:
            if end_date and weekly_hours and max_courses:
                try:
                    self.config_manager.edit_config(end_date, int(weekly_hours), int(max_courses))
                    message = "Configuration saved successfully."
                except ValueError:
                    message = "Error: Invalid input values."

        return (status, figure, message)

    def create_circle_figure(self):
        completed_courses = self.config_manager.max_courses - self.config_manager.remaining_courses
        remaining_courses = self.config_manager.remaining_courses

        # Create a pie chart for circular visualization
        figure = go.Figure(data=[go.Pie(
            labels=['Completed Courses', 'Remaining Courses'],
            values=[completed_courses, remaining_courses],
            marker=dict(colors=['green', 'grey']),
            hole=0.4  # Donut chart:)
        )])
        figure.update_layout(title='Course Completion Status',
                             annotations=[dict(text=f"{completed_courses}/{self.config_manager.max_courses} Completed", 
                                               font_size=20, showarrow=False)])
        return figure


if __name__ == "__main__":
    dash_app = DashInterface()
    dash_app.app.run_server(debug=True)


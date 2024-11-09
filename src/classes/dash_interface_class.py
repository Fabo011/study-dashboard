import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from .config_manager_class import ConfigManager
from .course_manager_class import CourseManager
from .progress_calculator_class import ProgressCalculator

class DashInterface:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.course_manager = CourseManager(self.config_manager)
        self.progress_calculator = ProgressCalculator(self.config_manager, self.course_manager)
        self.app = dash.Dash(__name__)
        self.render_dashboard()

    def render_dashboard(self):
        """Sets up the layout and initial callbacks for the Dash app."""
        self.app.layout = html.Div([
            html.H1("Study Dashboard"),
            dcc.Store(id="modal-visible", data=False),

            html.Div([
                html.Div([
                    dcc.Graph(id="circle-visualization", style={'width': '100%'}),
                    html.Div(id="completed-text", style={'text-align': 'center', 'font-size': '1.2rem', 'margin-top': '10px'}),
                    html.Div(id="study-status-circle", style={'text-align': 'center', 'margin-top': '10px'}),
                    html.Div(id="schedule-status", style={'text-align': 'center', 'font-size': '1.2rem'})
                ], style={'width': '40%', 'float': 'left'}),

                html.Div([
                    html.Button("Complete Course", id="complete-course-button", style={'display': 'block', 'margin': '20px auto'}),
                    html.Button("Edit Configuration", id="edit-config-button", style={'display': 'block', 'margin': '20px auto'}),
                    self.open_config_editor()
                ], style={'width': '40%', 'float': 'right', 'text-align': 'center'}),
            ], style={'width': '80%', 'margin': 'auto', 'display': 'flex', 'justify-content': 'space-between'}),
            
            dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0)
        ])

        self.app.callback(
            Output("schedule-status", "children"),
            Output("circle-visualization", "figure"),
            Output("completed-text", "children"),
            Output("config-save-output", "children"),
            Output("study-status-circle", "children"),
            Output("config-modal", "style"),
            Input("complete-course-button", "n_clicks"),
            Input("save-config-button", "n_clicks"),
            Input("edit-config-button", "n_clicks"),
            Input("close-config-button", "n_clicks"),
            Input("interval-component", "n_intervals"),
            State("modal-visible", "data"),
            State("end-date-input", "value"),
            State("weekly-hours-input", "value"),
            State("max-courses-input", "value"),
            State("hours-per-course-input", "value"),
            prevent_initial_call=True
        )(self.update_dashboard)

        self.app.callback(
            Output("modal-visible", "data"),
            Input("edit-config-button", "n_clicks"),
            Input("save-config-button", "n_clicks"),
            Input("close-config-button", "n_clicks"),
            State("modal-visible", "data"),
            prevent_initial_call=True
        )(self.toggle_modal_visibility)

    def open_config_editor(self):
        return html.Div([
            html.Div(id="config-modal", children=[
                html.Div([
                    html.H2("Edit Configuration"),
                    html.Label("End Date (YYYY-MM-DD):"),
                    dcc.Input(id="end-date-input", type="text", value=self.config_manager.end_date.strftime('%Y-%m-%d') if self.config_manager.end_date else ""),
                    html.Label("Weekly Study Hours:"),
                    dcc.Input(id="weekly-hours-input", type="number", value=self.config_manager.weekly_hours),
                    html.Label("Maximum Courses:"),
                    dcc.Input(id="max-courses-input", type="number", value=self.config_manager.max_courses),
                    html.Label("Hours per Course:"),
                    dcc.Input(id="hours-per-course-input", type="number", value=self.config_manager.hours_per_course, step=0.1),
                    html.Button("Save", id="save-config-button", style={'margin-top': '10px'}),
                    html.Button("Close", id="close-config-button", style={'margin-top': '10px'}),
                    html.Div(id="config-save-output", style={'margin-top': '10px'})
                ], style={'padding': '20px', 'border': '1px solid black', 'backgroundColor': 'white', 'width': '300px', 'margin': 'auto'}),
            ], style={'display': 'none', 'position': 'fixed', 'top': '50%', 'left': '50%', 'transform': 'translate(-50%, -50%)', 'background': 'rgba(0,0,0,0.6)', 'padding': '20px'})
        ])

    def update_dashboard(self, n_clicks_complete, n_clicks_save, n_clicks_edit, n_clicks_close, n_intervals, modal_visible, end_date, weekly_hours, max_courses, hours_per_course):
        ctx = dash.callback_context
        status = self.progress_calculator.check_schedule_status()
        figure = self.create_circle_figure()
        message = ""
        study_status_circle = ""

        # Retrieve completion data for display below the chart
        completed_courses = self.config_manager.max_courses - self.config_manager.remaining_courses
        completed_text = f"{completed_courses}/{self.config_manager.max_courses} Courses Completed"

        # Control modal visibility
        modal_style = {'display': 'block' if modal_visible else 'none'}

        # Handle Complete Course button click
        if ctx.triggered and "complete-course-button" in ctx.triggered[0]['prop_id']:
            self.course_manager.complete_course()
            status = self.progress_calculator.check_schedule_status()

        # Handle Save button click for configuration
        if ctx.triggered and "save-config-button" in ctx.triggered[0]['prop_id']:
            if end_date and weekly_hours and max_courses and hours_per_course:
                try:
                    self.config_manager.edit_config(end_date, int(weekly_hours), int(max_courses), float(hours_per_course))
                    message = "Configuration saved successfully."
                except ValueError:
                    message = "Error: Invalid input values."

        estimated_end = self.progress_calculator.calculate_estimated_end_date()
        if estimated_end and self.config_manager.end_date:
            status = self.progress_calculator.check_schedule_status()
            study_status_circle = html.Div(style={
                'width': '30px', 'height': '30px', 'borderRadius': '50%',
                'backgroundColor': 'green' if estimated_end <= self.config_manager.end_date else 'red'
            })

        return status, figure, completed_text, message, study_status_circle, modal_style

    def toggle_modal_visibility(self, n_clicks_edit, n_clicks_save, n_clicks_close, modal_visible):
        ctx = dash.callback_context
        if ctx.triggered:
            trigger = ctx.triggered[0]['prop_id']
            if "edit-config-button" in trigger:
                return True
            elif "save-config-button" in trigger or "close-config-button" in trigger:
                return False
        return modal_visible

    def create_circle_figure(self):
        completed_courses = self.config_manager.max_courses - self.config_manager.remaining_courses
        remaining_courses = self.config_manager.remaining_courses

        figure = go.Figure(data=[go.Pie(
            labels=['Completed Courses', 'Remaining Courses'],
            values=[completed_courses, remaining_courses],
            marker=dict(colors=['green', 'grey']),
            hole=0.4
        )])
        figure.update_layout(title='Course Completion Status')
        return figure

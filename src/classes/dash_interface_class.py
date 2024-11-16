import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from .config_manager_class import ConfigManager
from .course_manager_class import CourseManager
from .progress_calculator_class import ProgressCalculator

class DashInterface:
    """
    DashInterface initializes and manages a Dash web application for visualizing and managing study progress.
      
    Attributes:
        config_manager (ConfigManager): Manages configuration settings for the application.
        course_manager (CourseManager): Manages course data and progress.
        progress_calculator (ProgressCalculator): Calculates and tracks progress statistics.
    """
    def __init__(self):
        """
        Initializes the DashInterface, setting up the configuration, course management, 
        and progress tracking systems. Configures the Dash app and renders the dashboard.
        """
        self.config_manager = ConfigManager()
        self.course_manager = CourseManager(self.config_manager)
        self.progress_calculator = ProgressCalculator(self.config_manager, self.course_manager)
        self.app = dash.Dash()
        self.render_dashboard()

    def render_dashboard(self):
        """
        Configures the layout and callbacks of the Dash application.

        Sets up the dashboard structure, initializes UI elements, and binds callbacks 
        for interactivity and data updates.
        """
        self.app.layout = html.Div([
            html.H1("Study Dashboard", style={'text-align': 'center'}),
            dcc.Store(id="modal-visible", data=False),

            html.Div([
                html.Div([
                    dcc.Graph(id="circle-visualization", style={'width': '100%'}),
                    html.Div(id="study-status-circle", style={'text-align': 'center'}),
                    html.Div(id="schedule-status", style={'text-align': 'center', 'font-size': '1.2rem', 'margin-top': '-25px'})
                ], style={'width': '50%', 'float': 'left'}),

                html.Div([
                    # Insert configuration display above the buttons
                    html.Div(id="config-data", style={'text-align': 'center'}),

                    # Page buttons
                    html.Button("Kurs abschließen", id="complete-course-button", className="page-buttons"),
                    html.Button("Konfiguration Speichern und Editieren", id="edit-config-button", className="page-buttons"),
                    self.open_config_editor()
                ], style={'width': '40%', 'float': 'right', 'text-align': 'center'}),
            ], style={'width': '80%', 'margin': 'auto', 'display': 'flex', 'justify-content': 'space-between'}),

            dcc.Interval(id='interval-component', interval=1 * 1000, n_intervals=0)
        ])

        self.app.callback(
            Output("schedule-status", "children"),
            Output("config-data", "children"),
            Output("circle-visualization", "figure"),
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
        """
        Creates a modal for editing the configuration settings.

        Returns:
            html.Div: A Dash HTML Div containing the configuration editor modal.
        """
        return html.Div([
            html.Div(id="config-modal", children=[
                html.Div([
                    html.H2("Konfiguration", style={'text-align': 'center', 'color': '#333', 'margin-bottom': '20px'}),
                    
                    html.Label("Abschluss Datum vom Studienvertrag (YYYY-MM-DD):", style={'font-weight': 'bold', 'margin-top': '15px'}),
                    dcc.Input(id="end-date-input", type="text", value=self.config_manager.end_date.strftime('%Y-%m-%d') if self.config_manager.end_date else "", style={'width': '100%', 'padding': '8px', 'border': '1px solid #ddd', 'border-radius': '5px', 'margin-top': '8px'}),

                    html.Label("Wöchentlich verfügbare Stunden für das Studium:", style={'font-weight': 'bold', 'margin-top': '15px'}),
                    dcc.Input(id="weekly-hours-input", type="number", value=self.config_manager.weekly_hours, style={'width': '100%', 'padding': '8px', 'border': '1px solid #ddd', 'border-radius': '5px', 'margin-top': '8px'}),

                    html.Label("Maximum Anzahl an Kurse (zb. Bachelor = 35):", style={'font-weight': 'bold', 'margin-top': '15px'}),
                    dcc.Input(id="max-courses-input", type="number", value=self.config_manager.max_courses, style={'width': '100%', 'padding': '8px', 'border': '1px solid #ddd', 'border-radius': '5px', 'margin-top': '8px'}),

                    html.Label("Stunden die pro Modul gebraucht werden:", style={'font-weight': 'bold', 'margin-top': '15px'}),
                    dcc.Input(id="hours-per-course-input", type="number", value=self.config_manager.hours_per_course, step=0.1, style={'width': '100%', 'padding': '8px', 'border': '1px solid #ddd', 'border-radius': '5px', 'margin-top': '8px'}),

                    html.Div([
                        html.Button("Speichern", id="save-config-button", style={
                            'background-color': '#28a745', 'color': 'white', 'padding': '10px 20px', 'border': 'none', 'border-radius': '5px', 'cursor': 'pointer', 'margin-top': '20px'
                        }),
                        html.Button("Schließen", id="close-config-button", style={
                            'background-color': '#dc3545', 'color': 'white', 'padding': '10px 20px', 'border': 'none', 'border-radius': '5px', 'cursor': 'pointer', 'margin-top': '20px', 'margin-left': '10px'
                        })
                    ], style={'display': 'flex', 'justify-content': 'center', 'gap': '10px'}),
                    
                    html.Div(id="config-save-output", style={'margin-top': '10px', 'text-align': 'center', 'font-size': '1.2rem', 'color': 'green'})
                ], style={
                    'padding': '30px', 'border-radius': '10px', 'background-color': 'white', 'width': '400px', 'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.2)', 'text-align': 'left'
                }),
            ], style={'display': 'none', 'position': 'fixed', 'top': '50%', 'left': '50%', 'transform': 'translate(-50%, -50%)', 'background': 'rgba(0, 0, 0, 0.5)', 'padding': '10px', 'z-index': 1000})
        ])

    def update_dashboard(self, n_clicks_complete, n_clicks_save, n_clicks_edit, n_clicks_close, n_intervals, modal_visible, end_date, weekly_hours, max_courses, hours_per_course):
      """
      Updates the dashboard based on user interactions and configuration changes.

      Args:
            n_clicks_complete (int): Number of times the complete course button was clicked.
            n_clicks_save (int): Number of times the save config button was clicked.
            n_clicks_edit (int): Number of times the edit config button was clicked.
            n_clicks_close (int): Number of times the close config button was clicked.
            n_intervals (int): Number of intervals passed since the app started.
            modal_visible (bool): Whether the config modal is visible.
            end_date (str): The end date of the study contract.
            weekly_hours (int): Weekly hours available for study.
            max_courses (int): Maximum number of courses.
            hours_per_course (float): Hours required per course.

      Returns:
            tuple: Updated status, configuration data, circle visualization figure, 
            message, study status circle, and modal style.
      """
      ctx = dash.callback_context
      status = self.progress_calculator.check_schedule_status()
      figure = self.create_circle_figure()
      message = ""
      study_status_circle = ""
  
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
                  message = "Konfiguration erfolgreich gespeichert."
                  self.config_manager.load_config()  # Reload configuration
              except ValueError:
                  message = "Error: Konfiguration konnte nicht gespeichert werden."
  
      estimated_end = self.progress_calculator.calculate_estimated_end_date()
      if estimated_end and self.config_manager.end_date:
          status = self.progress_calculator.check_schedule_status()
          study_status_circle = html.Div(style={
              'width': '30px', 'height': '30px', 'borderRadius': '50%',
              'backgroundColor': 'green' if estimated_end <= self.config_manager.end_date else 'red'
          })
         
          config_data = html.Div([
            html.Div(f"Enddatum: {self.config_manager.end_date}", style={'margin-bottom': '10px'}),
            html.Div(f"Wöchentlich verfügbare Stunden für das Studium: {self.config_manager.weekly_hours}", style={'margin-bottom': '10px'}),
            html.Div(f"Maximum Anzahl an Kurse : {self.config_manager.max_courses}", style={'margin-bottom': '10px'}),
            html.Div(f"Stunden pro Kurs: {self.config_manager.hours_per_course}", style={'margin-bottom': '10px'}),
          ], style={'text-align': 'center', 'padding': '10px', 'border': '1px solid #ddd', 'border-radius': '5px', 'background-color': '#f9f9f9'})
  
      return status, config_data, figure, message, study_status_circle, modal_style

    def toggle_modal_visibility(self, n_clicks_edit, n_clicks_save, n_clicks_close, modal_visible):
        """
        Toggles the visibility of the configuration modal based on user interactions.

        Args:
            n_clicks_edit (int): Number of times the edit config button was clicked.
            n_clicks_save (int): Number of times the save config button was clicked.
            n_clicks_close (int): Number of times the close config button was clicked.
            modal_visible (bool): Current modal visibility state.

        Returns:
            bool: Updated modal visibility state.
        """
        ctx = dash.callback_context
        if ctx.triggered:
            trigger = ctx.triggered[0]['prop_id']
            if "edit-config-button" in trigger:
                return True
            elif "save-config-button" in trigger or "close-config-button" in trigger:
                return False
        return modal_visible

    def create_circle_figure(self):
        """
        Creates a pie chart visualization for completed and remaining courses.

        Returns:
            plotly.graph_objs.Figure: A Plotly figure object representing the pie chart.
        """
        completed_courses = self.config_manager.max_courses - self.config_manager.remaining_courses
        remaining_courses = self.config_manager.remaining_courses

        # Create the pie chart figure
        figure = go.Figure(data=[go.Pie(
            labels=['Abgeschlossene Kurse', 'Offene Kurse'],
            values=[completed_courses, remaining_courses],
            marker=dict(colors=['green', 'grey']),
            hole=0.4
        )])

        # Add the text annotation in the center of the pie chart
        figure.update_layout(
            title='Status der Kursabschlüsse',
            annotations=[
                dict(
                    x=0.5,
                    y=0.5,
                    text=f"<b><span style='color:green'>{completed_courses}</span>/<span style='color:gray'>{self.config_manager.max_courses}</span></b>",
                    font=dict(size=16, color="black"),
                    showarrow=False,
                    align="center"
                )
            ]
        )
        return figure

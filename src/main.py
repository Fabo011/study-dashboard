from classes.dash_interface_class import DashInterface

if __name__ == "__main__":
    dash_app = DashInterface()
    dash_app.app.run_server(debug=True)

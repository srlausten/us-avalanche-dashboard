from avalanche_dashboard.dashboard import create_dashboard
from avalanche_dashboard.fetch_data import fetch_avy_data
from avalanche_dashboard.parse_data import fill_latlon
df = fetch_avy_data()
df = fill_latlon(df)

if __name__ == '__main__':
    dashboard = create_dashboard(df)
    dashboard.show()
    dashboard.servable()

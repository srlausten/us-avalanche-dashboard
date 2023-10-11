import pandas as pd
import plotly.express as px
import panel as pn
from panel.widgets import DateSlider, DateRangeSlider
import panel as pn
import plotly.io as pio
from statsmodels.tsa.arima.model import ARIMA
import plotly.graph_objects as go


# Set Plotly's default template to dark mode
pio.templates.default = 'plotly_dark'

pn.extension()
pn.config.theme = 'dark'
title = "# US Avalanche Data Dashboard"
title_pane = pn.pane.Markdown(title, width=800, align='start')



def create_dashboard(df):
    min_date = df['Date'].min()
    max_date = df['Date'].max()

    # Creating CheckBoxGroup with dark background
    unique_activities = df['PrimaryActivity'].unique().tolist()
    activity_checkbox = pn.widgets.CheckBoxGroup(name='Select Activities', value=unique_activities, options=unique_activities)

    # DateRangeSlider with dark background
    date_slider = pn.widgets.DateRangeSlider(name='Date Range', value=(min_date, max_date), start=min_date, end=max_date)

    # Initially plotting with the entire range of dates and all activities
    initial_date_range = date_slider.value
    initial_prev_zoom = 2
    initial_map_fig = create_map_viz(df, initial_date_range, initial_prev_zoom, activity_checkbox.value)
    initial_hist_fig = create_histogram(df, initial_date_range, activity_checkbox.value)
    initial_heatmap_fig = create_heatmap(df, initial_date_range, initial_prev_zoom, activity_checkbox.value)
    initial_time_series_fig = create_time_series(df, initial_date_range, activity_checkbox.value)


    # Wrap initial Plotly Figures in Panel's Plotly panes with dark background
    map_pane = pn.pane.Plotly(initial_map_fig)
    hist_pane = pn.pane.Plotly(initial_hist_fig)
    heat_map_pane = pn.pane.Plotly(initial_heatmap_fig)
    time_series_pane = pn.pane.Plotly(initial_time_series_fig)

    def update_plots(event):
        selected_date_range = date_slider.value
        selected_activities = activity_checkbox.value
        prev_zoom = map_pane.object.layout.mapbox.zoom if hasattr(map_pane.object, 'layout') else initial_prev_zoom
        new_map_fig = create_map_viz(df, selected_date_range, prev_zoom, selected_activities)
        new_hist_fig = create_histogram(df, selected_date_range, selected_activities)
        new_heatmap_fig = create_heatmap(df, selected_date_range, prev_zoom, selected_activities)
        new_time_series_fig = create_time_series(df, selected_date_range, selected_activities)


        map_pane.object = new_map_fig
        hist_pane.object = new_hist_fig
        heat_map_pane.object = new_heatmap_fig
        time_series_pane.object = new_time_series_fig

    # Set up callbacks
    date_slider.param.watch(update_plots, 'value')
    activity_checkbox.param.watch(update_plots, 'value')

    sidebar = pn.Column(activity_checkbox, date_slider)
    
    map_row = pn.Row(map_pane, heat_map_pane)
    histogram_row = pn.Row(hist_pane, time_series_pane)  # Assuming barplot_pane is another plot you want to display
    
    plots_column = pn.Column(map_row, histogram_row)  # Nesting the rows of plots within a column
    main_row = pn.Row(sidebar, plots_column)  # Placing the sidebar and the plots column within a row
    forecasted_data = create_forecast_df(df)
    predictive_modeling_tab = pn.pane.Plotly(create_forecast_plot(forecasted_data, forecasted_data['Date'].min(), forecasted_data['Date'].max()))

    # Tabs
    data_analysis_tab = pn.Column(title_pane, main_row)

    
    tabs = pn.Tabs(("Data Analysis", data_analysis_tab), ("Predictive Modeling", predictive_modeling_tab))
    
    return tabs

def create_time_series(df, selected_date_range, selected_activities):
    start_date, end_date = pd.to_datetime(selected_date_range[0]), pd.to_datetime(selected_date_range[1])
    filtered_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date) & (df['PrimaryActivity'].isin(selected_activities))]
    
    # Example of aggregation by date; adjust as needed
    time_series_data = filtered_data.groupby('Date').agg({'Killed':'sum'}).reset_index()
    
    time_series_fig = px.line(time_series_data, x='Date', y='Killed', title='Avalanche Fatalities Over Time')
    return time_series_fig

def create_map_viz(df, selected_date_range, prev_zoom, selected_activities):
    start_date, end_date = pd.to_datetime(selected_date_range[0]), pd.to_datetime(selected_date_range[1])
    filtered_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date) & (df['PrimaryActivity'].isin(selected_activities))]
    filtered_data['Date'] = filtered_data['Date'].dt.strftime('%a, %d %b %Y')
    map_fig = px.scatter_mapbox(filtered_data, lat='lat', lon='lon', hover_data=['Location', 'Date'],
                                mapbox_style="open-street-map", title="Accident Map")
    map_fig.update_layout(mapbox=dict(center=dict(lat=39.76, lon=-105.02), zoom=prev_zoom))
    return map_fig

def create_heatmap(df, selected_date_range, prev_zoom, selected_activities):
    start_date, end_date = pd.to_datetime(selected_date_range[0]), pd.to_datetime(selected_date_range[1])
    filtered_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date) & (df['PrimaryActivity'].isin(selected_activities))]
    heatmap_fig = px.density_mapbox(filtered_data, lat='lat', lon='lon', z='Killed',
                                   radius=10, center=dict(lat=39.76, lon=-105.02), zoom=2,
                                   mapbox_style="open-street-map", title="Accident Heatmap")
    return heatmap_fig


def create_histogram(df, selected_date_range, selected_activities):
    start_date, end_date = pd.to_datetime(selected_date_range[0]), pd.to_datetime(selected_date_range[1])
    filtered_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date) & (df['PrimaryActivity'].isin(selected_activities))]
    hist_fig = px.histogram(filtered_data, x='MM', title="Monthly Accident Histogram")
    hist_fig.update_layout(xaxis_title="Month", xaxis=dict(tickmode='array', tickvals=list(range(1, 13))))
    return hist_fig



def create_forecast_df(df):
    """
    Generate forecasted avalanche counts using ARIMA.
    """
    # Aggregate data by month
    monthly_counts = df.resample('M', on='Date').size()
    monthly_counts_df = monthly_counts.reset_index()
    monthly_counts_df.columns = ['Date', 'Avalanche_Count']

    # Fit ARIMA model
    model_arima = ARIMA(monthly_counts_df['Avalanche_Count'], order=(5,1,0))
    model_fit = model_arima.fit()

    # Predict next 12 months
    forecast_result = model_fit.get_forecast(steps=12)
    forecast = forecast_result.predicted_mean
    conf_int = forecast_result.conf_int()

    # Generate forecast dates
    forecast_dates = pd.date_range(monthly_counts_df['Date'].iloc[-1] + pd.DateOffset(months=1), periods=12, freq='M')

    # Combine the forecast with the actual data
    forecast_df = pd.DataFrame({
        'Date': forecast_dates,
        'Forecast': forecast,
        'Lower_Bound': conf_int.iloc[:, 0],
        'Upper_Bound': conf_int.iloc[:, 1]
    })
    combined_df = pd.concat([monthly_counts_df, forecast_df], ignore_index=True)
    return combined_df

def create_forecast_plot(df, start_date, end_date):
    """
    Creates a plotly graph showing the actual vs. forecasted avalanche counts.
    """
    mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
    filtered_data = df[mask]
    
    fig = go.Figure()
    
    # Plotting actual data
    fig.add_trace(go.Scatter(x=filtered_data['Date'], y=filtered_data['Avalanche_Count'], 
                             mode='lines', name='Actual Counts'))

    # Plotting forecasted data
    fig.add_trace(go.Scatter(x=filtered_data['Date'], y=filtered_data['Forecast'], 
                             mode='lines', name='Forecasted Counts'))

    # Adding confidence interval
    fig.add_trace(go.Scatter(x=filtered_data['Date'], y=filtered_data['Upper_Bound'], 
                             mode='lines', name='Upper Bound', line=dict(dash='dash')))
    fig.add_trace(go.Scatter(x=filtered_data['Date'], y=filtered_data['Lower_Bound'], 
                             mode='lines', name='Lower Bound', line=dict(dash='dash')))
    
    fig.update_layout(title='Actual vs Forecasted Avalanche Counts')
    return fig

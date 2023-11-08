import pandas as pd
import dash
from dash import html, dcc, callback, Output, Input
import dash_ag_grid as dag
import plotly.express as px
import dash_chart_editor as dce
import utils

# Load and preprocess the dataset (loading only selected columns to optimize performance)
columns_needed = ['country', 'year', 'primary_energy_consumption', 'renewables_consumption']
df = pd.read_csv('data/owid-energy-data.csv', usecols=columns_needed)



# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    # New dropdown to select the filter category (countries, continents, etc.)
    dcc.Dropdown(
        id='country-filter',
        options=[{'label': k, 'value': k} for k in utils.filter_options.keys()],
        value='Countries',  # default value
        clearable=False,
        style={"width": "50%"}  # You can adjust the style as needed
    ),
    # Refactored dropdown for category selection based on the filter above
    dcc.Dropdown(
        id='category-dropdown',
        clearable=False,
        style={"width": "50%"}  # You can adjust the style as needed
    ),
    # Range Slider for Year selection
    dcc.RangeSlider(
        id='year-slider',
        min=df['year'].min(),
        max=df['year'].max(),
        value=[df['year'].min(), df['year'].max()],  # Default range
        marks={str(year): str(year) for year in range(df['year'].min(), df['year'].max()+1, 10)},  # Marks for years
        step=1  # Year steps
    ),
    # AG Grid component to display the data
    dag.AgGrid(
        id='my_ag_grid',
        rowData=df.to_dict('records'),
        columnDefs=[{'field': c} for c in df.columns],
        dashGridOptions={
            'pagination': True,
            'paginationPageSize': 20,
        },
    ),
    # Graph component to display the chart
    dcc.Graph(id='energy-chart'),
    # Dash Chart Editor component
    html.H4("Interactive Chart Editor"),
    dce.DashChartEditor(
        id='chart-editor',
        dataSources=df.to_dict("list"),
    )
])

# Callback for updating category dropdown based on country filter selection
@callback(
    Output('category-dropdown', 'options'),
    Output('category-dropdown', 'value'),
    Input('country-filter', 'value')
)
def set_category_options(selected_filter):
    # Update the options in category dropdown based on selected filter
    categories = utils.filter_options[selected_filter]
    options = [{'label': category, 'value': category} for category in categories]
    value = options[0]['value'] if options else None
    return options, value

# Callback for updating AG Grid, Chart, and Chart Editor based on category dropdown and slider
@callback(
    [Output('my_ag_grid', 'rowData'),
     Output('energy-chart', 'figure'),
     Output('chart-editor', 'dataSources')],  # Add this line to update the data sources of the chart editor
    [Input('category-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_output(selected_category, selected_years):
    # Handle case when selected_category is None
    if not selected_category:
        raise dash.exceptions.PreventUpdate
    
    # Filter the dataframe based on the inputs
    filtered_df = df[(df['country'] == selected_category) & 
                     (df['year'] >= selected_years[0]) & 
                     (df['year'] <= selected_years[1])]
    
    # Update the AG Grid data
    grid_data = filtered_df.to_dict('records')
    
    # Create a line chart for primary energy consumption over selected years
    fig = px.line(
        filtered_df,
        x='year',
        y='primary_energy_consumption',
        title=f'Primary Energy Consumption in {selected_category}'
    )
    
    # Update the data sources for the chart editor
    chart_data_sources = filtered_df.to_dict("list")
    
    # Return the updated data, figure, and data sources for the chart editor
    return grid_data, fig, chart_data_sources

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

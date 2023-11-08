import pandas as pd
import dash
from dash import html, dcc, callback, Output, Input
import dash_ag_grid as dag
import plotly.express as px
import dash_chart_editor as dce
from utils import filter_options

# Load and preprocess the dataset (loading only selected columns to optimize performance)
columns_needed = ['country', 'year', 'primary_energy_consumption', 'renewables_consumption']
df = pd.read_csv('data/owid-energy-data.csv', usecols=columns_needed)

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    # Dropdown to select the filter category (countries, continents, etc.)
    dcc.Dropdown(
        id='category-dropdown',
        options=[{'label': k, 'value': k} for k in filter_options.keys()],
        value='Countries',  # default value
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
        columnDefs=[
            {'field': c, 'filter': 'agTextColumnFilter', 'floatingFilter': True}
            for c in df.columns
        ],
        defaultColDef={
            'filter': True,  # Enable filters for all columns
            'sortable': True,  # Enable sorting for all columns
        },
        dashGridOptions={
            'pagination': True,
            'paginationPageSize': 20,
            'enableFilter': True,  # Turn on filtering
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

# Callback for updating AG Grid, Chart, and Chart Editor based on category dropdown and slider
@callback(
    [Output('my_ag_grid', 'rowData'),
     Output('energy-chart', 'figure'),
     Output('chart-editor', 'dataSources')],  # Update the data sources of the chart editor
    [Input('category-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_output(selected_category, selected_years):
    # Handle case when selected_category is None
    if not selected_category:
        raise dash.exceptions.PreventUpdate
    
    # Determine the filter list based on the selected category
    filter_list = filter_options.get(selected_category, [])

    # Filter the dataframe based on the selected years and category list
    filtered_df = df[(df['country'].isin(filter_list)) & 
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

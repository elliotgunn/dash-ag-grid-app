import pandas as pd
import dash
from dash import html, dcc, callback, Output, Input
import dash_ag_grid as dag
import plotly.express as px
import dash_chart_editor as dce

# Load and preprocess the dataset (loading only selected columns to optimize performance)
columns_needed = ['country', 'year', 'primary_energy_consumption', 'renewables_consumption']
df = pd.read_csv('data/owid-energy-data.csv', usecols=columns_needed)

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    # Dropdown for Country selection
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': country, 'value': country} for country in df['country'].unique()],
        value='World',  # Set a default value or you can leave it as None for no selection
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

# Callback for updating AG Grid and Chart based on dropdown and slider
@callback(
    [Output('my_ag_grid', 'rowData'),
     Output('energy-chart', 'figure')],
    [Input('country-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_output(selected_country, selected_years):
    # Filter the dataframe based on the inputs
    filtered_df = df[(df['country'] == selected_country) & 
                     (df['year'] >= selected_years[0]) & 
                     (df['year'] <= selected_years[1])]
    
    # Update the AG Grid data
    grid_data = filtered_df.to_dict('records')
    
    # Create a line chart for primary energy consumption over selected years
    fig = px.line(
        filtered_df,
        x='year',
        y='primary_energy_consumption',
        title=f'Primary Energy Consumption in {selected_country}'
    )
    
    # Update the layout or add more customization to the chart here if needed
    
    return grid_data, fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

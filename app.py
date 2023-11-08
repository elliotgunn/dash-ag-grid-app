import pandas as pd
import dash
from dash import html, dcc, callback, Output, Input, State, ctx
import dash_ag_grid as dag
import plotly.express as px
import dash_chart_editor as dce
from utils import filter_options
import dash_bootstrap_components as dbc

# Load and preprocess the dataset (loading only selected columns to optimize performance)
columns_needed = ['country', 'year', 'primary_energy_consumption', 'renewables_consumption']
df = pd.read_csv('data/owid-energy-data.csv', usecols=columns_needed)

# Initialize the Dash app with Bootstrap CSS
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout of the app using Bootstrap components
app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            dbc.Col(
                html.H1("Global Energy Dashboard: Tracking Consumption and Renewables",
                        className="text-center mt-4 mb-4"),  # Center align and margin top and bottom
                width=12
            )
        ),
        # First row with dropdown and slider on the left, and AG Grid on the right
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id='category-dropdown',
                            options=[{'label': k, 'value': k} for k in filter_options.keys()],
                            value='Countries',
                            clearable=False,
                        ),
                        dcc.RangeSlider(
                            id='year-slider',
                            min=df['year'].min(),
                            max=df['year'].max(),
                            value=[df['year'].min(), df['year'].max()],
                            marks={str(year): str(year) for year in range(df['year'].min(), df['year'].max()+1, 10)},
                            step=1,
                        ),
                    ],
                    md=4,  # Adjust the size for medium screens and up
                ),
                dbc.Col(
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
                    md=8,
                ),
            ]
        ),
        # Second row for charts
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id='energy-chart'),
                    md=6,
                ),
                dbc.Col(
                    [
                        html.H4("Interactive Chart Editor", className="mt-3 mb-3"),  # Added margin top and bottom for spacing
                        dce.DashChartEditor(id='chart-editor', dataSources=df.to_dict("list")),
                    ],
                    md=6,
                ),
            ]
        ),
    ],
)

# Combined callback for updating AG Grid, Chart, and Chart Editor based on category dropdown, slider, and AG Grid filtering
@callback(
    [Output('my_ag_grid', 'rowData'),
     Output('energy-chart', 'figure'),
     Output('chart-editor', 'dataSources')],
    [Input('category-dropdown', 'value'),
     Input('year-slider', 'value'),
     Input('my_ag_grid', 'filterModel')],
    [State('my_ag_grid', 'rowData')]
)
def update_output_and_chart(selected_category, selected_years, filter_model, row_data):
    # Use ctx to determine which input was triggered
    triggered_id = ctx.triggered_id

    # Initialize the dataframe
    filtered_df = df.copy()

    # If the AG Grid filter was triggered, apply filters to the DataFrame
    if triggered_id == 'my_ag_grid':
        # Convert the current AG Grid row data into a DataFrame
        filtered_df = pd.DataFrame(row_data)

        # Apply the filters to the dataframe
        # You'll need to customize this part to match the structure of your 'filterModel'
        for col, f in filter_model.items():
            if 'filter' in f:
                filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(f['filter'])]

    # If the category dropdown or year slider was triggered, filter based on those
    else:
        # Determine the filter list based on the selected category
        filter_list = filter_options.get(selected_category, [])

        # Filter the dataframe based on the selected years and category list
        filtered_df = filtered_df[(filtered_df['country'].isin(filter_list)) & 
                                  (filtered_df['year'] >= selected_years[0]) & 
                                  (filtered_df['year'] <= selected_years[1])]

    # Update the AG Grid data
    grid_data = filtered_df.to_dict('records')
    
    # Create the updated chart with the filtered data
    fig = px.line(
        filtered_df,
        x='year',
        y='primary_energy_consumption',
        title=f'Primary Energy Consumption {("for " + selected_category) if triggered_id != "my_ag_grid" else "(Filtered by AG Grid)"}'
    )
    
    # Update the data sources for the chart editor
    chart_data_sources = filtered_df.to_dict("list")
    
    # Return the updated data, figure, and data sources for the chart editor
    return grid_data, fig, chart_data_sources

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)




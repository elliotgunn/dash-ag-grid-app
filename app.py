import pandas as pd
import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import dash_ag_grid as dag

# Load and preprocess the dataset
df = pd.read_csv('data/owid-energy-data.csv')

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    dag.AgGrid(
        id='my_ag_grid',
        rowData=df.to_dict('records'),
        columnDefs=[{'field': c} for c in df.columns],
        dashGridOptions={
            'pagination': True,
            'paginationPageSize': 20,
        }
    )
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

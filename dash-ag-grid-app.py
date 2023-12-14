import pandas as pd
import dash
from dash import html, dcc, callback, Output, Input, State, ctx
import dash_ag_grid as dag
import plotly.express as px
from utils import filter_options
import dash_bootstrap_components as dbc

# Load and preprocess the dataset
columns_needed = [
    "country",
    "year",
    "primary_energy_consumption",
    "renewables_consumption",
]
df = pd.read_csv("data/owid-energy-data.csv", usecols=columns_needed)

# Initialize the Dash app with Bootstrap CSS
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout of the app using Bootstrap components
app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            dbc.Col(
                html.H1(
                    "Global Energy Dashboard: Tracking Consumption and Renewables",
                    className="text-center mt-4 mb-4",
                ),  # Center align and margin top and bottom
                width=12,
            )
        ),
        # Dropdown and Range Slider row
        dbc.Row(
            dbc.Col(
                [
                    dcc.Dropdown(
                        id="category-dropdown",
                        options=[
                            {"label": k, "value": k} for k in filter_options.keys()
                        ],
                        value="Countries",
                        clearable=False,
                        className="mb-3",  # Margin bottom for spacing
                    ),
                    dcc.RangeSlider(
                        id="year-slider",
                        min=df["year"].min(),
                        max=df["year"].max(),
                        value=[1965, df["year"].max()],
                        marks={
                            str(year): str(year)
                            for year in range(
                                df["year"].min(), df["year"].max() + 1, 10
                            )
                        },
                        step=1,
                    ),
                ],
                md=6,
                lg=4,  # Adjust the size for medium and large screens
                className="mx-auto",  # Center align the column
            )
        ),
        # Chart and Table row
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id="energy-chart"),
                    md=6,  # Half width for medium screens and up
                ),
                dbc.Col(
                    dag.AgGrid(
                        id="my_ag_grid",
                        rowData=df.to_dict("records"),
                        columnDefs=[
                            {
                                "field": c,
                                "filter": "agNumberColumnFilter" if c in ["year", "primary_energy_consumption", "renewables_consumption"] else "agTextColumnFilter",
                                "floatingFilter": True,
                                "resizable": True,
                                "sortable": True,
                                "editable": True
                            }
                            for c in df.columns
                        ],
                        defaultColDef={
                            "filter": True,
                            "sortable": True,
                        },
                        dashGridOptions={
                            "pagination": True,
                            "paginationPageSize": 20,
                            "enableFilter": True,
                        },
                    ),
                    md=6,  # Half width for medium screens and up
                ),
            ]
        ),
    ],
)

# Combined callback for updating AG Grid and Chart based on category dropdown, slider, and AG Grid filtering
@callback(
    [Output("my_ag_grid", "rowData"), Output("energy-chart", "figure")],
    [
        Input("category-dropdown", "value"),
        Input("year-slider", "value"),
        Input("my_ag_grid", "filterModel"),
    ],
)
def update_output_and_chart(selected_category, selected_years, filter_model):
    # Initialize the dataframe
    filtered_df = df.copy()

    # Check if the selected years have been set, otherwise set to default range
    if not selected_years:
        selected_years = [df["year"].min(), df["year"].max()]

    # Determine the filter list based on the selected category
    filter_list = filter_options.get(selected_category, [])

    # Apply filters based on dropdown and slider selections
    filtered_df = filtered_df[
        (filtered_df["country"].isin(filter_list))
        & (filtered_df["year"] >= selected_years[0])
        & (filtered_df["year"] <= selected_years[1])
    ]

    # Apply AG Grid filter if available
    if filter_model:
        for col, f in filter_model.items():
            if "filter" in f:
                filtered_df = filtered_df[
                    filtered_df[col].astype(str).str.contains(f["filter"])
                ]

    # Sort the DataFrame first by 'country' and then by 'year' in descending order
    filtered_df.sort_values(
        by=["country", "year"], ascending=[True, False], inplace=True
    )

    # Update the AG Grid data
    grid_data = filtered_df.to_dict("records")

    # Create the updated chart with the filtered data
    fig = px.line(
        filtered_df,
        x="year",
        y="primary_energy_consumption",
        title=f"Primary Energy Consumption for {selected_category}",
    )

    # Set the default x-axis to start at 1960
    fig.update_layout(xaxis_range=[1960, df["year"].max()])

    # Return the updated data and figure
    return grid_data, fig

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)

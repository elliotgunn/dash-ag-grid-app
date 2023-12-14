import pandas as pd
import dash
from dash import html, dcc, callback, Output, Input
import plotly.express as px
from utils import filter_options
import dash_bootstrap_components as dbc
import dash_table

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
                ),
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
                        className="mb-3",
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
                lg=4,
                className="mx-auto",
            )
        ),
        # Chart and DataTable row
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id="energy-chart"),
                    md=6,
                ),
                dbc.Col(
                    dash_table.DataTable(
                        id="my_datatable",
                        columns=[{"name": i, "id": i} for i in df.columns],
                        data=df.to_dict("records"),
                        page_size=20,
                        filter_action="native",
                        sort_action="native",
                    ),
                    md=6,
                ),
            ]
        ),
    ],
)


# Combined callback for updating DataTable and Chart based on category dropdown, slider, and DataTable filtering
@callback(
    [Output("my_datatable", "data"), Output("energy-chart", "figure")],
    [
        Input("category-dropdown", "value"),
        Input("year-slider", "value"),
    ],
)
def update_output_and_chart(selected_category, selected_years):
    # Filter based on dropdown and slider selections
    filtered_df = df[
        (df["country"].isin(filter_options.get(selected_category, [])))
        & (df["year"] >= selected_years[0])
        & (df["year"] <= selected_years[1])
    ]

    # Sort the DataFrame first by 'country' and then by 'year' in descending order
    filtered_df.sort_values(
        by=["country", "year"], ascending=[True, False], inplace=True
    )

    # Create the updated chart with the filtered data
    fig = px.line(
        filtered_df,
        x="year",
        y="primary_energy_consumption",
        title=f"Primary Energy Consumption for {selected_category}",
    )
    fig.update_layout(xaxis_range=[1960, df["year"].max()])

    # Return the updated data and figure
    return filtered_df.to_dict("records"), fig


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)

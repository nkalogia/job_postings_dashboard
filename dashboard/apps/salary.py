from typing import Optional, Tuple

from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px

from app import app, cache
import utilities


dropdown = dcc.Dropdown(
    id={
        "type": "feature-dropdown",
        "index": "salary"
    },
    options=[
        {"label": "Technologies", "value": "technologies"},
        {"label": "Roles", "value": "roles"},
        {"label": "Skills", "value": "skills"},
        {"label": "Industries", "value": "industries"},
        {"label": "Types", "value": "types"},
        {"label": "Experience", "value": "experience"}
    ],
    placeholder="Select a feature"
)

slider = dcc.Slider(
    id={
        "type": "number-slider",
        "index": "salary"
    },
    tooltip={"placement": "bottom"}
)

preferences = html.Div(
    children=[
        dropdown,
        slider
    ],
    className="d-flex flex-column"
)


content = html.Div(
    children=[
        html.H1("Salary Marginal Distribution Plot", className="h2 border-bottom py-2 mb-3"),
        dcc.Loading(
            dcc.Graph(
                id={"type": "graph", "index": "max_salary"},
                figure=utilities.create_empty_figure("Select a feature in the preferences")
                # figure=go.Figure(
                #     empty_figure
                # )
            )
        ),
        html.P(
            "This is a scatter plot of the maximum salary mentioned for the selected categorical feature values "
            "colored by the location type, showing as well the marginal distribution of the salary for each location type."
        ),
        dcc.Loading(
            dcc.Graph(
                id={"type": "graph", "index": "min_salary"},
                figure=utilities.create_empty_figure("Select a feature in the preferences")
                # figure=go.Figure(
                #     empty_figure
                # )
            )
        ),
        html.P(
            "This is a scatter plot of the minimum salary mentioned for the selected categorical feature values "
            "colored by the location type, showing as well the marginal distribution of the salary for each location type."
        )
    ]
)


# Callbacks
@app.callback(Output({"type": "graph", "index": "min_salary"}, "figure"),
              Output({"type": "graph", "index": "max_salary"}, "figure"),
              Input({"type":"feature-dropdown", "index": "salary"}, "value"),
              Input({"type": "number-slider", "index": "salary"}, "value"),
              Input("date-range-picker", "start_date"),
              Input("date-range-picker", "end_date"))
def render_graph(feature: Optional[str],
                 n: Optional[int],
                 start_date: Optional[str],
                 end_date: Optional[str]) -> Tuple[go.Figure, go.Figure]:
    if n is None or feature is None:
        return (utilities.create_empty_figure("Select a feature in the preferences"),
                utilities.create_empty_figure("Select a feature in the preferences"))
    df = cache.get("dataframe")
    df = df.explode(feature)
    df = utilities.filter_on_period(df, "created", start_date, end_date)
    df = utilities.filter_on_frequency(df, feature, n)
    data_0 = df[[feature, "salary.minimum", "remote"]].explode("remote").dropna()
    data_1 = df[[feature, "salary.maximum", "remote"]].explode("remote").dropna()
    fig_0 = px.scatter(data_0, x="salary.minimum", y=feature, color="remote", marginal_x="box")
    fig_0.update_layout(
        xaxis_title_text=feature.capitalize(),
        yaxis_title_text="Minimum Salary",
        legend_title="Location type"
    )
    # fig_0.update_yaxes(
    #     title_text=feature.capitalize()
    # )
    # fig_0.update_xaxes(
    #     title_text="Minimum Salary"
    # )
    fig_1 = px.scatter(data_1, x="salary.maximum", y=feature, color="remote", marginal_x="box")
    fig_1.update_layout(
        xaxis_title_text=feature.capitalize(),
        yaxis_title_text="Maximum Salary",
        # yaxis_tickangle=-45,
        legend_title="Location type"
    )
    # fig_1.update_yaxes(title_text=feature.capitalize())
    # fig_1.update_xaxes(title_text="Maximum Salary")
    return fig_0, fig_1
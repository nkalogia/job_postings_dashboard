from typing import Optional
import json

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from app import app, cache
import utilities


feature_dropdown = dcc.Dropdown(
    id={
        "type": "feature-dropdown",
        "index": "heatmap"
    },
    options=[
        {"label": "Technologies", "value": "technologies"},
        {"label": "Roles", "value": "roles"},
        {"label": "Skills", "value": "skills"},
        {"label": "Industries", "value": "industries"},
        {"label": "Job Types", "value": "types"},
        {"label": "Experience", "value": "experience"}
    ],
    placeholder="Select a feature"
)

feature_slider = dcc.Slider(
    id={
        "type": "number-slider",
        "index": "heatmap"
    },
    tooltip={"placement": "bottom", "always_visible": False}
)

countries_slider = dcc.Slider(
    id={
        "type": "single-number-slider",
        "index": "country"
    },
    tooltip={"placement": "bottom", "always_visible": False}
)

preferences = html.Div(
    children=[
        html.Div(
            children=[
                feature_dropdown,
                feature_slider
            ],
            className="d-flex flex-column"
        ),
        html.Div(
            children=[
                html.Div("Number of countries"),
                countries_slider,
                dcc.Store(
                    id={"type": "store", "index": "country"},
                    data={"feature": "location.country_code"}
                )
            ],
            className="d-flex flex-column"
        )
    ],
    className="d-flex flex-column"
)

content = html.Div(
    children=[
        html.H1("Heatmap", className="h2 border-bottom py-2 mb-3"),
        dcc.Loading(
            dcc.Graph(
                id={"type": "graph", "index": "heatmap"},
                figure=utilities.create_empty_figure("Select a feature in the preferences")
            )
        ),
        html.P(
            "This heatmap shows the number of job postings where a value of the selected "
            "categorical feature was found in for a certain country"
        )
    ]
)


@app.callback(Output({"type": "graph", "index": "heatmap"}, "figure"),
              Input({"type": "feature-dropdown", "index": "heatmap"}, "value"),
              Input({"type": "number-slider", "index": "heatmap"}, "value"),
              Input({"type": "single-number-slider", "index": "country"}, "value"),
              Input("date-range-picker", "start_date"),
              Input("date-range-picker", "end_date"))
def render_heatmap(feature: Optional[str],
                   n_values: Optional[int],
                   n_countries: Optional[int],
                   start_date: Optional[str],
                   end_date: Optional[str]) -> dash.development.base_component.Component:
    if feature is None:
        return utilities.create_empty_figure("Select a feature in the preferences")
    df = cache.get("dataframe")
    df = utilities.filter_on_period(df, "created", start_date, end_date)
    t_list = df.explode(feature).groupby(feature).size().sort_values(ascending=False).head(n_values).index.tolist()
    c_list = df.groupby("location.country_code").size().sort_values(ascending=False).head(n_countries).index.tolist()
    data = df.explode(feature).query("`{}` in @t_list".format(feature))
    data = data.query("`location.country_code` in @c_list")[[feature, "location.country_code", "country"]]
    # with open("data/countries.json") as f:
    #     countries = json.load(f)
    # data["country"] = data["location.country_code"].apply(lambda x: countries.get(x.upper(), np.nan)[0])
    ct = pd.crosstab(data["country"], data[feature])
    fig = go.Figure(
        go.Heatmap(
            z=ct,
            x=ct.columns,
            y=ct.index,
            text=ct,
            texttemplate="%{text}",
            hovertemplate="%{x} is in %{z} jobs postings for %{y}<extra></extra>"
        )
    )
    fig.update_yaxes()
    return fig
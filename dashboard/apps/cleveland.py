from typing import Optional

import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State, MATCH
import plotly.graph_objects as go
import pandas as pd

from app import app, cache
import utilities

dropdown = dcc.Dropdown(
    id={
        "type": "feature-dropdown",
        "index": "cleveland"
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

slider = dcc.Slider(
    id={
        "type": "number-slider",
        "index": "cleveland"
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
        html.H1("Cleveland dot plot of counts", className="h2 border-bottom py-2 mb-3"),
        dcc.Loading(
            dcc.Graph(
                id={"type": "graph", "index": "cleveland"},
                figure=utilities.create_empty_figure("Select a feature in the preferences")
            )
        ),
        html.P(
            "This plot shows us the number of job postings that each value of the selected "
            "categorical feature is mentioned and the number of them that are not remote."
        )
    ]
)


# Callbacks
@app.callback(Output({"type": "graph", "index": "cleveland"}, "figure"),
              Input({"type":"feature-dropdown", "index": "cleveland"}, "value"),
              Input({"type": "number-slider", "index": "cleveland"}, "value"),
              Input("date-range-picker", "start_date"),
              Input("date-range-picker", "end_date"))
def render_graph(feature: Optional[str],
                 n: Optional[int],
                 start_date: Optional[str],
                 end_date: Optional[str]) -> go.Figure:
    if n is None or feature is None:
        return utilities.create_empty_figure("Select a feature in the preferences")
    df = cache.get("dataframe")
    df = utilities.filter_on_period(df, "created", start_date, end_date)
    df = df.explode(feature)
    df = utilities.filter_on_frequency(df, feature, n)
    id_feat = df[["id", feature]]
    feat_remote = df[[feature, "remote"]].explode("remote").query("remote == 'remote'").explode(feature)
    data = id_feat.groupby(feature).size().reset_index(name="count")
    data = pd.merge(
        id_feat.groupby(feature).size().reset_index(name="count"),
        feat_remote.groupby(feature).size().reset_index(name="remote_count"),
        how="left", on=feature
    )
    data["remote_frac"] = data["remote_count"] / data["count"]
    data["onsite_count"] = data["count"] - data["remote_count"]
    totals_trace = go.Scatter(
        name="total",
        x=data["count"],
        y=data[feature],
        mode="markers",
        hovertemplate="%{y} found in %{x} job postings<extra></extra>",
        marker=dict(
            line_color="black",
            line_width=0.5,
            color="black"
        )
    )
    onsite_trace = go.Scatter(
        name="onsite",
        x=data["onsite_count"],
        y=data[feature],
        mode="markers",
        hovertemplate="%{y} found in %{x} non remote job postings<extra></extra>",
        marker=dict(
            line_color="black",
            line_width=0.5,
            color="white"
        )
    )
    xs = []
    ys = []
    for _, row in data.iterrows():
        xs += [row["onsite_count"], row["count"], None]
        ys += [row[feature], row[feature], None]
    lines_trace = go.Scatter(
        x=xs,
        y=ys,
        mode="lines",
        line=dict(
            width=0.5,
            color="grey"
        ),
        showlegend=False
    )
    fig = go.Figure(
        data=[
            onsite_trace,
            totals_trace,
            lines_trace
        ],
        layout=dict(
            xaxis=dict(
                title="Number of Job Listings",
                linecolor="black"
            ),
            yaxis=dict(
                title=feature.capitalize(),
                type="category",
                categoryorder="category ascending",
                linecolor="grey",
            ),
            plot_bgcolor="white",
            height=450 + max(0, (n - 20) * 20),
            font_size=max((100 - n) // 10, 8)
        )
    )
    return fig


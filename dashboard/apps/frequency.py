from typing import Optional

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd

from app import app, cache
import utilities



dropdowns = [
    dcc.Dropdown(
        id={
            "type": "feature-dropdown",
            "index": i
        },
        options=[
            {"label": "Technologies", "value": "technologies"},
            {"label": "Roles", "value": "roles"},
            {"label": "Skills", "value": "skills"},
            {"label": "Industries", "value": "industries"},
            {"label": "Job type", "value": "types"},
            {"label": "Experience", "value": "experience"}
        ],
        placeholder="Select a feature"
    )
    for i in range(2)
]

sliders = [
    dcc.Slider(
        id={
            "type": "number-slider",
            "index": i
        },
        tooltip={"placement": "bottom"}
    )
    for i in range(2)
]

preferences = html.Div(
    children=[
        html.Div(
            children=[
                dropdowns[i],
                sliders[i]
            ],
            className="d-flex flex-column"
        )
        for i in range(2)
    ]
)

content = html.Div(
    children=[
        html.H1("Bubble Plot Frequency Matrix", className="h2 border-bottom py-2 mb-3"),
        dcc.Loading(
            dcc.Graph(
                id={"type": "graph", "index": "frequency"},
                figure=utilities.create_empty_figure("Select the features in the preferences")
            )
        ),
        html.P(
            "This bubble plot shows the number of job postings that two values of the selected "
            "categorical features were found in together. It is colored according to the fraction of them "
            "that are for remote jobs."
        )
    ]
)


# Callbacks
@app.callback(Output({"type": "graph", "index": "frequency"}, "figure"),
              [Input({"type": "number-slider", "index": i}, "value") for i in range(2)],
              [State({"type": "feature-dropdown", "index": i}, "value") for i in range(2)],
              State("date-range-picker", "start_date"),
              State("date-range-picker", "end_date"))
def render_graph(n_0: Optional[int],
                 n_1: Optional[int],
                 feat_0: Optional[str],
                 feat_1: Optional[str],
                 start_date: Optional[str],
                 end_date: Optional[str]) -> go.Figure:
    if n_0 is None or n_1 is None:
        return utilities.create_empty_figure("Select the features in the preferences")
    df = cache.get("dataframe")
    df = utilities.filter_on_period(df, "created", start_date, end_date)
    id_feat_0 = df[["id", feat_0]].explode(feat_0)
    id_feat_1 = df[["id", feat_1]].explode(feat_1)
    feat_0_top = id_feat_0.groupby(feat_0).size().sort_values().tail(n_0).index.tolist()
    feat_1_top = id_feat_1.groupby(feat_1).size().sort_values().tail(n_1).index.tolist()
    id_feat_0 = id_feat_0.query("`{}` in @feat_0_top".format(feat_0))
    id_feat_1 = id_feat_1.query("`{}` in @feat_1_top".format(feat_1))
    data = pd.merge(id_feat_0, id_feat_1, on="id")
    data.columns = ["id", "feat_0", "feat_1"]
    remote = pd.merge(data, df[["id", "remote"]].explode("remote").query("remote == 'remote'"), on="id")
    data = data.groupby(["feat_0", "feat_1"]).size().reset_index(name="count")
    remote = remote.groupby(["feat_0", "feat_1", "remote"]).size().reset_index(name="remote_count")
    data = data.set_index(["feat_0", "feat_1"]).join(remote.set_index(["feat_0", "feat_1"])).reset_index().fillna(value={"remote_count":0, "remote":"onsite"})
    data["remote_frac"] = data["remote_count"] /data["count"]
    fig = go.Figure(
        data=go.Scatter(
            x=data["feat_0"],
            y=data["feat_1"],
            mode="markers",
            customdata=data["remote_count"],
            hovertemplate="%{x} and %{y} found in %{marker.size} job postings and %{customdata} of them were with no location requirements<extra></extra>",
            marker=dict(
                color=data["remote_frac"],
                size=data["count"],
                sizemode="area",
                coloraxis="coloraxis",
                opacity=1
            ),
        ),
        layout=go.Layout(
            xaxis=dict(
                title=feat_0.capitalize(),
                type="category",
                categoryorder="category ascending",
                gridcolor="grey",
                linecolor="grey"
            ),
            yaxis=dict(
                title=feat_1.capitalize(),
                type="category",
                categoryorder="category ascending",
                gridcolor="grey",
                linecolor="grey",
                autorange=True,
                # tickangle=-45
            ),
            coloraxis=dict(
                colorscale="solar",
                colorbar_title="Remote",
                colorbar_orientation="h",
                colorbar_tickformat=".0%"
            ),
            plot_bgcolor="white",
            height=450 + max((n_1 - 20) * 20, 0),
            font_size = max((100-n_1) // 10, 10)
        )
    )
    return fig
    return dcc.Graph(figure=fig)
import datetime
import plotly.graph_objects
from typing import Optional, List
import math
import functools
import json

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import networkx as nx
import plotly
import plotly.graph_objects as go
import plotly.express as px

from app import app, cache
import utilities


# Components
dropdown = dcc.Dropdown(
    id={"type": "feature-dropdown", "index": "network"},
    options=[
        {'label': 'Technologies', 'value': 'technologies'},
        {'label': 'Skills', 'value': 'skills'},
        {'label': 'Roles', 'value': 'roles'},
        {'label': 'Industries', 'value': 'industries'},
        {"label": "Job type", "value": "types"},
        {"label": "Experience", "value": "experience"}
    ],
    # value='technologies',
    placeholder="Select a feature"
)

slider = dcc.Slider(
    id={
        "type": "number-slider",
        "index": "network"
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
        html.H1("Network graph", className="h2 border-bottom py-2 mb-3"),
        dcc.Loading(
            dcc.Graph(
                id={"type": "graph", "index": "network"},
                figure=utilities.create_empty_figure("Select a feature in the preferences")
            )
        ),
        html.P("This is a graph of the selected feature values and their co-occurrence in the job postings."),
        html.P(
            "The size of the node indicates the number of job postings that this value was found in. "
            "The colour of the node indicates the number of values with which it was found in the same job posting. "
            "The strength of the color of the edge as well its length also, indicates the number of job postings that these two values were found in together."
        )
    ]
)


def create_graph(df: pd.DataFrame, nodes_values: pd.Series) -> go.Figure:
    # # create continjency table
    # merged = pd.merge(df, df, on='id')
    # merged = merged[merged["technologies_x"] != merged["technologies_y"]]
    # ct = pd.crosstab(merged["technologies_x"], merged["technologies_y"])
    max_weight = df.max().max()
    # create graph
    G = nx.from_pandas_adjacency(df, create_using=nx.MultiGraph)
    # calculate node positions
    pos = nx.spring_layout(G)
    edges_traces = []
    for node, adjacencies in G.adjacency():
        x_0, y_0 = pos[node]
        for t in adjacencies:
            if t < node:
                continue
            x_1, y_1 = pos[t]
            weight = adjacencies[t][0]['weight']
            edge_trace = go.Scatter(
                x=[x_0, x_1, None], y=[y_0, y_1, None],
                line=dict(width=0.5, # +math.log(weight, 10),
                          # color=[weight],
                          # coloraxis="coloraxis2"
                          color="rgb({},{},{})".format(int(200-200*weight/max_weight),
                                                       int(200-200*weight/max_weight),
                                                       int(200-200*weight/max_weight))
                ),
                # line=go.scatter.marker.Line(color=weight,
                #                             coloraxis="coloraxis1"),
                hoverinfo="none",
                mode="lines",
                showlegend=False,
                name=" {} {} ".format(node, t),
            )
            edges_traces.append(edge_trace)

    nodes_traces = []
    for node, adjacencies in G.adjacency():
        x, y = pos[node]
        weights = map(lambda x: x[0]['weight'], adjacencies.values())
        w = functools.reduce(lambda a, b: a + b, weights)
        v = nodes_values.loc[node]
        node_trace = go.Scatter(
            x=[x], y=[y],
            name=node,
            mode="markers",
            hoverinfo="text",
            text="<b>{}</b><br>jobs: {}<br>connections: {}".format(node, v, len(adjacencies)),
            marker=dict(
                size=math.sqrt(v), # math.sqrt(len(adjacencies)), # math.sqrt(w),
                line_width=1,
                coloraxis="coloraxis",
                color=[len(adjacencies)],
            ),
            customdata=[node, ]
        )
        # if node_trace.name == "other":
        #     node_trace.marker.color="#888"
        nodes_traces.append(node_trace)
    # create figure
    fig = go.Figure(
        data=edges_traces + nodes_traces,
        layout=go.Layout(
            hovermode="closest",
            margin=dict(b=0, l=0, r=0, t=25),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="#ffffff",
            coloraxis=dict(colorscale="YlGnBu", colorbar=dict(title="Connections", orientation='h')),
            showlegend=False
        ),
    )
    # fig.update_layout(plot_bgcolor="rgb(255,255,255)")
    # fig.update_layout(coloraxis=dict(colorscale="YlGnBu"), coloraxis_colorbar=dict(title="Connections")),
    # fig.update_layout(showlegend=False)
    return fig




# Callbacks
@app.callback(Output({"type": "graph", "index": "network"}, "figure"),
              Input({"type": "number-slider", "index": "network"}, "value"),
              Input("date-range-picker", "start_date"),
              Input("date-range-picker", "end_date"),
              State({"type": "feature-dropdown", "index": "network"}, "value"))
def render_content(n_values: Optional[int],
                   start_date: Optional[str],
                   end_date: Optional[str],
                   feature: str) -> go.Figure:
    """
    Render the network graph

    :param n_values: The number of most common values to filter the feature
    :type n_values: int
    :param start_date: The date at the start of the period in ISO format
    :type start_date: str
    :param end_date: The date at the end of the period in ISO format
    :type end_date: str
    :param feature: The name of the feature
    :type feature: str
    :return: The figure that is to be displayed
    :rtype: plotly.graph_objects.Figure
    """
    if n_values is None or feature is None:
        return utilities.create_empty_figure("Select a feature in the preferences")
    # get the data
    df = cache.get("dataframe")
    df = df.explode(feature)
    # restrict to period
    df = utilities.filter_on_period(df, "created", start_date, end_date)
    df = df[["id", feature]]
    # keep only the most common values for the feature
    filtered_df = utilities.filter_on_frequency(df, feature, n_values)
    # get the number of jobs for each value
    n_jobs = filtered_df.groupby(feature).nunique()["id"]
    # create contingency table
    merged = pd.merge(filtered_df, filtered_df, on="id")
    merged = merged[merged["{}_x".format(feature)] != merged["{}_y".format(feature)]]
    ct = pd.crosstab(merged["{}_x".format(feature)], merged["{}_y".format(feature)])
    fig = create_graph(ct, n_jobs)
    return fig


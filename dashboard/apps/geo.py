import datetime
from typing import Optional, List
import json

import dash
import pandas as pd
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

from app import app, cache
import components

import utilities

preferences = html.Div("No preferences available for this graph")

content = html.Div(
    children=[
        html.H1("Choropleth map", className="h2 border-bottom py-2 mb-3"),
        dcc.Loading(
            dcc.Graph(
                id={"type": "graph", "index": "map"},
                figure=utilities.create_empty_figure()
            )
        ),
        html.P("This map shows the distribution of job postings by country")
    ]
)


def render_jobs_map(df: pd.DataFrame) -> go.Figure:
    df = df[["id", "location.country_code", "country"]]
    df = df.groupby(["location.country_code", "country"]).size().reset_index(name="n")
    fig = go.Figure(data=go.Choropleth(
        locationmode="ISO-3",
        locations=df["location.country_code"],
        z=df["n"],
        text=df["country"],
        # colorscale="Portland",
        coloraxis="coloraxis",
        # colorbar=go.ColorBar(
        #     title="Job<br>listings",
        #     xanchor="right",
        #     # x=0.95,
        #     orientation="h"),
        # colorbar_title="Number of job listings",
        # colorbar_orientation="h",
        # colorbar_x=-0.2,
        hovertemplate="<b>%{text}</b><br>%{z} listings<extra></extra>",
        marker_line_color="black",
        marker_line_width=0.5,

    ))
    # fig = px.choropleth(df, locations="country_code",
    #                     color="jobs", hover_name="country",
    #                     hover_data=["jobs"],
    #                     color_continuous_scale=px.colors.sequential.Blues)
    fig.update_layout(
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        title_text="Number of jobs listings by country",
        coloraxis_colorbar_thicknessmode="fraction",
        coloraxis_colorbar_xpad=0,
        # coloraxis_colorbar_xanchor="right",
        coloraxis_colorbar_orientation="h",
        coloraxis_colorbar_title="Job<br>Listings",
        coloraxis_colorscale="Oranges", # "Portland",
    )
    # fig.update_traces(overwrite=True, hovertemplate="%{z} jobs")
    return fig # dcc.Graph(id="jobs-map", figure=fig)




def render_feature_map(df: pd.DataFrame,
                       feature: Optional[str],
                       n_values:Optional[int]=None) -> go.Figure:
    df = df[[feature, "location.latitude", "location.longitude"]]
    df = df.dropna()
    if n_values is not None:
        # find the most common values for feature
        top_k = df.groupby(feature).size().sort_values(ascending=False).head(n_values).index.tolist()
        # filter the dataframe with these
        df = df.query("{} in @top_k".format(feature))
    grp_df = df.groupby([feature, "location.latitude", "location.longitude"])
    df = grp_df.size().rename("size").reset_index()
    fig = px.scatter_geo(
        df,
        lat="location.latitude",
        lon="location.longitude",
        color=feature,
        size="size",
        scope="world",
        # height=800
    )
    fig.update_layout(showlegend=True, margin={"l":0, "r":0, "t": 0, "b": 0})
    return fig


def render_job_map(df: pd.DataFrame) -> go.Figure:
    df = df[["id", "location.latitude", "location.longitude"]]
    df = df.dropna()
    grp_df = df.groupby(["id", "location.latitude", "location.longitude"])
    df = grp_df.size().rename("size").reset_index()
    fig = px.scatter_geo(
        df,
        lat="location.latitude",
        lon="location.longitude",
        color="size",
        color_continuous_scale="Viridis",
        size="size",
        scope="world",
        # height=800
    )
    fig.update_layout(showlegend=True, margin={"l":0, "r":0, "t": 0, "b": 0})
    return fig


# Callbacks
@app.callback(Output({"type": "graph", "index": "map"}, "figure"),
              Input("date-range-picker", "start_date"),
              Input("date-range-picker", "end_date"),
              )
def render_content(start_date: Optional[str],
                   end_date: Optional[str]) -> go.Figure:
    df = cache.get("dataframe")
    print(df.columns)
    df = utilities.filter_on_period(df, "created", start_date, end_date)
    # remove missing values
    df.dropna(subset=["location.country_code"], inplace=True)
    # get country code mappings
    with open("data/countries.json", "r") as f:
        countries = json.load(f)
    # convert to 3 letter code
    df["location.country_code"] = df["location.country_code"].apply(
        lambda c: countries.get(c.upper(), [None, None])[1])
    # clean nulls
    df.dropna(subset=["location.country_code"], inplace=True)
    return render_jobs_map(df)
from typing import Optional
import json

import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State, MATCH
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots

from app import app, cache
import utilities


slider = dcc.Slider(
    id={
        "type": "single-number-slider",
        "index": "mosaic"
    },
    min=1,
    value=10,
    tooltip={"placement": "bottom"}
)

preferences = html.Div(
    children=[
        html.Div("Number of countries"),
        slider
    ],
    className="d-flex flex-column"
)

content = html.Div(
    children=[
        html.H1("Mosaic Plot", className="h2 border-bottom py-2 mb-3"),
        dcc.Loading(
            dcc.Graph(
                id={"type": "graph", "index": "mosaic"},
                figure=utilities.create_empty_figure()
            )
        ),
        html.P(
            "This mosaic plot shows the number of job postings per country, "
            "how many of them offer help for the acquirement of a visa if needed "
            "and how many offer relocation benefits"
        )
    ]
)


def create_fig(data: pd.DataFrame) -> go.Figure:
    total = data.sum()["countries_count"]
    gap_y = total * 0.01
    gap_x = 0.005
    pos_y = 0
    y_ticks = []
    y_ticks_pos = []
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(
        plot_bgcolor="white",
        showlegend=False,
        height=550
    )
    # fig = go.Figure(
    #     layout=dict(
    #         plot_bgcolor="white",
    #         showlegend=False
    #     )
    # )
    country_0 = None
    prev_height = 0
    for (country, visa, relocation), row in data.iterrows():
        height = row["countries_count"]
        if country_0 != country:
            country_0 = country
            pos_y += prev_height + gap_y
            prev_height = height
        width = row["visa_ratio"]
        if row["visa_ratio"] == 1:
            left = 0
            right = 1
        elif visa:
            left = 0
            right = row["visa_ratio"] - gap_x
        else:
            left = 1 - (row["visa_ratio"] - gap_x)
            right = 1

        if row["relocation_ratio"] == 1:
            bottom = pos_y
            top = bottom + height
        elif relocation:
            bottom = pos_y
            top = bottom + height * row["relocation_ratio"]
        else:
            top = pos_y + height
            bottom = top - height * row["relocation_ratio"]

        if country not in y_ticks:
            y_ticks.append(country)
            y_ticks_pos.append(pos_y + height / 2)

        name = "{:d} of the {:d} jobs in {} " \
               "{}provide help with visa <br>" \
               "of which {:d} {}provide help with relocation".format(
            int(row["visa_count"]),
            int(row["countries_count"]),
            country,
            "" if visa else "do{} not ".format("es" if row["visa_count"] == 1 else ""),
            int(row["relocation_count"]),
            "" if relocation else "do{} not ".format("es" if row["relocation_count"] == 1 else "")
        )
        fig.add_trace(
            go.Scatter(
                name=name,
                x=[left, left, right, right, left],
                y=[bottom, top, top, bottom, bottom],
                line=dict(
                    color="black"
                ),
                fill="toself",
                fillcolor="white",
                opacity=0,
                customdata=[
                    [country],
                    [row["countries_count"]],
                    [row["visa_count"]],
                    [row["relocation_count"]]
                ],
                hovertemplate="%{name}<extra></extra>",
                # hovertemplate="%{{customdata[2]}} of the %{{customdata[1]}} jobs in %{{customdata[0]}}<br>"
                #               "{}provide help with visa<br>"
                #               "of which %{{customdata[3]}} {}provide help with relocation".format(
                #     "" if visa else "do{} not ".format("es" if row["visa_count"] == 1 else ""),
                #     "" if relocation else "do{} not ".format("es" if row["relocation_count"] == 1 else "")
                # ),
                showlegend=False
            ),
            secondary_y=False
        )
        fig.add_shape(
            type="rect",
            x0=left, y0=bottom, x1=right, y1=top,
            line=dict(
                color="black",
                width=0.5
            ),
            secondary_y=False,
            fillcolor="#406882" if relocation else "#b1d0e0"
        )
    #
    # # add trace to show secondary y axis
    # fig.add_trace(
    #     go.Scatter(
    #         x=[-1],
    #         y=[-1],
    #         opacity=0,
    #         showlegend=False
    #     ),
    #     secondary_y=True
    # )

    # add traces to show legend for relocation
    fig.add_trace(
        go.Scatter(
            name="Yes",
            x=[-1],
            y=[-1],
            mode="markers",
            marker_color="#406882",
            # opacity=0,
            showlegend=True
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            name="No",
            x=[-1],
            y=[-1],
            mode="markers",
            marker_color="#b1d0e0",
            # opacity=0,
            showlegend=True
        ),
        secondary_y=False
    )

    fig.update_yaxes(
        range=[0, pos_y + prev_height],
        ticktext=y_ticks,
        tickvals=y_ticks_pos,
        title="Countries",
        secondary_y=False
    )
    # fig.update_yaxes(
    #     range=[0, 1],
    #     ticktext=["Yes", "No"],
    #     tickvals=[0.25, 0.75],
    #     title="Relocation",
    #     secondary_y=True
    # )
    fig.update_xaxes(
        range=[0, 1],
        ticktext=["Yes", "No"],
        tickvals=[0.25, 0.75],
        title="Visa",
        # side="top",
        # mirror="ticks",
        # anchor="free",
        # position=1
    )
    fig.update_shapes(dict(xref='x', yref='y'))
    fig.update_layout(
        showlegend=True,
        legend_title_text="Relocation"
    )
    return fig


# Callbacks
@app.callback(Output({"type": "graph", "index": "mosaic"}, "figure"),
              Input({"type": "single-number-slider", "index": "mosaic"}, "value"),
              Input("date-range-picker", "start_date"),
              Input("date-range-picker", "end_date"))
def render_graph(n: Optional[int],
                 start_date: Optional[str],
                 end_date: Optional[str]):
    if n is None:
        return utilities.create_empty_figure("Select the number of countries in the preferences")
    with open("data/countries.json", "r") as f:
        countries = json.load(f)
    df = cache.get("dataframe")
    df = utilities.filter_on_period(df, "created", start_date, end_date)
    df["country"] = df["location.country_code"].dropna().apply(lambda k: countries.get(k.upper(), np.nan)[0])
    df = utilities.filter_on_frequency(df, "country", n)
    data = df[["id", "country"]]\
        .dropna(subset=["country"])\
        .groupby("country")\
        .size()\
        .reset_index(name="countries_count")
    data = pd.merge(
        data,
        df[["id", "country", "visa"]]\
            .groupby(["country", "visa"])\
            .size()\
            .reset_index(name="visa_count"),
        on="country",
        how="left"
    ).dropna()
    # return data
    data = pd.merge(
        data,
        df[["id", "country", "visa", "relocation"]]\
            .groupby(["country", "visa", "relocation"])\
            .size()\
            .reset_index(name="relocation_count"),
        on=["country", "visa"],
        how="left"
    ).dropna()
    # data["visa"] = data["visa"].replace(to_replace={False: "No", True: "Yes"})
    # data["relocation"] = data["relocation"].replace(to_replace={False: "No", True: "Yes"})
    data = data.sort_values(by=["countries_count", "country"], ascending=False)
    data.set_index(["country", "visa", "relocation"], inplace=True)
    data["visa_ratio"] = data["visa_count"] / data["countries_count"]
    data["relocation_ratio"] = data["relocation_count"] / data["visa_count"]
    data.to_csv("mosaic.csv")
    fig = create_fig(data)
    return fig
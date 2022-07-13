import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_bio
import pandas as pd
import datetime

import colorsys
from typing import List, Tuple, Union
import json
import random
from urllib.request import urlopen, Request
import os

from app import app, cache
import utilities
import components
# from index import cache


dropdown = dcc.Dropdown(
    id={
        "type": "feature-dropdown",
        "index": "chord"
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
        "index": "chord"
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
        html.H1("Chord diagram", className="h2 border-bottom py-2 mb-3"),
        dcc.Loading(
            html.Div(id="chord-graph-panel")
        ),
        html.P(
            "This diagram shows the number of job postings in which two values of the selected"
            " categorical feature, are together"
        ),
        dcc.Store(id="size", storage_type="session")
    ]
)

# Utilities

def generate_color_palette(n: int) -> List[Tuple[str, str, str]]:
    """
    Generate a list of different colors in hex format

    :param n: The number of colors to generate
    :return: A list of strings that each represent a color in hex format
    """
    hsv_palette = [(i * 1 / n, 1/2, 1/2) for i in range(n)]
    rgb_palette = [colorsys.hsv_to_rgb(*c) for c in hsv_palette]
    hex_palette = ["#{:X}{:X}{:X}".format(int(r*255), int(g*255), int(b*255)) for (r, g, b) in rgb_palette]
    random.shuffle(hex_palette)
    return hex_palette

def create_circos(df: pd.DataFrame, height: int, width: int) -> dash.development.base_component.Component:
    size = min(height, width)
    df_grpby = df.groupby("feature_x")
    colors = generate_color_palette(df_grpby.ngroups)
    it = df_grpby.__iter__()
    data = dict()
    techs = dict()
    hist_data = []
    text_data = []
    high_data = []
    for block, grp in it:
        conns = grp.sort_values(by=["n"], ascending=False)
        for index, row in conns.iterrows():
            source = {"id": row["feature_x"]}
            target = {"id": row["feature_y"]}
            val = row["n"]
            if source["id"] not in techs:
                techs[source["id"]] = {"pos": 0, "color": colors.pop()}
            if target["id"] not in techs:
                techs[target["id"]] = {"pos": 0, "color": colors.pop()}
            source['start'] = techs[source['id']]['pos']
            target['start'] = techs[target['id']]['pos']
            key = tuple(sorted([source['id'], target['id']]))
            if key not in data:
                source['start'] = techs[source['id']]['pos']
                target['start'] = techs[target['id']]['pos']
                # increment position
                techs[source['id']]['pos'] += val
                techs[target['id']]['pos'] += val

                source['end'] = techs[source['id']]['pos']
                target['end'] = techs[target['id']]['pos']
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                color = "rgb({},{},{})".format(r, g, b)
                # color = techs[source["id"]]["color"]
                data[key] = {"color": color, 'source': source, 'target': target, 'value': val}

                hist_data.append({
                    'block_id': source['id'],
                    'start': source['start'],
                    'end': source['end'],
                    'value': val,
                    'color': techs[target['id']]['color']
                })
                hist_data.append({
                    'block_id': target['id'],
                    'start': target['start'],
                    'end': target['end'],
                    'value': val,
                    'color': techs[source['id']]['color']  # color
                })
        text_data.append({
            "block_id": block,
            "position": techs[block]["pos"]//2,
            "value": block
        })
        high_data.append({
            "block_id": block,
            "start": 0,
            "end": techs[block]["pos"]
        })

    layout = []
    for t in techs:
        color = techs[t]['color'] # colors.pop()
        len = techs[t]['pos']
        layout.append({'color': color, 'id': t, 'label': t, 'len': len})

    chord_data = list(data.values())
    graph = dash_bio.Circos(
        id='chord-graph',
        selectEvent={'0':'hover', '1':'click'},
        # enableZoomPan=True,
        layout=layout,
        config={
            'labels':{
                'display': False,
                'position':'center',
                'size':'15',
                'radialOffset':50
            },
            'tooltipContent':{'name':'all'},
            'ticks':{'display':False},
            'innerRadius':size/2-80,
            'outerRadius':size/2-40
        },
        tracks=[
            {
                'type': 'CHORDS',
                'data': chord_data,
                'config': {
                    'color': {'name': 'color'},
                    'opacity': '0.5',
                    'tooltipContent': {
                        # 'source': 'source',
                        # 'sourceID': 'id',
                        # 'target': 'target',
                        # 'targetID': 'id',
                        'name': 'value'
                    }
                }
            },
            {
                "type": "TEXT",
                "data": text_data,
                "config": {
                    "tooltipContent": {
                        "name": "value"
                    }
                }
            },
            {
                "type": "HIGHLIGHT",
                "data": high_data,
                "config": {
                    "tooltipContent": {
                        "name": "block_id"
                    },
                    "innerRadius": size/2-80,
                    "outerRadius": size/2-40,
                    "opacity": 0
                }
            }
        #     {
        #         'type': 'HISTOGRAM',
        #         'data': hist_data,
        #         'config': {
        #             'color': {'name': 'color'},
        #             'tooltipContent': {
        #                 'name': 'value'
        #             },
        #             'logScale': True
        #         }
        # }
        ],
        # style=dict(height="100-vh", width="100%")
        # enableZoomPan=True
        # innerRadius=size/2-80,
        # outerRadius=size/2-40,
        size=width
    )
    return graph


def create_chord(data: pd.DataFrame) -> dash.development.base_component.Component:
    url = os.getenv("GRAPHS_URL") + "/chord" # , "http://localhost:4219") + "/chord"
    print(url)
    body = data.to_json(orient="records").encode("utf-8")
    request = Request(url)
    request.add_header("Content-type", "application/json; charset=utf-8")
    with urlopen(request, body) as response:
        s = response.read().decode()
    return html.Iframe(srcDoc=s, style={"height": "100vh", "width": "100%"})


# Callbacks
@app.callback(Output('chord-graph-panel', 'children'),
              Input({"type": "number-slider", "index": "chord"}, 'value'),
              Input('date-range-picker', 'start_date'),
              Input('date-range-picker', 'end_date'),
              Input("size-store", "data"),
              State({"type": "feature-dropdown", "index": "chord"}, 'value'),
              prevent_initial_call=True)
def render_graph(n_values, start_date, end_date, size_store, feature):
    # return html.Iframe(src="assets/graph.html", style={"height": "500px", "width": "100%"}), html.Div()
    if feature is None:
        return html.Div("Select a feature in the preferences")
    height = size_store.get("window_height", 900) - 100
    width = size_store.get("content_width", 800)
    df = cache.get("dataframe")
    df = utilities.filter_on_period(df, "created", start_date, end_date)
    # df.dropna(subset=[feature])
    df = df.rename(columns={feature: "feature"})
    feature = "feature"
    df = df.explode(feature)
    df.dropna(subset=[feature], inplace=True)
    df = utilities.filter_on_frequency(df, feature, n_values)
    id_feat = df[["id", feature]]
    merged = pd.merge(id_feat, id_feat, on="id")
    merged = merged[merged["feature_x"] != merged["feature_y"]]
    data = merged.groupby(["feature_x", "feature_y"]).size().reset_index(name="n")
    return (
        html.Div(
            children=[
                html.Div(create_chord(data), className=""),
                # html.Div(create_circos(data, height, width))
            ]
        ),
    )


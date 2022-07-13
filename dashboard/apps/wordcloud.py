import io
from typing import Optional, Dict
import base64

import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import wordcloud

from app import app, cache
import utilities


dropdown = dcc.Dropdown(
    id={
        "type": "feature-dropdown",
        "index": "wordcloud"
    },
    options=[
        {"label": "Technologies", "value": "technologies"},
        {"label": "Roles", "value": "roles"},
        {"label": "Skills", "value": "skills"},
        {"label": "Industries", "value": "industries"}
    ],
    placeholder="Select a feature"
)

slider = dcc.Slider(
    id={
        "type": "number-slider",
        "index": "wordcloud"
    },
    tooltip={"placement": "bottom", "always_visible": True}
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
        html.H1("Word cloud", className="h2 border-bottom py-2 mb-3"),
        dcc.Loading(html.Div(id={"type": "graph", "index": "wordcloud"}, className="min-vh-100")),
        html.P("This a tag cloud of the selected feature values, where each tags size indicates a values frequency.")
    ]
)


@app.callback(Output({"type": "graph", "index": "wordcloud"}, "children"),
              Input({"type":"feature-dropdown", "index": "wordcloud"}, "value"),
              Input({"type": "number-slider", "index": "wordcloud"}, "value"),
              Input("date-range-picker", "start_date"),
              Input("date-range-picker", "end_date"),
              State("size-store", "data"))
def render_graph(feature: Optional[str],
                 n: Optional[int],
                 start_date: Optional[str],
                 end_date: Optional[str],
                 dims: Optional[Dict[str, float]]) -> dash.development.base_component.Component:
    if feature is None or n is None:
        return html.Div("Select a feature and number of values in the preferences")
    height = dims["window_height"]
    width = dims["content_width"]
    df = cache.get("dataframe")
    df = utilities.filter_on_period(df, "created", start_date, end_date)
    df = df.explode(feature)
    df = utilities.filter_on_frequency(df, feature, n)
    id_feat = df[["id", feature]].dropna()
    data = id_feat.groupby(feature).size()
    data.columns = ["n"]
    # print(data)
    # print(data.to_dict())
    # create wordcloud image
    wc = wordcloud.WordCloud(background_color=None, mode="RGBA", width=width, height=height)
    image = wc.generate_from_frequencies(data.to_dict()).to_image()
    # create an image file
    output = io.BytesIO()
    image.save(output, format="png")
    image_data = output.getvalue()
    # encode to base64
    image_data = base64.b64encode(image_data)
    # decode to string
    image_data = image_data.decode("utf-8")
    # add header
    image_url = "data:image/png;base64, " + image_data

    return html.Img(src=image_url, className="img-fluid")
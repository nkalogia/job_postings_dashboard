import dash.development.base_component
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from urllib.request import urlopen
import pandas as pd
import numpy as np

import os
import json
import logging
from typing import Optional, Tuple
import datetime

from app import app, cache
from apps import chord, geo, network, frequency, cleveland, mosaic, heatmap, wordcloud, polar, salary
import utilities
import callbacks


LOGGER = logging.getLogger(__name__)

DATA_URL = os.environ.get("DATA_URL")


# Components
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand("Dashboard", href="/"),
            dbc.NavbarToggler(id="sidebar-toggle"),
        ],
        fluid=True
    ),
    class_name="p-0 shadow",
    sticky="top",
    dark=True,
    color="dark"
)

nav = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("Chord", href="/chord")),
        dbc.NavItem(dbc.NavLink("Choropleth Map of Counts", href="/map")),
        dbc.NavItem(dbc.NavLink("Network", href="/network")),
        dbc.NavItem(dbc.NavLink("Bubble Plot Frequency Matrix", href="/frequency")),
        dbc.NavItem(dbc.NavLink("Cleveland Dot Plot of Counts", href="/cleveland")),
        dbc.NavItem(dbc.NavLink("Mosaic Plot", href="/mosaic")),
        dbc.NavItem(dbc.NavLink("Heatmap", href="/heatmap")),
        dbc.NavItem(dbc.NavLink("Wordcloud", href="/wordcloud")),
        dbc.NavItem(dbc.NavLink("Polar chart", href="/polar")),
        dbc.NavItem(dbc.NavLink("Salary Marginal Distribution", href="/salary"))
    ],
    vertical=True,
    className="d-flex flex-column flex-nowrap text-dark"
)

date_range_picker = dcc.DatePickerRange(id='date-range-picker', with_portal=False)

date_range_slider = html.Div(dcc.RangeSlider(id="date-range-slider"), className="d-flex flex-column align-items-stretch")

data_update_button = dbc.Button(id='data-update', children='Update', n_clicks=0)

global_filters = html.Div(
    children=[
        html.Div(['Select a period', date_range_picker]),
        date_range_slider,
    ],
    className="d-flex flex-column align-items-stretch pl-1"
)

filters = html.Div()

local_filters = html.Div(id='local-filters', children=filters)

sidebar = html.Div(
    children=[
        dbc.Accordion(
            id="sidebar-accordion",
            children=[
                dbc.AccordionItem(nav, title="Graphs", item_id="graphs"),
                dbc.AccordionItem(local_filters, title="Preferences", item_id="preferences"),
                dbc.AccordionItem(html.Div(global_filters), title="Filters", item_id="filters")

            ],
            flush=True,
            class_name="pb-2"
        ),
        dcc.Loading(
            html.Div(
                data_update_button,
                className='d-grid gap-2'
            ),
            fullscreen=True,
            id='update-loading'
        )
    ],
    className='d-flex flex-column align-items-between position-sticky pt-5',
)

content = html.Div(
    children=[
        html.H1("Welcome"),
        html.P(
            "This web application is a presentation of various informative plots "
            "about the jobs posted in the StackOverflow website."
        )
    ], 
    className='d-flex flex-column min-vh-100 justify-content-center align-items-center')

not_found_404 = html.Div('404 Not Found', className='d-flex min-vh-100 justify-content-center align-items-center')

main_panel = html.Div(id='main-content', children=content, className="px-2")

# Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(className="row", children=[
        dbc.Collapse(
            sidebar,
            id="sidebar",
            className="col-md-3 col-lg-2 d-md-block bg-white shadow",
            style={
                "position": "fixed",
                "top": "0",
                "bottom": "0",
                "left": "0",
                "z-index": "100",
                "maxHeight": "calc(100vh-9rem)",
                "overflowY": "auto"
            },
            is_open=False
        ),
        html.Main(main_panel, className="col-md-9 col-lg-10 ms-sm-auto px-md-4 min-vh-100")
    ]),
    dcc.Interval(
        id="interval",
        interval=3600000,
        n_intervals=0
    ),
    dcc.Store(id="size-store")
])


# Callbacks
@app.callback(Output('url', 'pathname'),
              Input('update-loading', 'fullscreen'),
              State('url', 'pathname'))
def redirect(initial: bool, pathname: str) -> str:
    """
    Refresh page after loading dataset.


    :param bool initial: if the app is initialized now
    :param str pathname: the current pathname
    :return: the target pathname
    :rtype: bool
    """
    if initial:
        return '/'
    return pathname


@app.callback(Output('local-filters', 'children'),
              Output('main-content', 'children'),
              Output("sidebar-accordion", "active_item"),
              Input('url', 'pathname'))
def display_page(pathname: str) -> Tuple[Optional[dash.development.base_component.Component],
                                         Optional[dash.development.base_component.Component]]:
    """
    Display the appropriate page for the location.

    :param pathname: The relative path name of the target location.
    :type pathname: str
    :return: The filters and the content for the target location
    :rtype: tuple
    """
    if pathname == '/chord':
        return chord.preferences, chord.content, "preferences"
    elif pathname == '/map':
        return geo.preferences, geo.content, "preferences"
    elif pathname == "/network":
        return network.preferences, network.content, "preferences"
    elif pathname == "/frequency":
        return frequency.preferences, frequency.content, "preferences"
    elif pathname == "/cleveland":
        return cleveland.preferences, cleveland.content, "preferences"
    elif pathname == "/mosaic":
        return mosaic.preferences, mosaic.content, "preferences"
    elif pathname == "/heatmap":
        return heatmap.preferences, heatmap.content, "preferences"
    elif pathname == "/wordcloud":
        return wordcloud.preferences, wordcloud.content, "preferences"
    elif pathname == "/polar":
        return polar.preferences, polar.content, "preferences"
    elif pathname == "/salary":
        return salary.preferences, salary.content, "preferences"
    elif pathname == '/':
        return filters, content, "graphs"
    else:
        return None, not_found_404


@app.callback(Output('sidebar', 'is_open'),
              Input('sidebar-toggle', 'n_clicks'),
              State('sidebar', 'is_open'))
def toggle_sidebar(n_clicks: int, is_open: bool) -> bool:
    """
    Toggle the visibility of the sidebar when in small screens.

    :param n_clicks: The number of times the toggle button has been clicked
    :type n_clicks: int
    :param is_open: True if the sidebar is visible, False if not
    :type is_open: bool
    :return: True if the sidebar is visible, False if not
    :rtype: bool
    """
    if n_clicks:
        return not is_open
    return is_open


@app.callback(Output("navbar-nav", "is_open"),
              Input("navbar-toggle", "n_clicks"),
              State("navbar-nav", "is_open"))
def toggle_navbar(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

@app.callback(Output("filters-canvas", "is_open"),
              Input("open-filters", "n_clicks"),
              State("filters-canvas", "is_open"))
def toggle_canvas(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


@app.callback(Output('update-loading', 'fullscreen'),
              Output('date-range-picker', 'min_date_allowed'),
              Output('date-range-picker', 'max_date_allowed'),
              Input('interval', 'n_intervals'),
              Input('data-update', 'n_clicks'),
              State("date-range-slider", "value"))
def update_data(n_intervals, n_clicks, slider_value):
    """
    Update data either on interval or on user request
    :param n_intervals: The number of intervals passed
    :param n_clicks: The number of clicks on update button
    :return: A tuple with the maximum and the minimum date allowed for selecting
    """
    # Comment/Uncomment to skip fetching the data (Testing)
    # return False, datetime.date.today().isoformat(), datetime.date.today().isoformat()
    with urlopen(DATA_URL) as response:
        jobs_dict = json.load(response)
    df = pd.json_normalize(jobs_dict)
    # convert to datetime (is Timestamp)
    df['created'] = df['created'].apply(lambda x: pd.to_datetime(x).date())
    # df[['created', 'updated']] = df[['created', 'updated']].apply(
    #     lambda x: pd.to_datetime(x).date())
    df.rename(columns={"employer.industries": "industries", "job_types": "types"}, inplace=True)
    # set country column
    with open("data/countries.json", "r") as f:
        countries = json.load(f)
    df["country"] = df["location.country_code"].apply(
        lambda x: countries.get(x.upper(), np.nan)[0] if type(x) is str else np.nan)
    # set dataframe
    cache.set('dataframe', df[df.columns.difference(['description'])])
    return False, df['created'].min().isoformat(), df['created'].max().isoformat()

server = app.server

if __name__=='__main__':
    logging.basicConfig(level=logging.INFO)
    app.run_server(host="0.0.0.0", port=8000)

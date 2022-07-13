import datetime
from typing import Optional, Tuple, List, Dict
import json

import dash
from dash.dependencies import Input, Output, State, MATCH

from app import app, cache
import utilities


@app.callback(Output("date-range-slider", "min"),
              Output("date-range-slider", "max"),
              Output("date-range-slider", "value"),
              Output("date-range-picker", "start_date"),
              Output("date-range-picker", "end_date"),
              Input("date-range-picker", "min_date_allowed"),
              Input("date-range-picker", "max_date_allowed"),
              Input("date-range-slider", "value"),
              Input("date-range-picker", "start_date"),
              Input("date-range-picker", "end_date"),
              prevent_initial_call=True)
def propagate_period_limits(min_date: Optional[str],
                            max_date: Optional[str],
                            date_range: Optional[List[int]],
                            start_date: Optional[str],
                            end_date: Optional[str]) -> Tuple[int, int, Tuple[int, int], str, str]:
    """
    Propagate the period limits to the period slider component.

    :param min_date: The lower limit for the date in ISO format
    :type min_date: str or None
    :param max_date: The upper limit for the date in ISO format
    :type max_date: str or None
    :param date_range: A list with the ordinal date for the start and end dates of the period
    :type date_range: List of int or None
    :param start_date: The date at the start of the period in ISO format
    :type start_date: str or None
    :param end_date: The date at the end of the period in ISO format
    :type end_date: str or None
    :return: A tuple with the lower and upper limit for the dates in ordinal numbers
    :rtype: tuple
    :raises TypeError: If any of min_date, max_date, start_date, end_date is not a string
    :raises ValueError: If any of min_date, max_date, start_date, end_date is not in ISO format
    """
    if start_date is not None:
        start = datetime.date.fromisoformat(start_date)
    else:
        start = datetime.date.fromisoformat(min_date)
    if end_date is not None:
        end = datetime.date.fromisoformat(end_date)
    else:
        end = datetime.date.fromisoformat(max_date)
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if triggered_id == "date-range-slider":
        start = datetime.date.fromordinal(date_range[0])
        end = datetime.date.fromordinal(date_range[1])

    start = max(start, datetime.date.fromisoformat(min_date))
    end = min(end, datetime.date.fromisoformat(max_date))

    return (
        datetime.date.fromisoformat(min_date).toordinal(),
        datetime.date.fromisoformat(max_date).toordinal(),
        (start.toordinal(), end.toordinal()),
        start.isoformat(),
        end.isoformat()
    )


@app.callback(Output({"type": "number-slider", "index": MATCH}, "min"),
              Output({"type": "number-slider", "index": MATCH}, "max"),
              Output({"type": "number-slider", "index": MATCH}, "value"),
              Input({"type": "feature-dropdown", "index": MATCH}, "value"),
              # Input({"type": "feature-store", "index": MATCH}, "id"),
              Input("date-range-picker", "start_date"),
              Input("date-range-picker", "end_date"),
              State({"type": "number-slider", "index": MATCH}, "value"),
              prevent_initial_call=True)
def init_slider(feature: Optional[str],
                start_date: Optional[str],
                end_date: Optional[str],
                value: Optional[int]) -> Tuple[int, int, int]:
    # d = json.loads(id)
    # feature = d["feature"]
    if feature is None:
        return None, None, None
    df = cache.get("dataframe")
    df = utilities.filter_on_period(df, "created", start_date, end_date)
    n = df[feature].explode(feature).dropna().nunique()
    return 1, n, min(n, 10)


@app.callback(Output({"type": "number-input", "index": MATCH}, "min"),
              Output({"type": "number-input", "index": MATCH}, "max"),
              Output({"type": "number-input", "index": MATCH}, "value"),
              Input({"type": "feature-dropdown", "index": MATCH}, "value"),
              # Input({"type": "feature-store", "index": MATCH}, "id"),
              Input("date-range-picker", "start_date"),
              Input("date-range-picker", "end_date"),
              State({"type": "number-input", "index": MATCH}, "value"),
              prevent_initial_call=True)
def init_slider(feature: Optional[str],
                start_date: Optional[str],
                end_date: Optional[str],
                value: Optional[int]) -> Tuple[int, int, int]:
    # d = json.loads(id)
    # feature = d["feature"]
    if feature is None:
        return None, None, None
    df = cache.get("dataframe")
    df = utilities.filter_on_period(df, "created", start_date, end_date)
    n = df[feature].explode(feature).dropna().nunique()
    return 1, n, min(n, 10)


@app.callback(Output({"type": "single-number-slider", "index": MATCH}, "min"),
              Output({"type": "single-number-slider", "index": MATCH}, "max"),
              Output({"type": "single-number-slider", "index": MATCH}, "value"),
              Input({"type": "store", "index": MATCH}, "data"),
              Input("date-range-picker", "start_date"),
              Input("date-range-picker", "end_date"),
              State({"type": "single-number-slider", "index": MATCH}, "value"))
def init_sole_slider(data: Dict[str,str],
                     start_date: Optional[str],
                     end_date: Optional[str],
                     n_values: Optional[int]) -> Tuple[int, int, int]:
    feature = data.get("feature", None)
    if feature is None:
        return None, None, None
    df = cache.get("dataframe")
    df = utilities.filter_on_period(df, "created", start_date, end_date)
    n = df[feature].explode(feature).dropna().nunique()
    return 1, n, min(n, 10)



@app.callback(Output({"type": "single-number-input", "index": MATCH}, "min"),
              Output({"type": "single-number-input", "index": MATCH}, "max"),
              Output({"type": "single-number-input", "index": MATCH}, "value"),
              Input({"type": "store", "index": MATCH}, "data"),
              Input("date-range-picker", "start_date"),
              Input("date-range-picker", "end_date"),
              State({"type": "single-number-input", "index": MATCH}, "value"))
def init_sole_slider(data: Dict[str,str],
                     start_date: Optional[str],
                     end_date: Optional[str],
                     n_values: Optional[int]) -> Tuple[int, int, int]:
    feature = data.get("feature", None)
    if feature is None:
        return None, None, None
    df = cache.get("dataframe")
    df = utilities.filter_on_period(df, "created", start_date, end_date)
    n = df[feature].explode(feature).dropna().nunique()
    return 1, n, min(n, 10)


app.clientside_callback(
    """
    function(contentId) {
        let wh = window.innerHeight;
        let ww = window.innerWidth;
        let cw = document.getElementById("main-content").offsetWidth;
        return {"window_width": ww, "window_height": wh, "content_width": cw}
    }
    """,
    Output("size-store", "data"),
    Input("main-content", "children")
)
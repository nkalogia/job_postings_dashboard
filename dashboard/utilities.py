import datetime
from typing import Optional, Any, Dict, Union
import os
from urllib.request import urlopen
import json

import pandas as pd
import numpy as np
import plotly.graph_objects as go


from app import cache


DATA_URL = os.getenv("DATA_URL", "http://localhost:8000/jobs")


def filter_on_period(df: Union[pd.DataFrame, pd.Series],
                     date_feature: str,
                     start_date: Optional[str],
                     end_date: Optional[str]) -> int:
    """
    Filter data on period.

    :param df: The data frame holding the data
    :type df: pandas.DataFrame or pandas.Series
    :param date_feature: The name of the feature holding the date values
    :type date_feature: str
    :param start_date: The date at the start of the period in ISO format
    :type start_date: str or None
    :param end_date: The date at the end of the period in ISO format
    :type end_date: str or None
    :return: The data frame filtered on the period
    :rtype: pandas.DataFrame
    :raises TypeError: If the date_feature column does not contain datetime.date values
                        or the date_feature is not a column name in the data frame
                        or one of the start_date and end_date is not a string
    :raises ValueError: If one of the start_date and end_date is a valid date in ISO format
    """
    if start_date is not None:
        df = df[df[date_feature] >= datetime.date.fromisoformat(start_date)]
    if end_date is not None:
        df = df[df[date_feature] <= datetime.date.fromisoformat(end_date)]
    return df


def filter_on_frequency(df: pd.DataFrame,
                        feature: str,
                        k: int,
                        value: Any = np.nan) -> pd.DataFrame:
    """
    Filter the data and keep the most common values for the feature.

    :param df: The data frame holding the data
    :type df: pandas.DataFrame
    :param feature: The name of the feature on the data frame
    :type feature: str
    :param k: The number of most common values to keep
    :type k: int
    :param value: Replace the filtered values with this value. If None, discard them.
    :type value: Any
    :return: The filtered data frame with the most common values
    :rtype: pandas.DataFrame
    """
    # drop missing values
    df.dropna(subset=[feature], inplace=True)
    # find the number of unique values
    n = df[feature].nunique()
    # find the least common values
    least_common = df[["id", feature]].groupby(feature).size().sort_values().head(max(n-k,0)).index.tolist()
    # replace them with value
    df[feature] = df[feature].replace(to_replace=least_common, value=value)
    if value is None:
        df = df.dropna(subset=[feature])
        # df.query("`{}` != None".format(feature), inplace=True)
    return df


def create_empty_figure(message: Optional[str]=None) -> go.Figure:
    """
    Create an empty figure serving as a placeholder component, optionally showing a message

    :param message: The message to show in the figure or None to show nothing
    :type message: str or None
    :return: The figure with the message
    :rtype: plotly.graph_objects.Figure
    """
    return go.Figure(
        layout=dict(
            xaxis_visible=False,
            yaxis_visible=False,
            plot_bgcolor="white",
            annotations=[
                dict(
                    text=message if message is not None else "",
                    xref="paper",
                    yref="paper",
                    showarrow=False,

                )
            ],
        )
    )


def fetch_data() -> pd.DataFrame:
    """
    Fetch the data

    :return: The data frame holding the data
    :rtype: pandas.DataFrame
    """
    with urlopen(DATA_URL) as response:
        df = pd.json_normalize(json.load(response))
    return df


def calculate_monthly_marks(start_date: datetime.date, end_date: datetime.date) -> Dict[int, str]:
    """
    Calculate the monthly marks for the period slider component.

    :param start_date: The date at the start of the period
    :type start_date: str or None
    :param end_date: The date at the end of the period
    :type end_date: str or None
    :return: A mapping of integers to months
    :rtype: dict
    """
    months = [
        "January", "February", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December"
    ]
    day = datetime.timedelta(days=1)
    monthly_marks = dict()
    current_date = start_date
    previous_month_mark = "{} {}".format(
        months[current_date.month-1][:3],
        str(current_date.year)[-2:]
    )
    while current_date < end_date:
        current_month_mark = "{} {}".format(
            months[current_date.month-1][:3],
            str(current_date.year)[-2:]
        )
        if current_month_mark != previous_month_mark:
            monthly_marks[current_date.toordinal()] = current_month_mark
            previous_month_mark = current_month_mark
        current_date += day
    return monthly_marks

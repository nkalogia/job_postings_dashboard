from typing import Optional, Tuple

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

from app import app, cache
import utilities

preferences = html.Div("No preferences available")

content = html.Div(
    children=[
        html.H1("Polar chart of Joel tests", className="h2 border-bottom py-2 mb-3"),
        dcc.Loading(
            dcc.Graph(
                id={"type": "graph", "index": "polar"},
                figure=utilities.create_empty_figure()
            )
        ),
        html.P(
            "This polar chart shows in many job postings, each value of the Joel test questionnaire "
            "is featured."
        ),
        dcc.Loading(
            dcc.Graph(
                id={"type": "graph", "index": "pie"},
                figure=utilities.create_empty_figure()
            )
        ),
        html.P(
            "This pie chart shows the number of job postings where Joel test is mentioned."
        )
    ]
)


@app.callback(Output({"type": "graph", "index": "polar"}, "figure"),
             Output({"type": "graph", "index": "pie"}, "figure"),
             Input({"type": "graph", "index": "polar"}, "id"),
             Input("date-range-picker", "start_date"),
             Input("date-range-picker", "end_date"))
def render_graph(id: Optional[str],
                 start_date: Optional[str],
                 end_date: Optional[str]) -> Tuple[go.Figure, go.Figure]:
    df = cache.get("dataframe")
    data = utilities.filter_on_period(df, "created", start_date, end_date)
    nan_count = (data["joel_test"].str.len() == 0).sum()
    total_count = data["id"].nunique()
    data = data[["id", "joel_test", "remote"]].explode("joel_test").explode("remote")
    data = data.dropna()
    remote_data = data[data["remote"] == "remote"].groupby("joel_test").size().reset_index(name="n")
    remote_data.loc[len(remote_data.index)] = remote_data.loc[0]
    onsite_data = data[data["remote"] == "onsite"].groupby("joel_test").size().reset_index(name="n")
    onsite_data.loc[len(onsite_data.index)] = onsite_data.loc[0]
    limitedremote_data = data[data["remote"] == "limitedremote"].groupby("joel_test").size().reset_index(name="n")
    limitedremote_data.loc[len(limitedremote_data.index)] = limitedremote_data.loc[0]
    total_data = data[["id", "joel_test"]].groupby("joel_test").nunique().rename(columns={"id": "n"}).reset_index()
    total_data.loc[len(total_data.index)] = total_data.loc[0]

    remote_trace = go.Scatterpolar(
        name="Remote",
        r=remote_data["n"],
        theta=remote_data["joel_test"],
        hovertemplate="%{r} remote jobs <br>state that use %{theta}<extra></extra>"
    )
    onsite_trace = go.Scatterpolar(
        name="Onsite",
        r=onsite_data["n"],
        theta=onsite_data["joel_test"],
        hovertemplate="%{r} onsite jobs <br>state that use %{theta}<extra></extra>"
    )
    limitedremote_trace = go.Scatterpolar(
        name="Limited remote",
        r=limitedremote_data["n"],
        theta=limitedremote_data["joel_test"],
        hovertemplate="%{r} limited remote jobs <br>state that use %{theta}<extra></extra>"
    )
    total_trace = go.Scatterpolar(
        name="total",
        r=total_data["n"],
        theta=total_data["joel_test"],
        hovertemplate="%{r} jobs <br>state that use %{theta}<extra></extra>"
    )
    # fig = make_subplots(rows=1, cols=2, specs=[[{"type": "polar"}, {"type": "domain"}]])
    # fig.add_trace(remote_trace, row=1, col=1)
    # fig.add_trace(onsite_trace, row=1, col=1)
    # fig.add_trace(limitedremote_trace, row=1, col=1)
    # fig.add_trace(
    #     go.Pie(
    #         labels=["Yes", "No"],
    #         values=[total_count - nan_count, nan_count]
    #     ),
    #     row=1, col=2
    # )

    fig_1 = go.Figure(
        data=[
            remote_trace,
            onsite_trace,
            limitedremote_trace,
            # total_trace
        ],
        layout=dict(
            title_text="Joel test questionnaire counts",
            polar=dict(
                radialaxis=dict(
                    visible=True,
                ),
                angularaxis=dict(
                    # showgrid=False
                )
            ),
        ),
    )

    fig_2 = go.Figure(
        go.Pie(
            labels=["Yes", "No"],
            values=[total_count - nan_count, nan_count],
        ),
        layout=dict(
            title_text="Joel test questionnaire presence"
        )
    )

    return fig_1, fig_2


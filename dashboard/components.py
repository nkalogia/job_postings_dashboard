from dash import html, dcc


def create_number_input(feature: str) -> dcc.Input:
    return dcc.Input(
        id={
            "type": "number-input",
            "feature": feature
        }
    )


def create_number_slider(feature: str) -> dcc.Slider:
    return dcc.Slider(
        id={
            "type": "number-slider",
            "feature": feature
        },
        tooltip=True
    )
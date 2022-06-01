# package imports
from dash import html, dcc, Output, Input, State, callback, MATCH
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import uuid


class PlaybackSliderAIO(html.Div):
    class ids:
        play = lambda aio_id: {
            "component": "PlaybackSliderAIO",
            "subcomponent": "button",
            "aio_id": aio_id,
        }
        play_icon = lambda aio_id: {
            "component": "PlaybackSliderAIO",
            "subcomponent": "i",
            "aio_id": aio_id,
        }
        slider = lambda aio_id: {
            "component": "PlaybackSliderAIO",
            "subcomponent": "slider",
            "aio_id": aio_id,
        }
        interval = lambda aio_id: {
            "component": "PlaybackSliderAIO",
            "subcomponent": "interval",
            "aio_id": aio_id,
        }

    ids = ids

    def __init__(
        self, button_props=None, slider_props=None, interval_props=None, aio_id=None
    ):
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        button_props = button_props.copy() if button_props else {}
        slider_props = slider_props.copy() if slider_props else {}
        interval_props = interval_props.copy() if interval_props else {}

        button_props["active"] = False

        super().__init__(
            [
                dbc.Button(
                    html.I(id=self.ids.play_icon(aio_id)),
                    id=self.ids.play(aio_id),
                    **button_props
                ),
                dcc.Slider(id=self.ids.slider(aio_id), **slider_props),
                dcc.Interval(id=self.ids.interval(aio_id), **interval_props),
            ]
        )

    @callback(
        Output(ids.play(MATCH), "active"),
        Output(ids.play_icon(MATCH), "className"),
        Output(ids.interval(MATCH), "disabled"),
        Input(ids.play(MATCH), "n_clicks"),
        State(ids.play(MATCH), "active"),
    )
    def toggle_play(clicks, curr_status):
        if clicks:
            text = "fa-solid fa-play" if curr_status else "fa-solid fa-pause"
            return not curr_status, text, curr_status
        return curr_status, "fa-solid fa-play", not curr_status

    @callback(
        Output(ids.slider(MATCH), "value"),
        Input(ids.play(MATCH), "active"),
        Input(ids.interval(MATCH), "n_intervals"),
        State(ids.slider(MATCH), "min"),
        State(ids.slider(MATCH), "max"),
        State(ids.slider(MATCH), "step"),
        State(ids.slider(MATCH), "value"),
    )
    def start_playback(play, interval, min, max, step, value):
        if not play:
            raise PreventUpdate

        new_val = value + step
        if new_val > max:
            new_val = min

        return new_val

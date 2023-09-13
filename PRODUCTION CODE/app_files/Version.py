import dash
from dash import Input, Output, State, html,callback
import dash_bootstrap_components as dbc
dash.register_page(__name__)
modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("VERSION SUMMARY"), close_button=True),
                dbc.ModalBody('Labor Hours: (Q2 2022 - Q3 2023)'),
                dbc.ModalBody('Labor Cost: (Burdened Rate) X (Avg. Hours) X (1.15 for Over Time)'),
                dbc.ModalBody('Material Cost: Burdened (Q3 TO CURRENT, Q2,Q1 2022, Q3,Q4 2021 Avg. in the order of last PO)'),
                dbc.ModalBody('OVS Cost: 2022 Avg.'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close",
                        id="close-centered",
                        className="ms-auto",
                        n_clicks=0,
                    )
                ),
            ],
            id="modal-centered",
            centered=True,
            is_open=True,
        ),
    ]
)
@callback(
    Output("modal-centered", "is_open"),
    Input("close-centered", "n_clicks"),
    State('modal-centered','is_open')
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open
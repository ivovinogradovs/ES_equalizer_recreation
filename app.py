#!/usr/bin/env python
# coding: utf-8

# In[33]:


from dash import Dash, dcc, html, Input, Output, State
import numpy as np
import dash

services = [
    "Timber",               # slider-rec-0
    "Climate Control",      # slider-rec-1
    "Habitat Maintenance",  # slider-rec-2
    "Water Control",        # slider-rec-3
    "Recreation"            # slider-rec-4 (active input)
]

input_index = 4  # Recreation

recreation_matrix_low = np.array([
    [-0.2, 0.1, -0.1, 0.1, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0]
])

recreation_matrix_med = np.array([
    [-0.4, 0.1, -0.3, 0.2, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0]
])

recreation_matrix_high = np.array([
    [-0.7, 0.0, -0.4, 0.2, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0]
])

recreation_matrices = {
    "Low-Impact Gathering Area": recreation_matrix_low,
    "Multi-Use Recreation Forest": recreation_matrix_med,
    "Urban Recreation Forest": recreation_matrix_high
}

#recreation_regime_weights = {
#   "Low-Impact Gathering Area": 0.6,
#   "Multi-Use Recreation Forest": 1.0,
#   "Urban Recreation Forest": 1.4
#
#}

GAMMA = 0.6

app = Dash(__name__)

app.layout = html.Div([
    html.H3("Recreation Equalizer", style={"textAlign": "center"}),

    html.Div([
        html.Label("Assessment area (ha):"),
        dcc.Input(id="input-total-area-rec", type="number", value=100, min=1, step=1),
        html.Label("Managed area (ha):", style={"marginLeft": "20px"}),
        dcc.Input(id="input-managed-area-rec", type="number", value=100, min=0, step=1)
    ], style={"display": "flex", "justifyContent": "center", "gap": "10px", "marginBottom": "20px"}),

    html.Div([
        dcc.RadioItems(
            id="regime-selector-rec",
            options=[{"label": k, "value": k} for k in recreation_matrices.keys()],
            value="Multi-Use Recreation Forest",
            inline=True,
            style={"display": "flex", "justifyContent": "center", "gap": "30px", "fontSize": "18px"}
        )
    ], style={"display": "flex", "justifyContent": "center", "marginBottom": "20px"}),

    html.Div([
        html.Div("Ecosystem Integrity", style={"textAlign": "center", "fontWeight": "bold", "marginBottom": "5px", "fontSize": "16px"}),
        dcc.Slider(
            id="ecosystem-integrity-rec",
            min=-5,
            max=5,
            step=1,
            value=0,
            marks={i: {'label': str(i), 'style': {'color': 'black'}} for i in range(-5, 6)},
            tooltip={"always_visible": False},
            included=False
        ),
        html.Div([
            html.Span("Fragile", style={"color": "black", "marginRight": "auto"}),
            html.Span("Resilient", style={"color": "black", "marginLeft": "auto"})
        ], style={"display": "flex", "justifyContent": "space-between", "width": "100%", "marginTop": "4px"})
    ], style={"width": "60%", "margin": "0 auto 30px auto"}),

    html.Div([
        html.Div([
            html.Div(service, style={
                "textAlign": "center",
                "width": "90px",
                "marginBottom": "10px",
                "whiteSpace": "nowrap",
                "wordBreak": "break-word",
                "lineHeight": "1.1"
            }),
            dcc.Slider(
                min=(0 if i == input_index else -5),
                max=5,
                step=0.1,
                value=0,
                id=f"slider-rec-{i}",
                vertical=True,
                updatemode='drag',
                marks={j: str(j) for j in range((0 if i == input_index else -5), 6)},
                tooltip={"always_visible": False},
                included=False,
                className=f"slider-{i}",
                disabled=(i != input_index)
            )
        ], style={
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "justifyContent": "flex-start",
            "width": "100px",
            "margin": "0 10px"
        })
        for i, service in enumerate(services)
    ], style={"display": "flex", "justifyContent": "center", "gap": "40px", "marginBottom": "40px"}),

    html.Div([
        html.Button("Reset", id="reset-button-rec", n_clicks=0)
    ], style={"display": "flex", "justifyContent": "flex-end", "marginRight": "60px", "marginTop": "30px"})

], style={"fontFamily": "sans-serif", "height": "100vh", "overflowY": "visible"})

@app.callback(
    [Output(f"slider-rec-{i}", "value") for i in range(5)],
    [Input(f"slider-rec-{input_index}", "value"), Input("reset-button-rec", "n_clicks")],
    [State("regime-selector-rec", "value"),
     State("input-total-area-rec", "value"),
     State("input-managed-area-rec", "value"),
     State("ecosystem-integrity-rec", "value")]
)
def update_from_recreation(rec_value, reset_clicks, regime, total_area, managed_area, integrity):
    ctx = dash.callback_context
    if not ctx.triggered or total_area is None or total_area <= 0:
        return [0] * 5

    if ctx.triggered[0]['prop_id'] == "reset-button-rec.n_clicks":
        return [0] * 5

    fraction = managed_area / total_area if managed_area and total_area else 0
    regime_weight = recreation_regime_weights[regime]
    raw_factor = fraction * regime_weight
    impact_factor = raw_factor ** GAMMA

    condition_multiplier = np.interp(integrity, [-5, 0, 5], [2.0, 1.0, 0.5])

    matrix_row = recreation_matrices[regime][0]
    result = matrix_row * rec_value * impact_factor * condition_multiplier
    result[input_index] = rec_value
    result = np.clip(result, -5, 5)

    return result.tolist()

app.run(port=8059, debug=False)


# In[ ]:





# In[ ]:





# In[ ]:





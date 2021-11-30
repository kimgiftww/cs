from dash import Dash, html, dcc, Output, Input
from callbacks import blank_fig
import dash_bootstrap_components as dbc
import pandas as pd
import os

toast = dbc.Toast(
    id="toast",
    header="Saved",
    is_open=False,
    dismissable=True,
    icon="success",
    duration=4000,
    # top: 66 positions the toast below the navbar
    style={"position": "fixed", "top": 66,
           "left": 20, "width": 300, 'z-index': '100'},
)


def drawText(textid, text, color):
    return dbc.Card([
        dbc.CardHeader(
            text, className='p-0 bg-primary text-white text-left font-weight-bold'),
        dbc.CardBody([

        ], className='p-0 text-right font-weight-bold', id=textid,  # , className='d-flex justify-content-center align-items-center font-weight-bold lead p-0',
        )  # , 'width':'100%'
    ], className='p-0 m-0 border-0')  # border-0 , color="light" , style={'padding': '0 0', 'margin': '0 0', 'font-size': 'x-large'})


zc = zip(['active', 'inactive', 'sum_premium', 'coveramount'],
         ['# Active', '# Inactive',
             'Total Premiums', 'Sum Insured'],
         ['success', 'info', 'primary', 'warning'])
cards = [drawText(textid, text, color) for textid, text, color in zc]
# , className='', style={'border-width': '3px'} p-0 m-0
# cards = dbc.CardGroup(cards, className='p-0 m-0 border-primary',
#                       style={'border-width': '3px'})
cards = dbc.Card(
    dbc.CardGroup(cards),
    className='p-0 m-0 border-primary', style={'border-width': '3px'})


cards_sublimit = dbc.CardGroup(id='cards_sublimit')
# , style={'margin-bottom': '5px'}
cards_dd = dbc.Collapse(id='cards_dd_col', is_open=False)
# cards_chart = dbc.Collapse(
#     dbc.CardGroup(id='cards_chart'),
#     id='cards_chart_col', is_open=True
# )


def drawSwitch(sw, text):
    return dbc.Card([
        dbc.CardHeader(
            dbc.Badge(text, href="#", color="secondary", pill=True,  # className="border",  # me-1
                      n_clicks=0, style={'font-size': 'small'}, id=text),
            className='d-flex justify-content-center align-items-center p-0 m-0',
        ),
        dbc.CardBody(sw, className='d-flex justify-content-center align-items-center p-0',
                     )  # 'height': '50px',
    ], color="light", className='p-0 m-0')


layoutl = ['Chart', 'Table', 'Map']
layoutd = [{"label": l, "value": l} for l in layoutl]
radio_layout = html.Div(
    dbc.RadioItems(
        options=layoutd, value='Chart', id="radio_layout", className="btn-group",
        labelClassName="btn btn-primary p-1 m-0", labelCheckedClassName="active"),
    className="radio-group")
radio_layout = [
    dbc.Checklist(options=[{'label': 'Summary', 'value': 1}], value=[1],
                  id='summary', switch=True, className='mx-3'),
    dbc.Checklist(options=[{'label': 'Insurer', 'value': 1}], value=[1],
                  id='insurer_col', switch=True, className='mr-3 my-0'),
    # dbc.Checklist(options=[{'label': 'Chart', 'value': 0}], value=[1],
    #               id='ccg', switch=True, className='mr-3 my-0'),
    radio_layout
]

rl = ['Flood', 'Storm', 'Hail', 'Quake', 'Sum']
rld = [{'label': i, 'value': i, 'disabled': False} for i in rl[:-1]]
# rld = rld + [{'label': i, 'value': i, 'disabled': True} for i in rl[-1:]]
radio_nd = html.Div(
    dbc.RadioItems(
        options=rld, value='Flood', id="radio_nd", className="btn-group",
        labelClassName="btn btn-primary p-1 m-0", labelCheckedClassName="active"), className="radio-group")

# quotal = ['Safe', 'Warning', 'Alert']
# quotad = [{'label': q, 'value': q} for q in quotal]
# quota_level = [
#     dbc.Checklist(options=quotad,  value=quotal,
#                   id='quota', inline=True) # , className='mx-3'
# ]

radio_nd = [
    radio_nd,
    dbc.Checklist(options=[{'label': 'Quota Map', 'value': 1}],  # value=[1],
                  id='map', switch=True, className='mx-2'),
]

zs = zip([radio_layout, radio_nd],  # afr,  mrr, dd
         ['Layout', 'Natural Disaster'])  # , 'Policy Type', 'Quota Level', 'Insurer'
cards_switch = [drawSwitch(sw, text) for sw, text in zs]
cards_switch = dbc.CardGroup(cards_switch, style={'width': '100%'})

img = html.Img(id='img',
               style={"width": "45px", "height": "45px",
                      "border-radius": "50%", "vertical-align": "middle",
                      'margin-left': '0.6rem', 'margin-right': '0.6rem'})
btn = [
    dbc.Badge('Logout', color="danger", pill=True, href='#',
              id='logout'),  # , className='m-0'
    dbc.Collapse(
        html.Div([
            dbc.Badge('Export', color="secondary", pill=True, href='#',
                      id='exportbtn'),
            dbc.Badge('Save', color="success", pill=True, href='#',
                      id='savebtn'),  # , className='p-0'
            dbc.Badge('Upload', color="warning", pill=True,  # href='#'
                      id='uploadbtn'),  # , className='p-0'

        ], className='d-flex justify-content-between'),
        id='btn_col', is_open=False)
]

btn = [
    dbc.Row([
        dbc.Col(
            html.Div(id='test'),
            className='d-flex align-items-start')  # justify-content-center mx-2
    ], no_gutters=True),
    dbc.Row([
        dbc.Col(
            btn,
            className='d-flex justify-content-between')  # align-items-center mx-2
    ], no_gutters=True)
]

search_bar = dbc.Row([
    dbc.Col(img, width='auto'),  # , style={"width": "2rem"}
    dbc.Col(btn, width='auto')  # , className='d-flex justify-content-start'
], no_gutters=True)  # , align="center", justify='between'

navbar = dbc.Navbar([
    html.Div(search_bar, style={'width': '18.8rem'}),
    html.Div(
        dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
        style={'padding': '0 0.6rem'}),
    dbc.Collapse(
        cards_switch, id="navbar-collapse", is_open=False, navbar=True)  # , style={'width': '75%'}
], style={'padding': '0 0 0 0'}, className='fixed-bottom pb-0')  # 0 0 0 0.6rem 'sidebar'


def init_dashboard(app, prefix):
    da = Dash(
        # server=app,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        assets_folder=f'{prefix}',  # 'assets', #
        assets_url_path=f'/{prefix}',
        routes_pathname_prefix=f'/{prefix}/',
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

    if prefix == 'dash_tqm':
        # from callbacks_a import init_callback_a
        # init_callback_a(da)
        from callbacks import init_callback
        init_callback(da)
        # print('successfully init_callbacks_a')
        from sidebar import sidebar
        print('successfully sb_a')
        da.layout = html.Div([
            dcc.Location(id="location"),
            sidebar,
            toast,
            html.Div([
                navbar,
                dbc.Collapse([cards, cards_sublimit, cards_dd],  # , cards_chart
                             is_open=True, id='cc'),
                html.Div(dbc.Row([
                    dbc.Col(id='sim'),  # , width=12
                    dbc.Col(
                        dbc.Collapse(
                            dcc.Graph(figure=blank_fig(), id='heatmap_nd', responsive=True,
                                      config=dict(displaylogo=False, autosizable=True)),
                            id='slm_col', is_open=False),
                        id='slm', width='auto')
                ], no_gutters=True),
                    id='main_map'),
                html.Div(id='main'),  # , style={'height': 'auto'}
            ], id="page-content")  # , style={'height': '100vh'}
        ])

        da.title = 'Accumulation'

    return da
    # return da.server

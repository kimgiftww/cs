from dash import html, dcc
import dash_bootstrap_components as dbc
from callbacks import region_cd, rcl
import pandas as pd

popover_insurer = dbc.Popover(
    id="popover_insurer",
    target="Insurer",  # dd1 Accumulation
    trigger="legacy",
    placement="left",
    style={'height': '0'},
)

sidebar_header = dbc.Row([
    dbc.Col([
        dbc.Badge("RMS", pill=True, color="primary",  # className="ms-1",
                  href="#", n_clicks=0, style={'font-size': 'x-large'}, id="Accumulation"),
    ]),
    dbc.Col([
        html.Button(
            html.Span(className="navbar-toggler-icon"),
            className="navbar-toggler",
            style={"color": "rgba(0,0,0,.5)",
                   "border-color": "rgba(0,0,0,.1)"},
            id="navbar-toggle",
        ),
        html.Button(
            html.Span(className="navbar-toggler-icon"),
            className="navbar-toggler",
            style={
                "color": "rgba(0,0,0,.5)",
                "border-color": "rgba(0,0,0,.1)",
            },
            id="sidebar-toggle")
    ], width='auto')  # , align='end'
], no_gutters=True)  # , justify='between' , className="ml-auto flex-nowrap" mt-3 mt-md-0 )

af = [{"label": "Active", "value": 0},
      {"label": "Inactive", "value": 1}]
mr = [{"label": "TQM", "value": 0, 'disabled': True},
      {"label": "TQR", "value": 1, 'disabled': True}]
afr = dbc.Checklist(options=af, value=[0, 1], inline=True, id="future")
mrr = dbc.RadioItems(options=mr, value=0, inline=True, id="MR")
suppliercode = pd.read_pickle('data/sc.pickle').suppliercode
sc = [{'label': c, 'value': c} for c in suppliercode]
all_region = [{"label": "All", "value": 1}]
all_province = [{"label": "All", "value": 1}]
all_district = [{"label": "All", "value": 1}]

quotal = ['Safe', 'Warning', 'Alert']
quotad = [{'label': q, 'value': q} for q in quotal]
btn_quota = dbc.Row([
    dbc.Col(html.H6(dbc.Badge('%Quota', href='#')), width='auto')])

btn_region = dbc.Row([
    dbc.Col(html.H6(dbc.Badge('Region', href='#')), width='auto'),
    dbc.Col(dbc.Checklist(options=all_region, value=[1], id='all_region',
            switch=True, className='mx-3')),
    # dbc.Col(html.H6(dbc.Badge('Clear', href='#', n_clicks=0, id='region_clear')))
], no_gutters=True)
btn_province = dbc.Row([
    dbc.Col(html.H6(dbc.Badge('Province', href='#')), width='auto'),
    dbc.Col(dbc.Checklist(options=all_province, value=[1], id='all_province',
            switch=True, className='mx-3')),
    # dbc.Col(html.H6(dbc.Badge('Clear', href='#', n_clicks=0, id='region_clear')))
], no_gutters=True)
btn_district = dbc.Row([
    dbc.Col(
        html.H6(
            dbc.Badge('District', href='#',  # color='secondary',
                      id='level_district_click', n_clicks=0)
        ), width='auto'),
    dbc.Col(
        dbc.Collapse(
            dbc.Checklist(options=all_district, id='all_district',
                          switch=True, className='mx-3'),
            id='level_district', is_open=False
        )
    ),  # , value=1
    # dbc.Col(html.H6(dbc.Badge('Clear', href='#', n_clicks=0, id='region_clear')))
], no_gutters=True)

sidebar = html.Div([
    popover_insurer,
    sidebar_header,  #
    dbc.Collapse([
        dbc.Row([
            dbc.Col([
                html.H6(dbc.Badge('Insurer', href='#', id='Insurer')),
                html.Div(
                    dbc.Checklist(id="dd1", options=sc, value=suppliercode, inline=True,
                                     inputClassName='mx-1 mt-0'),  # labelClassName='m-0'
                )  # , 'text-align': 'left' 360px , 'margin-bottom': '20px'
            ])
        ], style={'margin-bottom': '5px'}),
        dbc.Row([
            dbc.Col([
                html.H6(dbc.Badge('Policy Type', href='#')),
                afr]),
            dbc.Col([
                html.H6(dbc.Badge('Quota Level', href='#')),
                mrr
            ])
        ], style={'margin-bottom': '5px'}),
        dbc.Row([
            dbc.Col([
                btn_quota,
                html.Div(
                    dbc.Checklist(id='quota', options=quotad, inline=True,
                                  value=quotal)
                )
            ])
        ], style={'margin-bottom': '5px'}),

        dbc.Row([
            dbc.Col([
                btn_region,
                html.Div(
                    dbc.Checklist(id="region", options=region_cd, inline=True,  # value=rcl, # ['C'],
                                  inputClassName='m-1'),  # labelClassName='m-0'
                )  # , 'text-align': 'left' 360px , 'margin-bottom': '20px'
            ])
        ], style={'margin-bottom': '5px'}),
        dbc.Row([
            dbc.Col([
                btn_province,
                html.Div(
                    dbc.Checklist(id="province",  # value=['C_Pathum Thani'],
                                  className='small'),
                    style={'overflowY': 'scroll', 'height': '150px'})  # , 'text-align': 'left' 360px ,
            ])
        ], style={'margin-bottom': '5px'}),
        dbc.Row([
            dbc.Col([
                btn_district,
                dbc.Collapse(
                    html.Div(
                        dbc.Checklist(id="district",  # value=['C_Pathum Thani_Lam Luk Ka'],
                                      className='small'),
                        style={'overflowY': 'scroll', 'height': '150px'}),  # 'calc(100vh - 580px)' , 'text-align': 'left' 360px , 'margin-bottom': '20px'
                    id='level_district_c'
                )
            ])
        ]),
        # dbc.Row(
        #     dbc.Col(
        #         html.Div(
        #             html.Img(src='/dash_tqm/dash_tqm/android-chrome-192x192.png'),
        #             style={'text-align': 'center'}
        #         )
        #     )
        # )
    ], id="collapse")  # , navbar=True
], style={'text-align': 'left'}, id="sidebar")

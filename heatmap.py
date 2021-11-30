from dash import dcc  # , html  # Dash, # from data import ndmap
import dash_bootstrap_components as dbc
# import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import math

colorscale = [
    # 'white',
    # '#858789',
    # "#f7fbff",
    # "#f2fffb",
    "#4292c6",
    #     "#3082be",
    #     "#2171b5",
    "#1361a9",
    #     "#08519c",
    #     "#0b4083",
    "#08306b",
    'yellow',  # "#070C6B",
    'red'  # "#26076B"
]

classes = [1, 50000000, 100000000, 500000000, 1000000000]  # 1000000
ii = pd.IntervalIndex.from_breaks(classes + [math.inf])
colorclasses = [f'<{c:,.0f}' for c in classes[1:]] + \
    [f'>{classes[-1]:,.0f}']

cs = ['#00B74A', '#FFA900', '#F93154']  # "#f2fffb", "#bbffeb", "#10523e"
p = [0, 60, 80]  # 20, 40,
colorp = [f'<{c:,.0f}%' for c in p[1:]] + ['>80%']  # <100%
iq = pd.IntervalIndex.from_breaks(p + [math.inf])  # [100]

cd = dict(colorscale=colorscale,
          colorclasses=colorclasses,
          cs=cs,
          colorp=colorp)


def dfmm(dfm, ndl):
    # ndl = [nd, 'q_'+nd]
    # print(dfm)
    dfm[ndl] = dfm[ndl].astype(int)
    dfmg = dfm.groupby('R_P_A')[ndl].sum().reset_index()
    # print(dfmg)
    if len(ndl) > 1:

        dfmg['Percent'] = (dfmg[ndl[0]] / dfmg[ndl[1]])*100
        dfmg['qtext'] = dfmg.R_P_A + '<br>' + \
            dfmg.apply(lambda x: f'{x[ndl[0]]:,.0f} THB ({x.Percent:,.2f}%)', axis=1)
        col = ['R_P_A', 'qtext', 'Percent']  # , nd

    else:
        dfmg['text'] = dfmg.R_P_A + '<br>' + \
            dfmg['coveramount'].apply(lambda x: f'{x:,.0f} THB')
        col = ['R_P_A', 'text', 'coveramount']

    df = pd.read_pickle('data/gi.pickle')
    dfmm = df.merge(dfmg[col],
                    left_on='R_P_A', right_on='R_P_A', how='left')

    print(dfmm)
    dfmm = dfmm.dropna(subset=col).rename(columns={'R_P_A': 'name'})
    print('dfmm', len(dfmm), dfmm.columns)
    return dfmm


# def dfmmp(dfm, nd):
#     ndl = [nd, 'q_'+nd]
#     dfm[ndl] = dfm[ndl].astype(int)
#     dfmg = dfm.groupby('PROVINCE')[ndl].sum().reset_index()

#     dfmg['Percent'] = (dfmg[nd] / dfmg['q_'+nd])*100

#     dfmg['text'] = dfmg.PROVINCE + '<br>' + \
#         dfmg[nd].apply(lambda x: f'{x:,.0f} THB')

#     dfmg['qtext'] = dfmg.PROVINCE + '<br>' + \
#         dfmg['Percent'].apply(lambda x: f'{x:,.2f} %')

#     df = pd.read_pickle('data/province.pickle')
#     dfmm = df.merge(dfmg[['PROVINCE', 'text', 'qtext', nd, 'Percent']],
#                     left_on='PROVINCE', right_on='PROVINCE', how='left')

#     dfmm = dfmm.dropna(subset=[nd]).rename(columns={'PROVINCE': 'name'})
#     print('dfmm', len(dfmm), dfmm.columns)
#     return dfmm


def nation(dfmm, ndl, level_district):

    if len(ndl) > 1:
        x = pd.cut(dfmm['Percent'], iq)  # nd suffix is drop
        x.cat.categories = colorp
        y = x.copy()
        y.cat.categories = cs
        # dfmms['qrange'] = x
        dfmm['qcolor'] = y
        q = ['qtext', 'qcolor', 'Percent']  # + [nd]

    else:
        x = pd.cut(dfmm['coveramount'], ii)
        x.cat.categories = colorclasses
        # dfmms['range'] = x
        y = x.copy()
        y.cat.categories = colorscale
        dfmm['color'] = y
        q = ['text', 'color', 'coveramount']

    print('dfmm', len(dfmm), dfmm.columns)

    c = ['name', 'geometry', 'lat', 'lon'] + q  # , 'q_'+nd

    return dfmm[c].reset_index()  # .rename(columns={nd: 'density'})
    # return dfmm.rename(columns={nd: 'density'})


def heatmap(dfmms, nd, is_open, ccb, cct, cd1, cd2, t):

    # marker = dict(
    #     # size=10,
    #     color="white",
    #     # opacity=1,
    #     # symbol=dfmms.symbol
    # )

    data = [dict(
        type="scattermapbox",
        lat=dfmms.lat,
        lon=dfmms.lon,
        text=dfmms[cct],  # , dfmms.text
        hoverinfo="text",
        # marker=marker  # dict(symbol=[None]*len(dfmms))  #
    )]

    tt = f"<b>{t} {nd}</b>" if nd != 'coveramount' else '<b>Sum Insured</b>'
    annotations = [
        dict(
            showarrow=False,
            align="right",
            text=tt,
            font=dict(color="black", size=14),  # 2cfec1
            # bgcolor="#1f2630",
            x=0.95,
            y=0.95,
        )
    ]

    # enum = enumerate(zip(colorscale, colorclasses))
    enum = enumerate(zip(cd[cd1], cd[cd2]))
    for i, [bin, c] in enum:
        annotations.append(
            dict(
                arrowcolor=bin,  # color,
                text=f"<b>{c}</b>",
                x=0.95,
                y=0.85 - (i / 20),
                ax=-95,
                ay=0,
                arrowwidth=5,
                arrowhead=0,
                # bgcolor="#1f2630",
                font=dict(color="black", size=12),  # 2cfec1
            )
        )

    # k = "pk.eyJ1Ijoic3RlZmZlbmhpbGwiLCJhIjoiY2ttc3p6ODlrMG1ybzJwcG10d3hoaDZndCJ9.YE2gGNJiw6deBuFgHRHPjg"
    layout = dict(
        mapbox=dict(
            layers=[],
            # accesstoken=k,
            style="carto-positron",  # white-bg "open-street-map",  # dark light satellite-streets
            center=dict(lat=13.149, lon=101.493),
            zoom=4.5,
        ),
        # title=dict(text='Kim'),
        hovermode="closest",
        # width='1',
        # height='100%',
        margin=dict(r=0, l=0, t=0, b=0),
        # margin=dict(l=0, r=0, t=0, b=0, pad=0, autoexpand=True),
        annotations=annotations,
        dragmode="move",  # lasso
    )

    # for bin in colorscale:
    for bin in cd[cd1]:
        dfmmsc = dfmms.loc[dfmms[ccb] == bin]
        # dfmmsc = dfmms.loc[dfmms['color'] == bin]
        geo_layer = dict(
            sourcetype="geojson",
            source=dfmmsc['geometry'].__geo_interface__,
            type="fill",
            color=bin,
            opacity=0.65,
            # CHANGE THIS
            # fill=dict(outlinecolor="#afafaf"),
        )
        layout["mapbox"]["layers"].append(geo_layer)

    # hopen = {'height': 'calc(100vh - 109px)'}
    # hclose = {'height': 'calc(100vh - 50px)'}
    # h = hopen if is_open else hclose

    return dict(data=data, layout=layout)
    # return dcc.Graph(figure=dict(data=data, layout=layout), id=f'heatmap_{si_nd}', style=h)

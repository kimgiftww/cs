from requirements import *
import plotly.express as px
import plotly.graph_objects as go
region_c = pd.read_pickle('data/hdg.pickle').region_c.dropna().unique()
region_c = np.sort(region_c)
region_cd = [{'label': i, 'value': i} for i in region_c]
rcl = list(region_c)  # + ['All']
num = ['saleid', 'sum_premium', 'coveramount']


def levelf(x):
    if x > 80:
        return 'Alert'
    elif x > 60:
        return 'Warning'
    else:
        return 'Safe'


def drawSub(text, substr, cards_dd_col, nd):
    cn = 'm-0 p-0 border-0'  # border-info
    bm = '3px solid' if not cards_dd_col else 0
    if text == nd:
        cn = 'm-0 p-0 border-info'
    return dbc.Card([
        dbc.CardHeader(
            f'Sublimit {text}',
            className='p-0 m-0 border-0 bg-info text-white text-left font-weight-bold'),
        dbc.CardBody(
            substr,
            className='p-0 m-0 text-right font-weight-bold')
    ], className=cn, style={'border-left': '3px solid',
                            'border-bottom': bm,
                            'border-width': '3px', })


def drawSubdd(text, nd, dfm):
    dd_sublimit = dfm.loc[dfm.suppliercode == text][nd].sum()
    dd_quota = dfm.loc[dfm.suppliercode == text]['q_'+nd].sum()
    dd_percent = round((dd_sublimit/dd_quota)*100, 2)
    return dbc.Card([
        dbc.CardHeader(text, className='p-0 m-0 text-left'),  # bg-white
        dbc.CardBody([
            html.Small(f'{dd_sublimit:,.0f} THB ({dd_percent}%)')
        ], className='p-0 m-0 text-right')
    ], className='p-0 m-0 border-0')


def prep_data(gb, nd, future, dd1, province, district, quota, level_district):

    ndfl = ['Flood', 'Storm', 'Hail', 'Quake']
    ndql = ['q_'+nd for nd in ndfl]
    ndl = ndfl+ndql
    col = gb+num+ndl
    dfm = pd.read_pickle('data/hdg.pickle')[col].fillna(0)  # +ndq
    dfm.future = dfm.future.astype(int)
    print('\ndfm unfiltered', len(dfm), dfm.columns, dfm.nunique())

    # filter
    # dd1 = [] if not dd1 else dd1
    dfm = dfm.loc[dfm.suppliercode.isin(dd1)]
    if level_district:
        # district = [] if not district else district
        dfm = dfm.loc[dfm.R_P_A.isin(district)]
        print('dfm.sum()', dfm.sum())
    else:
        fc = num + ndl + ['num_district']
        dfm = dfm.loc[dfm.R_P.isin(province)]
        dfm['num_district'] = 0
        dfm.loc[dfm.future == 0, 'num_district'] = 1
        dfm = dfm.groupby(gb[:5])[fc].sum().reset_index()
        # print('dfm.sum()', dfm.sum())
    print('\ndfm filtered', len(dfm), dfm.columns, dfm.nunique())
    active = f'{dfm.loc[dfm.future==0].saleid.sum():,.0f} Policies'
    inactive = f'{dfm.loc[dfm.future==1].saleid.sum():,.0f} Policies'

    # future
    print('future', future)
    fg = gb[1:] if level_district else gb[1:4]
    print('fg', fg)
    if len(future):
        if len(future) == 1:
            cf = fg + num + ndl if level_district else \
                fg + num + ndl + ['num_district']
            dfm = dfm.loc[dfm.future == future[0]
                          ][cf]
        else:
            cf = num + ndl if level_district else \
                num + ndl + ['num_district']
            dfm = dfm.groupby(
                fg)[cf].sum().reset_index()
    else:
        dfm = dfm.iloc[:0][fg + num + ndl]  # .loc[dfm.future == future]
    # print('dfm futured', len(dfm), dfm.columns, dfm.nunique())

    # Percent
    dfm['Percent'] = round((dfm[nd]/dfm['q_'+nd])*100, 2)
    dfm['Level'] = [levelf(x) for x in dfm.Percent]
    dfm['Count'] = 1

    # Quota Level
    dfm['Quota'] = 'Safe'
    dfm.loc[dfm.Percent > 60, 'Quota'] = 'Warning'
    dfm.loc[dfm.Percent > 80, 'Quota'] = 'Alert'
    dfm = dfm.loc[dfm.Quota.isin(quota)]

    # Summary / Sublimit / Insurer Cards
    sum_premium = f'{dfm.sum_premium.sum():,.0f} THB'
    coveramount = f'{dfm.coveramount.sum():,.0f} THB'

    return dfm, active, inactive, sum_premium, coveramount


def init_callback(dashapp):

    # login

    @dashapp.callback([Output('test', 'children'), Output('img', 'src')], Input('location', 'pathname'))
    def test(path):
        if session:
            print(session, path)
            x = session['profile']
            return x['email'], x['picture']
        return None, None

    # logout

    @dashapp.callback(Output('location', 'pathname'), Input('logout', 'n_clicks'))
    def click_logout(nc):
        if nc:
            session.clear()
            print(session)  # ; redirect('/')#; layout = layout0
            return '/tqm'

    # add callback for toggling the collapse on small screens

    @dashapp.callback(Output("sidebar", "className"), [Input("sidebar-toggle", "n_clicks")], [State("sidebar", "className")])
    def toggle_classname(n, classname):
        if n and classname == "":
            return "collapsed"
        return ""

    @dashapp.callback(Output("collapse", "is_open"), [Input("navbar-toggle", "n_clicks")], [State("collapse", "is_open")])
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    @dashapp.callback(Output("navbar-collapse", "is_open"), [Input("navbar-toggler", "n_clicks")], [State("navbar-collapse", "is_open")])
    def toggle_navbar_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    # popover_insurer

    @dashapp.callback(Output("popover_insurer", "is_open"), Output("popover_insurer", "children"), Input("Insurer", "n_clicks"), State("dd1", "value"))
    def popover_insurer(test, dd1):
        if test:
            # print('dd1', dd1, len(dd1))
            sc = pd.read_pickle('data/sc.pickle')

            sc = sc.loc[sc.suppliercode.isin(dd1)]
            # print('dd2', len(sc))
            sc = dbc.Table.from_dataframe(sc,
                                          striped=True, bordered=True, hover=True,
                                          style={'background-color': 'white',
                                                 'width': '385px'},
                                          id='sc')
            return True, sc  # , 'info' , Output('sc','color')
        else:
            return False, None

    # hide summary

    @ dashapp.callback(Output("cc", "is_open"),
                       #    Output("heatmap_si", "style"),
                       #    Output("heatmap_nd", "style"),
                       #    Input('radio_layout', 'value'),
                       Input('summary', 'value'))
    def hide_summary(summary):
        hopen = {
            'height': 'calc(100vh - 109px)'}  # if radio_layout == 'Map' else None
        hclose = {
            'height': 'calc(100vh - 50px)'}  # if radio_layout == 'Map' else None
        # h = hopen if summary else hclose
        if summary:
            return True,  # hopen, hopen
        else:
            return False,  # hclose, hclose

    # hide insurer_col

    @ dashapp.callback(Output("cards_dd_col", "is_open"),
                       Input('insurer_col', 'value'), Input('dd1', 'value'))
    def hide_insurer(insurer_col, dd1):
        if insurer_col:
            if len(dd1) > 1:
                return True
            else:
                return False
        else:
            return False

    # hide district

    @ dashapp.callback(Output("level_district_click", "color"), Output("level_district", "is_open"), Output("level_district_c", "is_open"), Output('level_district_click', 'n_clicks'),
                       Input('level_district_click', 'n_clicks'), State('level_district', 'is_open'))
    def hide_district(ncs, is_open):
        not_open = not is_open
        not_color = 'primary' if not_open else 'secondary'
        if ncs:
            return not_color, not_open, not_open, 0
        else:
            return 'secondary', False, False, 0

    # dynamic checkbox

    @dashapp.callback(Output("province", "options"),  # Output("province", "value"),
                      #   Output("region", "value"),
                      Input("region", "value"), State("region", "value"))  # , Input("province", "value")
    def dynamic_ckl_p(region, regions):  # , province
        # region = regions if not region else region
        # print('region', region, regions)
        dfm = pd.read_pickle('data/gi.pickle')[['region_c', 'R_P']]
        provincel = dfm.loc[dfm.region_c.isin(region), 'R_P'].unique()
        provincel = np.sort(provincel)
        provinced = [{'label': i, 'value': i} for i in provincel]
        return provinced

    @ dashapp.callback(Output("district", "options"),  # Output("district", "value"),
                       Input("province", "value"))  # , Input("district", "value")
    def dynamic_ckl_d(province):  # , district
        dfm = pd.read_pickle('data/gi.pickle')[['R_P', 'R_P_A']]
        # province = [] if not province else province # Is this line important?
        districtl = dfm.loc[dfm.R_P.isin(province), 'R_P_A']
        districtl = np.sort(districtl)
        districtd = [{'label': i, 'value': i} for i in districtl]
        return districtd

    # all
    opa = [Output("region", "value"),
           Output("province", "value"), Output("district", "value")]
    ipa = [Input("all_region", "value"),
           Input("all_province", "value"), Input("all_district", "value")]
    spa = [State("region", "value"),
           State("province", "value"), State("province", "options"),
           State("district", "value"), State("district", "options")]

    @dashapp.callback(opa, ipa, spa)
    def all_chk(all_region, all_province, all_district,
                region, province, provinceo, district, districto):

        print('all_chk', all_region, all_province, all_district,
              region, province, provinceo, district, districto)

        changed_id = [p['prop_id'] for p in callback_context.triggered][0]
        print('changed_id', changed_id)
        if 'all_region' in changed_id:
            if all_region:
                return rcl, province, district
            else:
                return [], [], []
        elif 'all_province' in changed_id:
            provincel = [p['value'] for p in provinceo]
            if all_province:
                return region, provincel, district
            else:
                return region, [], district
        elif 'all_district' in changed_id:
            districtl = [d['value'] for d in districto]
            if all_district:
                return region, province, districtl
            else:
                return region, province, []
        elif changed_id == '.':
            return rcl, pd.read_pickle('data/gi.pickle').R_P.unique(), []
        else:
            return region, province, district

# select table / graph

    nmo = [Output('active', 'children'), Output('inactive', 'children'),
           Output('sum_premium', 'children'), Output('coveramount', 'children')]
    ndfl = ['Flood', 'Storm', 'Hail', 'Quake']
    cgo = [Output('cards_sublimit', 'children'),
           Output('cards_dd_col', 'children'), ]
    ipl = [Input('radio_layout', 'value'),  Input('radio_nd', 'value'),
           Input('future', 'value'), Input('dd1', 'value'),
           Input('province', 'value'), Input('district', 'value'),
           Input('quota', 'value'),
           Input("cc", "is_open"), Input("level_district", "is_open"), Input("cards_dd_col", "is_open")]

    @ dashapp.callback([Output('main', 'children')]+nmo+cgo, ipl)
    def select_content(layout, nd, future, dd1, province, district, quota,
                       cc_is_open, level_district, cards_dd_col):

        # print(future, dd1, district, nd)
        gb = ['future', 'suppliercode',
              'region_c', 'PROVINCE', 'R_P',
              'DISTRICT', 'R_P_A']
        dfm, active, inactive, sum_premium, coveramount = prep_data(
            gb, nd, future, dd1, province, district, quota, level_district)

        s, p, quota = {}, {}, {}
        for ndf in ndfl:
            s[ndf] = dfm[ndf].sum()
            quota[ndf] = dfm["q_"+ndf].sum()
            p[ndf] = round((s[ndf]/quota[ndf])*100, 2)
            s[ndf] = f'{s[ndf]:,.0f} THB ({p[ndf]:,.2f}%)'

        s = [drawSub(ndf, s[ndf], cards_dd_col, nd) for ndf in ndfl]
        cdd = dbc.Card(
            dbc.CardGroup([drawSubdd(dd, nd, dfm) for dd in dd1]),
            className='p-0 m-0 border-info', style={'border-width': '3px'})

        ndl = [nd, 'q_'+nd]
        if layout == 'Table':
            from table import table
            if level_district:
                tc = gb[1:]+num+ndl+['Percent']
                main = table(dfm[tc], cc_is_open, nd)
            else:
                tc = gb[1:4]+['num_district']+num+ndl+['Percent']
                # dbct = dfm[tc].groupby('PROVINCE')[tc]

                def dbc_table(ql, color):
                    dfm_dbct = dfm[tc].loc[dfm.Quota == ql].copy()
                    dfm_dbct = dfm_dbct.sort_values(
                        by='Percent', ascending=False)
                    dfm_dbct.Percent = dfm_dbct.Percent.astype(str) + '%'
                    dfm_dbct.saleid = [
                        f'{x:,.0f}' for x in dfm_dbct.saleid]
                    dfm_dbct.sum_premium = [
                        f'{x:,.0f}' for x in dfm_dbct.sum_premium]
                    dfm_dbct.coveramount = [
                        f'{x:,.0f}' for x in dfm_dbct.coveramount]
                    dfm_dbct[nd] = [f'{x:,.0f}' for x in dfm_dbct[nd]]
                    dfm_dbct['q_' +
                             nd] = [f'{x:,.0f}' for x in dfm_dbct['q_'+nd]]
                    cd = {'suppliercode': 'Insurer',
                          'region_c': 'Region',
                          'PROVINCE': 'Province',
                          'num_district': 'Total Districts',
                          'saleid': 'Total Policies',
                          'sum_premium': 'Total Premiums',
                          'coveramount': 'Total Sum Insured',
                          nd: 'Sublimit ' + nd,
                          'q_'+nd: 'Quota Sublimit ' + nd}
                    dfm_dbct.rename(columns=cd, inplace=True)
                    return dbc.Card(
                        dbc.Table.from_dataframe(
                            dfm_dbct,
                            className='p-0 m-0 text-right',
                            striped=True,
                            bordered=True,
                            hover=True),
                        className=f'p-0 m-0 border-{color}',
                        style={'border-width': '3px'})

                main = html.Div([
                    dbc_table('Alert', 'danger'),
                    dbc_table('Warning', 'warning'),
                    dbc_table('Safe', 'success'),
                    # html.Br(), html.Br()
                ], style={'padding-bottom': '55px'})
                # style={'background-color': 'white'})
                # main = dbc.table(dfm[tc], cc_is_open, nd)

        elif layout == 'Chart':
            import dash_table
            from data import stylesall, df_data_all, data_columns
            topen = {'overflowY': 'scroll', 'height': 'calc(100vh - 215px)'}
            tclose = {'overflowY': 'scroll', 'height': 'calc(100vh - 50px)'}
            t = topen if cc_is_open else tclose
            main = html.Div([
                dash_table.DataTable(
                    data=df_data_all,
                    columns=data_columns,
                    merge_duplicate_headers=True,
                    # page_action='none', # ห้ามเอา page_action ออก เพราะ load ไม่ไหว
                    sort_action='native',
                    style_data_conditional=stylesall,
                    style_table=t,
                    id='table1')
            ])
        else:
            main = None

        return main, active, inactive, sum_premium, coveramount, s, cdd

from dash_table.Format import Format, Group, Scheme, Symbol  # , Prefix,
# from dash_table import FormatTemplate
from dash import dash_table
# from callbacks import num
from layout import rl


style = [{
    'if': {
        'filter_query': '{Percent} < 60',
        'column_id': 'Percent'
    },
    'backgroundColor': 'green',
    'color': 'inherit'
},
    {
    'if': {
        'filter_query': '{Percent} >= 60 && {Percent} < 80',
        'column_id': 'Percent'
    },
    'backgroundColor': 'yellow',
    'color': 'inherit'
},
    {
    'if': {
        'filter_query': '{Percent} >= 80',
        'column_id': 'Percent'
    },
    'backgroundColor': 'red',
    'color': 'inherit'
}]


def table(df, is_open, nd):  # , height

    col = ['Percent', 'q_'+nd, nd,
           '#Policies', 'Total Premiums', 'Sum Insured',
           'suppliercode', 'region_c', 'PROVINCE', 'DISTRICT']
    df.rename(columns={'coveramount': 'Sum Insured',
                       'sum_premium': 'Total Premiums',
                       'saleid': '#Policies'}, inplace=True)
    df = df[col].sort_values(by=['Percent', nd], ascending=False)
    records = df.to_dict('records')

    center_align = [{
        'if': {'column_id': c},
        'textAlign': 'center'
    } for c in ['suppliercode', 'region_c', 'PROVINCE', 'Percent']]
    left_align = [{
        'if': {'column_id': c},
        'textAlign': 'left'
    } for c in ['DISTRICT']]

    ndl = ['Percent', 'q_'+nd, nd]
    num = ['#Policies', 'Total Premiums', 'Sum Insured']
    ccc = ndl+num
    print('ccc', ccc)
    scc = [{'if': {'column_id': c}, 'width': '10%'} for c in ccc[1:]]
    print('scc', scc)
    scc = center_align + left_align + scc

    cols = []
    for i in df.columns:
        if i in ccc:
            print(i)
            if i == 'Total Premiums':
                cols.append({"name": i, "id": i, 'type': 'numeric',
                             'format': Format(group=',', precision=2, scheme=Scheme.fixed)})
            elif i == 'Percent':
                cols.append({"name": i, "id": i, 'type': 'numeric',
                             'format': Format(symbol=Symbol.yes, symbol_suffix='%')})
            elif 'q_' in i:
                cols.append({"name": i, "id": i, 'type': 'numeric',
                             'format': Format(group=','), 'editable': True})
            else:
                cols.append({"name": i, "id": i, 'type': 'numeric',
                             'format': Format(group=',')})
        else:
            if i == 'suppliercode':
                cols.append({"name": 'Insurer', "id": i})
            elif i == 'region_c':
                cols.append({"name": 'Region', "id": i})
            elif i == 'PROVINCE':
                cols.append({"name": 'Province', "id": i})
            elif i == 'DISTRICT':
                cols.append({"name": 'District', "id": i})
            else:
                cols.append({"name": i, "id": i})  # , 'editable': False
    print(cols)

    topen = {'overflowY': 'scroll', 'height': 'calc(100vh - 215px)'}
    tclose = {'overflowY': 'scroll', 'height': 'calc(100vh - 50px)'}
    t = topen if is_open else tclose
    return dash_table.DataTable(data=records, columns=cols,
                                page_action='none',  # virtualization=True,
                                export_format='xlsx', export_headers='display',
                                # fixed_rows={'headers': True, 'data': 0},
                                style_data_conditional=style,
                                style_cell={'font_size': '12px',
                                            'fontWeight': 'bold'},
                                style_cell_conditional=scc,
                                style_table=t,
                                id='table1')

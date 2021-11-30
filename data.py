import dash
import dash_table
import pandas as pd
from collections import OrderedDict
import dash_html_components as html
from jupyter_dash import JupyterDash

df_la=pd.read_pickle('1_LeadAssign_dash.pickle')
df_la=df_la.sort_values(['depcode_ass','staffstatus','staffname','expirydate'])
df_churn=pd.read_pickle('2_Churn_dash.pickle')
df_churn=df_churn.sort_values(['depcode_ass','staffstatus','staffname','expirydate'])
df_crm=pd.read_pickle('3_CRM10_dash.pickle')
df_crm=df_crm.rename(columns = {'depcode_abdCS': 'depcode_ass'})
df_crm=df_crm.sort_values(['depcode_ass','depgoup_old','staffstatus','staffname','expirydate'])

def create_df(df,columns,i):    
    result= df.groupby(['depcode_ass','staffstatus','staffname','MM-YYYY','depgoup_old'])[columns].nunique().reset_index()
    result2 = pd.pivot_table(result, values= columns,  
                   index=['depcode_ass','staffstatus','staffname','MM-YYYY'],
                         columns='depgoup_old')
    result2=result2.fillna(0)
    result2=result2.reset_index()
    result2=result2.rename(columns = {'CS->CS':f"CS->CS{i}",'MB->CS':f"MB->CS{i}",'MK->CS':f"MK->CS{i}"})
    result2[f"Total_{i}"]=result2[f"CS->CS{i}"]+result2[f"MB->CS{i}"]+result2[f"MK->CS{i}"]
    globals()['df_pivot_%s' % i]=result2
    
    dfTotal=result2.groupby('staffname')[f"Total_{i}"].sum()
    dfTotal=pd.DataFrame(dfTotal)
    dfTotal=dfTotal.reset_index()
    globals()['dfTotal%s' % i]=dfTotal
    
    leadmerge=result2.merge(dfTotal,on='staffname',how='left')
    globals()['lead%s' % i]=leadmerge
    
    return (result2,dfTotal,leadmerge)

df_la_pivot,dfTotalla,leadass=create_df(df_la,'lead_ass',"")
df_ext_pivot,dfTotalext,leadassext=create_df(df_la,'saleid_ext',"ext_")
df_churn_pivot,dfTotalchurn,leadasschrun=create_df(df_churn,'lead_churn',"_c")
df_abdcs_pivot,dfTotalabdcs,leadassabdcs=create_df(df_crm,'lead_abdCS',"_cs")
df_abdmk_pivot,dfTotalabdmk,leadassabdmk=create_df(df_crm,'lead_abdMK',"_mk")
df_salemk_pivot,dfTotalsalemk,leadasssalemk=create_df(df_crm,'saleid_abdMK',"_sk")
df_abdmb_pivot,dfTotalabdmb,leadassabdmb=create_df(df_crm,'lead_abdMB',"_mb")
df_salemb_pivot,dfTotalsalemb,leadasssalemb=create_df(df_crm,'saleid_abdMB',"_sb")

leadass['keydate']=0
leadass.loc[leadass["MM-YYYY"]=='1-2021','keydate']=1
leadass.loc[leadass["MM-YYYY"]=='2-2021','keydate']=2
leadass.loc[leadass["MM-YYYY"]=='3-2021','keydate']=3
leadass.loc[leadass["MM-YYYY"]=='4-2021','keydate']=4
leadass.loc[leadass["MM-YYYY"]=='5-2021','keydate']=5
leadass.loc[leadass["MM-YYYY"]=='6-2021','keydate']=6
leadass.loc[leadass["MM-YYYY"]=='7-2021','keydate']=7
leadass.loc[leadass["MM-YYYY"]=='8-2021','keydate']=8
leadass.loc[leadass["MM-YYYY"]=='9-2021','keydate']=9
leadass.loc[leadass["MM-YYYY"]=='10-2021','keydate']=10
leadass.loc[leadass["MM-YYYY"]=='11-2021','keydate']=11
leadass.loc[leadass["MM-YYYY"]=='12-2021','keydate']=12
leadass.loc[leadass["MM-YYYY"]=='1-2022','keydate']=13
leadass.loc[leadass["MM-YYYY"]=='2-2022','keydate']=14
leadass=leadass.sort_values(['depcode_ass','staffstatus','staffname','keydate'])

def merge_n_cal(df,df2,i,j,k):  
    df3=df.merge(df2,on=['depcode_ass','staffstatus','staffname','MM-YYYY'],how='left')
    
    df3[f"CS->CS{i}"]=round(df3[f"CS->CS{j}"]/df3[f"CS->CS{k}"],2)
    df3[f"MB->CS{i}"]=round(df3[f"MB->CS{j}"]/df3[f"MB->CS{k}"],2)
    df3[f"MK->CS{i}"]=round(df3[f"MK->CS{j}"]/df3[f"MK->CS{k}"],2)
    if k == "":
        df3[f"Total {i}"]=round(df3[f"Total_{j}_x"]/df3[f"{k}Total__x"],2)
    else : 
        df3[f"Total {i}"]=round(df3[f"Total_{j}_x"]/df3[f"Total_{k}_x"],2)   
    if k == "":
        df3[f"GrandTotal {i}"]=round(df3[f"Total_{j}_y"]/df3[f"{k}Total__y"],2)
    else : 
        df3[f"GrandTotal {i}"]=round(df3[f"Total_{j}_y"]/df3[f"Total_{k}_y"],2)    
    return df3

all_df=merge_n_cal(leadass,leadassext,'_rn%','ext_','')
all_df2=merge_n_cal(all_df,leadasschrun,'_c%','_c','')
all_df3=merge_n_cal(all_df2,leadassabdcs,'_cs%','_cs','')
all_df4=merge_n_cal(all_df3,leadassabdmk,'404%','_mk','')
all_df5=merge_n_cal(all_df4,leadasssalemk,'_rnMK%','_sk','_mk')
all_df6=merge_n_cal(all_df5,leadassabdmb,'505%','_mb','')
all_df7=merge_n_cal(all_df6,leadasssalemb,'_rnMB%','_sb','_mb')
all_df7=all_df7.drop(columns='keydate')

for name in ['Total__y','Total_ext__y','GrandTotal _rn%','Total__c_y','GrandTotal _c%','Total__cs_y','GrandTotal _cs%','Total__mk_y','GrandTotal 404%','Total__sk_y','GrandTotal _rnMK%','Total__mb_y','GrandTotal 505%','Total__sb_y','GrandTotal _rnMB%']:
    all_df7[f"{name}2"]=all_df7[name]
    for i in range (1,all_df7.shape[0]):
        if all_df7['staffname'][i]== all_df7['staffname'][i-1]:
                all_df7[f"{name}2"][i]= None
        else : 
                all_df7[f"{name}2"][i]=all_df7[name][i]

    all_df7[name]=all_df7[f"{name}2"]
    all_df7=all_df7.drop(columns=f"{name}2")

for name in ['staffname','depcode_ass','staffstatus']:
    all_df7[f"{name}2"]=all_df7[name]
    for i in range (1,all_df7.shape[0]):
        if all_df7[name][i]== all_df7[name][i-1]:
                all_df7[f"{name}2"][i]= ""
        else : 
                all_df7[f"{name}2"][i]=all_df7[name][i]

    all_df7[name]=all_df7[f"{name}2"]
    all_df7=all_df7.drop(columns=f"{name}2")

df4=all_df7.drop(columns=['CS->CSext_', 'MB->CSext_','MK->CSext_', 'Total_ext__x', 'Total_ext__y',
        'CS->CS_c','MB->CS_c', 'MK->CS_c', 'Total__c_x', 'Total__c_y',
          'CS->CS404%', 'MB->CS404%', 'MK->CS404%', 'Total 404%','GrandTotal 404%',
           'CS->CS_sk', 'MB->CS_sk', 'MK->CS_sk', 'Total__sk_x','Total__sk_y',       
             'CS->CS505%', 'MB->CS505%','MK->CS505%', 'Total 505%', 'GrandTotal 505%', 
              'CS->CS_mb', 'MB->CS_mb','MK->CS_mb', 'Total__mb_x', 'Total__mb_y',            
                         ])

df5=df4.rename(columns = {'depcode_ass': 'DEPARTMENTNAME','staffstatus':'STAFFSTATUS','staffname': 'STAFFNAME','MM-YYYY': 'EXPIRY MONTH',
                          'Total__x':'TOTAL_ASSIGN','Total__y':'GrandTotal'})

d={'DEPARTMENTNAME':'0_STAFF INFO', 'STAFFSTATUS':'0_STAFF INFO', 'STAFFNAME':'0_STAFF INFO', 'EXPIRY MONTH':'0_STAFF INFO',
  "CS->CS": "1_Lead assign CS","MB->CS": "1_Lead assign CS","MK->CS": "1_Lead assign CS","TOTAL_ASSIGN": "1_Lead assign CS","GrandTotal": "1_Lead assign CS",
  'CS->CS_rn%': "2_renew% by CS", 'MB->CS_rn%': "2_renew% by CS", 'MK->CS_rn%': "2_renew% by CS", 'Total _rn%': "2_renew% by CS",'GrandTotal _rn%': "2_renew% by CS",
  'CS->CS_c%':'3_churn% by CS', 'MB->CS_c%':'3_churn% by CS', 'MK->CS_c%':'3_churn% by CS', 'Total _c%':'3_churn% by CS','GrandTotal _c%':'3_churn% by CS',
  'CS->CS_cs':'4_Abandon lead by CS', 'MB->CS_cs':'4_Abandon lead by CS', 'MK->CS_cs':'4_Abandon lead by CS', 'Total__cs_x':'4_Abandon lead by CS','Total__cs_y':'4_Abandon lead by CS',
  'CS->CS_cs%':'5_Abandon% by CS', 'MB->CS_cs%':'5_Abandon% by CS', 'MK->CS_cs%':'5_Abandon% by CS', 'Total _cs%':'5_Abandon% by CS','GrandTotal _cs%':'5_Abandon% by CS',
  'CS->CS_mk':'6_lead assign MK', 'MB->CS_mk':'6_lead assign MK', 'MK->CS_mk':'6_lead assign MK', 'Total__mk_x':'6_lead assign MK','Total__mk_y':'6_lead assign MK',
  'CS->CS_rnMK%':'7_renewal MK% ', 'MB->CS_rnMK%':'7_renewal MK% ', 'MK->CS_rnMK%':'7_renewal MK% ','Total _rnMK%':'7_renewal MK% ', 'GrandTotal _rnMK%':'7_renewal MK% ',  
  'CS->CS_sb':'8_lead assign MB', 'MB->CS_sb':'8_lead assign MB', 'MK->CS_sb':'8_lead assign MB','Total__sb_x':'8_lead assign MB',  'Total__sb_y':'8_lead assign MB',
  'CS->CS_rnMB%':'9_renewal MB% ', 'MB->CS_rnMB%':'9_renewal MB% ', 'MK->CS_rnMB%':'9_renewal MB% ','Total _rnMB%':'9_renewal MB% ','GrandTotal _rnMB%':'9_renewal MB% '
}

d['l1']='l2'
df6=pd.concat(dict(tuple(df5.groupby(d,axis=1))),1)

df=df6.copy()

def discrete_background_color_bins(df,hm_color,columnsA,columnsB, n_bins=9):
    import colorlover
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)] #list ของการแบ่งค่า 0 ถึง 1 เป็น n_bins+1 ค่า
    df_numeric_columns = df.select_dtypes('number') # สร้าง df_numeric_columns เก็บเฉพาะค่าที่เป็นตัวเลข
    df_numeric_columns=df_numeric_columns[[(columnsA,columnsB)]]
    
    df_max = df_numeric_columns.max().max() #หาค่ามากสุดใน df_numeric_columns
    df_min = df_numeric_columns.min().min() #หาค่าน้อยสุดใน df_numeric_columns
    ranges = [
        ((df_max - df_min) * i) + df_min
        for i in bounds
    ]                                       #สร้าง range ของค่าตามbin
    styles = []
    legend = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        backgroundColor = colorlover.scales[str(n_bins)]['seq'][hm_color][i - 1] #scalesสี
        color = 'white' if i > len(bounds) / 2. else 'inherit' 

        for column in ['_'.join([i[0],i[1]]) for i in df_numeric_columns.columns]:
            styles.append({
                'if': {
                    'filter_query': (
                        '{{{column}}} >= {min_bound}' +
                        (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                    ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                    'column_id': column
                },
                'backgroundColor': backgroundColor,
                'color': color
            })    #บอก ช่วงค่า บอกcolumns บอกสี
        legend.append(
            html.Div(style={'display': 'inline-block', 'width': '60px'}, children=[
                html.Div(
                    style={
                        'backgroundColor': backgroundColor,
                        'borderLeft': '1px rgb(50, 50, 50) solid',
                        'height': '10px'
                    }
                ),
                html.Small(round(min_bound, 2), style={'paddingLeft': '2px'})
            ])
        )

    return (styles, html.Div(legend, style={'padding': '5px 0 5px 0'}))


stylesall=[]
def call_function(col_list,color,first_ind):
    styles_fun=[]
    for i in col_list:
        (styles, legend) = discrete_background_color_bins(df,color,first_ind ,i)
        styles_fun=styles_fun+styles
    return  styles_fun

colass_list=['CS->CS','MB->CS','MK->CS','TOTAL_ASSIGN','GrandTotal']  
stylesall=stylesall+call_function(colass_list,'Blues','1_Lead assign CS')
colrenew_list=['CS->CS_rn%','MB->CS_rn%', 'MK->CS_rn%', 'Total _rn%', 'GrandTotal _rn%']
stylesall=stylesall+call_function(colrenew_list,'Greens','2_renew% by CS')
colchurn_list=['CS->CS_c%', 'MB->CS_c%', 'MK->CS_c%', 'Total _c%', 'GrandTotal _c%']
stylesall=stylesall+call_function(colchurn_list,'Reds','3_churn% by CS')
colabdcs_list=['CS->CS_cs', 'MB->CS_cs', 'MK->CS_cs', 'Total__cs_x', 'Total__cs_y']
stylesall=stylesall+call_function(colabdcs_list,'Oranges','4_Abandon lead by CS')
colabdcsp_list=['CS->CS_cs%', 'MB->CS_cs%', 'MK->CS_cs%', 'Total _cs%','GrandTotal _cs%']
stylesall=stylesall+call_function(colabdcsp_list,'Oranges','5_Abandon% by CS')
colassmk_list =['CS->CS_mk', 'MB->CS_mk', 'MK->CS_mk', 'Total__mk_x','Total__mk_y']
stylesall=stylesall+call_function(colassmk_list,'Blues','6_lead assign MK')
colassrenewmk_list =['CS->CS_rnMK%', 'MB->CS_rnMK%', 'MK->CS_rnMK%','Total _rnMK%', 'GrandTotal _rnMK%']
stylesall=stylesall+call_function(colassrenewmk_list,'Greens','7_renewal MK% ')
colassmb_list=['CS->CS_sb', 'MB->CS_sb','MK->CS_sb', 'Total__sb_x', 'Total__sb_y']
stylesall=stylesall+call_function(colassmb_list,'Blues','8_lead assign MB')
colassrenewmb_list =['CS->CS_rnMB%','MB->CS_rnMB%', 'MK->CS_rnMB%', 'Total _rnMB%', 'GrandTotal _rnMB%']
stylesall=stylesall+call_function(colassrenewmb_list,'Greens','9_renewal MB% ')

df_data_all=[]
df_todict_records=df.to_dict('records')
for j in range (0,len(df_todict_records)):
    df_to_dict = df_todict_records[j]
    df_data=[ { '_'.join([i[0],i[1]]) : df_to_dict[i]   for i in df_to_dict.keys() } ]
    df_data_all=df_data_all+df_data


data_columns=[{'name': [i[0],i[1]], 'id': '_'.join([i[0],i[1]])} for i in df.columns]
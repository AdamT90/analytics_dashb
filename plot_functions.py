import pandas as pd
import plotly.express as px
import numpy as np
from plotly import graph_objects as go
from itertools import chain

active_map={'brak aktywności':'gray',
            'tylko płacę składki':'lightcyan',
            'niska aktywność':'cyan',
            'średnia aktywność':'lawngreen',
            'wysoka aktywność':'forestgreen'}

gender_map={'Mężczyzna':'red',
            'Kobieta':'blue'}

reason_map = {'lewicowe poglądy' : 'red',
 'program Razem' : 'violet',
 'chęć kariery politycznej': 'gold',
 'znam ludzi z okręgu': 'green',
 'frustracja sytuacją w kraju': 'grey',
 'nudziło mi się': 'white'}

active_sorter = ['brak aktywności','tylko płacę składki',
                'niska aktywność', 'średnia aktywność', 'wysoka aktywność']

time_cols = ['obecna dostępność czasowa',
 'potencjalna dostępność czasowa',
 'potencjalny wzrost dostępności czasowej']

def group_and_calc(df, groupby=None, calc_cols=None,aggfunc='sum'):
    agg_series = pd.pivot_table(df[[groupby]+calc_cols],
               index=groupby,values = calc_cols, aggfunc = aggfunc)
    groups_count = df.groupby(by=groupby).count().iloc[:,0]
    return agg_series.apply(lambda x: x/groups_count), agg_series


def gen_piecharts(base_df, calc_cols, groupby='płeć', hover_info='liczba odpowiedzi',
                  aggfunc='sum', cdmap=active_map,
                  title=None, sorter=active_sorter):
    piedf, agg_df = group_and_calc(df=base_df, groupby=groupby,
                                   calc_cols=calc_cols,
                                   aggfunc=aggfunc)
    piedf = piedf.reset_index()
    agg_df = agg_df.reset_index()
    figs = []
    for idx, cat in enumerate(list(piedf[groupby])):
        if base_df[base_df[groupby] == cat].shape[0] > 1:
            if title is None:
                chart_title = ""
            elif isinstance(title, str):
                chart_title = title + " " + str(cat)
            elif isinstance(title, list):
                chart_title = title[idx - 1]
            else:
                raise (ValueError("unexpected title format"))
            df = piedf[piedf[groupby] == cat].T.reset_index().iloc[1:, :]
            df_count = agg_df[agg_df[groupby] == cat].T.reset_index().iloc[1:, :]

            # df_count = df_count[idx]
            df = df.rename(columns={idx: 'val'})
            df_count.columns = ['index_1', hover_info]

            df = df.join(df_count)
            if sorter is not None:
                df['index'] = df['index'].astype('category')
                df['index'].cat.set_categories(sorter, inplace=True)
                df = df.sort_values(['index']).reset_index()
            fig = px.pie(df[df['val'] != 0],
                         names='index',
                         color='index',
                         hover_name='index',
                         custom_data=[hover_info],
                         values='val', title=chart_title,
                         color_discrete_map=cdmap, template='plotly_dark')
            fig.update_traces(hovertemplate="Aktywność: %{label};\
                              <br>Liczba odpowiedzi: %{customdata[0][0]}</br>")
            figs.append(fig)
    return figs

def gen_scatter(df, xcolname, ycolname, sizecolname, colorcolname, cmap=active_map, skipcat = None):

    if skipcat is not None:
        df = df[df[colorcolname] != skipcat]

    fig = px.scatter(df,
                     x=xcolname,
                     y=ycolname,
                     size=sizecolname,
                     color=colorcolname, color_discrete_map=active_map,
                     template='plotly_dark'
                     )
    return fig

def gen_corr_table(df, cols_list_y=None, cols_list_x=None,lab_x=None,lab_y=None, width=1000, height=800):
    dfcorr = df[cols_list_y+cols_list_x].corr().iloc[:len(cols_list_y),len(cols_list_y):]
    dfcorr = dfcorr.sort_values(by=list(dfcorr.columns)).sort_values(axis=1, by=list(dfcorr.index))
    fig=px.imshow(
        dfcorr,
        template='plotly_dark',labels={'x':lab_x,
                                      'y':lab_y,
                                      'color':'korelacja'},width=width,height=height)
    return fig

def gen_series_list(df, cols,catname,numeric_cols=time_cols):
    series_l = []
    for col in cols:
        df = df[df[col]==1]
        tdf = df[numeric_cols].T
        tdf[catname] = col
        tdf.head()
        series_l.append(tdf)
    return series_l

def gen_box_data(df, cols,catname,numeric_cols=time_cols):
    series_l = gen_series_list(df, cols,catname,numeric_cols=numeric_cols)
    cat_num_df = pd.concat(series_l).reset_index().rename(columns={'index':'wartość'})
    catcol = cat_num_df.pop(catname)
    cat_num_df.insert(loc=1,column=catname,value=catcol)
    col = cat_num_df.pop('wartość')
    cat_num_df.insert(loc=1,column='wartość',value=col)
    return cat_num_df

def gen_box_plot(data, cols, num_col, catname,color_dict=None, height=1000):
    plotdf = data[data['wartość']==num_col].drop(columns=[
        catname,'wartość'
    ]).T
    plotdf.columns=cols
    return px.box(plotdf,template='plotly_dark',height=height)

def gen_box_plots(df, cols, catname, numeric_cols=time_cols, height=1000):
    boxdf = gen_box_data(df, cols, catname, numeric_cols)
    box_plots = []
    for nc in numeric_cols:
        box_plots.append(gen_box_plot(boxdf, cols, nc, catname, height=height))
    return box_plots

def gen_sum_bar_plot(df, cols,title):
    cols_s = df[cols].sum()
    fig = px.bar(cols_s, orientation='h', template='plotly_dark', width=1000,
                 title=title,
                 labels={'index': 'obszar', 'value': 'ilość odpowiedzi'})
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    fig.update(layout_showlegend=False)
    fig.update_traces(hovertemplate="Ilość odpowiedzi: %{value}")
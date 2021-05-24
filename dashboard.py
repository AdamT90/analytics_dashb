import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import prep_data
import plot_functions
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

df, UNFILTERED_COLS_DICT, COLS_DICT = prep_data.prep_data()


external_stylesheets = [dbc.themes.DARKLY]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
dark_style = {
        'background-color': '#444',
        'color': '#e4e4e4'}

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
TITLE = "ANKIETA OKRĘGOWA - ANALIZA"
Opening_markdown = f'''
\n
W ankiecie wzięło udział 51 respondentów. Nie jest to duża próbka, wobec czego do wyników analizy należy podchodzić ostrożnie.
Z drugiej strony, biorąc pod uwagę fakt, że do okręgu należy ok 200 osób, można uznać, że próbka 51 osób powinna być w miarę reprezentatywna.
Na uwadze warto mieć to, że prawdopodobnie osoby, które wypełniły ankietę należą do aktywniejszej części okręgu, więc w zebranych danych występuje nadreprezentacja cech typowych dla aktywniejszych członków.

Wyniki podzieliłem na kilka zakładek dla większej przejrzystości.
'''

def pie_charts(groupby, calc_cols, title=None):
    return [dcc.Graph(figure=g) for g in plot_functions.gen_piecharts(df, calc_cols=calc_cols,
                                 groupby=groupby,title=title)]

def general_stats(s,text,style):
    stats = {
        'mediana': s.median(),
        'średnia': s.mean(),
        'odchylenie standardowe': s.std()
    }
    return [dcc.Markdown(children=f"{text}, {k}: **{round(v,2)}**\n",style=style) for k,v in stats.items()]

def num_stats(col):
    return general_stats(df[col], col, style=dark_style)

app.layout = html.Div(children=[
    html.H1(children=TITLE,style={'textAlign': 'center'}),

    html.Div(children='''
        Uwagi wstępne:
    ''',style={'font-size': '200%'}),

    dcc.Markdown(Opening_markdown),
    dcc.Tabs(id='tabs-1', vertical=True, style=dark_style, value='tab-11', children=[
        dcc.Tab(label='Aktywność a płeć', style=dark_style, value='tab-11',
                children=pie_charts(
                    groupby='płeć',
                    calc_cols=COLS_DICT['aktywność'],
                    title=["Rozkład aktywności dla Kobiet",
                     "Rozkład aktywności dla Mężczyzn"]
                )),
        dcc.Tab(label='Aktywność a wiek', style=dark_style, value='tab-12',
                children=pie_charts(
                    groupby='wiek',
                    calc_cols=COLS_DICT['aktywność'],
                    title="Rozkład aktywności dla wieku z przedziału"
                )),
        dcc.Tab(label='Aktywność a wykształcenie', style=dark_style, value='tab-13',
                children=pie_charts(
                    groupby='wykształcenie',
                    calc_cols=COLS_DICT['aktywność'],
                    title="Rozkład aktywności dla osób które swoje wykształcenie określiły jako"
                )),
        dcc.Tab(label='Dostępność czasowa', style=dark_style, value='tab-14',
                children=[
                    html.Div(children=num_stats('obecna dostępność czasowa')),
                    html.Div(children=num_stats('potencjalna dostępność czasowa')),
                    html.Div(children=num_stats('potencjalny wzrost dostępności czasowej'))
                ]),
        dcc.Tab(label='Aktywność` a płeć', style=dark_style, value='tab-111'),
        dcc.Tab(label='Aktywność1 a wiek', style=dark_style, value='tab-112'),
        dcc.Tab(label='Aktywność1 a wykształcenie', style=dark_style, value='tab-113'),
        dcc.Tab(label='Dostępność1 czasowa', style=dark_style, value='tab-114'),
        dcc.Tab(label='Dostępność czasowa', style=dark_style, value='tab-21'),
        dcc.Tab(label='Staż w partii a aktywność', style=dark_style, value='tab-22'),
        dcc.Tab(label='Przyczyny dołączenia do partii', style=dark_style, value='tab-23'),
        dcc.Tab(label='Istotne obszary działania lewicy', style=dark_style, value='tab-24'),
    ]),
    html.Div(id='tabs-content',children=[dcc.Markdown("Lorem ipsum")])
])

#@app.callback(Output('tabs-example-content', 'children'),
#              Input('tabs-example', 'value'))
#def render_content(tab):
#    if tab == 'tab-1':
#        return html.Div([
#            html.H3('Tab content 1')
#        ])
#    elif tab == 'tab-2':
#        return html.Div([
#            html.H3('Tab content 2')
#        ])

if __name__ == '__main__':
    app.run_server(debug=True)
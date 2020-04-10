#!/usr/bin/python3
import io
import dash
import base64
import argparse
import dash_table
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pandasql import sqldf
pysqldf = lambda q: sqldf(q, globals())

app = dash.Dash(__name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"])
app.title = 'GOG Galaxy 2.0 Stats Analysis'
app.layout = html.Div(children=[
    html.H1(children='GOG Galaxy 2.0 Stats Analysis'),
    html.Div(children='View analysis of your whole game library!'),
    html.H2(children='CSV import'),
    html.Div(
        children=
        'Select the file that you generated using "src/gog_stats_exporter.py". Loading might take a short while.'
    ),
    dcc.Upload(id='upload-data',
               children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
               style={
                   'height': '60px',
                   'lineHeight': '60px',
                   'borderWidth': '1px',
                   'borderStyle': 'dashed',
                   'borderRadius': '5px',
                   'textAlign': 'center',
                   'margin': '10px'
               }),
    html.Div(id='output-data-upload'),
])


@app.callback(Output('output-data-upload', 'children'), [Input('upload-data', 'contents')])
def parse_contents(data):
    if data is None:
        return html.Div(['Please provide a CSV file above.'])
    try:
        global df
        _, content_string = data.split(',')
        df = pd.read_csv(io.StringIO(base64.b64decode(content_string).decode('utf-8')))

        stats_df = pysqldf('''SELECT
            platform as Platform, count(`title.title`) as `Number of Games`, 
            round(sum(`minutesInGame`)/60.0, 2) as `Hours Total (h)`, 
            sum(`myAchievementsCount.unlocked`) as `Achievements Total`,
            round(sum(`price.current`), 2) as `Value Current (€)`,
            round(sum(`price.high`), 2) as `Value New (€)`
        FROM df GROUP BY platform
        UNION ALL
        SELECT
            'Total' as `Number of Games`,
            count(`title.title`) as `Number of Games`,
            round(sum(`minutesInGame`)/60.0, 2) as `Hours Total (h)`, 
            sum(`myAchievementsCount.unlocked`) as `Achievements Total`,
            round(sum(`price.current`), 2) as `Value Current (€)`,
            round(sum(`price.high`), 2) as `Value New (€)`
        FROM df ORDER BY `Hours Total (h)` DESC, `Value New (€)` DESC''')

        stats_table = dash_table.DataTable(id='stats_table',
                                           columns=[{
                                               "name": i,
                                               "id": i
                                           } for i in stats_df.columns],
                                           data=stats_df.to_dict('records'),
                                           style_cell_conditional=[{
                                               'if': {
                                                   'column_id': c
                                               },
                                               'textAlign': 'left'
                                           } for c in ['Date', 'Region']],
                                           style_data_conditional=[{
                                               'if': {
                                                   'row_index': 'odd'
                                               },
                                               'backgroundColor': 'rgb(248, 248, 248)'
                                           }],
                                           style_header={
                                               'backgroundColor': 'rgb(230, 230, 230)',
                                               'fontWeight': 'bold'
                                           })

        price_df = pysqldf('''SELECT
            `title.title` as Title,
            `price.high`/`minutesInGame`*60.0 as `Price per hour`
        FROM df WHERE `price.high` > 0 and `minutesInGame` > 0 ORDER BY `Price per hour` DESC''')

        price_fig = px.bar(price_df, x='Price per hour', y='Title', orientation='h', text='Price per hour')
        price_fig.update_traces(texttemplate='%{text:.4f}', textposition='outside')
        price_fig.update_layout(height=20 * price_df['Title'].count())

        hours_df = pysqldf('''SELECT
            `title.title` as Title,
            `minutesInGame`/60.0 as Hours
        FROM df WHERE Hours > 5 ORDER BY Hours''')

        hours_fig = px.bar(hours_df, x='Hours', y='Title', orientation='h', text='Hours')
        hours_fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        hours_fig.update_layout(height=20 * hours_df['Title'].count())

        achievements_df = pysqldf('''SELECT
            `title.title` as Title, 
            100.0 * `myAchievementsCount.unlocked` / `myAchievementsCount.all` as Achievements 
        FROM df WHERE Achievements > 0 ORDER BY Achievements''')

        achievements_fig = px.bar(achievements_df,
                                  x='Achievements',
                                  y='Title',
                                  orientation='h',
                                  text='Achievements')
        achievements_fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        achievements_fig.update_layout(height=20 * achievements_df['Title'].count())
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file.'])

    return html.Div([
        html.H2(children='Overall stats'), stats_table,
        html.H2(children='Price per hour playtime'),
        dcc.Graph(figure=price_fig),
        html.H2(children='Hours playtime'),
        dcc.Graph(figure=hours_fig),
        html.H2(children='Achievements percentage'),
        dcc.Graph(figure=achievements_fig)
    ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=
        'Launching a Plotly Dash server that provides nice statistics for your whole games library.')
    parser.add_argument('-d',
                        '--debug',
                        help='enables debugging features',
                        nargs='?',
                        const=True,
                        default=False)
    args = parser.parse_args()

    app.run_server(debug=args.debug)

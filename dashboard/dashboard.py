import dash, json
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output

#slate theme (?)
app = dash.Dash(
        external_stylesheets=[dbc.themes.SANDSTONE],
        suppress_callback_exceptions=True
        )

dataframes = {
    2006 : pd.read_csv('../csv/lombardia/air_quality/2006.csv', sep=','),
    2007 : pd.read_csv('../csv/lombardia/air_quality/2007.csv', sep=','),
    2008 : pd.read_csv('../csv/lombardia/air_quality/2008.csv', sep=','),
    2009 : pd.read_csv('../csv/lombardia/air_quality/2009.csv', sep=','),
    2010 : pd.read_csv('../csv/lombardia/air_quality/2010.csv', sep=','),
    2011 : pd.read_csv('../csv/lombardia/air_quality/2011.csv', sep=','),
    2012 : pd.read_csv('../csv/lombardia/air_quality/2012.csv', sep=','),
    2013 : pd.read_csv('../csv/lombardia/air_quality/2013.csv', sep=','),
    2014 : pd.read_csv('../csv/lombardia/air_quality/2014.csv', sep=','),
    2015 : pd.read_csv('../csv/lombardia/air_quality/2015.csv', sep=','),
    2016 : pd.read_csv('../csv/lombardia/air_quality/2016.csv', sep=','),
    2017 : pd.read_csv('../csv/lombardia/air_quality/2017.csv', sep=','),
    2018 : pd.read_csv('../csv/lombardia/air_quality/2018.csv', sep=',')
}

pollutants = {
    'PM10' : 'PM10 (SM2005)',
    'NO2' : 'Biossido di Azoto',
    'PM25' : 'Particelle sospese PM2.5',
    'CO_8h' : 'Monossido di Carbonio',
    'O3' : 'Ozono',
    'SO2' : 'Biossido di Zolfo',
    'C6H6' : 'Benzene'
}

max_pollutant = {
    'NO2': 200,
    'PM10': 50,
    'PM25': 25,
    'O3': 120,
    'CO_8h': 10,
    'SO2' : 125,
    'C6H6': 5
}

ranges = {
    'PM10' : [18, 55],
    'NO2' : [14, 72],
    'PM25' : [10, 31],
    'CO_8h' : [0.2, 2.5],
    'O3' : [12, 120],
    'SO2' : [0, 20],
    'C6H6' : [0.5, 4]
}

####################
#   SPYDER GRAPH   #
####################
#TODO Modificare le label con le stringhe dei mesi
def sg2(pollutant, year, province):
    months = {
            '01': 'gen', 
            '02': 'feb', 
            '03': 'mar',
            '04': 'apr',
            '05': 'may',
            '06': 'jun',
            '07': 'jul',
            '08': 'aug',
            '09': 'sep',
            '10': 'oct',
            '11': 'nov',
            '12': 'dec'}
    yearcolor = {}
    tot = pd.DataFrame(columns=['Data', 'Valore', 'Provincia'])
    for y in range(2006, 2019):
        if y == year:
            yearcolor[y] = "red"
        else:
            yearcolor[y] = "grey"
        df = dataframes[y]
        pdf = df[df['NomeTipoSensore']==pollutants[pollutant]]
        pdf['Data'] = pdf['Data'].apply(lambda x: x[5:7])
        pdf = pdf[pdf['Provincia'] == province]
        pdf = pdf.set_index('Data').groupby(['Data', 'Provincia']).mean().reset_index()
        pdf = pdf.assign(anno = lambda x: y)
        tot = tot.append(pdf, ignore_index=True)
    fig = px.line_polar(tot,
                        r='Valore',
                        theta='Data',
                        color='anno',
                        color_discrete_map=yearcolor,
                        line_close=True)
    fig.update_layout(showlegend=False)
    return fig
    
##################
#   AREA GRAPH   #
##################
#TODO togliere sfondo e anno dalle x, aggiungere trasparenza e titolo con anno
#TODO in alternativa togliere il riempimento e mettere un secondo asse y e un istogramma basato su quell'asse
#TODO grafico leggibile per SO2
def area_graph(pollutant, year, province, mode='mean'):
    max_daily = max_pollutant[pollutant]
    ds = dataframes[year]
    ds = ds[ds['Provincia'] == province]
    ds = ds[ds['NomeTipoSensore'] == pollutants[pollutant]]
    ds = ds[['Data', 'Valore']]
    if mode == 'max':
        ds = ds.groupby(by='Data').max()
    if mode == 'mean':
        ds = ds.groupby(by='Data').mean()
    x = ds.index
    y = ds['Valore']
    maxY = [max_daily] * x.size             #max legal level
    warY = [max_daily+max_daily] *x.size    #warning level
    cleanY = [-max_daily*0.5]*x.size        #clean level
    posY = (y.where(y>maxY, maxY)) - maxY
    negY = (y.where(y<maxY, maxY)) - maxY
    fig = go.Figure()
    fig.update_layout(
        xaxis = dict(domain=[0, 0.29], anchor='y'),
        xaxis2 = dict(domain=[0.3, 1], anchor='y2'),
        yaxis = dict(anchor='x2', domain=[0,1], side='right'),
        yaxis2 = dict(anchor='x', domain=[0,1], overlaying='y',side='left')
    )
    fig.add_trace(go.Box(y=y, yaxis='y', xaxis='x'))
    fig.add_trace(go.Histogram(x=x,y=negY, marker_color='green',
        yaxis= 'y2',
        xaxis= 'x2',
        xbins=dict(
            start=x.min(),
            end=x.max(),
            size='D1'
        ),
        histfunc='sum')
    )
    fig.add_trace(go.Histogram(x=x,y=posY, marker_color='red',
        yaxis= 'y2',
        xaxis= 'x2',
        xbins=dict(
            start=x.min(),
            end=x.max(),
            size='D1'
        ),
        histfunc='sum')
    )
    fig.add_trace(go.Scatter(x=x, y=y, xaxis='x2',yaxis='y',line_color='black', line_width=1))
    fig.add_trace(go.Scatter(x=x, y=maxY, xaxis='x2',yaxis='y',line_color='black', line_width=3))
    fig.add_trace(go.Scatter(x=x, y=warY, xaxis='x2',yaxis='y',line_color='purple', line_width=1))
    fig.add_trace(go.Scatter(x=x, y=maxY, xaxis='x2',yaxis='y2',line_color='purple', line_width=1))
    fig.add_trace(go.Scatter(x=x, y=cleanY, xaxis='x2',yaxis='y2',line_color='blue', line_width=1))
    fig.update_layout(
        showlegend=False,
        bargap=0,
        yaxis2 = dict(
            title = 'micrograms over limit',
            showline=True
        ),
        yaxis = dict(
            title = 'micrograms/metric cube',
            showline=True
        )
    )
    return fig

#################
#   MAP GRAPH   #
#################
with open("../geojson/lombardia_province.geojson") as f:
    province_geo=json.load(f)

prov_lookup = {feature['properties']['prov_acr']: feature for feature in province_geo['features']}

def highlight(province):
    geojson_highlights = dict()
    for k in province_geo.keys():
        if k != 'features':
            geojson_highlights[k] = province_geo[k]
        else:
            geojson_highlights[k] = [prov_lookup[province]]
    return geojson_highlights

def map_graph(poll, year, province):
    if year > 2018 :
        return
    pollutant = pollutants[poll]
    pollutant_range = ranges[poll]
    chosen_year = dataframes[year]
    #Remove unwanted pollutants
    df = chosen_year[chosen_year['NomeTipoSensore']==pollutant]
    #Calculate yearly mean by Province
    df = df.groupby(by=['Provincia'])
    df = df["Valore"].mean().reset_index()
    #Generate map
    fig = px.choropleth_mapbox(
        df,
        geojson=province_geo,
        locations='Provincia',
        featureidkey='properties.prov_acr',
        color='Valore',
        color_continuous_scale="YlOrRd",
        range_color=(pollutant_range[0], pollutant_range[1]),
        mapbox_style="carto-positron",
        zoom=7,
        center = {"lat": 45.67, "lon": 9.7119},
        opacity=0.5,
        labels={'Valore': poll + ' in ' + str(year)}
    )
    highlights = highlight(province)
    fig.add_trace(
        px.choropleth_mapbox(
            df,
            geojson=highlights,
            color="Valore",
            locations="Provincia",
            featureidkey="properties.prov_acr",
            opacity=1,
        ).data[0]
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

##########################
#   WEATHER CONDITIONS   #
##########################
def weather_pollutant(year, pollutant, weather_attribute = []):
    csv = pd.read_csv('../csv/lombardia/scatter/'+str(year)+'/mean_'+str(year)+'_'+pollutants[pollutant]+'_'+weather_attribute[0]+'.csv', encoding='utf-8', sep=',')
    #Remove outliers
    if weather_attribute[0]=='Precipitazione':
        csv.drop(csv.index[(csv["Valore meteo"] > 0.4 )],axis=0,inplace=True)
    #Plot
    fig = px.scatter(csv, x='Valore meteo', y='Valore inquinante')
    fig.update_traces(marker=dict(size=12,
                    line=dict(width=2,
                    color='DarkSlateGrey')),
                    selector=dict(mode='markers'))
    return fig
    #weather = np.array(csv['Valore meteo'])
    #pollutant = np.array(csv['Valore inquinante'])
    #Pearson
    #print(scipy.stats.pearsonr(weather, pollutant))
    #Spearman
    #print(scipy.stats.spearmanr(weather, pollutant))
    #Kendall
    #print(scipy.stats.kendalltau(weather, pollutant))


#################
#   PIE CHART   #
#################
def doughnut_graph(poll, year, province):
    # Selected pollutant
    chosen_year = dataframes[year]
    # Remove broken values
    polls = [item for item in pollutants.values()]
    # Remove unwanted pollutants
    df = chosen_year[chosen_year['NomeTipoSensore'].isin(polls)]
    df = df[df['Provincia'] == province]
    df = df.groupby(by=['NomeTipoSensore'])
    df = df["Valore"].mean().reset_index()
    # Calculate average
    poll_average = []
    limit_value = [5, 40, 125, 10, 120, 40, 25]
    counter = 0
    for index, row in df.iterrows():
        poll_average.append((row['Valore'] / limit_value[counter]) * 100)
        counter += 1
    # Donut chart
    labels = ['C6H6', 'NO2', 'SO2', 'CO_8h',
              'O3', 'PM 10', 'PM 2.5']
    ordered_poll = ['C6H6', 'NO2', 'SO2', 'CO_8h', 'O3', 'PM10', 'PM25']
    pull = [0, 0, 0, 0, 0, 0, 0]
    c = 0
    for i in ordered_poll:
        if i == poll:
            pull[c] = 0.15
        c += 1
    fig = go.Figure(data=[go.Pie(labels=labels, values=poll_average, hole=.4, pull=pull)])
    # pull argument for exploding
    fig.update_layout(
        annotations=[dict(text=f'{str(year)}', x=0.50, y=0.5, font_size=30, showarrow=False)])
    return fig

#############
#   LAYOUT  #
#############

sg_card = dbc.Card(
        [
            dcc.Graph(
                id='spyder_graph',
                figure=sg2('PM10', 2018, 'MI')
            )
        ])

area_card = dbc.Card(
        [
            dcc.Graph(
                id='area_graph',
                figure=area_graph('PM10', 2018, 'MI')
            )
        ])

map_card = dbc.Card([
                dcc.Graph(
                    id='map_graph',
                    figure=map_graph('PM10', 2018, 'MI')
                )
            ])

doughnut_card = dbc.Card([
                dcc.Graph(
                    id='doughnut_graph',
                    figure=doughnut_graph('PM10', 2018, 'MI')
                    )
                ])
weather_scatter_card = dbc.Card([
                dcc.Graph(
                    style = {'height':'85vh'},
                    id='weather_graph',
                    figure=weather_pollutant(2018, 'PM10', ['Precipitazione']))
                ])
weather_controls =   dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        id='pollutant',
                        options=[
                                {'label': 'Pm 10', 'value': 'PM10'},
                                {'label': 'Pm 2.5', 'value': 'PM25'},
                                {'label': 'CO 8h mean', 'value': 'CO_8h'},
                                {'label': 'O3', 'value': 'O3'},
                                {'label': 'C6H6', 'value': 'C6H6'},
                                {'label': 'SO2', 'value': 'SO2'},
                                {'label': 'NO2', 'value': 'NO2'}
                                ],
                        value='PM10'
                    ),
                    md=6
                ),

                dbc.Col(
                     dcc.Dropdown(
                        id='weather',
                        options=[
                                {'label': 'Humidity', 'value': 'Umidità Relativa'},
                                {'label': 'Temperature', 'value': 'Temperatura'},
                                {'label': 'Wind speed', 'value': 'Velocità Vento'},
                                {'label': 'Global radiation', 'value': 'Radiazione Globale'},
                                {'label': 'Precipitation', 'value': 'Precipitazione'}
                                ],
                        value='Velocità Vento'
                    ),
                    md=6
                )
            ], className='mb-4')

specific_controls =  dbc.Row([
                dbc.Col(dcc.Dropdown(
                        id='pollutant',
                        options=[
                                {'label': 'Pm 10', 'value': 'PM10'},
                                {'label': 'Pm 2.5', 'value': 'PM25'},
                                {'label': 'CO 8h mean', 'value': 'CO_8h'},
                                {'label': 'O3', 'value': 'O3'},
                                {'label': 'C6H6', 'value': 'C6H6'},
                                {'label': 'SO2', 'value': 'SO2'},
                                {'label': 'NO2', 'value': 'NO2'}
                                ],
                        value='PM10'
                    ),
                    md=4
                ),

                dbc.Col(
                    dcc.Slider(
                        id='year',
                        min=2006,
                        max=2018,
                        marks={i: str(i)  for i in range(2006, 2019)},
                        value=2018,
                    ),
                    md=8
                )
            ], className='mb-4')


app.layout = html.Div([
    dcc.Tabs(id='main-tabs', value='tab-1', children=[
        dcc.Tab(label='General Tab', value='tab-1'),
        dcc.Tab(label='Specific Tab', value='tab-2'),
        dcc.Tab(label='Weather Tab', value='tab-3'),
        dcc.Tab(label='Desease', value='tab-4'),
        ]),
    html.Div(id='tab-content')
    ])

specific_tab = html.Div([
    specific_controls,

    
    dbc.Row(
        [
            dbc.Col(map_card, md=6),
            dbc.Col(sg_card, md=4)
        ], className='mb-4'),
    
    dbc.Row([
            dbc.Col(doughnut_card, md=4),
            dbc.Col(area_card, md=6)
        ])
])

general_tab = html.Div([
    html.H3('general_tab')
    ])

weather_tab = html.Div([
    weather_controls,
    weather_scatter_card
    ])

desease_tab = html.Div([
    html.H3('desease_tab')
    ])


#################
#   CALLBACKS   #
#################
@app.callback(Output('tab-content', 'children'),
              Input('main-tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return general_tab
    elif tab == 'tab-2':
        return specific_tab
    elif tab == 'tab-3':
        return weather_tab
    elif tab == 'tab-4':
        return desease_tab

@app.callback(
        Output('weather_graph', 'figure'),
        Input('pollutant', 'value'),
        Input('weather', 'value')
        )
def weather_update(pollutant, weather):
    return weather_pollutant(2018, pollutant, [weather])

@app.callback(
        Output(component_id='map_graph', component_property='figure'),
        Output(component_id='spyder_graph', component_property='figure'),
        Output(component_id='doughnut_graph', component_property='figure'),
        Output(component_id='area_graph', component_property='figure'),
        Input(component_id='pollutant', component_property='value'),
        Input(component_id='year', component_property='value'),
        Input(component_id='map_graph', component_property='clickData'),
        )
def update(pollutant, year, click):
    province = 'MI'
    if click is not None:
        province = click['points'][0]['location']
    print(province)
    return (
        map_graph(pollutant, year, province),
        sg2(pollutant, year, province),
        doughnut_graph(pollutant, year, province),
        area_graph(pollutant, year, province)
    )

if __name__ == '__main__':
    app.run_server(debug=True)

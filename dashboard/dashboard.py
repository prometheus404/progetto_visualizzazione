import dash, json
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output

#slate theme (?)
app = dash.Dash(
        external_stylesheets=[dbc.themes.SANDSTONE]
        )

@app.callback(
        Output(component_id='map_graph', component_property='figure'),
        Output(component_id='spyder_graph', component_property='figure'),
        Output(component_id='area_graph', component_property='figure'),
        Input(component_id='pollutant', component_property='value'),
        Input(component_id='year', component_property='value')
        )
def update(input1, input2):
    return ( 
            map_graph(input1, input2),
            sg2(input1, input2),
            area_graph(input1, input2)
            )


#################################
#   CANCER POLLUTION RELATION   #
#################################

def cps(input1, input2):
    print(input1 + ' ' + str(input2))
    inqui = pd.read_csv('../csv/tumori.csv', encoding='utf-8', sep=',')
    inqui_s = inqui.sort_values(by=["Pm10"], ascending=True)
    return px.scatter(inqui_s, x='Value', y='Pm10')


#############################
#   POLLUTION SPYDER GRAPH  #
#############################
def dataset_to_monthly_mean(filename, pollutant):
    #importa il dataset
    dataset = pd.read_csv(filename, sep=';')
    #prende solo la sostanza scelta
    no2 = dataset[dataset['inquinante']==pollutant]
    #toglie i valori nulli
    no2 = no2[no2['valore'] >= 0]
    no2.data = no2.data.map(lambda x: x[5:-3])
    # restituisce la
    return no2.groupby(by='data', as_index=False).mean('valore')

#TODO chiudere la linea
def sg(pollutant, year):
    fig = go.Figure()
    for y in range(2014, 2019):
        if y == year:
            col = "red"
        else:
            col = "gray"
        no2 = dataset_to_monthly_mean('../csv/pollution_detection/qaria_'+str(y)+'.csv', pollutant)
        fig.add_trace(go.Scatterpolar(r=no2['valore'], theta=no2['data'],mode = 'lines', name=y, line_color=col))
    return fig

#########################
#   SPYDER GRAPH 2.0    #
#########################
#TODO togliere legenda
def sg2(pollutant, year):
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
    tot = pd.DataFrame(columns=['mese', 'stazione_id', 'valore', 'anno'])
    for y in range(2011, 2019):
        if y == year:
            yearcolor[y] = "red"
        else:
            yearcolor[y] = "grey"
        df = pd.read_csv('../csv/pollution_detection/qaria_'+str(y)+'.csv', sep=';')
        pdf = df[df['inquinante']==pollutant]
        pdf = pdf[pdf['valore'] >= 0]
        pdf = pdf.assign(mese = lambda x: x.data)
        pdf.mese = pdf.mese.map(lambda x: x[5:-3])
        print(pdf)
        pdf = pdf.groupby(by='mese', as_index=False).mean()
        pdf = pdf.assign(anno = lambda x: y)
        print(pdf)
        tot = tot.append(pdf, ignore_index=True)
    print(tot)
        #print(pdf)
    fig = px.line_polar(tot,
                        r='valore',
                        theta='mese',
                        color='anno',
                        color_discrete_map=yearcolor,
                        line_close=True)
    return fig

    
##################
#   AREA GRAPH   #
##################
max_pollutant = {
        'NO2': 200,
        'PM10': 50,
        'PM25': 25,
        'O3': 120, 
        'CO_8h': 10,
        'SO2' : 125,
        'C6H6': 5
        }

#TODO togliere legenda, sfondo e anno dalle x, aggiungere trasparenza e titolo con anno
#TODO in alternativa togliere il riempimento e mettere un secondo asse y e un istogramma basato su quell'asse
#TODO grafico leggibile per SO2
def area_graph(pollutant, year, mode='mean'):
    max_daily = max_pollutant[pollutant]
    ds =pd.read_csv('../csv/pollution_detection/qaria_'+str(year)+'.csv', sep=';')
    ds = ds[ds['inquinante'] == pollutant].dropna()[['data', 'valore']]
    if mode == 'max':
        ds = ds.groupby(by='data').max()
    if mode == 'mean':
        ds = ds.groupby(by='data').mean()
    x = ds.index#.map(lambda i: i[-5:])
    y = ds['valore']
    year = ds.index[0][:4]
    maxY = [max_daily] * x.size             #max legal level
    warY = [max_daily+max_daily] *x.size    #warning level
    posY = (y.where(y>maxY, maxY)) - maxY
    negY = (y.where(y<maxY, maxY)) - maxY
    
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True)
    #fig.add_trace(go.Scatter(x=x, y=maxY, line_color='white'))
    fig.add_trace(go.Histogram(x=x,y=negY, marker_color='green',
        yaxis= 'y2',
        xbins=dict(
            start=x.min(),
            end=x.max(),
            size='D1'
            ),
        histfunc='sum'),
        row=1,
        col=2
        )
    
    fig.add_trace(go.Histogram(x=x,y=posY, marker_color='red',
        yaxis= 'y2',
        xbins=dict(
            start=x.min(),
            end=x.max(),
            size='D1'
            ),
        histfunc='sum'),
        row=1,
        col=2)

    #fig.add_trace(go.Scatter(x=x, y=negY, fill='tonexty', fillcolor='green', mode='none'))
    #fig.add_trace(go.Scatter(x=x, y=maxY, line_color='white'))
    #fig.add_trace(go.Scatter(x=x, y=posY, fill='tonexty', fillcolor='red',mode='none'))
    #fig.add_trace(go.Scatter(x=x, y=y, yaxis='y1',line_color='black', line_width=1), row=1,col=2)
    fig.add_trace(go.Box(y=(y-maxY), yaxis='y1'),row=1, col=1)
    fig.update_layout(
            bargap=0,
            yaxis = dict(
                range =[1.5*negY.min(), 1.5*posY.max()],
                title = 'micrograms/metric cube',
                showline=True
            ))


    return fig

#################
#   MAP GRAPH   #
#################
with open("../geojson/lombardia_province.geojson") as f:
    province_geo=json.load(f)

years = range(2005, 2019)

ranges = {
        'PM10' : [18, 55],
        'NO2' : [14, 72],
        'PM25' : [10, 58],
        'CO_8h' : [0.2, 1.6],
        'O3' : [12, 64],
        'SO2' : [0, 12],
        'C6H6' : [0.5, 4]
        }

pollutants = {
        'PM10' : ['PM10', 'PM10 (SM2005)'],
        'NO2' : ['Biossido di Azoto'],
        'PM25' : ['Particelle sospese PM2.5'],
        'CO_8h' : ['Monossido di Carbonio'],
        'O3' : ['Ozono'],
        'SO2' : ['Biossido di Zolfo'],
        'C6H6' : ['Benzene']
        }


def map_graph(poll, year):
    if year > 2018 :
        return
    pollutant = pollutants[poll]
    pollutant_range = ranges[poll]
    stations = pd.read_csv('../csv/lombardia/Stazioni_qualit__dell_aria(lombardia).csv', encoding='utf-8', sep=',')
    chosen_year = pd.read_csv('../csv/lombardia/sensori_aria_'+str(year)+'/'+str(year)+'.csv', encoding='utf-8', sep=',')
    #Remove broken values
    chosen_year.drop(chosen_year.index[(chosen_year["Valore"] < 0)],axis=0,inplace=True)
    #Remove unwanted pollutants
    for index, row in stations.iterrows():
        if row["NomeTipoSensore"] not in pollutant:
            stations.drop(index, inplace=True)
    result = pd.merge(stations,chosen_year,on='IdSensore')
    #Calculate yearly mean by Province
    df = result.groupby(by=['Provincia'])
    df = df["Valore"].mean().reset_index()
    #Generate map
    fig = px.choropleth_mapbox(df, geojson=province_geo,
                               locations='Provincia',
                               featureidkey='properties.prov_acr',
                               color='Valore',
                               color_continuous_scale="YlOrRd",
                               range_color=(pollutant_range[0], pollutant_range[1]),
                               mapbox_style="carto-positron",
                               zoom=7,
                               center = {"lat": 45.67, "lon": 9.7119},
                               opacity=0.5,
                               labels={'Valore':pollutant[0]+': '+str(year)}
                              )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

#############
#   LAYOUT  #
#############

sg_card = dbc.Card(
        [
            dcc.Graph(
                id='spyder_graph',
                figure=sg('PM10', 2017)
            )
        ])

area_card = dbc.Card(
        [
            dcc.Graph(
                id='area_graph',
                figure=area_graph('PM10', 2017)
            )
        ])

map_card = dbc.Card([
                dcc.Graph(
                    id='map_graph',
                    figure=map_graph('PM10', 2017)
                )
            ])

controls =  dbc.Row([
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
                        min=2011,
                        max=2017,
                        marks={i: str(i)  for i in range(2011, 2018)},
                        value=2017,
                    ),
                    md=8
                )
            ])


app.layout = dbc.Container([
    html.H1(children='Regional Pollution'),
    controls,

    
    dbc.Row(
        [
            dbc.Col(map_card, md=8),
            dbc.Col(sg_card, md=4)
        ]),
    
    dbc.Row([
            dbc.Col(area_card, md=8)
        ])
])

if __name__ == '__main__':
    app.run_server(debug=True)

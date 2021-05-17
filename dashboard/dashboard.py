import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

@app.callback(
        Output(component_id='spyder_graph', component_property='figure'),
        Output(component_id='area_graph', component_property='figure'),
        Input(component_id='pollutant', component_property='value'),
        Input(component_id='year', component_property='value')
        )
def update(input1, input2):
    return ( 
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
    for y in range(2014, 2019):
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
    posY = y.where(y>maxY, maxY)
    negY = y.where(y<maxY, maxY)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=maxY, line_color='white'))
    fig.add_trace(go.Scatter(x=x, y=negY, fill='tonexty', fillcolor='green', mode='none'))
    fig.add_trace(go.Scatter(x=x, y=maxY, line_color='white'))
    fig.add_trace(go.Scatter(x=x, y=posY, fill='tonexty', fillcolor='red',mode='none'))
    fig.add_trace(go.Scatter(x=x, y=y, line_color='black'))

   
    return fig

#############
#   LAYOUT  #
#############

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    html.Label('Pollutant'),
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

    html.Label('year'),
    dcc.Slider(
        id='year',
        min=2014,
        max=2018,
        marks={i: str(i)  for i in range(2014, 2019)},
        value=2018,
    ),
    dcc.Graph(
        id='spyder_graph',
        figure=sg('PM10', 2018)
    ) , 
    dcc.Graph(
        id='area_graph',
        figure=area_graph('PM10', 2018)
    ) 
])

if __name__ == '__main__':
    app.run_server(debug=True)

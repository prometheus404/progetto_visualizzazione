import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

#################
#   EXAMPLE     #
#################

df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

ex = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

@app.callback(
        Output(component_id='cancer_pollution_graph', component_property='figure'),
        Output(component_id='spyder_graph', component_property='figure'),
        Input(component_id='pollutant', component_property='value'),
        Input(component_id='year', component_property='value')
        )
def update(input1, input2):
    return (cps(input1, input2), 
            sg(input1, input2))


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
            {'label': 'CO 8h mean', 'value': 'CO_8h'}
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
        id='cancer_pollution_graph',
        figure=cps('a', 'b')
    ), 
    dcc.Graph(
        id='spyder_graph',
        figure=cps('a', 'b')
    ) 
])

if __name__ == '__main__':
    app.run_server(debug=True)

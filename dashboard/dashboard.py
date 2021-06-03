import dash, json
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import scipy.stats
import numpy as np
from dash.dependencies import Input, Output

# slate theme (?)
app = dash.Dash(
    __name__,
    external_stylesheets=['../assets/style.css', dbc.themes.SANDSTONE ],
    suppress_callback_exceptions=True
)
palette = {
        'red' : 'red',
        'yellow' : 'yellow',
        'purple' : 'purple',
        'green' : 'green',
        'blue' : 'blue',
        'black' : 'black',
        'grey' : 'grey',
        'white' : 'white',
        }
dataframes = {
    2006: pd.read_csv('../csv/lombardia/air_quality/2006.csv', sep=','),
    2007: pd.read_csv('../csv/lombardia/air_quality/2007.csv', sep=','),
    2008: pd.read_csv('../csv/lombardia/air_quality/2008.csv', sep=','),
    2009: pd.read_csv('../csv/lombardia/air_quality/2009.csv', sep=','),
    2010: pd.read_csv('../csv/lombardia/air_quality/2010.csv', sep=','),
    2011: pd.read_csv('../csv/lombardia/air_quality/2011.csv', sep=','),
    2012: pd.read_csv('../csv/lombardia/air_quality/2012.csv', sep=','),
    2013: pd.read_csv('../csv/lombardia/air_quality/2013.csv', sep=','),
    2014: pd.read_csv('../csv/lombardia/air_quality/2014.csv', sep=','),
    2015: pd.read_csv('../csv/lombardia/air_quality/2015.csv', sep=','),
    2016: pd.read_csv('../csv/lombardia/air_quality/2016.csv', sep=','),
    2017: pd.read_csv('../csv/lombardia/air_quality/2017.csv', sep=','),
    2018: pd.read_csv('../csv/lombardia/air_quality/2018.csv', sep=','),
}

deaths = pd.read_csv('../csv/lombardia/deaths/deaths_lombardia_2006_2018.csv', encoding='utf-8', sep=',')

pollutants = {
    'PM10': 'PM10 (SM2005)',
    'NO2': 'Biossido di Azoto',
    'PM25': 'Particelle sospese PM2.5',
    'CO_8h': 'Monossido di Carbonio',
    'O3': 'Ozono',
    'SO2': 'Biossido di Zolfo',
    'C6H6': 'Benzene'
}

max_pollutant = {
    'NO2': 200,
    'PM10': 50,
    'PM25': 25,
    'O3': 120,
    'CO_8h': 10,
    'SO2': 125,
    'C6H6': 5
}

ranges = {
    'PM10': [18, 55],
    'NO2': [14, 72],
    'PM25': [10, 31],
    'CO_8h': [0.2, 2.5],
    'O3': [12, 120],
    'SO2': [0, 20],
    'C6H6': [0.5, 4]
}

population = {
    2006: 9475202,
    2007: 9545441,
    2008: 9642406,
    2009: 9742676,
    2010: 9826141,
    2011: 9917714,
    2012: 9700881,
    2013: 9794525,
    2014: 9973397,
    2015: 10002615,
    2016: 10008349,
    2017: 10019166,
    2018: 10036258,
}

deseases = [
    # CANCERS
    'di cui tumori maligni della trachea, dei bronchi e dei polmoni',
    'di cui tumori maligni della prostata',
    'di cui tumori maligni del cervello e del sistema nervoso centrale',
    'di cui altri tumori maligni',  ###
    'di cui melanomi maligni della cute',
    "di cui tumori maligni dell'esofago",
    'tumori non maligni (benigni e di comportamento incerto)',
    'di cui leucemia',
    'di cui morbo di hodgkin e linfomi',  ###
    'di cui tumori maligni delle labbra, cavità orale e faringe',
    'di cui tumori maligni della laringe',  ###
    'di cui tumori maligni della tiroide',
    'di cui tumori maligni del seno',
    'malattie della cute e del tessuto sottocutaneo',
    # RESPIRATORY
    'polmonite',
    'di cui altre malattie croniche delle basse vie respiratorie',
    'altre malattie del sistema respiratorio',
    'tubercolosi',  ###
    'influenza',
    'di cui asma',  ###
    # CIRCULATORY
    'du cui altre malattie ischemiche del cuore',  ###
    'malattie cerebrovascolari',  ###
    'altre malattie del sistema circolatorio',
    'di cui infarto miocardico acuto',  ###
    'altre malattie del cuore',
    # OTHER
    'di cui tumori maligni dello stomaco',  ###
    'di cui tumori maligni del pancreas',
    'malattia di alzheimer',
    'morbo di parkinson',
    'di cui tumori maligni della vescica',
    'di cui tumori maligni del rene',
    'di cui altri tumori maligni del tessuto linfatico/ematopoietico',  ###
    "di cui tumori maligni dell'ovaio",  #
    'altre malattie del sistema nervoso e degli organi di senso',
    'diabete mellito',
    'malattie del sangue e degli organi ematopoietici ed alcuni disturbi del sistema immunitario',
    'di cui tumori maligni della cervice uterina',
    'di cui tumori maligni della prostata',
    'di cui tumori maligni del fegato e dei dotti biliari intraepatici',
]

with open("../geojson/lombardia_province.geojson") as f:
    province_geo = json.load(f)


####################
#   SPIDER GRAPH   #
####################
# TODO Modificare le label con le stringhe dei mesi
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
            yearcolor[y] = palette["red"]
        else:
            yearcolor[y] = palette["grey"]
        df = dataframes[y]
        pdf = df[df['NomeTipoSensore'] == pollutants[pollutant]]
        pdf['Data'] = pdf['Data'].apply(lambda x: x[5:7])
        pdf = pdf[pdf['Provincia'] == province]
        pdf = pdf.set_index('Data').groupby(['Data', 'Provincia']).mean().reset_index()
        pdf = pdf.assign(anno=lambda x: y)
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
# TODO togliere sfondo e anno dalle x, aggiungere trasparenza e titolo con anno
# TODO in alternativa togliere il riempimento e mettere un secondo asse y e un istogramma basato su quell'asse
# TODO grafico leggibile per SO2
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
    maxY = [max_daily] * x.size  # max legal level
    warY = [max_daily + max_daily] * x.size  # warning level
    cleanY = [-max_daily * 0.5] * x.size  # clean level
    posY = (y.where(y > maxY, maxY)) - maxY
    negY = (y.where(y < maxY, maxY)) - maxY
    fig = go.Figure()
    fig.update_layout(
        xaxis=dict(domain=[0, 0.29], anchor='y'),
        xaxis2=dict(domain=[0.3, 1], anchor='y2'),
        yaxis=dict(anchor='x2', domain=[0, 1], side='right'),
        yaxis2=dict(anchor='x', domain=[0, 1], overlaying='y', side='left')
    )
    fig.add_trace(go.Box(y=y, yaxis='y', xaxis='x'))
    fig.add_trace(go.Histogram(x=x, y=negY, marker_color=palette['green'],
                               yaxis='y2',
                               xaxis='x2',
                               xbins=dict(
                                   start=x.min(),
                                   end=x.max(),
                                   size='D1'
                               ),
                               histfunc='sum')
                  )
    fig.add_trace(go.Histogram(x=x, y=posY, marker_color=palette['red'],
                               yaxis='y2',
                               xaxis='x2',
                               xbins=dict(
                                   start=x.min(),
                                   end=x.max(),
                                   size='D1'
                               ),
                               histfunc='sum')
                  )
    fig.add_trace(go.Scatter(x=x, y=y, xaxis='x2', yaxis='y', line_color=palette['black'], line_width=1))
    fig.add_trace(go.Scatter(x=x, y=maxY, xaxis='x2', yaxis='y', line_color=palette['black'], line_width=3))
    fig.add_trace(go.Scatter(x=x, y=warY, xaxis='x2', yaxis='y', line_color=palette['purple'], line_width=1))
    fig.add_trace(go.Scatter(x=x, y=maxY, xaxis='x2', yaxis='y2', line_color=palette['purple'], line_width=1))
    fig.add_trace(go.Scatter(x=x, y=cleanY, xaxis='x2', yaxis='y2', line_color=palette['blue'], line_width=1))
    fig.update_layout(
        showlegend=False,
        bargap=0,
        yaxis2=dict(
            title='micrograms over limit',
            showline=True
        ),
        yaxis=dict(
            title='micrograms/metric cube',
            showline=True
        )
    )
    return fig


#################
#   MAP GRAPH   #
#################
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
    if year > 2018:
        return
    pollutant = pollutants[poll]
    pollutant_range = ranges[poll]
    chosen_year = dataframes[year]
    # Remove unwanted pollutants
    df = chosen_year[chosen_year['NomeTipoSensore'] == pollutant]
    # Calculate yearly mean by Province
    df = df.groupby(by=['Provincia'])
    df = df["Valore"].mean().reset_index()
    # Generate map
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
        center={"lat": 45.67, "lon": 9.7119},
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
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


##########################
#   WEATHER CONDITIONS   #
##########################
def weather_pollutant(year, pollutant, weather_attribute=[]):
    csv = pd.read_csv(
        '../csv/lombardia/scatter/' + str(year) + '/mean_' + str(year) + '_' + pollutants[pollutant] + '_' +
        weather_attribute[0] + '.csv', encoding='utf-8', sep=',')
    # Remove outliers
    if weather_attribute[0] == 'Precipitazione':
        csv.drop(csv.index[(csv["Valore meteo"] > 0.4)], axis=0, inplace=True)
    # Plot
    fig = px.scatter(csv, x='Valore meteo', y='Valore inquinante',
                     labels={
                         "Valore meteo": "Weather attribute value",
                         "Valore inquinante": "Pollutant value",
                     },
                     )
    fig.update_traces(marker=dict(size=12,
                                  line=dict(width=2,
                                            color='DarkSlateGrey')),
                      selector=dict(mode='markers'))

    return fig
    # weather = np.array(csv['Valore meteo'])
    # pollutant = np.array(csv['Valore inquinante'])
    # Pearson
    # print(scipy.stats.pearsonr(weather, pollutant))
    # Spearman
    # print(scipy.stats.spearmanr(weather, pollutant))
    # Kendall
    # print(scipy.stats.kendalltau(weather, pollutant))


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


####################
#   DESCRIPTION    #
####################
descriptions = {
    'PM10': 'PM 10: Particulates are microscopic particles of solid or liquid matter suspendend in the air, wiht Pm 10 we refer to  suspended particulate matter with a diameter of 10 micrometers. Some particulates occur naturally, originating from volcanoes, dust storms or forest fires. Human activities, such as the burning of fossil fuels in vehicles, stubble burning, cooling systems and various industrial processes also generate significant amounts of particulates. This kind of particulates have impact on climate and precipitation that adversely affect human health, in ways additional to direct inhalation.',
    'PM25': 'PM 2,5: Particulates are microscopic particles of solid or liquid matter suspendend in the air, wiht Pm 2,5 we refer to  suspended particulate matter with a diameter of 2,5 micrometers. Some particulates occur naturally, originating from volcanoes, dust storms or forest fires. Human activities, such as the burning of fossil fuels in vehicles, stubble burning, cooling systems and various industrial processes also generate significant amounts of particulates. This kind of particulates have impact on climate and precipitation that adversely affect human health, in ways additional to direct inhalation.',
    'CO_8h': 'Carbon monoxide (CO), refers to the 8-hours average concentration. Carbon monoxide is a colorless, odorless, tasteless, flammable gas that is slightly less dense than air, that\'s why it creates a smog type formation in the air. Humans utilize carbon monoxide for various industrial processes, which causes a proplematic air pollutant arising.',
    'O3': 'Ozone (O3) is a trace gas, with an average concentration of 20-30 parts per billion by volume, with close to 100 in polluted areas. At abnormally high concentrations, brought about by human activities (largely the combustion of fossil fuel), it is a pollutant and a constituent of smog. Its levels have increased significantly since the industrial revolution.',
    'C6H6': ' Benzene (C6H6) is a colorless and highly fammable liquid with a sweet smell. It is a natural constituent of crude oil and is one ot the elementary petrochemicals. The benzene naturally occurs in process that includes volcanic eruptions and wild fires. The major sources of benzene exposure are tobacco smoje, automobile service stations, exhaust from motor vehicles, and industrial emissions. Although a major industrial chemical, benzene finds limited use in consumer items because of its toxicity.',
    'SO2': 'Sulfur dioxide (SO2) is a colorless gas. Sulfur dioxide is produced by volcanoes and in various industrial processes. Coal and petroleum often contain sulfur compounds, and their combustion generates sulfur dioxide. Its oxidation is the main cause of acid rain. This is one of the causes for concern over the environmental impact of the use of these fuels as power sources.',
    'NO2': 'Nitrogen dioxideÂ (NO2) is a reddish-brown toxic gas with a characteristic sharp, biting odor. Nitrogen dioxide is expelled from high temperature combustion. It is one of the most prominent air pollutant.For the general public, the most prominent sources of NO2 are internal combustion engines burning fossil fuels. Outdoors, NO2 can be a result of traffic from motor vehicles. Indoors, exposure arises from cigarette smoke, and butane and kerosene heaters and stoves.'
}


def update_description(pollutant):
    return descriptions[pollutant]


#################
#   DAYS OVER   #
#################
def update_days(pollutant, year, province):
    max_daily = max_pollutant[pollutant]
    df = dataframes[year]
    df = df[df['Provincia'] == province]
    df = df[df['NomeTipoSensore'] == pollutants[pollutant]]
    df = df.groupby('Data').mean()
    days_warning = len(df[df['Valore'] >= (2 * max_daily)])
    days_max = len(df[df['Valore'] >= (max_daily)]) - days_warning
    days_low = len(df[df['Valore'] >= (0.5 * max_daily)]) - (days_warning + days_max)
    days_clean = len(df[df['Valore'] <= (0.25 * max_daily)])
    return html.Div([
        html.H1(str(days_warning) + ' days'),
        html.P("extremely polluted"),
        html.H1(str(days_max) + ' days'),
        html.P("highly polluted"),
        html.H1(str(days_low) + ' days'),
        html.P("mildly polluted"),
        html.H1(str(days_clean) + ' days'),
        html.P("clean"),
    ])


#################
#   TOTAL MAP   #
#################
def total_map_graph():
    tot = pd.DataFrame(columns=['Provincia', 'NomeTipoSensore', 'Valore'])
    for y in range(2006, 2019):
        df = dataframes[y]
        result = df.groupby(by=['Provincia', 'NomeTipoSensore'])
        result = result["Valore"].mean().reset_index()
        tot = tot.append(result, ignore_index=True)
    for x in pollutants:
        tot.loc[tot.NomeTipoSensore == pollutants[x], 'Valore'] = (tot['Valore'] / max_pollutant[x]) * 100
    final = tot.groupby(by=['Provincia']).sum().reset_index()
    fig = px.choropleth_mapbox(
        final,
        geojson=province_geo,
        locations='Provincia',
        featureidkey='properties.prov_acr',
        color='Valore',
        color_continuous_scale="YlOrRd",
        range_color=(2500, 4500),
        mapbox_style="carto-positron",
        zoom=7,
        center={"lat": 45.67, "lon": 9.7119},
        opacity=0.5,
        labels={'Valore': 'Global sum 2006/2018'}
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


###################
#   TREND GRAPH   #
###################
def trend_graph(chosen_deseases=[], tab='general'):
    tot = pd.DataFrame(columns=['Data', 'NomeTipoSensore', 'Valore'])
    for y in range(2006, 2019):
        df = pd.read_csv(f"../csv/lombardia/air_quality/{str(y)}.csv", encoding='utf-8', sep=',')
        result = df.groupby(by=['NomeTipoSensore'])
        result = result["Valore"].mean().reset_index()
        result = result.assign(Data=lambda x: y)
        tot = tot.append(result, ignore_index=True)
    for x in pollutants:
        tot.loc[tot.NomeTipoSensore == pollutants[x], 'Valore'] = (tot['Valore'] / max_pollutant[x]) * 100
    pollution = tot.groupby(by=['Data']).sum().reset_index()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if tab == 'desease':
        deaths = pd.read_csv('../csv/lombardia/deaths/deaths_lombardia_2006_2018.csv', encoding='utf-8', sep=',')
        deaths.drop(deaths.index[(deaths["TIPO_DATO15"] == "MRATE")], axis=0, inplace=True)
        # Print figures
        # Generate desease dataframe
        df = deaths[deaths['Causa iniziale di morte - European Short List'].isin(chosen_deseases)]
        df = df.groupby(by=['Data'])
        df = df["Value"].sum().reset_index()
        for x in population:
            df.loc[df.Data == x, 'Value'] = (df['Value'] / population[x]) * 10000
        # Draw desease lines
        fig.add_trace(
            go.Scatter(x=df['Data'], y=df['Value'], name="Desease trend"),
            secondary_y=True,
        )
        fig.update_yaxes(title_text="<b>Yearly sum</b> deaths every 10000 people", secondary_y=True)
    # Add traces
    fig.add_trace(
        go.Scatter(x=pollution['Data'], y=pollution['Valore'], name="Pollution trend"),
        secondary_y=False,
    )
    # Set x-axis title
    fig.update_xaxes(title_text="Years")
    # Set y-axes titles
    fig.update_yaxes(title_text="<b>Yearly sum</b> pollution level", secondary_y=False)
    return fig


#####################
#   DESEASE GRAPH   #
#####################
def desease_graph(pollutant, chosen_deseases=[]):
    tot = pd.DataFrame(columns=['Data', 'NomeTipoSensore', 'Valore'])
    for y in range(2006, 2019):
        df = dataframes[y]
        result = df.groupby(by=['NomeTipoSensore', 'Provincia'])
        result = result["Valore"].mean().reset_index()
        result = result.assign(Data=lambda x: y)
        tot = tot.append(result, ignore_index=True)
    # LINE CHART DEATHS
    death = deaths
    death.drop(death.index[(death["TIPO_DATO15"] == "DEATH")], axis=0, inplace=True)
    # Inner-join between 'data' from inq_mean and weather
    csv = pd.merge(tot, death, on=['Data', 'Provincia'])
    # Prepare scatter
    result = csv[csv['NomeTipoSensore'] == pollutants[pollutant]]
    result2 = result[result['Causa iniziale di morte - European Short List'].isin(chosen_deseases)]
    result2 = result2.groupby(['Provincia', 'Data'])
    result2 = result2.sum().reset_index()
    # Plot
    fig = px.scatter(result2, x='Valore', y='Value', color='Data',
                     labels={
                         "Valore": pollutant + " value",
                         "Value": "Death rate (10000) value",
                     },
                     )
    fig.update_traces(marker=dict(size=7,
                                  line=dict(width=2,
                                            color=palette['grey'])),
                      selector=dict(mode='markers'))
    return fig

#################################
#   CORRELATION COEFFICIENT     #
#################################
def update_cc(pollutant, chosen_deseases=[]):
    tot = pd.DataFrame(columns=['Data', 'NomeTipoSensore', 'Valore'])
    for y in range(2006, 2019):
        df = dataframes[y]
        result = df.groupby(by=['NomeTipoSensore', 'Provincia'])
        result = result["Valore"].mean().reset_index()
        result = result.assign(Data=lambda x: y)
        tot = tot.append(result, ignore_index=True)
    # LINE CHART DEATHS
    death = deaths
    death.drop(death.index[(death["TIPO_DATO15"] == "DEATH")], axis=0, inplace=True)
    # Inner-join between 'data' from inq_mean and weather
    csv = pd.merge(tot, death, on=['Data', 'Provincia'])
    # Prepare scatter
    result = csv[csv['NomeTipoSensore'] == pollutants[pollutant]]
    result2 = result[result['Causa iniziale di morte - European Short List'].isin(chosen_deseases)]
    result2 = result2.groupby(['Provincia', 'Data'])
    result2 = result2.sum().reset_index()
    x = result2['Valore']
    y = result2['Value']
    pearson, p_pearso = scipy.stats.pearsonr(x, y)
    spearman, p_spear = scipy.stats.spearmanr(x, y)
    kendall, p_kendall = scipy.stats.kendalltau(x, y)
    return html.Div([
        html.H1('Pearson:'),
        html.P(f"r = {str(pearson)}"),
        html.P(f"p_value = {str(p_pearso)}"),
        html.H1('Spearman:'),
        html.P(f"r = {str(spearman)}"),
        html.P(f"p_value = {str(p_spear)}"),
        html.H1('Kendall:'),
        html.P(f"r = {str(kendall)}"),
        html.P(f"p_value = {str(p_kendall)}")
    ])




#######################
#   TOTAL PIE CHART   #
#######################
def total_doughnut_graph():
    reverse_pollutants = {
        'PM10 (SM2005)': 'PM10',
        'Biossido di Azoto': 'NO2',
        'Particelle sospese PM2.5': 'PM25',
        'Monossido di Carbonio': 'CO_8h',
        'Ozono': 'O3',
        'Biossido di Zolfo': 'SO2',
        'Benzene': 'C6H6'
    }

    tot = pd.DataFrame(columns=['Data', 'NomeTipoSensore', 'Valore'])
    for y in range(2006, 2019):
        df = dataframes[y]
        tot = tot.append(df, ignore_index=True)
    result = tot.groupby(by=['NomeTipoSensore'])
    result = result["Valore"].mean().reset_index()
    for x in pollutants:
        result.loc[result.NomeTipoSensore == pollutants[x], 'Valore'] = (result['Valore'] / max_pollutant[x]) * 100
    for x in reverse_pollutants:
        result.replace(to_replace=x, value=reverse_pollutants[x], inplace=True)
    fig = go.Figure(data=[go.Pie(labels=result['NomeTipoSensore'], values=result['Valore'], hole=.4)])
    return fig

#################################
#   CORRELATION COEFFICIENT     #
#################################
#def update_cc(pollutant, chosen_deseases):
    
#############
#   LAYOUT  #
#############
days_over_card = dbc.Card([
    html.Div(id='days_over_card', children=update_days('PM10', 2018, 'MI'))
],style={'text-align' : 'center'})
description_card = dbc.Card([
    html.P(id='description', children=update_description('PM10'))
    ],style={'text-align' : 'center'})

sg_card = dbc.Card(
    [
        dcc.Graph(
            id='spider_graph',
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
        style={'height': '85vh'},
        id='weather_graph',
        figure=weather_pollutant(2018, 'PM10', ['Precipitazione']))
])

total_map_card = dbc.Card([
    dcc.Graph(
        id='total_map_graph',
        figure=total_map_graph()
    )
])

trend_card = dbc.Card([
    dcc.Graph(
        style={'height': '40vh'},
        id='trend_graph',
        figure=trend_graph()
    )
])

desease_card = dbc.Card([
    dcc.Graph(
        id='desease_graph',
        figure=desease_graph('PM10', ['du cui altre malattie ischemiche del cuore']),
    )
])

correlation_coeff_card = dbc.Card([
    html.Div(id='correlation_coeff_card', children='PM10')
    ], style={ 'text-align' : 'center',"font-family":'georgia,garamond,serif','font-size':'16px','font-style':'italic'})

total_doughnut_card = dbc.Card([
    dcc.Graph(
        id='total_doughnut_graph',
        figure=total_doughnut_graph()
    )
])

weather_controls = dbc.Row([
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
            value='PM10',
            clearable=False
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
            value='Velocità Vento',
            clearable=False
        ),
        md=6
    )
], className='mb-4')

specific_controls = dbc.Row([
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
        value='PM10',
        clearable=False
    ),
        md=4
    ),

    dbc.Col(
        dcc.Slider(
            id='year',
            min=2006,
            max=2018,
            marks={i: str(i) for i in range(2006, 2019)},
            value=2018,
        ),
        md=8
    )
], className='mb-4')

app.layout = html.Div( [
    dcc.Tabs(id='main-tabs', value='tab-1', children=[
        dcc.Tab(label='General Tab', value='tab-1'),
        dcc.Tab(label='Specific Tab', value='tab-2'),
        dcc.Tab(label='Weather Tab', value='tab-3'),
        dcc.Tab(label='Desease', value='tab-4'),
    ]),
    html.Div(id='tab-content', style = {'font_size' : '26px'})
] )

specific_tab = html.Div([
    specific_controls,

    dbc.Row(
        [
            dbc.Col(map_card, md=6),
            dbc.Col(sg_card, md=4),
            dbc.Col(description_card, md=2)
        ], className='mb-4'),

    dbc.Row([
        dbc.Col(days_over_card, md=2),
        dbc.Col(doughnut_card, md=4),
        dbc.Col(area_card, md=6)
    ])
])

general_tab = html.Div([
    dbc.Row(
        [
            dbc.Col(total_map_card, md=6),
            dbc.Col(trend_card, md=6),
        ], className='mb-4'),
    dbc.Row(
        [
            dbc.Col(total_doughnut_card, md=6),
        ], className='mb-4'),
])

weather_tab = html.Div([
    weather_controls,
    weather_scatter_card
])

desease_tab = html.Div([
    dbc.Row(
        [
            dbc.Col(dcc.Dropdown(
                id='desease',
                options=[
                    {'label': 'Malignant tumors of the trachea, bronchi and lungs',
                     'value': 'di cui tumori maligni della trachea, dei bronchi e dei polmoni'},
                    {'label': 'Malignant tumors of the prostate', 'value': 'di cui tumori maligni della prostata'},
                    {'label': 'Malignant tumors of the brain and central nervous system',
                     'value': 'di cui tumori maligni del cervello e del sistema nervoso centrale'},
                    {'label': 'Other malignant tumors', 'value': 'di cui altri tumori maligni'},
                    {'label': 'Malignant skin melanomas', 'value': 'di cui melanomi maligni della cute'},
                    {'label': 'Malignant tumors of the esophagus', 'value': "di cui tumori maligni dell'esofago"},
                    {'label': 'Non-malignant tumors (benign and of uncertain behavior)',
                     'value': 'tumori non maligni (benigni e di comportamento incerto)'},
                    {'label': 'Leukemia', 'value': 'di cui leucemia'},
                    {'label': "Hodgkin's disease and lymphomas", 'value': 'di cui morbo di hodgkin e linfomi'},
                    {'label': 'Malignant tumors of the lips, oral cavity and pharynx',
                     'value': 'di cui tumori maligni delle labbra, cavità orale e faringe'},
                    {'label': 'Malignant tumors of the larynx', 'value': 'di cui tumori maligni della laringe'},
                    {'label': 'Malignant thyroid tumors', 'value': 'di cui tumori maligni della tiroide'},
                    {'label': 'Malignant breast tumors', 'value': 'di cui tumori maligni del seno'},
                    {'label': 'Malignant tumors of the stomach', 'value': 'di cui tumori maligni dello stomaco'},
                    {'label': 'Malignant tumors of the pancreas', 'value': 'di cui tumori maligni del pancreas'},
                    {'label': 'Malignant tumors of the bladder', 'value': 'di cui tumori maligni della vescica'},
                    {'label': 'Malignant tumors of the kidney', 'value': 'di cui tumori maligni del rene'},
                    {'label': 'Malignant tumors of the lymphatic / hematopoietic tissue',
                     'value': 'di cui altri tumori maligni del tessuto linfatico/ematopoietico'},
                    {'label': 'Malignant tumors of the ovary', 'value': "di cui tumori maligni dell'ovaio"},
                    {'label': 'Malignant tumors of the cervix', 'value': 'di cui tumori maligni della cervice uterina'},
                    {'label': 'Malignant tumors of the liver and intrahepatic bile ducts',
                     'value': 'di cui tumori maligni del fegato e dei dotti biliari intraepatici'},
                    {'label': 'Diseases of the skin and subcutaneous tissue',
                     'value': 'malattie della cute e del tessuto sottocutaneo'},
                    {'label': 'Pneumonia', 'value': 'polmonite'},
                    {'label': 'Other chronic diseases of the lower respiratory tract',
                     'value': 'di cui altre malattie croniche delle basse vie respiratorie'},
                    {'label': 'Other diseases of the respiratory system',
                     'value': 'altre malattie del sistema respiratorio'},
                    {'label': 'Tuberculosis', 'value': 'tubercolosi'},
                    {'label': 'Flu', 'value': 'influenza'},
                    {'label': 'Asthma', 'value': 'di cui asma'},
                    {'label': 'Other ischemic heart diseases', 'value': 'du cui altre malattie ischemiche del cuore'},
                    {'label': 'Cerebrovascular diseases', 'value': 'malattie cerebrovascolari'},
                    {'label': 'Other diseases of the circulatory system',
                     'value': 'altre malattie del sistema circolatorio'},
                    {'label': 'Acute myocardial infarction', 'value': 'di cui infarto miocardico acuto'},
                    {'label': 'Other heart diseases', 'value': 'altre malattie del cuore'},
                    {'label': "Alzheimer's disease", 'value': 'malattia di alzheimer'},
                    {'label': "Parkinson's disease", 'value': 'morbo di parkinson'},
                    {'label': 'Other diseases of the nervous system and sense organs',
                     'value': 'altre malattie del sistema nervoso e degli organi di senso'},
                    {'label': 'Diabetes mellitus', 'value': 'diabete mellito'},
                    {'label': 'Diseases of the blood and hematopoietic organs and some disorders of the immune system',
                     'value': 'malattie del sangue e degli organi ematopoietici ed alcuni disturbi del sistema immunitario'}
                ],
                value=['du cui altre malattie ischemiche del cuore'],
                multi=True,
                clearable=False
            ),
                md=6
            ),
            dbc.Col(dcc.Dropdown(
                id='desease_pollutant',
                options=[
                    {'label': 'Pm 10', 'value': 'PM10'},
                    {'label': 'Pm 2.5', 'value': 'PM25'},
                    {'label': 'CO 8h mean', 'value': 'CO_8h'},
                    {'label': 'O3', 'value': 'O3'},
                    {'label': 'C6H6', 'value': 'C6H6'},
                    {'label': 'SO2', 'value': 'SO2'},
                    {'label': 'NO2', 'value': 'NO2'}
                ],
                value='PM10',
                clearable=False
            ),
                md=6
            ),
        ], className='mb-4'),
    dbc.Row(
        [
            dbc.Col(trend_card, md=6),
            dbc.Col(desease_card, md=6),
        ], className='mb-4'),
    dbc.Row([
            dbc.Col(trend_card,md=6),
            dbc.Col(correlation_coeff_card, md=6)
        ], className='mb-4')
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
    Output(component_id='spider_graph', component_property='figure'),
    Output(component_id='doughnut_graph', component_property='figure'),
    Output(component_id='area_graph', component_property='figure'),
    Output(component_id='description', component_property='children'),
    Output(component_id='days_over_card', component_property='children'),
    Input(component_id='pollutant', component_property='value'),
    Input(component_id='year', component_property='value'),
    Input(component_id='map_graph', component_property='clickData'),
)
def update(pollutant, year, click):
    province = 'MI'
    if click is not None:
        province = click['points'][0]['location']
    return (
        map_graph(pollutant, year, province),
        sg2(pollutant, year, province),
        doughnut_graph(pollutant, year, province),
        area_graph(pollutant, year, province),
        update_description(pollutant),
        update_days(pollutant, year, province)
    )


@app.callback(
    Output('trend_graph', 'figure'),
    Input('desease', 'value')
)
def trend_update(desease):
    return trend_graph(desease, tab='desease')


@app.callback(
    Output('desease_graph', 'figure'),
    Output('correlation_coeff_card', 'children'),
    Input('desease_pollutant', 'value'),
    Input('desease', 'value')
)
def desease_update(pollutant, desease):
    return (desease_graph(pollutant, desease), update_cc(pollutant, desease))

if __name__ == '__main__':
    app.run_server(debug=True)

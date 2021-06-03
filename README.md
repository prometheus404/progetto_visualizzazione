# Air quality analysis

## Case study
We observed the pollution levels in Lombardia (Italy) from 2006 to 2018. We decided to study 2 different relations:
- Relation between pollution and weather conditions
- Relation between pollution and deseases

We made a dashboard using plotly, a powerful Python module.
Here is the list of the pollutants we analyzed:
- PM 10
- PM 2.5
- NO2
- O3
- SO2
- CO 8h
- C6h6
## Weather conditions
We checked if different weather conditions affected the pollution levels in Lombardia.
Using the dashboard, a user can choose the pollutant and a weather condition between:
- Humidity
- Temperature
- Wind speed
- Global radiation
- Precipitation

The dashboard will show the "scatter plot" between the chosen elements.
## Deseases
We checked if a specified pollutant affected the number of deaths for a given desease in Lombardia.
Using the dashboard, a user can choose the pollutant and a desease.
The dashboard will show the scatter plot between that elements.
## Other tabs of the dashboard
- General Tab

Here we displayed a "choropleth map" that clearly shows which province is the most polluted, a "line chart" that shows the pollution trend among the years and a "donut chart" that shows the most prevalent pollutant.

- Specific Tab

Here we displayed an "interactive choropleth map" that permits the user to click to a specific province and analyze the pollution levels for that province in the specified year. Based on the user's click the dashboard shows also a "spider graph" that highlights the pollutant level among the months of the selected year, a "donut chart" like the one explained above that shows the most prevalent pollutant in the selected year and finally a "box plot" and a "area chart" that show the distribution of the pollutant level and if the pollutant exceeded the legally admitted limits.

## Datasets used
We took the datasets about the deseases from ISTAT:
- (https://www.istat.it/).

We took the datasets about the weather conditions and the pollution levels from Open Data Lombardia:
- (https://www.dati.lombardia.it/)
## Project made by
Carmini Marco - marco.carmini@studenti.unimi.it - @marco-carmini<br>
Cesana Marco - marco.cesana@studenti.unimi.it - @baltornat<br>
Conforto Galli Riccardo - riccardo.confortogalli@studenti.unimi.it - @prometheus404<br>
Intagliata Giacomo - giacomo.intagliata@studenti.unimi.it - @GiacomoInt<br><br>
Copyright © Università degli Studi di Milano

**Design choices**

First of all, we chose to divide the software in to several separate modules to decrease coupling and increase maintainability.
Four modules can be distinguished:
1. A module that uses the Strava API to obtain data from Strava and filter this.
2. A module that uses web scraping to obtain weather data, filters this data and calculates weather scores.
3. A module that uses the Strava and weather data to perform the actual analysis.
4. A module that uses the analysis to generate visualisations like heat maps.

An visualisation of the modules is attached.

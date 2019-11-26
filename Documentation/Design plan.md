**Design choices**

*Modules*

First of all, we chose to divide the software in to several separate modules to decrease coupling and increase maintainability.
Four modules can be distinguished:
1. A module that uses the Strava API to obtain data from Strava and filter this.
2. A module that uses web scraping to obtain weather data, filters this data and calculates weather scores.
3. A module that uses the Strava and weather data to perform the actual analysis.
4. A module that uses the analysis to generate visualisations like heat maps.

An visualisation of the modules is attached, including interfaces and methods per module.

Another advantage of modularization is that different team members can work on separate modules, without having to wait for others to finish their work.

*External libraries*

During this project, we plan to use the following external libraries:
* BeautifulSoup to scrape the weather data
* Pandas to perform data analysis
* Numpy to perform data analysis
* Requests to scrape the weather data
* Strava API to obtain segment data

*Data storage*

If needed, we plan to store obtained data for later analysis, using ...

**Design validation**

**MOSCOW method of features**

*Must Have*
* Strava module
* Weather module
* Analysis module
* Controller module

*Should Have*
* Visualisation Module

*Could Have*
* Advice where you should bike based on weather predictions
* Interactive heat map

*Won't Have*
* App to show data results
* Feedback to Strava
* Expand data analysis to outside The Netherlands
* Implementation of traffic signs and jam avoidance


**Modules**

First of all, we chose to divide the software in to several separate modules to decrease coupling and increase maintainability.
Four modules can be distinguished:
1. A module that uses the Strava API to obtain data from Strava and filter this.

2. A module that uses web scraping to obtain weather data, filters this data and calculates weather scores.
    - The weather data will be obtained from the KNMI API. Here the weather scores are determined. Sun hours, windspeed, extreme wheather conditions (mist, thunder, ice forming), hours of rain

3. A module that uses the Strava and weather data to perform the actual analysis.
    - A baseline will be determined for each day of the week. The baseline represents the average number of visitors per Strava segment for the
      past couple of years (the amount of years needs to be further defined). 
    - The data per day of the week will be sorted on base of the three weather types. Afterwards the data of these three types will also be averaged seperately as the baseline. 

4. A module that uses the analysis to generate visualisations like heat maps.
    - The averages of the weather types will be compared to the baseline in percentages. These percentages will become the intensities for the heatmaps. 

5. A module for the control of the four other modules and where parameters for the tool can be filled in.
    - The type of weather can be choosen and the day of interest. 

An visualisation of the modules is attached (Modules.jpg), including interfaces and methods per module.

Another advantage of modularization is that different team members can work on separate modules, without having to wait for others to finish their work.

**External libraries**

During this project, we plan to use the following external libraries:
* BeautifulSoup to scrape the weather data
* Pandas to perform data analysis
* Numpy to perform data analysis
* Requests to scrape the weather data
* Strava API to obtain segment data


**Data storage**

If needed, we plan to store obtained data for later analysis, using a csv file. 

**Design validation**
For the analysis of the data a baseline will be determined for each day of the week. This baseline represents an average of the number of visitors per Strava segment for the
past couple of years (this number needs to be further defined). While this baseline is used for the visualization of the heatmaps, it can also be used to check if the weather has a significant influence
on the number of visitors per segment. A difference of 20% (this percentage could change later in the project) in comparision with the baseline stands for a causation between the (certain type of) weather and outdoor sporting activities. 


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
# **Modules**

We will divide the software into several separate modules to decrease coupling and increase maintainability. The diagram below maps the interfaces of each module,
which clarifies each module's requirements and should facilitate clear communication between development teams. The primary functions of each are outlined below.

**Strava Module**
Historic data will be retrieved from Strava via the API. This allows us to gather data for a specific time frame up to the current date. In this way the data is "live", 
as each day the data source is updated. The module will then:
- Filters and store the data in a pandas dataframe
- Determine which segments which will be used in the analysis
- Filter the leaderboard as needed


**Weather Module**
The weather will be obtained from the KNMI. This module will then:
- Filter and store the data in a pandas dataframe
- Determine a Weather Score for each day. This will consist of 5 individual scores: sun hours, average windspeed, extreme wheather (boolean), hours of rain
- Calculate an overall weather score and verify acceptable accuracy with the KNMI weercijfer
- Extreme weather such as fog, ice, or thunder will also be taken into account


**Analysis Module**
This is the core of the program, and will follow in general a 3 step process:

0. Calculate a baseline segment intensity<sup>[1]</sup>. This will represent the averge usage intensity of each segment over the past few years. (This may not need to be done each time)
1. For each day in the requested time frame, compare the all segments' intensity to the baseline. This will result in a positive or negative percentage, where 0% is no change.
2. For each weather type (tbd), create an aggregate segment intensity map. Segment  days with the same weather type
* A baseline will be determined for each day of the week. The baseline represents the average number of visitors per Strava segment for the
  past couple of years (the amount of years needs to be further defined). 
* The data per day of the week will be sorted on base of the five paremeters. Afterwards the data of these five will be seperately averaged as the baseline. 

[1]: segment intensity refers to number of users of a segment for the given time frame


**Visualization Module**
4. A module that uses the analysis to generate visualizations like heat maps. 
    * The averages of the weather parameters will be compared to the baseline in percentages. These percentages will become the intensities for the heatmaps. A heatmap of the overall weather score is also included.

**Control Module**
5. A module for the control of the four other modules and where parameters for the tool can be filled in.
    - The type of weather and the day of interest for the visualization can be choosen.


![PackageInterfaces](./PackageInterfaces.svg "Module Interfaces diagram")



Another advantage of modularization is that different team members can work on separate modules, without having to wait for others to finish their work.

**External libraries**

During this project, we plan to use the following external libraries:
* BeautifulSoup to scrape the weather data
* Pandas to perform data analysis
* Numpy to perform data analysis
* Requests to scrape the weather data
* Strava API to obtain segment data
* Gmplot to display the data as a heatmap


**Data storage**

If needed, we plan to store obtained data for later analysis, using a csv file. 

**Design validation**
For the analysis of the data a baseline will be determined for each day of the week. This baseline represents an average of the number of visitors per Strava segment for the
past couple of years (this number needs to be further defined). While this baseline is used for the visualization of the heatmaps, it can also be used to check if the weather has a significant influence
on the number of visitors per segment. A difference of 20% (this percentage could change later in the project) in comparision with the baseline stands for a causation between the (certain type of) weather and outdoor sporting activities.

The overall weatherscore will be compared with the weatherscore the KNMI provides to check whether it makes sense. 


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
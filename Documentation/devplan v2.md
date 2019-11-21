**Objectives**

Compare Strava segment activity with weather scores.


**Context**

Strava segments may differ in popularity based on the weather.
Our aim is to check whether a correlation between segment activity and the type of weather exists.

**Requirements**
*





* User can input start and destination (GPS coordinates)
* User can select time of day
* User can select mode of transportation
* data from Buienradar/EWI and google maps needed
* multiple routes needed from google maps
* pipeline to obtain weather data at specific time and location
* need for data analysation, not simple web requests
* function to calculate weather score

**Constraints**
* EWI radar data is limited for Delft region
* route with smallest chance of rain is not the fastest
* Buienradar provides data up to 2 hours into the future, so prediction window is limited
* Buienradar data is provided every 5 minutes
* Buienradar uses interpolation to provide weather at a given coordinate, so the resolution of this interpolation needs to be taken into account. 
* Sometimes google does not provide alternative routes, then only one score is calculated, with a message saying that there is only one route

**Approach**

User inputs start and origin coordinates and mode of transportation. Use google api to obtain all possible routes. Obtain weather data per waypoint for each route from Buienradar/EWI.
Calculate a weather score based on the weather data of the entire route. Return route with best score.

**Resources**
* Google maps api
* Buienradar (webscrape) or EWI weather data
* Beautifulsoup?

**Priorities**
* responding to change over following a plan
* working software over comprehensive documentation
* global design plan with clear modules needed before implementation is started
* first a working back end is made, if possible some kind of user interface
* follow Test Driven Development and use Gitlab pipeline

**Results expected**
* ranking of Google Maps routes with smallest chance of rain
* proof that different routes result in different chances of getting wet

**Code base and documentation**

GitLab will be used to manage code versions and store documentation.

**Implementation planning**


**Data Validation**
* Heat map of segment activity for different weather types
* Filtering of obviously false data is mostly done by Strava

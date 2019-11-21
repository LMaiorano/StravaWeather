**Objectives**

Compare Strava segment activity with weather scores.


**Context**

Strava segments may differ in popularity based on the weather.
Our aim is to check whether a correlation between segment activity and the type of weather exists.

**Requirements**
* Obtain weather data and KNMI warnings
* Use Strava API to obtain segment activity data
* function to calculate weather scores based on wind, rain, and KNMI warnings
* Date range is specified to 
* Strava activity is specified to cycling
* pipeline output should be verifiable

**Constraints**
* Weather data is available for The Netherlands only
* Not all people who do sports use Strava, and not all Strava users publish their activities, so not all activities on the segments are registered


**Approach**




**Resources**
* Google maps api
* Buienradar (webscrape) or EWI weather data
* Beautifulsoup?

**Priorities**
* responding to change over following a plan
* working software over comprehensive documentation
* global design plan with clear modules needed before implementation is started
* follow Test Driven Development and use Gitlab CI pipeline

**Results expected**


**Code base and documentation**

GitLab will be used to manage code versions and store documentation.

**Implementation planning**


**Data Validation**
* Heat map of segment activity for different weather types
* Filtering of obviously false data is mostly done by Strava
* If a KNMI warning is given, there should be very little activities

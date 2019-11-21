**Objectives**

Investigate correlation between Strava segment activity and weather scores.

**Context**

Strava is widely used by atheletes around the world to keep track of their sports activities.
Moreover, usings so-called segments, users can compete against each other on certain specified tracks.
Strava segments may differ in popularity based on the weather.
Our aim is to check whether a correlation between segment activity and the type of weather exists.

**Approach**
First, using the Strava API, segment ranking data is used to calculate daily activity frequency per segment for a given timeframe.
Next, weather data from these days and locations are obtained from the KNMI, as well as the KNMI weather warnings.
This is used to calculate weather scores based on rain, wind, and the weather warnings.
For a given weather type, filter the days with that specific weather type.
Then, filter the strava data for those days and generate a heat map displaying the activities per segment.
A reference output is generated, so that further weather dependent outputs can be interpreted.


**Requirements**
* Obtain weather data and KNMI warnings
* Use Strava API to obtain segment activity data
* function to calculate weather scores based on wind, rain, and KNMI warnings
* Date range is specified
* Strava activity is specified to cycling
* pipeline output should be verifiable
* reference output to interpret weather dependent outputs

**Constraints**
* Weather data is available for The Netherlands only
* Not all people who do sports use Strava, and not all Strava users publish their activities, so not all activities on the segments are registered


**Resources**
* Strava api
* KNMI weather data
* Beautifulsoup?

**Priorities**


* 
* responding to change over following a plan
* working software over comprehensive documentation
* global design plan with clear modules needed before implementation is started
* follow Test Driven Development and use Gitlab CI pipeline

**Results expected**
* Difference between different segments dependent on the weather type
* 

**Code base and documentation**

GitLab will be used to manage code versions, store documentation and enable a Continuous Integration pipeline.

**Implementation planning**


**Data Validation**
* Heat map of segment activity for different weather types
* Filtering of obviously false data is mostly done by Strava
* If a KNMI warning is given, there should be very little activities

**Requirements validation**


*  Obtain weather data and KNMI warnings: check
* Use Strava API to obtain segment activity data: check 
* Create function to calculate weather scores based on wind, rain, and KNMI warnings: check
* Date range as input parameter: check
* Strava activity is specified to cycling: check
* Pipeline output should be verifiable: done using specified weather scenarios
* The intensity (total number) of activities must be normalized, to allow for comparison between high and low usage days: check


**MOSCOW method of features**

The Must Have and Should Have requirements are incoporated in the design.

**Approach validation**

The pipeline is correctly based on the approach, as can be seen in the interface diagram.
The main difference is that the filtering of the weather data is done within the weather module, instead of an external one.

**Priorities validation**

Priorities have shifted a bit, vizualisation has become more important, because without it, there is no way of validating the analysis results
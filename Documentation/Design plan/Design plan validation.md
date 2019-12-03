**Requirements validation**

* [x] Obtain weather data and KNMI warnings
* [x] Use Strava API to obtain segment activity data
* [x] Create function to calculate weather scores based on wind, rain, and KNMI warnings
* [x] Date range as input parameter
* [x] Strava activity is specified to cycling
* [x] Pipeline output should be verifiable
* [x] The intensity (total number) of activities must be normalized, to allow for comparison between high and low usage days

the verification of the output is done by comparing the outputs to logical scenarios.

**MOSCOW method of features**

The Must Have and Should Have requirements are incoporated in the design.

**Approach validation**

The pipeline is correctly based on the approach, as can be seen in the interface diagram.
The main difference is that the filtering of the weather data is done within the weather module, instead of an external one.
In practice, the approach has not changed, just the implementation in the design. The design plan has been adjusted accordingly.

**Priorities validation**

The priorities have shifted a bit, vizualisation has become more important, because without it, there is no way of validating the analysis results
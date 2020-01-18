**Test Plan**

As described in the Development Plan, Test Driven Development will be used to make sure that all functions and systems are tested properly before implementation. This has resulted in a lot of tests using unittest. 

**Test Validation**

A lot of tests are for small functions, so validation for those tests was done using a code and test results review. For the Strava Module however, it proved very difficult to validate the tests, since functions were often dependent on whether the request or a certain time limit was reached. This implied a lot of waiting time, so those functions were often tested for functionality using log files to check if something had gone wrong. Also, instead of actually performing requests, a virtual environment was built to check whether the system as a whole performed as expected. The virtual environment enabled the test to run in less than a minute, whereas the actual program takes around 40 hours to complete all iterations. 

**Hypothesis Testing**

The output of the data analysis pipeline is visualised through a series of heat maps. The user can specify the weather types that need to be taken into account. To validate the results and test the hypothesis specified in the Development Plan, visual inspection is needed so multiple heat maps can be compared with each other. In a next project this could be done automatically, but that was out of the scope of this project.

*stuk over hypothesis test results!*

**Test results validation**

By using Continuous Integration on GitLab, tests were always done when a commit was pushed. By using Test Driven Development, the tests were written alongside with the code, which improves the accuracy of the tests.

The analysis results can be validated using a list of weather types and their expected outcomes:
*  Cyclists will less likely ride on the road in the rain, and will therefore look for routes in the forest or rural areas.
*  On days with high wind, coastal areas will have less activity than other regions.
*  On days with extreme weather, the overall activity will be much less.


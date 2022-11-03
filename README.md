# Transit Equity Analysis in Baltimore

This is the repository for the project by the Transit Equity team at [Data Science for Democracy 2022](https://snfagora.jhu.edu/event/ams-data-science-for-democracy/). The code here can be used to reproduce the analysis presented on the [website representing the final product](https://storymaps.arcgis.com/stories/a25710230e0a428dbe8dc3c1d9049f84).

## Where to start

The `docs` directory contains a [step-by-step listing](docs/README.md) of all documentation and associated source code. Since most of the code was written in Jupyter notebooks and Rmarkdown, this is really the same thing as the `src` directory, just in a more convenient to read format.

## Question/comments/contributions

If you find a mistake or have a question, please don't hesitate to create a New Issue.

## Next Steps:
- Uncertainties for estimates:
  - Job Accessibility:
    - Tune time threshold + multiple plots
    - Tune travel time of the red line (some deterministic estimate + error)
    - Simulation using Job accessibility to define probabilities to travel and get distributions of average commute time for each tract
    
- Disadvantaged/Non-disadvantaged Groups 
  - Increase in job accessibility: add confidence interval by percentile cuts
  
- Data Requests
  - Verify the validity of driving time (where that data comes from) -> for interpretability
  - Check all census data updates - make sure to check changes in cencus tracts
  - Travel time between tracts outside Baltimore City

## Authors

- [Craig Gross](https://math.msu.edu/~grosscra)
- Adam Lee
- Kethaki Varadan
- Xinyu Xie

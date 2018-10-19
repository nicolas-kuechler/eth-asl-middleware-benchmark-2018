# Art Of Computer Systems Performance Analysis Techniques

## 6. Workloads

### 6.3 Specifying Dispersion
- specify variability by min/max range
- specify variability by percentiles
- Use std. dev instead of variance
- C.O.V Coefficient of Variation: The ratio between standard deviation and mean = std dev / mean (if C.O.V=0 => 0 Variance, C.O.V. high => high variance => not good enough) C.O.V. of 5 is large, and a C.O.V. of 0.2 (or 20%) is small no matter what the unit is.

## 12. Stats

### Selecting index of dispersion
If there are no natural bounds, then check to see if the **distribution is unimodal symmetric**. If it is, then it makes sense to measure the average distance from the mean, that is, the variance, standard deviation, or coefficient of variation. If the **distribution is nonsymmetric**, percentiles are the best indices. These guidelines are summarized in Figure 12.4.


## 10. Data Presentation

- Require min Effort from Reader: direct labelling of line charts / column charts better than legend box

- Maximize Info: (CPU time in seconds vs CPU time) (Daily CPU Usage vs. CPU Usage)

- Minimize Ink: Present as much info as possible with as little ink as possible
(no grid lines)

- Use Commonly Accepted Practices: (origin 0,0) (cause on x-axis, effect on y-axis) (linear scales)

- Avoid Ambiguity: Show coordinate axis, scale divisions and origin, not plot multiple variables in same plot

- **three-quarter-high rule?**: The right way to scale a graph is to choose scales such that the vertical height of the highest point is at least three-quarters of the horizontal offset of the right-most point

- don't plot throughput and response time together -> dramatization

- Plotting Random Quantities without Showing Confidence Interval **( Overlapping confidence intervals are generally enough to deduce that the two random quantities are statistically indifferent. This is explained further in Chapter 13.)**

- histogram: determine correct number of bars: at least 5 datapoints per bucket

### Checklist Good Graphics
 1. Are both coordinate axes shown and labeled?
 2.  Are the axes labels self-explanatory and concise?
 3.  Are the scales and divisions shown on both axes?
 4.  Are the minimum and maximum of the ranges shown on the axes appropriate to present the maximum information?
 5.  Is the number of curves reasonably small? (A line chart should generally have no more than six curves).
 6.  Do all graphs use the same scale? (Multiple scales on the same chart are confusing.)
 7.  Is there no curve that can be removed without reducing the information?
 8.  Are the curves on a line chart individually labeled?
 9.  Are the cells in a bar chart individually labeled?
 10.  Are all symbols on the graph accompanied by appropriate textual explanations?
 11.  If the curves cross, are the line patterns different to avoid confusion?
 12.  Are the units of measurement indicated?
 13.  Is the horizontal scale increasing from left to right?
 14.  Is the vertical scale increasing from bottom to top?
 15.  Are the grid lines aiding in reading the curves? (If not, the grid lines should not be shown.)
 16.  Does this whole chart add to information available to the reader?
 17.  Are the scales contiguous? (Breaks in the scale should be avoided or clearly shown.)
 18.  Is the order of bars in a bar chart systematic? (Alphabetic, temporal, or best-to-worst ordering is to be preferred over random placement.)
 19.  If the vertical axis represents a random quantity, are confidence intervals shown?
 20.  Are there no curves, symbols, or texts on the graph that can be removed without affecting the information?
 21.  Is there a title for the whole chart?
 22.  Is the chart title self-explanatory and concise?
 23.  For bar charts with unequal class interval, is the area and width representative of the frequency and interval, respectively?
 24.  Do the variables plotted on this chart give more information than other alternatives?
 25.  Does the chart clearly bring out the intended message?
26.  Is the figure referenced and discussed in the text of the report?

### Common Mistakes
- Presenting Too Many Alternatives on a Single Chart: (line chart <= 6 curves, bar chart <= 10, pie chart <= 8, number of bars in histogram should indicate that each cell has at least 5 data points)

- Presenting many y-variables on single chart: not showing "a line chart of response time, utilization, and throughput as a function of number of users" do it separately
- Using Symbols instead of text (mean vs jobs/sec)
- Placing Exraneous Information on the Chart (eg grid lines)
- Selecting Scale Ranges Improperly
- **Using a Line Chart in Place of a Column Chart:  Line chart should not be used if intermediate values cannot be interpolated.**

# Projection method

The base projection has Gies undergraduate headcount rising from 3,652 in Fall 2026 to 3,841 in Fall 2030, with low and high scenarios of 3,632 and 4,171. Online graduate headcount is projected flat at 5,763, with an 80% interval of 3,682 to 7,844 by Fall 2030. In the backtest the undergraduate model did about as well as the naive forecast, not clearly better, and the plan's model for the online series lost to naive at every horizon, so it was replaced. `make forecast` reruns both and rewrites data/marts/mart_projection and reports/backtest.md.

## Undergraduate headcount

Headcount is a stock with two inflows and one rate:

    H(t+1) = F(t+1) + T(t+1) + c × H(t)

H is Gies undergraduate headcount, F first-time freshmen, T new transfers, and c the share of last fall's undergraduates enrolled again this fall. c is estimated from the totals:

    c(t) = (H(t+1) − F(t+1) − T(t+1)) / H(t)

so it absorbs graduation, attrition, readmits, and nondegree students in one number. Class levels come from credit hours (312 of the 787 first-time freshmen in Fall 2025 had sophomore standing), so the model never moves students from one class to the next. The identity holds exactly in the data: in every fall from 2012 to 2026, continuing students, first-time freshmen, new transfers, and readmits add up to undergraduate headcount.

| Transition into fall | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c | 0.792 | 0.808 | 0.791 | 0.794 | 0.796 | 0.779 | 0.780 | 0.750 | 0.806 | 0.781 | 0.771 | 0.790 | 0.769 | 0.801 |

The transitions into Fall 2020 and Fall 2021 are covid-affected and left out of every estimate of c. Into Fall 2020, c fell to 0.750, the lowest in the series; into Fall 2021 it rebounded to 0.806.

| Scenario | First-time freshmen | New transfers | c | Fall 2027 | Fall 2030 |
|---|---:|---:|---:|---:|---:|
| Low | 744 | 83 | 0.772 | 3,645 | 3,632 |
| Base | 783 | 83 | 0.781 | 3,718 | 3,841 |
| High | 822 | 83 | 0.800 | 3,828 | 4,171 |

- Base: freshmen and transfers at their mean over Falls 2024 to 2026, and c at the median of the last five non-covid transitions (into Falls 2022 to 2026).
- Low and high: c at the 10th and 90th percentiles of the 12 non-covid transitions, and freshmen 5% below or above base. Transfers stay at base.
- The base assumes fewer freshmen than Fall 2026's 901, yet headcount still rises: 783 freshmen and 83 transfers a year at c = 0.781 sustain about 3,950 undergraduates, more than the 3,652 enrolled now.

## Online graduate headcount

The series is every Gies graduate student in an online program (a program code ending in U), 982 in Fall 2017 and 5,763 in Fall 2026. There are no Gies online codes before Fall 2017. The projection is exponential smoothing with additive errors and no trend (statsmodels ETSModel), with an 80% prediction interval. The fitted smoothing weight is 0.9999, so the point forecast is the last value and the interval carries the uncertainty. Ten falls is a short series, and the first five are the launch ramp.

The plan called for a damped trend. It carried the 2017 to 2021 ramp forward: from Fall 2021 it forecast 10,083 for Fall 2025 against an actual 5,466, and it lost to the naive forecast by 8 to 54 percentage points at every horizon. I replaced it with the no-trend model on Oct 24, 2026, and the backtest still reports both.

## Backtest

Each fall from 2016 to 2025 is an origin. From each, the model sees only data through that fall and forecasts 1 to 4 falls ahead, through Fall 2026. Naive is the last value; drift adds the average yearly change since the series began. Each cell is the mean absolute percentage error, the mean signed error (positive means the forecast ran high), and the number of forecasts.

| Undergraduate headcount | 1 year | 2 years | 3 years | 4 years |
|---|---:|---:|---:|---:|
| Stock and flow, three-year mean intake | 2.8% (−0.9%, 10) | 3.6% (−1.3%, 9) | 3.7% (−1.3%, 8) | 4.2% (−1.3%, 7) |
| Stock and flow, latest intake | 2.9% (−0.5%, 10) | 4.7% (−1.0%, 9) | 5.0% (−1.1%, 8) | 5.7% (−1.2%, 7) |
| Naive | 2.9% (−1.6%, 10) | 3.9% (−2.4%, 9) | 3.9% (−2.9%, 8) | 4.7% (−3.3%, 7) |
| Drift | 3.1% (−0.6%, 10) | 4.1% (−0.6%, 9) | 5.0% (−0.1%, 8) | 6.0% (+0.6%, 7) |
| Stock and flow given the actual intake | 1.5% (+0.6%, 10) | 1.7% (+1.4%, 9) | 2.6% (+2.2%, 8) | 3.4% (+3.2%, 7) |

The model with three-year mean intake has a lower error than naive at every horizon, by 0.1 to 0.5 points, on 7 to 10 forecasts each. That is too small a margin to call a win. Holding intake at its latest value loses to naive at every horizon. Given the freshmen and transfers that actually arrived, the one-year error halves, so most of the error is in guessing intake, not in c.

| Online graduate headcount | 1 year | 2 years | 3 years | 4 years |
|---|---:|---:|---:|---:|
| Damped-trend ETS (the plan's model) | 15.5% (+8.0%, 5) | 33.1% (+17.2%, 4) | 49.6% (+24.9%, 3) | 60.1% (+60.1%, 2) |
| ETS without trend (used) | 7.6% (+0.2%, 5) | 12.5% (+0.2%, 4) | 10.8% (−2.3%, 3) | 6.0% (−1.3%, 2) |
| Naive | 7.6% (+0.2%, 5) | 12.5% (+0.2%, 4) | 10.8% (−2.3%, 3) | 6.0% (−1.3%, 2) |
| Drift | 14.8% (+14.8%, 5) | 32.0% (+32.0%, 4) | 47.9% (+47.9%, 3) | 72.3% (+72.3%, 2) |

The online origins start in Fall 2021, once five falls exist. With 2 to 5 forecasts per horizon these errors are a sanity check, not a measurement.

## WICHE what-if

This is a what-if, not a forecast, and it is institution-level. If UIUC's in-state applicants rise and fall with Illinois's public and private high school graduates from Fall 2025 on, and in-state yield holds at its Fall 2025 level, what in-state admit rate keeps in-state enrollment flat through Fall 2035? Flat enrollment at a fixed yield needs the same number of admits each year, so the answer is Fall 2025's in-state admits divided by each year's projected in-state applicants. WICHE projects 144,561 Illinois graduates in the class of 2025 and 119,005 in the class of 2035, 17.7% fewer.

The what-if reads only verified Common Data Set rows (data/manual/cds_c1.csv). Illinois's Fall 2025 in-state figures are 29,419 applicants, 14,509 admits (49.3%), and 6,587 enrolled (a yield of 45.4%). Holding in-state enrollment flat as the class of 2035 shrinks would take an in-state admit rate of 59.9% by Fall 2035. This leans on two simplifications: that in-state applicants move one for one with Illinois graduates, and that yield holds; neither is likely to hold exactly, which is why it is a what-if.

## What would change the outlook

Each 50 more first-time freshmen a year adds 143 undergraduates by Fall 2030. Each 0.01 added to c adds 109. If freshmen hold at Fall 2026's 901 instead of the three-year mean, the base reaches 4,180 by Fall 2030 instead of 3,841.

Holding freshmen at Fall 2026's 901 instead of the three-year mean of 783 would add about 340 undergraduates by Fall 2030, about as much as the whole high scenario. A one-point change in the share who continue moves Fall 2030 by about 110, so intake, not continuation, is the number to watch.

## Decisions

Om made these on Oct 24, 2026: leave the transitions into Fall 2020 and Fall 2021 out of c; hold intake at the three-year mean, after the backtest; project four falls, to Fall 2030, the horizons the backtest checks; replace the damped-trend model for the online series with exponential smoothing without trend, after the backtest.

import QuantLib as ql
from scipy.interpolate import CubicSpline
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def parse_tenor(tenor_str):
    tenor_to_time = {
        'D': ql.Days,
        'W': ql.Weeks,
        'M': ql.Months,
        'Y': ql.Years
    }
    # Extract the number and unit
    num = int(tenor_str[:-1])
    unit = tenor_str[-1].upper()
    if unit not in tenor_to_time:
        raise ValueError(f"Unsupported tenor unit: {unit}")
    return ql.Period(num, tenor_to_time[unit])


def tenor_to_date(input_tenor, ref_date=None):
    """
    Convert a tenor string (e.g., "1D", "1M", "10Y") to a date offset from today.

    Parameters:
        tenor (str): The tenor string (e.g., "1D", "1M", "10Y").
        ref_date (datetime, optional): Reference date. If None, today's date is used.

    Returns:
        datetime: The target date.
    """
    if ref_date is None:
        ref_date = datetime.today()
    tenor = '1D' if input_tenor == 'ON' else input_tenor
    match tenor[-1].upper(), tenor[:-1]:
        case 'D', number_str:
            number = int(number_str)
            target_date = ref_date + timedelta(days=number)
        case 'W', number_str:
            number = int(number_str)
            target_date = ref_date + timedelta(weeks=number)
        case 'M', number_str:
            number = int(number_str)
            target_date = ref_date + pd.DateOffset(months=number)
        case 'Y', number_str:
            number = int(number_str)
            target_date = ref_date + pd.DateOffset(years=number)
        case _:
            raise ValueError(f"Unsupported tenor format: {tenor}")
    result = (target_date - ref_date).days/365.25
    return result


def piecewise_cubic_curve(zero_rates, query_points):
    """
    Create a MonotonicCubicZeroCurve from given tenors and zero rates, and evaluate it
    over a given set of queried points.

    Parameters:
        zero_rates (pd.DataFrame): Input DataFrame with columns ['Tenor', 'Value'].
                           'Tenor' should be strings representing tenors (e.g., '1D', '1M', '1Y').
                           'Value' should be floats with the corresponding rates.

        query_points (list or np.ndarray): Tenors as a list of strings or NumPy array of floats
                                           (years or fractional years) where the interpolated
                                           curve is evaluated.

    Returns:
        pd.DataFrame: DataFrame with columns ['Query Points', 'Interpolated Value'].
    """
    calendar = ql.NullCalendar()
    today = ql.Date.todaysDate()
    day_counter = ql.Actual360()

    times = []
    for tenor_str in zero_rates['Tenor']:
        parsed_period = parse_tenor(tenor_str)
        future_date = calendar.advance(today, parsed_period)
        # time_fraction = day_counter.yearFraction(today, future_date)
        times.append(future_date)

    # Step 2: Prepare QuantLib Interpolation Inputs
    zero_rates = zero_rates['Zero Rate'].values.tolist()

    # Ensure monotonic behavior: QuantLib likes dates + rates
    curve_points = [(t, r) for t, r in zip(times, zero_rates)]
    curve_points.sort()

    # Step 3: Create MonotonicCubicZeroCurve
    quantlib_curve = ql.LogLinearZeroCurve(
        [point[0] for point in curve_points],  # Times
        [point[1] / 100 for point in curve_points],  # Rates (converted to decimal)
        day_counter
    )
    quantlib_curve.enableExtrapolation()

    # Step 4: Evaluate Curve at Query Points
    if isinstance(query_points, np.ndarray):
        query_times = [
            day_counter.yearFraction(today, calendar.advance(today, ql.Period(str(t)))) for t in query_points
        ]
    else:  # Assume query_points is a NumPy array of fractional times (years)
        query_times = query_points

    interpolated_values = [quantlib_curve.zeroRate(t, day_counter, ql.Continuous) * 100
                           for t in query_times]

    result_df = pd.DataFrame({
        'Query Points': query_points,
        'Interpolated Value': interpolated_values
    })

    return result_df


def cubic_spline(df_zero_rates, query_points):
    maturities = [tenor_to_date(tenor) for tenor in df_zero_rates['Tenor']]
    spline = CubicSpline(maturities, df_zero_rates['Zero Rate'])
    result_df = pd.DataFrame({
        'Tenor': query_points,
        'Zero Rate': [spline(t) for t in query_points]
    })
    return result_df


if __name__ == '__main__':
    df = pd.DataFrame({
        'Tenor':     ['1M' , '3M' , '6M' , '1Y' , '2Y' , '3Y' , '5Y' , '7Y' , '10Y', '15Y', '20Y', '30Y'],
        'Zero Rate': [4.496, 4.448, 4.442, 4.087, 4.328, 4.321, 4.419, 4.502, 4.778, 5.085, 5.287, 4.589]
    })
    print(cubic_spline(df, np.linspace(0, 30, 101)))

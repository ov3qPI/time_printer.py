import time
from datetime import datetime
from skyfield.api import load
from skyfield.almanac import find_discrete, seasons
from skyfield.toposlib import Topos

def get_decimal_time(solar_midnight, current_time=None):
    if current_time is None:
        current_time = datetime.now()
    
    seconds_in_day = 24 * 60 * 60
    elapsed_seconds = (current_time - solar_midnight).total_seconds()
    
    if elapsed_seconds < 0:
        elapsed_seconds += seconds_in_day
    
    return round(elapsed_seconds / seconds_in_day, 5)

def calculate_day_of_year(current_time):
    return current_time.timetuple().tm_yday

def calculate_days_since_solstice(current_time, hemisphere="North"):
    year = current_time.year
    if hemisphere == "North":
        solstice_date = datetime(year, 12, 21)
        if current_time < solstice_date:
            solstice_date = datetime(year - 1, 12, 21)
    else:
        solstice_date = datetime(year, 6, 21)
        if current_time < solstice_date:
            solstice_date = datetime(year - 1, 6, 21)

    return (current_time - solstice_date).days

def get_year_fraction(observer_lat=38.478752, observer_lon=-107.877739):
    eph = load('de440s.bsp')
    ts = load.timescale()

    observer = Topos(latitude_degrees=observer_lat, longitude_degrees=observer_lon)
    longitudinal_offset_hours = observer_lon / 15.0

    now = ts.now()
    t_start = ts.tt_jd(now.tt - 365)
    t_end = ts.tt_jd(now.tt + 365)

    times, events = find_discrete(t_start, t_end, seasons(eph))
    december_solstices = [t for t, e in zip(times, events) if e == 3]

    recent_solstice = max([t for t in december_solstices if t.tt < now.tt])
    next_solstice = min([t for t in december_solstices if t.tt > now.tt])

    longitudinal_time_tt = now.tt + (longitudinal_offset_hours / 24.0)
    longitudinal_time = ts.tt_jd(longitudinal_time_tt)

    year_duration = next_solstice.tt - recent_solstice.tt
    elapsed_time = longitudinal_time.tt - recent_solstice.tt

    year_fraction = elapsed_time / year_duration
    return {
        "year_fraction": year_fraction,
        "division_2": int(year_fraction * 2) + 1,
        "division_4": int(year_fraction * 4) + 1,
        "division_8": int(year_fraction * 8) + 1,
        "division_16": int(year_fraction * 16) + 1,
        "division_32": int(year_fraction * 32) + 1,
        "division_64": int(year_fraction * 64) + 1,
    }

def live_decimal_time(solar_midnight):
    try:
        print("Press Ctrl+C to stop.")
        print("\n" * 6)
        
        while True:
            current_time = datetime.now()
            decimal_time = get_decimal_time(solar_midnight, current_time)
            octal_time = round(decimal_time * 800)
            day_of_year = calculate_day_of_year(current_time)
            days_since_solstice = calculate_days_since_solstice(current_time, hemisphere="North")

            year_fraction_data = get_year_fraction()

            print("\033[F\033[K" * 6, end="")
            print(f"Decimal Time: {decimal_time}")
            print(f"Octal Time: {octal_time}")
            print(f"Cal. Year Day: {day_of_year}")
            print(f"Tropical Year Day: {days_since_solstice}")
            print(f"Year Fraction: {year_fraction_data['year_fraction']:.5f}")
            print(f"Divisions: {year_fraction_data['division_2']}/2, {year_fraction_data['division_4']}/4, {year_fraction_data['division_8']}/8, {year_fraction_data['division_16']}/16, {year_fraction_data['division_32']}/32, {year_fraction_data['division_64']}/64")
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    solar_midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    live_decimal_time(solar_midnight)
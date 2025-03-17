import time
from datetime import datetime
from skyfield.api import load
from skyfield.almanac import find_discrete, seasons

def get_decimal_time(solar_midnight, current_time=None):
    if current_time is None:
        current_time = datetime.now()
    
    seconds_in_day = 24 * 60 * 60
    elapsed_seconds = (current_time - solar_midnight).total_seconds()
    
    if elapsed_seconds < 0:
        elapsed_seconds += seconds_in_day
    
    return round(elapsed_seconds / seconds_in_day, 5)

def calculate_days_since_solstice(current_time, observer_lat=38.478752, observer_lon=-107.877739):
    eph = load('de440s.bsp')
    ts = load.timescale()
    now = ts.utc(current_time.year, current_time.month, current_time.day)

    t_start = ts.tt_jd(now.tt - 365)
    t_end = ts.tt_jd(now.tt + 365)
    
    times, events = find_discrete(t_start, t_end, seasons(eph))
    recent_solstice = max([t for t, e in zip(times, events) if e == 3 and t.tt <= now.tt])
    
    return int(now.tt - recent_solstice.tt)

def get_year_fraction(observer_lat=38.478752, observer_lon=-107.877739):
    eph = load('de440s.bsp')
    ts = load.timescale()

    now = ts.now()
    t_start = ts.tt_jd(now.tt - 365)
    t_end = ts.tt_jd(now.tt + 365)

    times, events = find_discrete(t_start, t_end, seasons(eph))
    december_solstices = [t for t, e in zip(times, events) if e == 3]

    recent_solstice = max([t for t in december_solstices if t.tt < now.tt])
    next_solstice = min([t for t in december_solstices if t.tt > now.tt])

    year_duration = next_solstice.tt - recent_solstice.tt
    elapsed_time = now.tt - recent_solstice.tt

    return elapsed_time / year_duration

def live_decimal_time(solar_midnight):
    try:
        print("Press Ctrl+C to stop.")
        print("\n" * 6)
        
        while True:
            current_time = datetime.now()
            decimal_time = get_decimal_time(solar_midnight, current_time)
            days_since_solstice = calculate_days_since_solstice(current_time)
            year_fraction = get_year_fraction()

            print("\033[F\033[K" * 4, end="")
            print(f"Day Decimal: {decimal_time}")
            print(f"Day-of-Year: {days_since_solstice}")
            print(f"Year Decimal: {year_fraction:.7f}")
            print("Year is tropical")

            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    solar_midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    live_decimal_time(solar_midnight)
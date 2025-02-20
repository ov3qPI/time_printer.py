import time
from datetime import datetime, timedelta

def get_decimal_time(solar_midnight, current_time=None):
    """
    Calculate the decimal time from solar midnight to the next midnight.
    
    :param solar_midnight: datetime object representing today's solar midnight.
    :param current_time: datetime object of the current time (default: now).
    :return: Decimal time (float) normalized to a full day.
    """
    if current_time is None:
        current_time = datetime.now()
    
    seconds_in_day = 24 * 60 * 60
    elapsed_seconds = (current_time - solar_midnight).total_seconds()
    
    if elapsed_seconds < 0:
        elapsed_seconds += seconds_in_day
    
    return round(elapsed_seconds / seconds_in_day, 5)

def calculate_day_of_year(current_time):
    """
    Calculate the day of the year.
    
    :param current_time: datetime object of the current time.
    :return: Day of the year as an integer.
    """
    return current_time.timetuple().tm_yday

def calculate_days_since_solstice(current_time, hemisphere="North"):
    """
    Calculate the number of days since the most recent solstice.
    
    :param current_time: datetime object of the current time.
    :param hemisphere: Hemisphere (either "North" or "South").
    :return: Number of days since the solstice.
    """
    year = current_time.year
    if hemisphere == "North":
        solstice_date = datetime(year, 12, 21)  # December solstice
        if current_time < solstice_date:
            solstice_date = datetime(year - 1, 12, 21)
    else:
        solstice_date = datetime(year, 6, 21)  # June solstice
        if current_time < solstice_date:
            solstice_date = datetime(year - 1, 6, 21)

    return (current_time - solstice_date).days

def live_decimal_time(solar_midnight):
    """
    Print live updates of decimal time from solar midnight, day of year, 
    and days since the December solstice, overwriting each line dynamically.
    
    :param solar_midnight: datetime object representing today's solar midnight.
    """
    try:
        print("Press Ctrl+C to stop.")
        print("\n" * 4)  # Reserve space for 4 lines of dynamic output
        
        while True:
            current_time = datetime.now()
            decimal_time = get_decimal_time(solar_midnight, current_time)
            octal_time = round(decimal_time * 800)  # Multiply Decimal Time by 800
            day_of_year = calculate_day_of_year(current_time)
            days_since_solstice = calculate_days_since_solstice(current_time, hemisphere="North")
            
            # Move up 4 lines and clear them
            print("\033[F\033[K" * 4, end="")
            print(f"Decimal Time: {decimal_time}")
            print(f"Octal Time: {octal_time}")
            print(f"Cal. Year Day: {day_of_year}")
            print(f"Tropical Year Day: {days_since_solstice}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    # Replace this with dynamic solar midnight retrieval for accurate results
    # Example: 12:00 AM as solar midnight
    solar_midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    live_decimal_time(solar_midnight)
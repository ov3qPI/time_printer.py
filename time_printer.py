import time
from datetime import datetime, timedelta, timezone
from typing import Optional
from skyfield.api import load
from skyfield.almanac import find_discrete, seasons

DEFAULT_LONGITUDE = -107.877741
SECONDS_IN_DAY = 24 * 60 * 60

def longitudinal_now(longitude: float, now_utc: Optional[datetime] = None) -> datetime:
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)
    offset = timedelta(hours=longitude / 15.0)
    return now_utc.astimezone(timezone(offset))

def day_decimal_from_longitudinal_time(longitude: float, now_utc: Optional[datetime] = None, precision: int = 5) -> float:
    lt = longitudinal_now(longitude, now_utc)
    local_midnight = lt.replace(hour=0, minute=0, second=0, microsecond=0)
    elapsed_seconds = (lt - local_midnight).total_seconds()
    if elapsed_seconds < 0:
        elapsed_seconds += SECONDS_IN_DAY
    frac = elapsed_seconds / SECONDS_IN_DAY
    r = round(frac, precision)
    return 0.0 if r >= 1.0 else r

def _recent_december_solstice_tt(now_tt: float):
    eph = load('de440s.bsp')
    ts = load.timescale()
    t_start = ts.tt_jd(now_tt - 365)
    t_end = ts.tt_jd(now_tt + 365)
    times, events = find_discrete(t_start, t_end, seasons(eph))
    return max([t.tt for t, e in zip(times, events) if e == 3 and t.tt <= now_tt])

def days_since_solstice_local(longitude: float, now_utc: Optional[datetime] = None) -> int:
    lt = longitudinal_now(longitude, now_utc)
    local_midnight = lt.replace(hour=0, minute=0, second=0, microsecond=0)
    utc_at_local_midnight = local_midnight.astimezone(timezone.utc)
    ts = load.timescale()
    now = ts.utc(utc_at_local_midnight.year, utc_at_local_midnight.month, utc_at_local_midnight.day,
                 utc_at_local_midnight.hour, utc_at_local_midnight.minute, utc_at_local_midnight.second)
    sol_tt = _recent_december_solstice_tt(now.tt)
    return int(now.tt - sol_tt)

def get_year_fraction() -> float:
    eph = load('de440s.bsp')
    ts = load.timescale()
    now = ts.now()
    t_start = ts.tt_jd(now.tt - 365)
    t_end = ts.tt_jd(now.tt + 365)
    times, events = find_discrete(t_start, t_end, seasons(eph))
    decs = [t for t, e in zip(times, events) if e == 3]
    recent = max([t for t in decs if t.tt < now.tt])
    nxt = min([t for t in decs if t.tt > now.tt])
    return (now.tt - recent.tt) / (nxt.tt - recent.tt)

def day_of_year_decimal(longitude: float, now_utc: Optional[datetime] = None, precision: int = 5) -> float:
    frac = day_decimal_from_longitudinal_time(longitude, now_utc, precision + 2)
    whole = days_since_solstice_local(longitude, now_utc)
    v = whole + frac
    return float(f"{v:.{precision}f}")

def live_decimal_time(longitude: float = DEFAULT_LONGITUDE, precision: int = 5) -> None:
    try:
        print("Press Ctrl+C to stop.")
        print("\n" * 5)
        while True:
            now_utc = datetime.now(timezone.utc)
            doy_dec = day_of_year_decimal(longitude, now_utc, precision)
            year_frac = get_year_fraction()
            print("\033[F\033[K" * 3, end="")
            print(f"Day-of-Year.Dec: {doy_dec:.{precision}f}")
            print(f"Year Decimal: {year_frac:.7f}")
            print("Year is tropical")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    live_decimal_time()
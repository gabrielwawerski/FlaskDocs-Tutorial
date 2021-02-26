def timestamp() -> str:
    from datetime import datetime
    dt = datetime.now()
    hour, minute, second, day, month, year = format_date_time(dt.hour, dt.minute, dt.second, dt.day, dt.month, dt.year)
    del dt
    return f"{hour}:{minute}:{second} {day}.{month}.{year}"


def format_date_time(*data: int) -> tuple:
    fdata = list()
    for d in data:
        if d <= 9:
            d = str(d)
            fdata.append(d.replace(d, f"0{d}"))  # if value is below 9, insert 0 for proper formatting.
        else:
            fdata.append(str(d))
    return tuple(fdata)

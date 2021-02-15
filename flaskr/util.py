def timestamp():
    from datetime import datetime
    dt = datetime.now()
    hour, minute, second, day, month = format_date_time(dt.hour, dt.minute, dt.second, dt.day, dt.month)
    return f"{hour}:{minute}:{second} {day}.{month}.{dt.year}"


def format_date_time(*data):
    fdata = list()
    for d in data:
        if d <= 9:
            d = str(d)
            fdata.append(d.replace(d, f"0{d}"))  # if value is below 9, insert 0 for proper formatting.
        else:
            fdata.append(str(d))
    return tuple(fdata)

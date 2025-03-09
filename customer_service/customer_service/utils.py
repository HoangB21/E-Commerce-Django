from datetime import datetime
import pytz

def format_datetime(iso_string):
    dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00")).replace(tzinfo=pytz.UTC)
    local_dt = dt.astimezone(pytz.timezone("Asia/Ho_Chi_Minh"))
    return local_dt.strftime("%d/%m/%Y - %H:%M:%S")
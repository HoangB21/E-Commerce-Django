from datetime import datetime
import pytz
import os

def format_datetime(iso_string):
    dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00")).replace(tzinfo=pytz.UTC)
    local_dt = dt.astimezone(pytz.timezone("Asia/Ho_Chi_Minh"))
    return local_dt.strftime("%d/%m/%Y - %H:%M:%S")

# Kiểm tra nếu đang chạy trong container Docker
def is_running_in_docker():
    print("Checking if running in Docker...", os.path)
    return os.path.exists('/.dockerenv') or os.getenv('RUNNING_IN_DOCKER') == 'true'
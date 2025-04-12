# Kiểm tra nếu đang chạy trong container Docker
import os


def is_running_in_docker():
    print("Checking if running in Docker...", os.path)
    return os.path.exists('/.dockerenv') or os.getenv('RUNNING_IN_DOCKER') == 'true'
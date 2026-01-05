import requests

BASE_URL = "http://localhost:5000"


def start_register(user_id: str):
    """
    Sends register command with user ID to backend
    """
    try:
        response = requests.post(
            f"{BASE_URL}/start_register",
            json={"user_id": user_id},
            timeout=3
        )
        return response.status_code == 200
    except requests.RequestException as e:
        print("Register request failed:", e)
        return False


def start_match():
    """
    Sends match command to backend
    """
    try:
        response = requests.post(
            f"{BASE_URL}/start_match",
            timeout=3
        )
        return response.status_code == 200
    except requests.RequestException as e:
        print("Match request failed:", e)
        return False


def stop():
    """
    Sends stop command to backend
    """
    try:
        response = requests.post(
            f"{BASE_URL}/stop",
            timeout=3
        )
        return response.status_code == 200
    except requests.RequestException as e:
        print("Stop request failed:", e)
        return False

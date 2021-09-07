import requests
import os
import sys
from typing import List

import psutil


def send_message(msg: str):
    BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
    if not BOT_TOKEN:
        print("Bot token not found", file=sys.stderr)
    CHAT_ID = os.getenv("TG_CHAT_ID", "")
    if not CHAT_ID:
        print("Chat id not found", file=sys.stderr)
    BOT_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    print(f"Sending message: {msg}")
    response = requests.post(BOT_URL + "sendMessage", {"chat_id": CHAT_ID, "text": msg})
    if response.ok:
        print("Message sent")


def generate_message(
    cpu_usages: List[float],
    mem_percent: float,
    swap_percent: float,
    disk_percent: float,
):
    cpu_str = ", ".join(map(str, cpu_usages))
    return f"""CPU %usage: {cpu_str}
Mem %usage: {mem_percent}
Swap %usage: {swap_percent}
Disk %usage: {disk_percent}"""


def collect_and_send_stats(check_ok=True):
    THRESH = 60
    ok = True

    cpu_usages: List[float] = psutil.cpu_percent(interval=0.1, percpu=True)
    max_usage = max(cpu_usages)
    if max_usage > THRESH:
        ok = False

    mem_percent = psutil.virtual_memory().percent
    if mem_percent > THRESH:
        ok = False
    swap_percent = psutil.swap_memory().percent
    if swap_percent > THRESH:
        ok = False
    disk_percent = psutil.disk_usage("/").percent
    if disk_percent > THRESH:
        ok = False

    if (check_ok and not ok) or (not check_ok):
        send_message(
            generate_message(cpu_usages, mem_percent, swap_percent, disk_percent)
        )


if __name__ == "__main__":
    collect_and_send_stats(check_ok=True)

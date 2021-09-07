"""
Do not put type annotations 
because the centos server runs python3.6
which doesn't support them
"""

from datetime import datetime
import requests
import os
import sys

import psutil

def flatten_list(lst):
    return ",".join(map(str, lst))

def send_message(msg):
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
    cpu_usages,
    mem_percent,
    swap_percent,
    disk_percent,
):
    return f"""CPU %usage: {flatten_list(cpu_usages)}
Mem %usage: {mem_percent}
Swap %usage: {swap_percent}
Disk %usage: {disk_percent}"""


def collect_and_send_stats(check_ok=True):
    THRESH = 60
    ok = True

    cpu_usages = psutil.cpu_percent(interval=0.1, percpu=True)
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

    msg = generate_message(cpu_usages, mem_percent, swap_percent, disk_percent)
    timestamp = datetime.now()
    time_minute = timestamp.time().minute

    # append the CPU usage data every five minutes to the log
    if time_minute == 5:
        with open("data.csv", "wa") as f:
            csv_msg = (
                flatten_list(cpu_usages) + "," + str(mem_percent) +
                    "," + str(swap_percent) + "," + str(disk_percent)
            )
            f.write(csv_msg + "\n")

    if (check_ok and not ok) or (not check_ok):
        send_message(msg)


if __name__ == "__main__":
    collect_and_send_stats(check_ok=True)

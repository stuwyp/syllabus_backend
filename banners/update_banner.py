# coding=utf-8
import os
import time
import json

NOTIFICATION_FILENAME = "banner.txt"
dirname = os.path.dirname(os.path.abspath(__file__))

NOTIFICATION_FILE_PATH = NOTIFICATION_FILENAME


def backup_previous():
    if os.path.exists(os.path.join(dirname, NOTIFICATION_FILE_PATH)):
        with open(os.path.join(dirname, NOTIFICATION_FILE_PATH), encoding='utf-8') as f:
            obj = json.load(f)
            with open(os.path.join(dirname, NOTIFICATION_FILE_PATH) + "_" + str(obj["timestamp"]) + ".txt", "w", encoding='utf-8') as o:
                json.dump(obj, o)
                print("backup finished!")
                return True
    return False

def new_notification():
    backup_previous()
    count = input("input pictures count(default 3): ")
    assert isinstance(count, str)
    if count.strip() == "":
        count = int(3)
    else:
        count = int(count)

    notifications = []

    for i in range(1, count + 1):
        print("info for ", i)
        url = input("picture url: ")
        link = input("link to go to: ")
        description = input("description: ")

        notification = {
            "id": i,
            "url": url,
            "link": link,
            "description": description
        }
        notifications.append(notification)

    timestamp = int(time.time())

    return {
        "notifications": notifications,
        "timestamp": timestamp
    }




if __name__ == "__main__":
    print(NOTIFICATION_FILE_PATH)
    obj =  new_notification()
    with open(os.path.join(dirname, NOTIFICATION_FILE_PATH), "w", encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False)
        print("生成成功!")



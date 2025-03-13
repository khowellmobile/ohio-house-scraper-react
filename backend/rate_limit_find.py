import requests  # type: ignore
import time
import math


def connect(url):
    response = requests.get(url)
    return checkResponse(response)


def checkResponse(response):
    if response.status_code:
        if response.status_code != 200:
            return response.status_code
        else:
            return 0
    else:
        return 0


def batch_loop_until_fail(url, batch_size):
    no429 = True
    runLoop = True
    req_count = 0
    sleep_timer = 0
    time_list = []
    batch_count = 0

    start_time = time.time()

    while runLoop:
        while no429:
            batch_index = 0
            while batch_index < batch_size:
                res_code = connect(url)

                req_count += 1
                batch_index += 1

                if res_code == 429:
                    end_time = time.time()
                    no429 = False
                    break

            batch_count = math.ceil(req_count / batch_size)

            time.sleep(sleep_timer)

        sleep_timer += 0.25
        elapsed_time = end_time - start_time
        no429 = True
        """ print(
            f"429 hit @ {elapsed_time}s, {req_count} reqs. Sleeping {sleep_timer}s. Batch maxed during {batch_count}th batch"
        ) """

        if batch_count > 4:
            print(f"Batch size {batch_size} stable @ {sleep_timer}s")
            runLoop = False
            return (batch_size, sleep_timer)
        else:
            time.sleep(10)


def loop_until_fail(url):
    no429 = True
    limitHit = False
    req_count = 0
    sleep_timer = 0
    time_list = []

    while not limitHit:
        start_time = time.time()

        while no429:
            res_code = connect(url)

            req_count += 1

            if req_count >= 500:
                limitHit = True
                break

            if res_code == 429:
                end_time = time.time()
                no429 = False
            time.sleep(sleep_timer)

        elapsed_time = end_time - start_time
        print(
            f"429 hit after {elapsed_time}s and {req_count} requests with sleeping {sleep_timer}s"
        )
        time_list.append([elapsed_time, req_count, sleep_timer])

        req_count = 0
        sleep_timer += 0.5
        no429 = True

        time.sleep(10)

    return time_list


def manual_test(url, batch_size, batch_delay):
    for batch in range(500):
        print(f"Running batch {batch + 1}...")

        for i in range(batch_size):
            res_code = connect(url)

            if res_code == 429:
                print("429 hit")
                return False

        time.sleep(batch_delay)

    print(f"batch size of {batch_size} with sleep of {batch_delay} is stable")
    return True


def main():
    url = "https://ohiohouse.gov/members/directory?start=1&sort=LastName"

    """ time_list = loop_until_fail(url)

    print(time_list) """

    """ data = []
    for i in range(1, 14):
        data.append(batch_loop_until_fail(url, i))

    print(data) """

    if manual_test(url, 1, 0.8):
        print("stable")
    else:
        print("Nope")


if __name__ == "__main__":
    main()

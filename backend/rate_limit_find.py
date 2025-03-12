import requests  # type: ignore
import time


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
    

    while req_count < batch_size:

        res_code = connect(url)

        if res_code == 429:
            




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
        print(f"429 hit after {elapsed_time}s and {req_count} requests with sleeping {sleep_timer}s")
        time_list.append([elapsed_time, req_count, sleep_timer])

        req_count = 0
        sleep_timer += 0.5
        no429 = True

        time.sleep(10)


    return time_list


def main():
    url = "https://ohiohouse.gov/members/directory?start=1&sort=LastName"

    time_list = loop_until_fail(url)

    print(time_list)


if __name__ == "__main__":
    main()

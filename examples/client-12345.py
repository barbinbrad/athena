import requests
import random

endpoint = 'http://127.0.0.1:8000/12345'

requestToExample = {
    "method": "example", # define in device @dispatch.add_method
    "jsonrpc": "2.0",
    "id": 0
}

requestToExampleWithParams = {
    "method":"exampleWithParams", # define in device @dispatch.add_method
    "params": {
        "sleep": 0,
    },
    "jsonrpc": "2.0",
    "id": 0
}

def test():
    for i in range(0,50):
        sleep = random.uniform(0.05, 2.5)
        requestToExampleWithParams["params"]["sleep"] = sleep
        r = requests.post(endpoint, json=requestToExampleWithParams)
        print(i, sleep,  r.json())

if __name__ == "__main__":
    test()
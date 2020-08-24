import redis
from rejson import Client, Path
import json


def learn_example():
    rj = Client(host='localhost', port=6379, decode_responses=True)
    rj.jsondel('frame0')

    # Set the key `obj` to some object
    lst = [None] * 5
    lst[0] = {"name":"fire","state":"True", "area":[0,0,0,0]}
    lst[1] = {"name":"climb","state":"False","area":[1,1,1,1]}
    lst[2] = {"name":"fight","state":"True", "area":[2,2,2,2]}
    lst[3] = {"name":"gun","state":"False","area":[3,3,3,3]}
    lst[4] = {"name":"jump","state":"True", "area":[4,4,4,4]}

    if rj.jsonget('frame0') is None:
        rj.jsonset('frame0', Path.rootPath(), {"test":"a"})
    for dic in lst:
        path_name = "." + dic["name"]
        rj.jsonset('frame0', Path(path_name), dic)

    # ret = rj.jsonget('frame0')
    # print(json.dumps(ret, indent=4))

    for dic in lst:
        path_name = "." + dic["name"]
        ret = rj.jsonget('frame0',Path(path_name))
        print(ret)

def learn_arr_example():
    rj = Client(host='localhost', port=6379, decode_responses=True)
    rj.jsondel('frame0')

    # Set the key `obj` to some object
    lst = [None] * 5
    lst[0] = {"area":[]}
    lst[1] = {"name":"climb","state":"False","area":[1,1,1,1]}
    lst[2] = {"name":"fight","state":"True", "area":[2,2,2,2]}
    lst[3] = {"name":"gun","state":"False","area":[3,3,3,3]}
    lst[4] = {"name":"jump","state":"True", "area":[4,4,4,4]}

    if rj.jsonget('frame0') is None:
        rj.jsonset('frame0', Path.rootPath(), {"test":[]})
    for dic in lst:
        path_name = ".test"
        rj.jsonarrappend('frame0', Path(path_name), dic)

    # ret = rj.jsonget('frame0')
    # print(json.dumps(ret, indent=4))

    ret = rj.jsonget('frame0')
    print(ret)


def test_multi():
    rj = Client(host='localhost', port=6379, decode_responses=True)
    for idx in range(110):
        if idx % 10 == 0:
            ret = rj.jsonget(idx)
            print(idx, end = ":")
            print(ret)
            rj.jsondel(idx)

if __name__ == "__main__":
    test_multi()


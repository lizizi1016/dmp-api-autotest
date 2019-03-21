# -*- coding:utf-8 -*-
import sys
import urllib
import urllib2
import json
import time
import re


class umcHander:

    def __init__(self, addr, port):
        self.addr = addr
        self.port = port

    @staticmethod
    def headers():
        return {
            "authorization":
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NTMyNDM2NTQsIm5iZiI6MTU1MzE1NzI1NCwic2VlZCI6ImdaQ0J4RFJxUm1DQzJpaG4iLCJ1c2VyIjoiYWRtaW4ifQ.qWvFGKF__XnusMw08LXffGStWBIXDSBmDZSaNArhWvk"
        }

    def full_url(self, short_url):
        return "http://{}:{}/{}".format(self.addr, self.port, short_url)

    def post(self, short_url, data):
        req = urllib2.Request(
            self.full_url(short_url),
            data=urllib.urlencode(data),
            headers=self.headers())
        res = urllib2.urlopen(req)
        return res.read()

    def get(self, short_url):
        req = urllib2.Request(self.full_url(short_url), headers=self.headers())
        res = urllib2.urlopen(req)
        return res.read()

    def post_wait_progress(self, short_url, data):
        try:
            res = self.post(short_url, data)
        except Exception as e:
            error_message = e.read()
            print ("[error]connect to umc failed:" + error_message)
            return
        j = json.loads(res)
        progress_url = "progress?id={}".format(j["progress_id"])
        step = 0
        print ("")
        print ("====================START====================")
        while True:
            try:
                res = self.get(progress_url)
            except Exception:
                time.sleep(5)
                continue
            progress_data = json.loads(res)
            done = progress_data.get("doneMsg", "").encode('utf-8')
            err = progress_data.get("err", "").encode('utf-8')
            if "Desc" in progress_data.keys():
                desc = progress_data.get("Desc", "").encode('utf-8')
            else:
                desc = progress_data.get("desc", "").encode('utf-8')
            # print total
            if step == 0:
                print (desc)
                step = step + 1
            # print steps
            steps = progress_data["steps"]
            current_step = progress_data.get("step", 0)
            while step <= current_step and current_step > 0:
                print (steps[step - 1].encode('utf-8'))
                step = step + 1
            if done:
                print (done)
                break
            if err:
                print (err)
                exit(1)
            time.sleep(1)
        print ("=====================END=====================")

    def run_from_json(self, data):
        self.post_wait_progress(data["url"], data["json"])


def replace_rpm_version(v, rpm_name):
    return re.sub("-\d{1,2}.\d{1,2}.\d{1,2}.\d{1,2}-", "-{}-".format(v),
                  rpm_name)


if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    umc_addr = sys.argv[1]
    umc_port = sys.argv[2]
    data_json_file = sys.argv[3]
    u = umcHander(umc_addr, umc_port)
    with open(data_json_file) as f:
        data_json = json.loads(f.read())
        if isinstance(data_json, list):
            for data in data_json:
                u.run_from_json(data)
        else:
            print ("data json is invalid")

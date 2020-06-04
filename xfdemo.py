# xfyun-demo

import requests

size10m = 10*1024*1024

base_url = "https://raasr.xfyun.cn/api"
prepare_url = "/prepare"
upload_url = "/upload"
merge_url = "/merge"
getprogress_url = "/getProgress"
getresult_url = "/getResult"

# logger
def stg_log(msg = "test log", level="info", filenanme = "./xfdemo.log", do_print = 1):
    """
    msg: info message to be printed
    level: info or warning or error
    """
    from datetime import datetime
    std_log_msg = f"xfdemo: {datetime.now().isoformat(timespec='seconds')}: [{level}]: {msg}"
    if (do_print):
        print(std_log_msg)
    std_log_msg += "\n"
    with open(filenanme, 'a') as fo:
        fo.write(std_log_msg)

class SliceIdGenerator:
    """slice id生成器"""
    def __init__(self):
        self.__ch = 'aaaaaaaaa`'

    def getNextSliceId(self):
        ch = self.__ch
        j = len(ch) - 1
        while j >= 0:
            cj = ch[j]
            if cj != 'z':
                ch = ch[:j] + chr(ord(cj) + 1) + ch[j+1:]
                break
            else:
                ch = ch[:j] + 'a' + ch[j+1:]
                j = j -1
        self.__ch = ch
        return self.__ch

class xfdemo(object):

    def __init__(self, audio_file_name):
        self.__file_name = audio_file_name
        self.__file_size = 0
        self.__slice_num = 1
        stg_log(f"xfdemo loaded")

    # load addid & secret key
    def loadConfig(self, configfile = "config.json"):
        import json
        with open(configfile) as fi:
            configobj = json.load(fi)
            self.__appid = configobj["appid"]
            self.__secret_key = configobj["secret_key"]
        stg_log(f"loadConfig: loaded")
        return 0

    # check the file and calculate slice amount
    def preCheck(self):
        import os
        self.__file_size = os.path.getsize(self.__file_name)
        self.__slice_num = int(self.__file_size/(size10m)) + 1
        stg_log(f"preCheck done file_name: {self.__file_name}, file_size: {str(self.__file_size)}, slice_num: {str(self.__slice_num)}")
        return 0

    # Generate timestamp and sign 
    def getTimeAndSign(self):
        from datetime import datetime
        import hashlib, hmac, base64
        now_time = datetime.now()
        now_stamp = int(now_time.timestamp())
        base_string = f"{self.__appid}{now_stamp}"

        hash_obj = hashlib.md5(base_string.encode('utf8'))
        hash_str = hash_obj.hexdigest()
        b_key = str.encode(self.__secret_key) # to bytes

        hmac_obj = hmac.new(b_key, hash_str.encode('utf8'), 'sha1')
        hmac_str = hmac_obj.digest()
        final_str = base64.b64encode(hmac_str).decode('utf8')
        return str(now_stamp), final_str

    # step 1: pre treat
    def reqPreTreat(self):
        stamp, sign = self.getTimeAndSign()
        headers = {"Content-Type": "application/x-www-form-urlencoded", "charset": "UTF-8"}
        req_data = {"app_id": self.__appid, "signa": sign, "ts": stamp, 
                    "file_len": str(self.__file_size), "file_name": self.__file_name, "slice_num": self.__slice_num}
        try:
            req = requests.post(base_url+prepare_url, data=req_data, headers=headers, timeout=10)
            res = req.json()
            # to be checked
            self.__task_id = res["data"]
        except TimeoutError as e:
            stg_log(f"reqPreTreat timeout error occured")
        finally:
            pass
        return 0

    # step 2: upload file in slices 
    def reqFileSlice(self):
        with open(self.__file_name, 'rb') as fi:
            slice_id_getter = SliceIdGenerator()
            for slice_index in range(0, self.__slice_num):
                current_slice_id = slice_id_getter.getNextSliceId()
                stamp, sign = self.getTimeAndSign()
                current_slice = fi.read(size10m)
                if not current_slice or (len(current_slice) == 0):
                    stg_log(f"reqFileSlice file ends")
                    break
                # headers not required
                # headers = {"Content-Type": "multipart/form-data"}
                headers = None
                req_data = {"app_id": self.__appid, "signa": sign, "ts": stamp,
                            "task_id": self.__task_id, "slice_id": current_slice_id }
                # be caution of the format!
                req_file = { "filename": None, "content": current_slice }
                try:
                    req = requests.post(base_url+upload_url, data=req_data, files=req_file, headers=headers, timeout=100)
                    res = req.json()
                except TimeoutError as e:
                    stg_log(f"reqFileSlice timeout error occured")
                finally:
                    pass
        return 0

    # step 3: finish the upload process
    def reqMergeFile(self):
        stamp, sign = self.getTimeAndSign()
        headers = {"Content-Type": "application/x-www-form-urlencoded", "charset": "UTF-8"}
        req_data = {"app_id": self.__appid, "signa": sign, "ts": stamp, "task_id": self.__task_id}
        try: 
            req = requests.post(base_url+merge_url, data=req_data, headers=headers, timeout=10)
            res = req.json()
        except TimeoutError as e:
            stg_log(f"reqMergeFile timeout error occured")
        finally:
            pass
        return 0

    # step 4: query for convert status
    def reqStatus(self):
        stamp, sign = self.getTimeAndSign()
        headers = {"Content-Type": "application/x-www-form-urlencoded", "charset": "UTF-8"}
        req_data = {"app_id": self.__appid, "signa": sign, "ts": stamp, "task_id": self.__task_id}
        try: 
            req = requests.post(base_url+getprogress_url, data=req_data, headers=headers, timeout=10)
            res = req.json()
            if res["data"]["status"] == 9:
                stg_log(f"reqStatus convert done")
                return 0
            elif res["data"]["status"] == 3:
                stg_log(f"reqStatus still converting")
                return 2
            # tbd...
            else:
                stg_log(f"reqStatus failed")
                return 3
        except TimeoutError as e:
            stg_log(f"reqStatus timeout error occured")
        finally:
            pass
        return 1

    # step 5: query for convert result
    def reqResult(self):
        stamp, sign = self.getTimeAndSign()
        headers = {"Content-Type": "application/x-www-form-urlencoded", "charset": "UTF-8"}
        req_data = {"app_id": self.__appid, "signa": sign, "ts": stamp, "task_id": self.__task_id}
        try: 
            req = requests.post(base_url+getresult_url, data=req_data, headers=headers, timeout=10)
            res = req.json()
            stg_log(f"getResult res {str(res)}")
            self.__result = res
        except TimeoutError as e:
            stg_log(f"reqResult timeout error occured")
        finally:
            pass
        return 0

    def getFinalResult(self):
        return self.__result

    def checkTempdir(self, dirname = 'temp_audioclip'):
        import os
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return 0

def main():
    import sys
    import time
    if (len(sys.argv) > 1):
        file_name = sys.argv[1] 
    else:
        file_name = "./0.mp3"
    myxf = xfdemo(file_name)
    myxf.loadConfig()
    myxf.preCheck()

    myxf.reqPreTreat()
    myxf.reqFileSlice()
    myxf.reqMergeFile()

    while 1:
        convert_status = myxf.reqStatus()
        if convert_status == 0:
            break
        time.sleep(60)

    myxf.reqResult()

    final_text = str(myxf.getFinalResult())
    stg_log(f"final result {final_text}")
    with open("out.txt", 'a') as fo:
        fo.write(final_text)


if __name__ == "__main__":
    main()

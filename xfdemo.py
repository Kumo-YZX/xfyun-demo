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

# generater timetag for lrc files, in [mm:ss.xx] format
def lrc_time_conveter(time_in_ms):
    time_in_s = int(time_in_ms/1000)
    return f"{(str(int(time_in_s/60))).zfill(2)}:{(str(time_in_s%60)).zfill(2)}.{(str(int((time_in_ms%1000)/10))).zfill(2)}"

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
        from pathlib import PurePath
        self.__file_path = audio_file_name
        pathobj = PurePath(self.__file_path)
        self.__file_name = pathobj.parts[-1]
        self.__file_size = 0
        self.__slice_num = 1
        self.__keywords = ""
        stg_log(f"xfdemo loaded with filename: {self.__file_name}")

    # load addid & secret key
    def loadConfig(self, configfile = "config.json"):
        import json
        with open(configfile) as fi:
            configobj = json.load(fi)
            self.__appid = configobj["appid"]
            self.__secret_key = configobj["secret_key"]
        stg_log(f"loadConfig: loaded")
        return 0

    def loadKeywords(self, keywordfile = "keywords.txt"):
        # load keywords from text file and convert into string 
        with open(keywordfile, encoding='utf8') as fi:
            keyword_str = fi.read()
        self.__keywords = keyword_str.replace('\n', ',')
        stg_log(f"keywords loaded: {str(self.__keywords)}, len: {str(len(self.__keywords))}")
        return 0

    # check the file and calculate slice amount
    def preCheck(self):
        import os
        self.__file_size = os.path.getsize(self.__file_path)
        self.__slice_num = int(self.__file_size/(size10m)) + 1
        stg_log(f"preCheck done file_name: {self.__file_path}, file_size: {str(self.__file_size)}, slice_num: {str(self.__slice_num)}")
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
                    "file_len": str(self.__file_size), "file_name": self.__file_path, "slice_num": self.__slice_num}
        # set keywords if avilable
        if len(self.__keywords) != 0:
            req_data["has_sensitive"] = 'true' 
            req_data["sensitive_type"] = '1'
            req_data["keywords"] = self.__keywords
        try:
            req = requests.post(base_url+prepare_url, data=req_data, headers=headers, timeout=10)
            res = req.json()
            # to be checked
            self.__task_id = res["data"]
        except TimeoutError as e:
            stg_log(f"step 1: reqPreTreat timeout error occured")
            stg_log(f"{str(e)}")
        finally:
            pass
        stg_log(f"step 1: pre treat done")
        return 0

    # step 2: upload file in slices 
    def reqFileSlice(self):
        with open(self.__file_path, 'rb') as fi:
            # get next slice id
            slice_id_getter = SliceIdGenerator()
            for slice_index in range(0, self.__slice_num):
                current_slice_id = slice_id_getter.getNextSliceId()
                stamp, sign = self.getTimeAndSign()
                # read file in 10m
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
                    stg_log(f"step 2: upload file done: {str(slice_index)}/{str(self.__slice_num-1)}")
                except TimeoutError as e:
                    stg_log(f"reqFileSlice timeout error occured")
                    stg_log(f"{str(e)}")
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
            stg_log(f"step 3: merge file done")
        except TimeoutError as e:
            stg_log(f"reqMergeFile timeout error occured")
            stg_log(f"{str(e)}")
        finally:
            pass
        return 0

    # step 4: query for convert status
    def reqStatus(self):
        import json
        stamp, sign = self.getTimeAndSign()
        headers = {"Content-Type": "application/x-www-form-urlencoded", "charset": "UTF-8"}
        req_data = {"app_id": self.__appid, "signa": sign, "ts": stamp, "task_id": self.__task_id}
        try: 
            req = requests.post(base_url+getprogress_url, data=req_data, headers=headers, timeout=10)
            res = req.json()
            # res.data is in string format..
            res_status = json.loads(res["data"])
            if res_status["status"] == 9:
                stg_log(f"step 4: reqStatus convert done")
                return 0
            elif res_status["status"] == 3:
                stg_log(f"reqStatus still converting")
                return 2
            # tbd...
            else:
                stg_log(f"reqStatus failed")
                return 3
        except TimeoutError as e:
            stg_log(f"reqStatus timeout error occured")
            stg_log(f"{str(e)}")
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
            stg_log(f"step 5: getResult res done")
            self.__result = res["data"]
        except TimeoutError as e:
            stg_log(f"reqResult timeout error occured")
            stg_log(f"{str(e)}")
        finally:
            pass
        return 0

    def getFinalResult(self):
        return self.__result

    # export content to json
    def writeFinalResultTemp(self):
        with open(f"./export/{self.__file_name}.json", 'a') as fo:
            fo.write(self.__result)
        return 0

    # export content to txt
    def writeFinalResultText(self):
        import json
        with open(f"./export/{self.__file_name}.json", 'r') as fi:
            text_json = json.load(fi)
        
        with open(f"./export/{self.__file_name}.txt", "a") as fo:
            # audio_result and keyword matchs is listed individually in keyword-porvided mode
            # same as below
            if "audio_result" in text_json:
                sentence_list = json.loads(text_json["audio_result"])
            else:
                sentence_list = text_json
            for every_sentence in sentence_list:
                es_gbk = every_sentence["onebest"]
                fo.write(f"{es_gbk}\n")
        stg_log(f"write to text file done")
        return 0

    # export content to lrc file with timetags 
    def writeFinalResultLrc(self):
        import json
        with open(f"./export/{self.__file_name}.json", 'r') as fi:
            text_json = json.load(fi)
        
        with open(f"./export/{self.__file_name}.lrc", "a") as fo:
            if "audio_result" in text_json:
                sentence_list = json.loads(text_json["audio_result"])
            else:
                sentence_list = text_json
            for every_sentence in sentence_list:
                es_gbk = every_sentence["onebest"]
                es_timetag = lrc_time_conveter(int(every_sentence["bg"]))
                fo.write(f"[{es_timetag}]{es_gbk}\n")
        stg_log(f"write to lrc file done")
        return 0

    # create dir if not exist
    def checkTempdir(self, dirname):
        import os
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return 0

def loadArgs():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f',
        '--filename',
        # default='0.flac',
        required=True,
        type=str,
        help="File to be converted"
    )
    parser.add_argument(
        '-u',
        '--usekeyword',
        default='n',
        type=str,
        help="Do you want to use keywords? n:No, y:Yes"
    )
    return parser

def main():
    import sys
    import time
    args = loadArgs().parse_args()

    myxf = xfdemo(args.filename)
    # myxf.checkTempdir("temp_audioclip")
    myxf.checkTempdir("export")
    myxf.loadConfig()

    # addition space added to args in few times
    if args.usekeyword.find('y') >= 0:
        # ! load keywords
        myxf.loadKeywords()
        stg_log(f"use keyword")

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
    myxf.writeFinalResultTemp()

    myxf.writeFinalResultText()
    myxf.writeFinalResultLrc()
    # stg_log(f"final result {final_text}")

if __name__ == "__main__":
    main()

# xfyun-demo

import requests

class xfdemo(object):

    def __init__(self, audio_file_name):
        self._info = "zero"
        # absolute path
        self._file_name = audio_file_name
        file_split = self._file_name.split('.')
        self._audio_prefix = file_split[0]
        self._audio_subfix = file_split[-1]
        self._config = {}
        self._file_size = 0
        self._slice_num = 1

    def loadConfig(self, configfile = "config.json"):
        import json
        with open(configfile) as fi:
            self._config = json.load(fi)
        return 0

    def checkTempdir(self, dirname = 'temp_audioclip'):
        import os
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return 0

    def audioPreTreat(self, do_cut = 1):
        import os
        # How many parts the file need to be devided into? 
        self._file_size = os.path.getsize(self._file_name)
        if do_cut == 0:
            return 1

        self._slice_num = int(self._file_size/(10*1024*1024)) + 1

        from pydub import AudioSegment
        from pydub.utils import mediainfo
        self._bitrate = mediainfo(self._file_name)['bit_rate']
        audio_obj = AudioSegment.from_mp3(self._file_name)
        # sec to milisec
        audio_time_length = audio_obj.duration_seconds*1000
        # audio_clip = []
        for clip_index in range(0, self._slice_num):
            print(int(audio_time_length*((clip_index)/self._slice_num)))
            print(int(audio_time_length*((clip_index+1)/self._slice_num)))
            print('-')
            current_clip = audio_obj[int(audio_time_length*((clip_index)/self._slice_num)): int(audio_time_length*((clip_index+1)/self._slice_num))]
            self.checkTempdir()
            current_clip.export(f"./temp_audioclip/{self._audio_prefix}.{str(clip_index)}.{self._audio_subfix}", format=self._audio_subfix, bitrate=self._bitrate)
        return 0

def main():
    import sys
    if (len(sys.argv) > 1):
        file_name = sys.argv[1] 
    else:
        file_name = "111.mp3"
    myxf = xfdemo(file_name)
    myxf.audioPreTreat()

if __name__ == "__main__":
    main()

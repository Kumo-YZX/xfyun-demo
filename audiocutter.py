# cut videos and convet

# import requests

size10m = 10*1024*1024

class xfdemo(object):

    def __init__(self, audio_file_name):
        self.__info = "zero"
        self.__file_name = audio_file_name
        file_split = self.__file_name.split('.')
        self.__audio_prefix = file_split[0]
        self.__audio_subfix = file_split[-1]
        self.__export_subfix = "flac"
        self.__config = {}
        self.__file_size = 0
        self.__slice_num = 1

    # def loadConfig(self, configfile = "config.json"):
    #     import json
    #     with open(configfile) as fi:
    #         self.__config = json.load(fi)
    #     return 0

    def checkTempdir(self, dirname = 'temp_audioclip'):
        import os
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return 0

    def audioPreTreat(self, do_cut = 1):
        import os
        # How many parts the file need to be devided into? 
        self.__file_size = os.path.getsize(self.__file_name)
        if do_cut == 0:
            return 1

        self.__slice_num = int(self.__file_size/(size10m)) + 1

        from pydub import AudioSegment
        from pydub.utils import mediainfo
        self.__bitrate = mediainfo(self.__file_name)['bit_rate']
        audio_obj = AudioSegment.from_file(self.__file_name, self.__audio_subfix)
        # sec to milisec
        audio_time_length = audio_obj.duration_seconds*1000
        # audio_clip = []
        for clip_index in range(0, self.__slice_num):
            print(int(audio_time_length*((clip_index)/self.__slice_num)))
            print(int(audio_time_length*((clip_index+1)/self.__slice_num)))
            print('-')
            current_clip = audio_obj[int(audio_time_length*((clip_index)/self.__slice_num)): int(audio_time_length*((clip_index+1)/self.__slice_num))]
            self.checkTempdir()
            self.checkTempdir("export")
            current_clip.export(f"./export/{self.__audio_prefix}.{str(clip_index)}.{self.__export_subfix}", format=self.__export_subfix, bitrate=self.__bitrate)
        return 0

def main():
    import sys
    if (len(sys.argv) > 1):
        file_name = sys.argv[1] 
    else:
        file_name = "example.m4a"
    myxf = xfdemo(file_name)
    myxf.audioPreTreat()

if __name__ == "__main__":
    main()
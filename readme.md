# xfyun audio to text api demo

[cn version](https://github.com/Kumo-YZX/xfyun-demo/blob/master/readme-cn.md)

## How to use

### Step 1: Download the code and install requirements

we recommand to use virtualenv

```
me@host:~$ git clone https://github.com/Kumo-YZX/xfyun-demo.git
me@host:~$ pip install -r requirements.txt
```
### Step 2: Prepare for config.json

should be placed under main dir

content like this
```
{
    "appid": "your appid",
    "secret_key": "your key"
}
``` 

### Step 3: Prepare for keyword list (Only required in keyword model)

should be placed under main dir and be named with keywords.txt

only one word for each line
```
keyword1
keyword2
...
```

### Step 4: Prepare for your audio file

mp3 & m4a & wmv & flac format are supported.

After finishing step 2 and 3, your dir will be like this:
```
xfyun-demo
├───xfdemo.py
├───audiocutter.py
├───requirements.txt
├───readme.txt
├───readme-cn.txt
├───+example.m4a
├───+keywords.txt
└───+config.json
```

### Step 5: Run it! You can pass the audio name as arguments

Args: 
- -f: required, file to be converted, both realtive path and absolute path are supported
- -u: optional, use keyword list or not, y:Yes, n:No, default: No
- -s: optional, time offset in ms, starttime of this clip, used to correct lrc timetags. default: 0
- -l: language of this audio. In [ISO 639-1](https://www.loc.gov/standards/iso639-2/php/English_list.php) language code. Chinese(zh) and English(en) have already been supported now. default: zh

like this:
```
me@host:~$ python xfdemo.py -f example.m4a
me@host:~$ python xfdemo.py -f example.m4a -l zh
me@host:~$ python xfdemo.py -f /home/me/Audio/example.mp3
me@host:~$ python xfdemo.py -f example.flac -u y
me@host:~$ python xfdemo.py -f example.m4a -u y -s 100000 -l en
```

### Step 6: Check for your results

export dir will be created under the main dir, containing files below:

- example.m4a.json: Raw data returned by API
- example.m4a.txt: text generated
- example.m4a.lrc: text with timetags

## Develop guide

### Structure

tbd...
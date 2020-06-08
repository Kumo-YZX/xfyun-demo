# xfyun audio to text api demo

[cn version](https://github.com/Kumo-YZX/xfyun-demo/blob/master/readme-cn.md)

## How to use

### Step 1: Download the code and install requirements

```
me@host:~$ git clone https://github.com/Kumo-YZX/xfyun-demo.git
me@host:~$ pip install -r requirements.txt
```
### Step 2: Prepare config.json

should be placed behind xfdemo.py

content like this
```
{
    "appid": "your appid",
    "secret_key": "your key"
}
``` 

### Step 3: Prepare keyword list (Only required in keyword model)

should be placed behind xfdemo.py

only one words for each line
```
keyword1
keyword2
...
```

### Step 4: Prepare your audio file

mp3 and flac format have already been tested.

After finishing step 2 and 3, your dir will be like this:
```
xfyun-demo
├───xfdemo.py
├───requirements.txt
├───audio.mp3
├───keywords.txt
└───config.json
```

### Step 5: Run it! You can pass the audio name as arguments

Args: -f: required, file to be converted,
      -u: optional, use keyword list or not, y:Yes, n:No, default: No
```
me@host:~$ python xfdemo.py -f audio.mp3 -u y
```
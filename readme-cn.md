# 讯飞云语音转文字API使用演示

## 如何使用

请使用python3！

### 第一步：下载代码并安装依赖库

当然使用virtualenv安装requirement会更好

```
me@host:~$ git clone https://github.com/Kumo-YZX/xfyun-demo.git
me@host:~$ pip install -r requirements.txt
```

### 第二步：准备config.json文件

在目录里面已经包含有一个config_example.json文件，可以进行参考：

```
me@host:~$ cp config_example.json config.json
me@host:~$ nano config.json
```

文件大概长这样，是一个json格式的文本：

```
{
    "appid": "your appid",
    "secret_key": "your key"
}
```

### 第三步：准备关键词表（如果你需要使用的话）

**注意**：我们使用的体验表明，对比于使用讯飞云平台网站内的自定义关键词表，这样添加关键词事实上效果并不好。

在讯飞网站内添加自定义关键词表，详见其网站。

这个关键词表需要被命名为keywords.txt，同时与xfdemo.py放在同一个目录下。

一行只能放置一个词汇，可以使用英文/中文/数字的组合，不能使用特殊字符，例如横杠/斜杠/空格等。

格式如下：

```
keyword1
keyword2
关键词3
关键词4
...

```

### 第四步：准备你的音频文件

可以是mp3、m4a、flac、wmv格式。对于路径没有要求。

如果你把这个文件和xfdemo.py放在同一个目录下，最后目录会变成以下这样，其中带+标注的是我们添加的。

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

### 第五步: 运行它！所需要被上传的文件名字在参数中给出

参数有：

- -f：必须，被处理的**文件**路径。可以是相对路径也可以是绝对路径。
- -u：可选，是否**使用**本地配置的关键词表。y：是，n：否。默认为否。
- -s：可选，音频的**起始**位置偏移，单位为毫秒。只被用于在音频被拆分成多段处理时，确定其输出LRC文件时的起始时间。默认为0。

举例：
```
me@host:~$ python xfdemo.py -f example.m4a
me@host:~$ python xfdemo.py -f /home/me/Audio/example.mp3
me@host:~$ python xfdemo.py -f example.flac -u y
me@host:~$ python xfdemo.py -f example.m4a -u y -s 100000
```

### 第六步：查看结果

在主目录下会多出一个export目录，里面包含了如下文件：

- example.m4a.json：API返回的原始数据
- example.m4a.txt：提取出来的所有文字
- example.m4a.lrc：标注了时间戳的文字

备注：若出现打开乱码的情况，请尝试以GB2312/UTF8文本编码重新打开

## 开发指南

### 整体结构
主要包括xfdemo的class主体、处理log和lrc时间戳的函数、处理argv参数的函数、引用自讯飞的slice id生成器class等。

xfdemo的class主体包括预加载config和keywords、预检查、检查输出目录、5个步骤的请求、写json/txt/lrc文件几个函数。

欢迎pr。
tbd...

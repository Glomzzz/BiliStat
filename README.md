# BiliFollowers

## 项目介绍

BiliFollowers 是一个基于 B 站 API 的关注者查询工具，可以查询某个 B 站用户的关注者列表。

都是 GPT-4 写的。

## 使用方法

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 配置

在 `config.py` 中填入你的 B 站 Cookie，与 User-Agent.
在 `main.py` 中填入你要查询的用户的 UID。

3. 运行

```bash
python main.py
```

（目前只是个小toy，我没有严肃写，准备用Rust重构一套。）
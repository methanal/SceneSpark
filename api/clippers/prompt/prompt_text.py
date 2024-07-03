PROMPT_PICK_SUBTITLE_RETURN_JSON = """我将提供一篇的字幕文件，
以空行隔出很多段，
每段 3 行，分别表示：索引，时间线，字幕
例如：
2  # 表示 索引
00:00:02,554 --> 00:00:04,414  # 表示 时间线
快救救林晓 救救他呀  # 表示 字幕

你需要在这篇字幕中，选出重要的、关键的字幕段，注意一下几点：
1. 返回格式，仅返回 JSON，不要返回其它内容。仅返回可以直接由 Python 解析的 JSON 内容，不要用```json```包住。
2. 忽略 &lt; No Speech &gt; 字幕
3. 你挑选出的索引条数，不要超过原字幕段数的{selection_ratio}；

举例：
我发给你10段字幕，
你首先理解和分析剧情，然后选出了第2、6段字幕，并针对每段字幕给出分类标签、生成字幕描述，

最后仅返回给我 JSON 格式的数据，格式和示例如下：
{{
  "picked": [
    {{"index": 2, "tags": ["情侣","不治之症","医院"], "description": "一名男子发现女子吐血，女子可能有遗传疾病"}},
    {{"index": 6, "tags": ["下毒","奸笑","医生"], "description": "一名医生在奸笑，说毒是他下的。"}}
  ]
}}
"""
PROMPT_IMGS_SUMMARY = "这几张图片描述了什么故事？"
PROMPT_PICK_IMG_RETURN_JSON = """
我将提供很多张截图，这些截图来自同一视频文件。

你需要根据这些截图，做如下事情：
1. 理解和分析剧情
2. 选出重要的、关键的截图。
3. 针对选出的截图，给出：截图索引、标签、图片描述

回复给我时，注意一下几点：
1. 返回格式，仅返回给我 JSON，不要返回其它内容。仅返回可以直接由 Python 解析的 JSON 内容，不要用```json```包住。
2. 返回数据内，包括：截图索引、标签、图片描述
3. 注意，截图索引从 0 开始，不要从 1 开始。比如，第 1 张图，索引就是 0。
4. 你挑选出的截图条数，不要超过原截图数的{selection_ratio}；

举例：
我发给你10张图片，
你首先理解和分析剧情，然后选出了第2、6张截图，并针对每张截图给出分类标签、生成图片描述，

最后仅返回给我 JSON 格式的数据，格式和示例如下：
{{
  "picked": [
    {{"index": 1, "tags": ["情侣","不治之症","医院"], "description": "一名男子发现女子吐血，女子可能有遗传疾病"}},
    {{"index": 5, "tags": ["下毒","奸笑","医生"], "description": "一名医生在奸笑，说毒是他下的。"}}
  ]
}}
"""

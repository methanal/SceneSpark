# flake8: noqa

# PROMPT_PICK_SUBTITLE_RETURN_JSON = """我将提供一篇的字幕文件，
# 以空行隔出很多段，
# 每段 3 行，分别表示：索引，时间线，字幕
# 例如：
# 2  # 表示 索引
# 00:00:02,554 --> 00:00:04,414  # 表示 时间线
# 快救救林晓 救救他呀  # 表示 字幕
#
# 你需要在这篇字幕中，选出重要的、关键的字幕段，注意一下几点：
# 1. 返回格式，仅返回 JSON，不要返回其它内容。仅返回可以直接由 Python 解析的 JSON 内容，不要用```json```包住。
# 2. 忽略 &lt; No Speech &gt; 字幕
# 3. 你挑选出的索引条数，不要超过原字幕段数的{selection_ratio}；
#
# 举例：
# 我发给你10段字幕，
# 你首先理解和分析剧情，然后选出了第2、6段字幕，并针对每段字幕给出分类标签、生成字幕描述，
#
# 最后仅返回给我 JSON 格式的数据，格式和示例如下：
# {{
#   "picked": [
#     {{"index": 2, "tags": ["情侣","不治之症","医院"], "description": "一名男子发现女子吐血，女子可能有遗传疾病"}},
#     {{"index": 6, "tags": ["下毒","奸笑","医生"], "description": "一名医生在奸笑，说毒是他下的。"}}
#   ]
# }}
# """
PROMPT_IMGS_SUMMARY = "这几张图片描述了什么故事？"
# PROMPT_PICK_IMG_RETURN_JSON = """我将提供很多张截图，这些截图来自同一视频文件。
#
# 你需要根据这些截图，做如下事情：
# 1. 理解和分析剧情
# 2. 选出重要的、关键的截图。
# 3. 针对选出的截图，给出：截图索引、标签、图片描述
#
# 回复给我时，注意一下几点：
# 1. 返回格式，仅返回给我 JSON，不要返回其它内容。仅返回可以直接由 Python 解析的 JSON 内容，不要用```json```包住。
# 2. 返回数据内，包括：截图索引、标签、图片描述
# 3. 注意，截图索引从 0 开始，不要从 1 开始。比如，第 1 张图，索引就是 0。
# 4. 你挑选出的截图条数，不要超过原截图数的{selection_ratio}；
#
# 举例：
# 我发给你10张图片，
# 你首先理解和分析剧情，然后选出了第2、6张截图，并针对每张截图给出分类标签、生成图片描述，
#
# 最后仅返回给我 JSON 格式的数据，格式和示例如下：
# {{
#   "picked": [
#     {{"index": 1, "tags": ["情侣","不治之症","医院"], "description": "一名男子发现女子吐血，女子可能有遗传疾病"}},
#     {{"index": 5, "tags": ["下毒","奸笑","医生"], "description": "一名医生在奸笑，说毒是他下的。"}}
#   ]
# }}
# """
PROMPT_WHISPER = ""

PROMPT_PICK_SUBTITLE_RETURN_JSON = """我将提供一篇的字幕文件，
以空行隔出很多段，
每段 3 行，分别表示：索引，时间线，字幕
例如：
2  # 表示 索引
00:00:02,554 --> 00:00:04,414  # 表示 时间线
快救救林晓 救救他呀  # 表示 字幕

你需要在这篇字幕中，选出重要的、关键的字幕段，注意一下几点：
1. 返回格式，仅返回 JSON，不要返回其它内容。仅返回可以直接由 Python 解析的 JSON 内容，不要用```json```包住。
2. 忽略 &lt; No Speech &gt; 字幕；
3. 你挑选出的索引条数，不要超过原字幕段数的{selection_ratio}；
4. 挑选出来的字幕段，符合体现剧情关键度，体现剧情转折点，有剧情冲突度体现；

举例：
我发给你10段字幕，
首先理解和分析剧情，按照字幕段剧情关键度，体现剧情转折点，有剧情冲突度体现来筛选出关键字幕段。
譬如说选出了第2、5段字幕，并针对每段字幕给出分类标签，内容关键度评级打分（1-5分），内容冲突打分（1-5分）、剧情转折打分（1-5分），生成字幕描述，

最后仅返回给我 JSON 格式的数据，格式和示例如下：
{{
  "picked": [
    {{"index": 2, "tags": ["情侣","不治之症","医院"], "rating":4, "confliction": 3,"changing": 4, "description": "一名男子发现女子吐血，女子可能有遗传疾病"}},
    {{"index": 5, "tags": ["下毒","奸笑","医生"], "rating":5, "confliction": 2,"changing": 2,  "description": "一名医生在奸笑，说毒是他下的。"}}
  ]
}}
"""

PROMPT_PICK_IMG_RETURN_JSON = """我将提供很多张短剧的截图，这些截图来自同一视频文件。

你需要根据这些截图，做如下事情：
1. 通过截图里的字幕，还有截图里的动作，人物表情等内容，理解和分析剧情
2. 按照剧情重要度，关键剧情转折点，关键动作/人物特征表情，冲突程度等重要信息，选出重要的、关键的截图。
3. 针对选出的截图，给出：截图索引、标签、图片描述

回复给我时，注意一下几点：
1. 返回格式，仅返回给我 JSON，不要返回其它内容。仅返回可以直接由 Python 解析的 JSON 内容，不要用```json```包住。
2. 返回数据内，包括：截图索引、标签、图片描述
3. 注意，截图索引从 0 开始，不要从 1 开始。比如，第 1 张图，索引就是 0。
4. 你挑选出的截图条数，不要超过原截图数的{selection_ratio}；

举例：
我发给你10张图片，
你首先理解和分析剧情，按照字幕段的剧情关键度，剧情转折度，关键动作/表情，冲突程度来筛选出关键字幕段。
譬如说选出了第2、6段字幕，并针对每张截图给出分类标签tag，内容关键度评级（rating）打分（1-5分），截图关键动作/表情描述（movement），内容冲突（confliction）打分（1-5分）、剧情转折（changing）打分（1-5分），生成图片描述，并把画面字幕信息放入subtitle里

最后仅返回给我 JSON 格式的数据，格式和示例如下：
{{
  "picked": [
    {{"index": 2, "tags": ["情侣","不治之症","医院"], "rating":4, "movement": ["阴笑","打耳光"],"confliction": 3,"changing": 4, "description": "一名男子发现女子吐血，女子可能有遗传疾病","subtitle": "我家里有遗传病，没有办法治"}},
    {{"index": 6, "tags": ["下毒","奸笑","医生"], "rating":5, "movement": ["得意大笑","鼓掌"],"confliction": 2,"changing": 2,  "description": "一名医生在奸笑，说毒是他下的。","subtitle": "看来软骨散奇效了，你这次完蛋了！"}}
  ]
}}
"""

import json
import os

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")

def load_settings():
    default = {
      "font_size": 20,
      "scroll_speed":2,
      "background":"",
      "title":"初三11班 - 回家作业",
      "key_words":{
        "tasks":["练习册","课本","试卷","练习纸","作业本","课时"],
        "child_tasks":["写完","完成","抄写","默写","背诵","签字"]
      },
      "block_row":3,
      "subjects":["语文","数学","英语","历史","政治","物理","化学","生物","地理"],
      "tags":["重要","放学交","背诵","笔头","优先"]
}
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # 保证所有键都存在
            for key in default:
                if key not in data:
                    data[key] = default[key]
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        # 修补
        save_settings(default)
        return default

def save_settings(settings_dict):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings_dict, f, ensure_ascii=False, indent=2)

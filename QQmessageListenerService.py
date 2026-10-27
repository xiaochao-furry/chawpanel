from wintoastlistener import ToastListener
import os

user_profile = os.environ['USERPROFILE']
db_path_ = os.path.join(
    user_profile, 'AppData', 'Local', 'Microsoft',
    'Windows', 'Notifications', 'wpndatabase.db'
)


def parse_launch_params(launch_str):
    """解析 @launch 中的参数（按分号分割）"""
    params = {}
    if not launch_str:
        return params
    if '?' in launch_str:
        query = launch_str.split('?', 1)[1]
        for part in query.split(';'):
            if '=' in part:
                key, val = part.split('=', 1)
                params[key] = val
    return params


def get_text(texts, idx, default="无"):
    """安全地从 texts 列表中提取文本"""
    if idx >= len(texts):
        return default
    item = texts[idx]
    if isinstance(item, dict):
        return item.get('#text', default)
    return str(item) if item else default


def callback(event_data, resources):
    launch_str = ''  # 提前初始化，避免未赋值错误

    try:
        # 防止 resources 为 None
        resources = resources or {}

        # 没用的撇了
        visual = resources.get('visual', {}) or {}
        binding = visual.get('binding', {}) or {}
        texts = binding.get('text', []) or []

        # 标题（发送者）
        title = get_text(texts, 0, "无")
        # 内容
        content = get_text(texts, 1, "无")

        # @launch里的东西
        launch_str = resources.get('@launch', '') or ''
        params = parse_launch_params(launch_str)

        chat_type = params.get('chatType', '0')
        peer_id = params.get('peerUid', '未知')



        if "ntqq-notification" not in launch_str:
            return

        # 判断类型
        if chat_type == '2':
            target_type = "群聊"

        elif chat_type == '1':
            target_type = "好友"

        else:
            target_type = "未知"
        target_info = peer_id

        # 输出
        print("\n" + "——" * 60)
        print(f"群名/好友名: {title}")
        print(f"消息内容: {content}")
        print(f"源自用户/群聊：{target_type} 用户qq号/群号：{target_info}")

        print("——" * 60 + "\n")


        return {
            "title": title,
            "content": content,
            "target_type": target_type,
            "target_info": target_info,

        }

    except Exception as e:
        print(f"解析通知出错: {e}")
        print("launch_str:", repr(launch_str))
        print("resources:", resources)


# 启动监听
listener = ToastListener(callback=callback, wpndatabase_path=db_path_)
print("🟢 开始监听qq通知，按 Ctrl+C 退出...")
listener.listen()
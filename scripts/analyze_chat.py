import json
import argparse
import datetime
import re
import random
import os
import sys
from collections import Counter, defaultdict

# Try to import jieba, fallback if not available
try:
    import jieba
    import jieba.analyse
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    print("Warning: 'jieba' module not found. Word cloud will use simple whitespace splitting.")

def parse_arguments():
    parser = argparse.ArgumentParser(description='Analyze WeChat chat records.')
    parser.add_argument('input_file', help='Path to the input JSON file')
    parser.add_argument('--output-stats', default='stats.json', help='Path to output statistics JSON')
    parser.add_argument('--output-text', default='simplified_chat.txt', help='Path to output simplified text for AI')
    return parser.parse_args()

def load_chat_records(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def format_timestamp(ts):
    dt = datetime.datetime.fromtimestamp(ts)
    return dt.strftime('%Y-%m-%d %H:%M:%S'), dt

def get_message_hour(ts):
    return datetime.datetime.fromtimestamp(ts).hour

def get_display_name(msg):
    """获取用户显示名称，优先使用 groupNickname，否则使用 accountName"""
    return msg.get('groupNickname') or msg.get('accountName') or 'Unknown'


def is_night_time(hour):
    # 23:00 - 06:00
    return hour >= 23 or hour < 6

def generate_word_cloud_data(text_messages, top_n=60):
    words = []
    stopwords = set(['的', '了', '我', '是', '你', '在', '他', '我们', '好', '去', '都', '就', '那', '有', '这', '也', '要', '吗', '啊', '吧', '呢', '哈', '哈哈', '哈哈哈', '图片', '表情', '动画表情'])
    
    combined_text = " ".join([m['content'] for m in text_messages])
    
    if JIEBA_AVAILABLE:
        # Use simple tag extraction or cut
        seg_list = jieba.cut(combined_text)
        for word in seg_list:
            if len(word) > 1 and word not in stopwords:
                words.append(word)
    else:
        # Fallback: simple split by non-alphanumeric (for English/mixed) or just char by char for Chinese? 
        # Simple whitespace/punctuation split is not good for Chinese. 
        # Using regex to find 2+ char words if possible, or just skip if no jieba.
        # For this script's robustness, let's assume if no jieba, we stick to basic heuristic
        pass

    word_counts = Counter(words)
    common_words = word_counts.most_common(top_n)
    
    cloud_data = []
    # Simple layout simulation
    # In a real scenario, this implementation would need a complex packing algorithm.
    # Here we randomize positions within a safe area (container is ~800px wide, cloud area ~320px height)
    # We will generate relative positions (%) to keep it responsive-ish
    
    colors = ["#07C160", "#576B95", "#FA5151", "#FFD200", "#333333", "#888888", "#1AAD19", "#2782D7"]
    
    for word, count in common_words:
        size = min(40, max(12, 10 + (count / common_words[0][1]) * 30)) if common_words else 12
        item = {
            "text": word,
            "count": count,
            "size": int(size),
            "color": random.choice(colors),
            "left": random.randint(5, 85), # Percentage
            "top": random.randint(10, 280), # Pixels (height is 320)
            "rotate": random.randint(-20, 20),
            "weight": "bold" if count > common_words[0][1] * 0.5 else "normal"
        }
        cloud_data.append(item)
        
    return cloud_data

def analyze(args):
    data = load_chat_records(args.input_file)
    messages = data.get('messages', [])
    members = {m['platformId']: m['accountName'] for m in data.get('members', [])}
    
    # Basic Stats
    total_messages = len(messages)
    
    # Filter text messages (type 0: 纯文本, type 2: 语音转文字)
    text_messages = [m for m in messages if m['type'] in (0, 2)]
    
    # Active Users (优先使用 groupNickname)
    active_users = set(get_display_name(m) for m in messages)
    
    # Time Range
    timestamps = [m['timestamp'] for m in messages]
    if timestamps:
        start_time, start_dt = format_timestamp(min(timestamps))
        end_time, end_dt = format_timestamp(max(timestamps))
        date_str = start_dt.strftime('%Y-%m-%d')
    else:
        start_time = end_time = "N/A"
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')

    # --- Talkative List (Top 3) ---
    user_msg_counts = Counter(get_display_name(m) for m in messages)
    top_talkers_tuple = user_msg_counts.most_common(3)
    
    top_talkers = []
    top_talker_names = set()
    for rank, (name, count) in enumerate(top_talkers_tuple, 1):
        top_talkers.append({
            "rank": rank,
            "name": name,
            "count": count
        })
        top_talker_names.add(name)

    # 统计每个话唠的常用词
    talker_all_text = defaultdict(list)
    for m in text_messages:
        name = get_display_name(m)
        if name in top_talker_names:
            talker_all_text[name].append(m['content'])
    
    stopwords = set(['的', '了', '我', '是', '你', '在', '他', '我们', '好', '去', '都', '就', '那', '有', '这', '也', '要', '吗', '啊', '吧', '呢', '哈', '哈哈', '哈哈哈', '图片', '表情', '动画表情', '一个', '这个', '那个', '什么', '怎么', '可以', '就是', '不是', '没有', '还有', '但是', '现在', '知道', '真的', '感觉', '觉得', '可能', '应该', '已经', '还是', '一下'])
    
    for talker in top_talkers:
        name = talker["name"]
        common_words = []
        if JIEBA_AVAILABLE and name in talker_all_text:
            combined = " ".join(talker_all_text[name])
            words = [w for w in jieba.cut(combined) if len(w) > 1 and w not in stopwords]
            word_counts = Counter(words)
            common_words = [w for w, _ in word_counts.most_common(5)]
        talker["common_words"] = common_words

    # --- Night Owl Champion ---
    # 23:00 - 06:00, Find the user who spoke latest (closest to 06:00 from the left or right?)
    # Usually "Night Owl" means staying up late. So we look for messages in 23:00-05:59.
    # The "Champion" is the one who spoke latest in that window (e.g. at 04:30 is later than 01:00).
    candidates = []
    
    for m in messages:
        ts = m['timestamp']
        dt = datetime.datetime.fromtimestamp(ts)
        h = dt.hour
        if is_night_time(h):
            # Calculate "lateness"
            # 23:00 -> 0, 00:00 -> 60, ... 05:59 -> highest
            minutes_from_23 = (h - 23 if h >= 23 else h + 1) * 60 + dt.minute
            candidates.append({
                "name": get_display_name(m),
                "time": dt.strftime('%H:%M'),
                "lateness": minutes_from_23,
                "content": m.get('content', ''),
                "raw_ts": ts
            })

    night_owl = None
    if candidates:
        # Sort by lateness descending
        candidates.sort(key=lambda x: x['lateness'], reverse=True)
        champion = candidates[0]
        
        # Count late night messages for this user
        champ_name = champion['name']
        count = sum(1 for c in candidates if c['name'] == champ_name)
        
        night_owl = {
            "name": champ_name,
            "last_time": champion['time'],
            "msg_count": count,
            "last_msg": champion['content'] if champion['content'] else "[非文本消息]",
            "title": "深夜守门员" if champion['lateness'] > 300 else "修仙党"
        }

    # --- Word Cloud ---
    word_cloud_data = generate_word_cloud_data(text_messages)

    # --- Simplified Text Generation for AI ---
    # Strategies:
    # 1. Uniform handling if total text messages <= 500: Keep all
    # 2. If > 500: Apply filters
    
    kept_indices = set()
    total_text_count = len(text_messages)
    
    # 保留全部消息（测试模式）
    kept_indices = set(range(len(text_messages)))

    simplified_lines = []
    
    # Sort indices
    sorted_indices = sorted(list(kept_indices))
    
    summary_header = f"=== 群名称: {data['meta'].get('name', 'Unknown')} ===\n"
    summary_header += f"=== 日期: {date_str} ===\n"
    summary_header += f"=== 消息总数: {total_messages} (显示精简文本) ===\n\n"
    
    simplified_lines.append(summary_header)
    
    for idx in sorted_indices:
        if idx >= len(text_messages): continue
        m = text_messages[idx]
        dt = datetime.datetime.fromtimestamp(m['timestamp'])
        time_str = dt.strftime('%H:%M')
        # 去除 [语音转文字] 前缀
        content = m['content']
        if content.startswith('[语音转文字] '):
            content = content[7:]  # len('[语音转文字] ') = 7
        line = f"[{time_str}] {get_display_name(m)}: {content}"
        simplified_lines.append(line)

    # --- Output ---
    stats = {
        "meta": {
            "name": data['meta'].get('name'),
            "date": date_str,
            "total_count": total_messages,
            "active_user_count": len(active_users),
            "time_range": f"{start_dt.strftime('%H:%M')} 至 {end_dt.strftime('%H:%M')}"
        },
        "top_talkers": top_talkers,
        "night_owl": night_owl,
        "word_cloud": word_cloud_data,
        "raw_text_path": args.output_text
    }
    
    with open(args.output_stats, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
        
    with open(args.output_text, 'w', encoding='utf-8') as f:
        f.write("\n".join(simplified_lines))
        
    print(f"Analysis complete.")
    print(f"Stats saved to: {args.output_stats}")
    print(f"Simplified text saved to: {args.output_text}")

if __name__ == "__main__":
    args = parse_arguments()
    analyze(args)

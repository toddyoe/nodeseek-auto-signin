# NodeSeek 自动签到 - GitHub Actions 版

基于 GitHub Actions 的 NodeSeek 论坛自动化工具，无需服务器，Fork 即用。

## ✨ 功能

- ✅ 自动签到 + 领取奖励
- 💬 随机评论帖子（5-10 篇，间隔 3-7 分钟）
- 👥 **多账号支持**（Cookie 用 `|` 分隔）
- 🎯 **可配置评论区域**
- ⏰ **随机延迟执行**（防止固定时间触发）
- 📱 Telegram 执行结果通知
- 🔄 失败自动重试
- 🔐 Cookie 过期检测告警

## 🚀 快速开始

1. Fork 本仓库
2. 在 `Settings → Secrets and variables → Actions` 中添加配置
3. Actions 将每天 **北京时间 00:30** 自动执行

## ⚙️ 配置说明

### Secrets（敏感信息）

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `NS_COOKIE` | ✅ | NodeSeek Cookie，多账号用 `\|` 分隔 |
| `NS_RANDOM` | ❌ | `true`: 试试手气 / `false`: 鸡腿 x 5 |
| `NS_COMMENT_URL` | ❌ | 评论区域 URL（默认交易区） |
| `TG_BOT_TOKEN` | ❌ | Telegram Bot Token |
| `TG_CHAT_ID` | ❌ | Telegram Chat ID |

### Variables（非敏感配置）

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `NS_DELAY_MIN` | `0` | 随机延迟最小分钟 |
| `NS_DELAY_MAX` | `30` | 随机延迟最大分钟 |

## 📝 多账号配置示例

```
cookie1=value1; cookie2=value2|cookie1=value3; cookie2=value4
```

用 `|` 分隔不同账号的 Cookie。

## 📱 通知示例

### 单账号
```
🎯 NodeSeek 自动任务完成

📝 签到状态: ✅ 成功
💬 评论数量: 7 条

⏰ 执行时间: 北京时间 2026-02-08 00:30:00
```

### 多账号
```
🎯 NodeSeek 多账号任务完成

👤 账号1: 签到✅ | 评论7条
👤 账号2: 签到✅ | 评论5条

⏰ 执行时间: 北京时间 2026-02-08 00:30:00
```

## License

MIT

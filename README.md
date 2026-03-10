# NodeSeek 自动签到 - GitHub Actions 版

基于 GitHub Actions 的 NodeSeek 论坛自动化工具，无需服务器，Fork 即用。

## ✨ 功能

- ✅ 自动签到 + 领取奖励（支持"试试手气"和"鸡腿 x 5"智能选择）
- 💬 随机评论帖子（3-5 篇，间隔 1-2 分钟）
- 👥 **多账号支持**（Cookie 用 `|` 分隔）
- 🎯 **可配置评论区域**
- ⏰ **随机延迟执行**（0-10 分钟，防止固定时间触发）
- 📱 Telegram 极简科技风通知
- 🔄 失败自动重试 + 智能容错
- 🔐 Cookie 过期检测告警

## 🚀 快速开始

1. Fork 本仓库
2. 在 `Settings → Secrets and variables → Actions` 中添加配置
3. Actions 将每天自动执行两次：
   - **北京时间 00:10**（签到 + 评论）
   - **北京时间 12:20**（签到 + 评论）

## 🍪 如何获取 NodeSeek Cookie

1. 打开浏览器，访问 [NodeSeek](https://www.nodeseek.com) 并登录
2. 按 `F12` 打开开发者工具，切换到 **Network（网络）** 标签
3. 刷新页面，在请求列表中点击任意一个请求
4. 在右侧 **Headers（标头）** 中找到 `Cookie` 字段
5. 复制整个 Cookie 值（一长串文本）

**示例：**
```
session=abc123xyz; token=def456uvw; user_id=12345
```

> ⚠️ Cookie 包含登录凭证，请勿泄露！

## ⚙️ 配置说明

### Secrets（敏感信息）

在 `Settings → Secrets and variables → Actions → Secrets` 中添加：

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `NS_COOKIE` | ✅ | NodeSeek Cookie，多账号用 `\|` 分隔 |
| `NS_RANDOM` | ❌ | `true`(默认): 试试手气 / `false`: 鸡腿 x 5 |
| `NS_COMMENT_URL` | ❌ | 评论区域 URL（默认交易区） |
| `TG_BOT_TOKEN` | ❌ | Telegram Bot Token |
| `TG_CHAT_ID` | ❌ | Telegram Chat ID |
| `NS_COMMENT` | ❌ | `true`(默认),关闭评论功能则改为false |

### Variables（非敏感配置）

在 `Settings → Secrets and variables → Actions → Variables` 中添加：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `NS_DELAY_MIN` | `0` | 随机延迟最小分钟 |
| `NS_DELAY_MAX` | `10` | 随机延迟最大分钟 |

## 📝 多账号配置示例

```
账号1的完整Cookie|账号2的完整Cookie
```

示例：
```
session=abc123; token=xyz|session=def456; token=uvw
```

## 📱 通知示例

### 单账号
```
NodeSeek 每日简报
━━━━━━━━━━━━━━━
👤 账号: 账号 1
🏆 奖励: 5 🍗
💬 评论: 4 条
━━━━━━━━━━━━━━━
✅ 状态: 已签到
🕒 2026-02-10 00:10:00
```

### 多账号
```
🎯 NodeSeek 多账号任务完成

👤 账号1: 签到✅ | 评论4条
👤 账号2: 签到✅ | 评论3条

⏰ 执行时间: 北京时间 2026-02-10 00:10:00
```

## ❓ 常见问题

**Q: Cookie 多久过期？**  
A: 一般 7-30 天，过期后会收到 Telegram 告警通知。

**Q: 如何手动运行测试？**  
A: 进入 Actions 页面，选择 workflow，点击 "Run workflow"。

## License

MIT

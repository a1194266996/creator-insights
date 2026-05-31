# Creator Insights

每天搜索小红书公开索引里的萌宠内容，做简短选题分析，并推送到飞书机器人。

合规边界：项目只查询公开搜索索引中的公开页面，不绕过登录、验证码、签名、设备指纹、风控或小红书私有接口。

## 快速运行

```bash
cd /data/work/creator-insights
source ~/miniconda3/etc/profile.d/conda.sh
conda activate myenv
python -m creator_insights init-db
python -m creator_insights daily --limit 20 --days 7
```

## 配置

复制 `.env.example` 为 `.env`，配置：

- `CREATOR_INSIGHTS_SOURCE=web_search`
- `XHS_KEYWORDS=猫,萌宠`
- `XHS_SEARCH_SITE=xiaohongshu.com/explore`
- `FEISHU_WEBHOOK_URL=飞书机器人 webhook`

## 定时任务

安装 Linux cron：

```bash
cd /data/work/creator-insights
bash scripts/install_linux_cron.sh
```

默认每天 08:30 运行：

```bash
python -m creator_insights daily --limit 20 --days 7
```

## 输出

- SQLite 数据库：`data/creator_insights.db`
- Markdown 日报：`exports/insights-*.md`
- CSV 明细：`exports/latest-notes.csv`
- 飞书推送：每条结果包含关键词、标题、链接、内容类型、简短分析和创作启发。

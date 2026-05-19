# Creator Insights

面向小红书萌宠猫方向的日常内容观察工程。

这个项目提供定时采集、SQLite 存储、基础分析导出和可替换采集适配器。默认适配器不会绕过登录、验证码、签名、风控或平台权限，只保留清晰的扩展点，方便你接入自己有权限的数据来源、官方/授权接口，或人工导出的数据。

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python -m creator_insights init-db
python -m creator_insights collect --limit 20
python -m creator_insights analyze --days 7
python -m creator_insights daily --limit 100 --days 7
```

## 每日定时

Windows 任务计划程序示例：

```powershell
$project = "O:\work\creator-insights"
$python = "$project\.venv\Scripts\python.exe"
$action = New-ScheduledTaskAction -Execute $python -Argument "-m creator_insights daily --limit 100 --days 7" -WorkingDirectory $project
$trigger = New-ScheduledTaskTrigger -Daily -At 08:30
Register-ScheduledTask -TaskName "creator-insights-daily" -Action $action -Trigger $trigger -Description "Daily Xiaohongshu pet-cat content collection"
```

Linux/macOS cron 示例：

```cron
30 8 * * * cd /path/to/creator-insights && .venv/bin/python -m creator_insights daily --limit 100 --days 7 >> logs/cron.log 2>&1
```

## 配置

`.env` 支持：

- `CREATOR_INSIGHTS_DB_PATH`: SQLite 文件路径，默认 `data/creator_insights.db`
- `CREATOR_INSIGHTS_EXPORT_DIR`: 分析导出目录，默认 `exports`
- `CREATOR_INSIGHTS_SOURCE`: 数据源适配器，默认 `sample`
- `XHS_KEYWORDS`: 逗号分隔关键词，默认 `猫,萌宠,布偶猫,英短,橘猫`

## 合规说明

请只采集你有权访问和使用的数据，并遵守平台服务条款、robots、隐私和版权要求。项目不包含绕过登录态、验证码、签名校验、频控或反爬机制的实现。

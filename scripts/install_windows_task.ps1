param(
    [string]$TaskName = "creator-insights-daily",
    [string]$ProjectDir = "O:\work\creator-insights",
    [string]$PythonExe = "python",
    [string]$At = "08:30",
    [int]$Limit = 100
)

$action = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument "-m creator_insights daily --limit $Limit" `
    -WorkingDirectory $ProjectDir

$trigger = New-ScheduledTaskTrigger -Daily -At $At

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Description "Daily Xiaohongshu pet-cat content insight collection" `
    -Force

Write-Host "Registered task '$TaskName' at $At."

param(
    [string]$RepoRoot = "D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain",
    [int]$IntervalSeconds = 3600,
    [switch]$RunOnce
)

$ErrorActionPreference = "Stop"

$StateDir = Join-Path $RepoRoot ".codex_builder_state"
$LogDir = Join-Path $StateDir "logs"
$StateFile = Join-Path $StateDir "hourly_builder_state.json"
$LockFile = Join-Path $StateDir "builder_loop.lock"
$HeartbeatFile = Join-Path $StateDir "heartbeat.jsonl"

function Ensure-StateDirs {
    New-Item -ItemType Directory -Force -Path $StateDir | Out-Null
    New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
}

function Write-Heartbeat {
    param([hashtable]$Record)
    $Record["recorded_at"] = (Get-Date).ToString("o")
    ($Record | ConvertTo-Json -Compress -Depth 8) | Add-Content -Path $HeartbeatFile -Encoding UTF8
}

function Read-State {
    if (Test-Path $StateFile) {
        try {
            return Get-Content -Raw -Path $StateFile | ConvertFrom-Json
        } catch {
            return $null
        }
    }
    return $null
}

function Write-State {
    param([hashtable]$State)
    ($State | ConvertTo-Json -Depth 8) | Set-Content -Path $StateFile -Encoding UTF8
}

function Get-FileSha256 {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        return ""
    }
    return (Get-FileHash -Algorithm SHA256 -Path $Path).Hash.ToLowerInvariant()
}

function Invoke-Git {
    param([string[]]$Args)
    $output = & git -C $RepoRoot @Args 2>&1
    $exitCode = $LASTEXITCODE
    return [pscustomobject]@{
        ExitCode = $exitCode
        Output = ($output -join [Environment]::NewLine)
    }
}

function Get-CommitSha {
    $result = Invoke-Git @("rev-parse", "HEAD")
    if ($result.ExitCode -eq 0) {
        return $result.Output.Trim()
    }
    return ""
}

function Get-ActiveTaskPathFromIndex {
    $indexPath = Join-Path $RepoRoot "tasks\TASK_INDEX.md"
    if (-not (Test-Path $indexPath)) {
        return ""
    }
    $text = Get-Content -Raw -Path $indexPath
    $match = [regex]::Match($text, "tasks/[0-9]{8}_[0-9]{6}_T[0-9]{3}_[^`\s|]+\.md")
    if ($match.Success) {
        return $match.Value
    }
    return "tasks/NEXT_TASK.md"
}

function Invoke-ActiveTask {
    param([string]$TaskText)
    if ($TaskText -match "T001" -and $TaskText -match "06_true_moving_geometry_R3_phase3_diagnostic_repair") {
        $scriptPath = Join-Path $RepoRoot "06_true_moving_geometry_R3_phase3_diagnostic_repair\scripts\R3_B_minimal_phase3_repro.py"
        if (-not (Test-Path $scriptPath)) {
            throw "Known T001 runner is missing: $scriptPath"
        }
        $venvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
        $python = "python"
        if (Test-Path $venvPython) {
            $python = $venvPython
        }
        $logPath = Join-Path $LogDir ("task_runner_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".log")
        $output = & $python $scriptPath 2>&1
        $exitCode = $LASTEXITCODE
        ($output -join [Environment]::NewLine) | Set-Content -Path $logPath -Encoding UTF8
        return [pscustomobject]@{
            ExitCode = $exitCode
            LogPath = $logPath
            Output = ($output -join [Environment]::NewLine)
        }
    }
    $stopReportDir = Join-Path $RepoRoot "builder_loop_reports"
    New-Item -ItemType Directory -Force -Path $stopReportDir | Out-Null
    $stopReport = Join-Path $stopReportDir ("unknown_active_task_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".md")
    @(
        "# Builder Loop Stopped",
        "",
        "- Reason: active task is new or not recognized by the local safe runner.",
        "- The loop intentionally stops instead of inventing task execution logic.",
        "- Re-run Codex Builder Agent against tasks/NEXT_TASK.md, then update the local runner if needed."
    ) | Set-Content -Path $stopReport -Encoding UTF8
    throw "Unknown active task; wrote stop report: $stopReport"
}

function Invoke-WorkCycle {
    Ensure-StateDirs
    if (Test-Path $LockFile) {
        Write-Heartbeat @{
            started_at = (Get-Date).ToString("o")
            active_task = ""
            executed = $false
            pushed = $false
            commit_sha = Get-CommitSha
            status = "SKIP_LOCK_PRESENT"
        }
        return
    }
    New-Item -ItemType File -Path $LockFile -Force | Out-Null
    $cycle = @{
        started_at = (Get-Date).ToString("o")
        active_task = ""
        executed = $false
        pushed = $false
        commit_sha = ""
        status = "STARTED"
    }
    try {
        $pull = Invoke-Git @("pull", "--ff-only")
        if ($pull.ExitCode -ne 0) {
            $cycle.status = "STOP_GIT_PULL_FAILED"
            $cycle.error = $pull.Output
            Write-Heartbeat $cycle
            throw "git pull --ff-only failed: $($pull.Output)"
        }

        $nextTaskPath = Join-Path $RepoRoot "tasks\NEXT_TASK.md"
        $indexPath = Join-Path $RepoRoot "tasks\TASK_INDEX.md"
        if (-not (Test-Path $nextTaskPath) -or -not (Test-Path $indexPath)) {
            $cycle.status = "STOP_TASK_FILES_MISSING"
            Write-Heartbeat $cycle
            throw "Required task files are missing."
        }
        $taskText = Get-Content -Raw -Path $nextTaskPath
        $taskHash = Get-FileSha256 $nextTaskPath
        $activeTask = Get-ActiveTaskPathFromIndex
        $cycle.active_task = $activeTask

        $state = Read-State
        if ($state -and $state.last_completed_task_hash -eq $taskHash -and $state.last_completed_active_task -eq $activeTask) {
            $cycle.status = "HEARTBEAT_ALREADY_COMPLETED"
            $cycle.commit_sha = Get-CommitSha
            Write-Heartbeat $cycle
            return
        }

        $runner = Invoke-ActiveTask -TaskText $taskText
        $cycle.executed = $true
        if ($runner.ExitCode -ne 0) {
            $cycle.status = "TASK_RAN_WITH_FAIL_STATUS"
            $cycle.runner_log = $runner.LogPath
        } else {
            $cycle.status = "TASK_RAN_PASS_STATUS"
            $cycle.runner_log = $runner.LogPath
        }

        $status = Invoke-Git @("status", "--short")
        if ($status.ExitCode -ne 0) {
            throw "git status failed: $($status.Output)"
        }
        if (-not [string]::IsNullOrWhiteSpace($status.Output)) {
            $add = Invoke-Git @("add", "--all")
            if ($add.ExitCode -ne 0) {
                throw "git add failed: $($add.Output)"
            }
            $message = "Run Codex Builder active task " + (Get-Date -Format "yyyyMMdd_HHmmss")
            $commit = Invoke-Git @("commit", "-m", $message)
            if ($commit.ExitCode -ne 0) {
                throw "git commit failed: $($commit.Output)"
            }
            $push = Invoke-Git @("push")
            if ($push.ExitCode -ne 0) {
                throw "git push failed: $($push.Output)"
            }
            $cycle.pushed = $true
        }
        $cycle.commit_sha = Get-CommitSha
        Write-State @{
            last_completed_task_hash = $taskHash
            last_completed_active_task = $activeTask
            last_completed_at = (Get-Date).ToString("o")
            last_commit_sha = $cycle.commit_sha
            last_status = $cycle.status
        }
        Write-Heartbeat $cycle
    } catch {
        $cycle.status = "STOP_EXCEPTION"
        $cycle.error = $_.Exception.Message
        $cycle.commit_sha = Get-CommitSha
        Write-Heartbeat $cycle
        throw
    } finally {
        Remove-Item -Path $LockFile -Force -ErrorAction SilentlyContinue
    }
}

do {
    Invoke-WorkCycle
    if ($RunOnce) {
        break
    }
    Start-Sleep -Seconds $IntervalSeconds
} while ($true)

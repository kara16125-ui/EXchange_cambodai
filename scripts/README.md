# Automation helper scripts

Place this entire `scripts` folder in the repository root:

```text
Cambodian Exchange Rate Automation/
├── scripts/
├── fetch_daily_rate.py
├── download_historical_rates.py
├── telegram_bot.py
├── requirements.txt
└── .venv/
```

## Files

| File | Purpose |
| --- | --- |
| `run_daily.ps1` | Runs one selected Python job and writes a dated log. |
| `install_daily_task.ps1` | Installs a Windows Task Scheduler task for one selected job. |
| `remove_daily_task.ps1` | Removes a previously installed job. |
| `publish_current_year.ps1` | Commits and pushes only the current `YYYY` archive folder, plus `txt/YYYY` when requested. |

## Before installing a task

From the repository root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Configure Git authentication once under the same Windows account that runs Task Scheduler. Test this manually:

```powershell
git pull --rebase origin main
git push origin main
```

Keep `.env`, `.venv/`, and `logs/` in `.gitignore`.

## Run a job manually

```powershell
.\scripts\run_daily.ps1 -Job daily-rate
.\scripts\run_daily.ps1 -Job historical
.\scripts\run_daily.ps1 -Job telegram
```

Run the daily-rate job and publish the current year afterward:

```powershell
.\scripts\run_daily.ps1 -Job daily-rate -PublishAfterRun
```

Also publish extracted text files from `txt/YYYY`:

```powershell
.\scripts\run_daily.ps1 -Job daily-rate -PublishAfterRun -IncludeTextArchive
```

## Install one daily scheduled task

Run PowerShell as the Windows account that should own the task.

```powershell
.\scripts\install_daily_task.ps1 -Job daily-rate -Time "08:00" -PublishAfterRun -IncludeTextArchive
```

Other examples:

```powershell
.\scripts\install_daily_task.ps1 -Job historical -Time "08:15"
.\scripts\install_daily_task.ps1 -Job telegram -Time "08:30"
```

The valid job names are:

- `daily-rate` → `fetch_daily_rate.py`
- `historical` → `download_historical_rates.py`
- `telegram` → `telegram_bot.py`

Each job gets its own scheduled task, so users install only the jobs they want.

## Remove a scheduled task

```powershell
.\scripts\remove_daily_task.ps1 -Job daily-rate
```

## Publishing behavior

`publish_current_year.ps1`:

1. Detects the current year automatically, such as `2026`.
2. Stages only the current `YYYY` folder.
3. Optionally stages `txt/YYYY`.
4. Stops without creating an empty commit when nothing changed.
5. Creates a dated commit.
6. Pulls with rebase and auto-stash.
7. Pushes to `origin/main`.

The script deliberately does not run `git add .`, reducing the risk of committing `.env` or unrelated local changes.

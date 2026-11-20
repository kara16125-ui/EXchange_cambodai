# Cambodian Exchange Rate Automation 🇰🇭

> Because checking the same exchange rate every day is exactly the kind of thing a computer should be doing.

A small Python automation project for retrieving, archiving, and distributing the official **USD/KHR exchange rate published by the National Bank of Cambodia (NBC)**.

I originally built this around a straightforward requirement: get the official NBC rate automatically and make the result easy to use in other workflows.

It grew into a small toolkit that can retrieve the daily rate, preserve NBC's published PDF, rebuild historical records, provide simple text output for automation, and optionally send the rate through Telegram.

The idea is simple: **understand the process first, automate the repetition second.**

## How it works

```text
National Bank of Cambodia
          |
          v
 Official USD/KHR Rate
          |
   +------+------+
   |             |
   v             v
Extract Rate   Download PDF
   |             |
   v             v
Text Output   Local Archive
   |
   +-----------> Power Automate
   |
   +-----------> Telegram (optional)
```

The text output intentionally contains only the numeric exchange rate, for example:

```text
4100
```

Keeping the output boring is useful. It means Power Automate, Python, scheduled jobs, or another workflow can consume the value without parsing the NBC webpage again.

## Why this project exists

The National Bank of Cambodia publishes official exchange-rate information online, but repeatedly checking a webpage is not particularly useful when the same information needs to feed another business process.

So I automated it.

The project retrieves the published USD/KHR rate, keeps the corresponding official document as a source record, and produces a simple machine-readable output for other automations to consume.

## Features

- Retrieve the current official USD/KHR rate from NBC
- Save the daily rate to a dated `.txt` file
- Download and archive the corresponding NBC exchange-rate PDF
- Download and process historical exchange-rate records from January 1, 2025
- Extract the official rate from historical PDFs
- Organize PDF and text records automatically by year and month
- Skip files that have already been downloaded
- Produce simple output that can be consumed by Power Automate and other workflows
- Optionally send the daily rate to a Telegram chat or topic
- Designed to run unattended with Windows Task Scheduler

## Project scripts

| Script                     | Purpose                                                                             |
| -------------------------- | ----------------------------------------------------------------------------------- |
| `fetch_daily_rate.py`    | Retrieves today's NBC rate, saves it to a `.txt` file, and downloads today's PDF. |
| `download_historical.py` | Downloads and processes NBC exchange-rate PDFs for a date range.                    |
| `telegram_bot.py`        | Retrieves today's NBC rate and sends it to Telegram.                                |

> **Note:** The Telegram script currently keeps its original filename, including `Exhange`. Rename the file and update the commands below together if you want to correct it to `Exchange`.

## Design principles

**Official source first**
Rates are retrieved from information published by NBC.

**Keep the source record**
The corresponding official PDF can be stored alongside the extracted data.

**Machine-readable output**
A plain numeric text file is intentionally simple and easy to integrate.

**Safe to rerun**
Existing historical files are skipped instead of being downloaded repeatedly.

**Understand before automating**
The workflow should remain understandable even without the automation running.

## Requirements

- Windows
- Python 3.10 or newer
- Internet access
- Git, if cloning or updating the repository
- A Telegram bot token and chat ID only if using the Telegram script

## Getting started

### 1. Clone

Install Git and Python 3, then open PowerShell:

```powershell
git clone <repository-url>
cd "Cambodian Exchange Rate Automation"
```

Replace `<repository-url>` with the GitHub clone URL for this repository.

To clone directly to a chosen location:

```powershell
git clone https://github.com/justvroth-create/Cambodian-Exchange-Rate-Automation "C:\Projects\Cambodian Exchange Rate Automation"
cd "C:\Projects\Cambodian Exchange Rate Automation"
```

### 2. Create a Python environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Keep the environment activated while running the scripts manually.

### 3. Configure Telegram (optional)

Telegram configuration is required only for the Telegram bot script.

```powershell
Copy-Item .example.env .env
notepad .env
```

Set the values in `.env`:

```dotenv
BOT_TOKEN=123456789:replace-with-your-bot-token
CHAT_ID=-1001234567890
MESSAGE_THREAD=123
```

- `BOT_TOKEN`: token from Telegram's BotFather
- `CHAT_ID`: destination chat or supergroup ID
- `MESSAGE_THREAD`: optional numeric topic/thread ID; remove the line or leave it empty for a normal chat without a topic

**Do not commit `.env`.** It should remain excluded through `.gitignore`.

## Running the project

### Download today's rate and PDF

```powershell
python "Exchange Rate For Power Automate.py"
```

This creates records using the following structure:

```text
txt\<YEAR>\<MM. Month>\<MM-DD-YY>.txt
<YEAR>\<MM. Month>\<DD-MM-YY>.pdf
```

The text file contains only the numeric rate, for example `4100`.

### Build or update the historical archive

```powershell
python "Exchange Rate Period to PDF.py"
```

By default, the historical script processes **January 1, 2025 through yesterday**. Existing PDF and text files are skipped, so rerunning the script does not intentionally duplicate existing records.

To change the date range, edit these values near the top of `Exchange Rate Period to PDF.py`:

```python
START_DATE = date(2025, 1, 1)
END_DATE = date.today() - timedelta(days=1)
```

### Send today's rate to Telegram

```powershell
python "NBC Exhange Rate USD-KHR Telegram_BOT.py"
```

The script sends an HTML-formatted Telegram message containing the date, currency, and current NBC rate.

## Output structure

```text
Cambodian Exchange Rate Automation/
├── txt/
│   └── YYYY/
│       └── MM. Month/
│           └── MM-DD-YY.txt
├── YYYY/
│   └── MM. Month/
│       └── DD-MM-YY.pdf
├── Exchange Rate For Power Automate.py
├── Exchange Rate Period to PDF.py
├── NBC Exhange Rate USD-KHR Telegram_BOT.py
├── .example.env
├── requirements.txt
└── README.md
```

## Data archive

The generated year folders can also act as a growing archive of the records retrieved by the automation:

```text
YYYY/
└── MM. Month/
    └── DD-MM-YY.pdf

txt/
└── YYYY/
    └── MM. Month/
        └── MM-DD-YY.txt
```

When daily scheduling and Git publishing are enabled, new records can be committed after a successful run. This lets the repository serve both as the automation source code and as a continuously maintained archive of the records it retrieves.

## Schedule with Windows Task Scheduler

For unattended daily execution:

1. Open **Task Scheduler**.
2. Select **Create Task**.
3. Enable **Run whether user is logged on or not** if the automation must run in the background.
4. Under **Actions**, create a new action:
   - **Program/script:** full path to `.\.venv\Scripts\python.exe`
   - **Arguments:** `"Exchange Rate For Power Automate.py"` or `"NBC Exhange Rate USD-KHR Telegram_BOT.py"`
   - **Start in:** the cloned project folder
5. Add a daily trigger at the desired Cambodia time.

Example:

```text
Program/script: C:\Projects\Cambodian Exchange Rate Automation\.venv\Scripts\python.exe
Arguments: "Exchange Rate For Power Automate.py"
Start in: C:\Projects\Cambodian Exchange Rate Automation
```

Use one task per script if the scripts are scheduled independently. The Windows account running the task must have permission to write inside the project folder.

## Troubleshooting

### `Could not find exchange rate`

- Check the internet connection.
- Confirm that the [official NBC exchange-rate page](https://www.nbc.gov.kh/english/economic_research/exchange_rate.php) is available.
- NBC may have changed the page layout or temporarily published a value the current parser does not recognize.

### `PDF failed` or `[NOT AVAILABLE]`

- The NBC PDF may not have been published for that date yet.
- Re-run the script later.
- Existing historical files are skipped, so rerunning does not intentionally duplicate existing records.

### Telegram message fails

- Verify `BOT_TOKEN`, `CHAT_ID`, and `MESSAGE_THREAD`.
- Ensure the bot has been added to the destination chat or supergroup.
- If using a topic, ensure the bot is allowed to post there.

### PowerShell activation fails

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Updating

```powershell
git pull
python -m pip install --upgrade -r requirements.txt
```

## Disclaimer

This is an independent open-source project and is **not affiliated with or endorsed by the National Bank of Cambodia**.

Exchange-rate data and source documents are retrieved from official NBC publications. For financial, accounting, or other critical use, verify the exchange rate against the official NBC source.

## Author

**Khun Virakroth (Steav Roth)**

Automation developer from Cambodia working with Python, RPA, Power Automate, and practical business-process automation.

If this project saves someone from manually checking the same exchange rate every morning, it did its job.

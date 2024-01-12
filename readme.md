User Guide for JIRA Ticket Generator Script (Version 2)
Introduction

The updated script allows you to generate JIRA tickets from an Excel (.xlsx) file.

Pre-requisites

    Python 3.x
    pip (Python Package Installer)

Installing Dependencies

Run the following command to install the required Python packages.

``` pip install -r requirements.txt ```

Configuration File Setup

Create a config.json file in the same directory as your script with the following structure:

```
{
    "jira_server_url": "https://x.atlassian.net",
    "basic_auth": {
      "username": "x",
      "api_token": "x"
    }
}
  
```

Setting up Authentication
Basic Authentication + API Key

    Generate API Token: Log into your JIRA account and navigate to Account Settings > Security > API Token > Create and manage API tokens.
    Retrieve Username: Your username is usually your email.
    Update Config File: Populate the config.json file with your username and generated API token.

Command-line Arguments

    --new-sheet: Creates a new Excel sheet template.
    -t or --create-tickets: Reads the Excel file and creates JIRA tickets.
    -a or --auth: Specifies the authentication method (oauth or basic).
    -f or --file: Specifies the Excel file name.

Usage Examples
Create a New Excel Sheet

bash

python script.py --new-sheet

Create JIRA Tickets (OAuth)

```
python script.py -t -a basic -f my_tickets.xlsx

## Create JIRA Tickets (Basic Authentication)

python script.py -t -a basic -f my_tickets.xlsx
```

Important Note:
Make sure the config.json file is securely stored and has appropriate file permissions to prevent unauthorized access. Also, ensure it is not committed to your version control system.

User Guide for JIRA Ticket Generator Script (Version 2)
Introduction

The updated script allows you to generate JIRA tickets from an Excel (.xlsx) file. This version offers the flexibility of choosing between OAuth 2.0 and Basic Authentication methods, and it reads credentials from a JSON configuration file.
Pre-requisites
Software Requirements

    Python 3.x
    pip (Python Package Installer)

Installing Dependencies

Run the following command to install the required Python packages.

pip install -r requirements.txt

Configuration File Setup

Create a config.json file in the same directory as your script with the following structure:

json

{
  "oauth": {
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uri": "YOUR_REDIRECT_URI"
  },
  "basic_auth": {
    "username": "YOUR_USERNAME",
    "api_token": "YOUR_API_TOKEN"
  }
}

Setting up Authentication
OAuth 2.0

    Register Your Application: Visit the Atlassian Developer console to register your application and obtain a Client ID and Client Secret.
    Redirect URI: Set up a redirect URI. This is the URL to which you'll be redirected after you authorize the app. Configure this in the Atlassian developer console.
    Update Config File: Populate the config.json file with your OAuth 2.0 credentials.

Step-by-step OAuth 2.0 Setup

    Go to Atlassian Developer Console.
    Click "Create new app".
    Fill in the details and create your app.
    In the "OAuth 2.0" tab, add a redirection URI. This should match the redirect_uri in your config.json.
    Retrieve your Client ID and Client Secret and update config.json.

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

bash

python script.py -t -a oauth -f my_tickets.xlsx

Create JIRA Tickets (Basic Authentication)

bash

python script.py -t -a basic -f my_tickets.xlsx

Important Note

Make sure the config.json file is securely stored and has appropriate file permissions to prevent unauthorized access. Also, ensure it is not committed to your version control system.

By following this guide, you should be able to securely and effectively use the script to automate your JIRA ticket creation process.
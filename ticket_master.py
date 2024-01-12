import argparse
import pandas as pd
import json
import xlsxwriter
from jira import JIRA
from jira.exceptions import JIRAError
from var_dump import var_dump

# Connect to Jira with Basic Auth
def connect_to_jira_basic_auth(server_url, username, api_token):
    basic_auth = (username, api_token)
    return JIRA(server_url, basic_auth=basic_auth)

# Load Basic Auth credentials from JSON config
def load_basic_auth_config(json_file_path):
    with open(json_file_path, 'r') as f:
        config = json.load(f)
    return config["jira_server_url"], config["basic_auth"]["username"], config["basic_auth"]["api_token"]

# Read Excel file into DataFrame
def read_excel(file_path):
    return pd.read_excel(file_path)

# Helper function to convert email to account ID
def email_to_account_id(jira, email):
    try:
        # Search users with query parameter as 'query' instead of 'username'
        user = jira.search_users(query=email)
        if user:
            return user[0].accountId
        else:
            print(f"No user found for email: {email}")
            return None
    except JIRAError as e:
        print(f"Failed to fetch account ID for email {email}. Error: {e}")
        return None

# Create Jira issues from DataFrame
def create_jira_issues(jira, df, project_key):
    # Fetch priority and issue type data from Jira
    priorities = {priority.name: priority.id for priority in jira.priorities()}
    issue_types = {issue_type.name: issue_type.id for issue_type in jira.issue_types()}

    fields_id_dict = fetch_fields_id_for_projects(jira)
    for _, row in df.iterrows():
        issue_dict = {'project': {'key': project_key}}
        for col in df.columns:
            if pd.notna(row[col]):
                # Map the DataFrame's column name to its corresponding Jira field ID
                field_id = fields_id_dict.get(col, col)

                # Check if the field is one of the fields that require mapping
                if col == 'Priority' and row[col] in priorities:
                    issue_dict[field_id] = {'id': priorities[row[col]]}
                elif col == 'Issue Type' and row[col] in issue_types:
                    issue_dict[field_id] = {'id': issue_types[row[col]]}
                elif col == 'Reporter':
                    account_id = email_to_account_id(jira, row[col])

                    if account_id:
                        issue_dict['reporter'] = {'accountId': account_id}
                    else:
                        print(f"Could not set reporter for email {row[col]}")
                else:
                    issue_dict[field_id] = row[col]

        new_ticket = jira.create_issue(fields=issue_dict)
        print(f"Successfully created issue {new_ticket.key} for project {project_key}.")

# Function to test basic authentication
def test_basic_auth(jira):
    try:
        user = jira.current_user()
        print(f"Successfully authenticated as {user}.")
    except Exception as e:
        print(f"Failed to authenticate. Error: {e}")

# Function to list projects
def list_projects(jira):
    try:
        projects = jira.projects()
        for project in projects:
            print(f"Project ID: {project.id}, Key: {project.key}, Name: {project.name}")
    except Exception as e:
        print(f"Failed to list projects. Error: {e}")

# Dynamic mapping of field ids and display names
def fetch_fields_id_for_projects(jira):
    fields_dict = {}
    fields = jira.fields()
    for field in fields:
        fields_dict[field['name']] = field['id']
    return fields_dict

# Function to fetch fields for each project and save to dictionary
def fetch_fields_for_projects(jira, project_keys):
    # # Priority
    # priorities = jira.priorities()
    # if priorities:
    #     priority_attributes = dir(priorities[0])
    # else:
    #     priority_attributes = "No priorities found"

    # # Issue Type
    # issue_types = jira.issue_types()
    # issue_type_attributes = dir(issue_types[0]) if issue_types else "No issue types found"

    # # Assignee
    # assignable_users = jira.search_assignable_users_for_projects('', project_keys)
    # assignee_attributes = dir(assignable_users[0]) if assignable_users else "No assignable users found"

    # # Reporter
    # reporter_attributes = assignee_attributes  # Assuming reporter attributes are the same as assignee

    # # Print the attributes
    # print("Priority attributes:", priority_attributes,"\n")
    # print("Issue Type attributes:", issue_type_attributes,"\n")
    # print("Assignee attributes:", assignee_attributes,"\n")
    # print("Reporter attributes:", reporter_attributes,"\n")

    fields_dict = {}
    for key in project_keys:
        fields = [field['name'] for field in jira.fields() if field['custom'] is False]
        fields_dict[key] = fields
    return fields_dict

# Create new spreadsheet with all fields for each project
def create_project_spreadsheet(fields_dict, jira):
    for project_key, fields in fields_dict.items():
        primary_fields = ['Summary', 'Description', 'Priority', 'Assignee', 'Reporter', 'Issue Type']
        sorted_fields = [field for field in primary_fields if field in fields]
        sorted_fields.extend([field for field in fields if field not in primary_fields])

        # Create a DataFrame with sorted_fields as columns
        df = pd.DataFrame(columns=sorted_fields)
        output_file = f"report_spreadsheet_{project_key}.xlsx"
        df.to_excel(output_file, index=False, engine='xlsxwriter')

        # Open workbook and worksheet using xlsxwriter
        workbook = xlsxwriter.Workbook(output_file)
        worksheet = workbook.add_worksheet()

        # Define cell formats
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': 'gray', 'font_color': 'white'})

        # Write header to worksheet
        for idx, field in enumerate(sorted_fields):
            worksheet.write(0, idx, field, header_format)

        # Define table columns based on sorted_fields
        table_columns = [{'header': field} for field in sorted_fields]
        
        # Add the Excel table structure. Pandas will add the data.
        worksheet.add_table(0, 0, 20, len(sorted_fields) - 1, {
            'columns': table_columns,
            'name': 'Jira_Issues',
            'style': 'Table Style Light 12',
        })

        # Creating a dict of field names to dropdown values
        dropdown_values = {
            'Priority': list(set(priority.name for priority in jira.priorities())),
            'Issue Type': [issue_type.name for issue_type in jira.issue_types()],
            'Assignee': list(set(user.emailAddress for user in jira.search_assignable_users_for_projects('', project_key))),
            'Reporter': list(set(user.emailAddress for user in jira.search_assignable_users_for_projects('', project_key)))
            # Add more logic to fetch options for other primary fields here
        }

        dropdown_values = {key: val for key, val in dropdown_values.items() if key in primary_fields}

        # Add data validation (dropdowns)
        for col_idx, col_name in enumerate(sorted_fields):
            if col_name in dropdown_values:
                dv_values = dropdown_values.get(col_name, [])
                dv_str = ','.join(dv_values)
                worksheet.data_validation(1, col_idx, 1000, col_idx,
                                         {'validate': 'list',
                                          'source': dv_values,
                                          'input_message': f'Pick a value for {col_name}',
                                          'error_title': 'Invalid input',
                                          'error_message': f'Must be one of {dv_str}'})

        workbook.close()

# Function to parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Manage Jira tickets and fetch project fields.')
    parser.add_argument('-d', '--debug-basic', action='store_true', help='Run functions to test basic authentication.')
    parser.add_argument('-t', '--create-tickets', action='store_true', help='Create Jira tickets from the Excel sheet.')
    parser.add_argument('-f', '--file', type=str,  help='Specify the Excel file name.')
    parser.add_argument('--new-sheet', '--new-sheets', type=str, help='Create new sheet(s) with tailored columns, using fetched fields for specified projects. Use comma-separated project keys.')

    return parser.parse_args()

# Main function
def main():
    args = parse_args()
    
    if args.debug_basic:
        jira_server_url, username, api_token = load_basic_auth_config("config.json")
        jira = connect_to_jira_basic_auth(jira_server_url, username, api_token)
        test_basic_auth(jira)
        list_projects(jira)

    if args.create_tickets and args.file:
        jira_server_url, username, api_token = load_basic_auth_config("config.json")
        jira = connect_to_jira_basic_auth(jira_server_url, username, api_token)

        df = read_excel(args.file)
        project_key = args.file.split("_")[-1].split(".")[0]  # Extract project_key from filename
        create_jira_issues(jira, df, project_key)

    if args.new_sheet:
        project_keys = args.new_sheet.split(',')
        jira_server_url, username, api_token = load_basic_auth_config("config.json")
        jira = connect_to_jira_basic_auth(jira_server_url, username, api_token)
        fields_dict = fetch_fields_for_projects(jira, project_keys)
        create_project_spreadsheet(fields_dict, jira)
        print("Fields fetched and spreadsheets created.")

if __name__ == "__main__":
    main()

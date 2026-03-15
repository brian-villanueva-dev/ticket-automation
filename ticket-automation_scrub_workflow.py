"""
Scrub sensitive data from n8n workflow JSON before publishing to GitHub.
Double-click to run, or: python scrub_workflow.py
"""

import json
import re

INPUT_FILE = r"C:\Users\bav40\OneDrive\Documents\New Career\Projects\ticket-automation\n8n_ticket_automation_workflow_unedited.json"
OUTPUT_FILE = r"C:\Users\bav40\OneDrive\Documents\New Career\Projects\ticket-automation\n8n_ticket_automation_workflow.json"

SCRUB_PATTERNS = {
    # Slack
    r'xoxb-[A-Za-z0-9\-]+': 'xoxb-YOUR-SLACK-BOT-TOKEN',
    # Claude API
    r'sk-ant-[A-Za-z0-9\-_]+': 'YOUR_CLAUDE_API_KEY',
    # Jira domain
    r'https://[a-zA-Z0-9\-]+\.atlassian\.net': 'https://YOUR_DOMAIN.atlassian.net',
    # Jira API token
    r'ATATT[A-Za-z0-9\-_+=]+': 'YOUR_JIRA_API_TOKEN',
}

# Fields where the value should be replaced regardless of pattern
FIELD_SCRUB = {
    'apikey': 'YOUR_API_KEY',
    'accesstoken': 'YOUR_ACCESS_TOKEN',
    'password': 'YOUR_PASSWORD',
    'token': 'YOUR_TOKEN',
    'webhookid': 'auto-generated',
}

# Top-level and meta fields to scrub
TOP_LEVEL_SCRUB = {
    'versionId': 'YOUR_VERSION_ID',
}

# Fields inside credential references to scrub
CREDENTIAL_ID_FIELDS = {'slackApi', 'jiraSoftwareCloudApi', 'httpHeaderAuth'}

def scrub_string(text):
    for pattern, replacement in SCRUB_PATTERNS.items():
        text = re.sub(pattern, replacement, text)
    return text

def scrub_node(obj, parent_key=None):
    if isinstance(obj, dict):
        # Scrub top-level workflow fields
        for key in TOP_LEVEL_SCRUB:
            if key in obj and isinstance(obj[key], str):
                obj[key] = TOP_LEVEL_SCRUB[key]

        # Scrub the workflow-level id (only the short alphanumeric one)
        if 'id' in obj and 'name' in obj and obj.get('name') == 'Slack \u2192 AI Ticket Parser \u2192 Jira':
            obj['id'] = 'YOUR_WORKFLOW_ID'

        # Scrub meta block
        if 'meta' in obj and isinstance(obj['meta'], dict):
            if 'instanceId' in obj['meta']:
                obj['meta']['instanceId'] = 'YOUR_INSTANCE_ID'

        # Scrub credential references
        if 'credentials' in obj and isinstance(obj['credentials'], dict):
            for cred_type, cred_val in obj['credentials'].items():
                if isinstance(cred_val, dict) and 'id' in cred_val:
                    cred_val['id'] = f'YOUR_{cred_type.upper()}_CREDENTIAL_ID'

        # Scrub channel IDs (Slack channel IDs start with C and are 9-12 uppercase alphanumeric)
        if parent_key == 'channelId' and 'value' in obj:
            val = obj['value']
            if isinstance(val, str) and re.match(r'^C[A-Z0-9]{8,12}$', val):
                obj['value'] = 'YOUR_CHANNEL_ID'

        for key, value in obj.items():
            if key.lower() in FIELD_SCRUB and isinstance(value, str) and len(value) > 10:
                obj[key] = FIELD_SCRUB[key.lower()]
            elif isinstance(value, str):
                obj[key] = scrub_string(value)
            elif isinstance(value, (dict, list)):
                scrub_node(value, parent_key=key)

    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, str):
                obj[i] = scrub_string(item)
            elif isinstance(item, (dict, list)):
                scrub_node(item, parent_key=parent_key)

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    scrub_node(workflow)

    # Final pass: scrub the top-level workflow id
    if 'id' in workflow and isinstance(workflow['id'], str) and len(workflow['id']) > 8:
        workflow['id'] = 'YOUR_WORKFLOW_ID'

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)

    print(f"Input:  {INPUT_FILE}")
    print(f"Output: {OUTPUT_FILE}")
    print()
    print("Scrubbed:")
    print("  - Slack bot tokens")
    print("  - Claude API keys")
    print("  - Jira domain URLs")
    print("  - Jira API tokens")
    print("  - Slack channel IDs")
    print("  - Credential reference IDs")
    print("  - n8n instance ID")
    print("  - Workflow ID and version ID")
    print()
    print("Review the output before pushing to GitHub.")
    input("Press Enter to close...")

if __name__ == '__main__':
    main()

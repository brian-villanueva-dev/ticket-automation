# Ticket Automation — Setup Checklist

## Before you import the workflow

### 1. Slack workspace (free)
- [ ] Create a free Slack workspace (or use an existing one)
- [ ] Create channel: `#infra-issues` (where developers post complaints)
- [ ] Create channel: `#infra-digest` (for weekly trend summaries — bonus workflow)
- [ ] Create a Slack App at https://api.slack.com/apps
- [ ] Bot token scopes needed:
  - `channels:history` (read messages)
  - `chat:write` (post replies)
  - `reactions:read` (for the X-to-flag feature, optional)
- [ ] Install app to workspace → copy Bot User OAuth Token (starts with `xoxb-`)
- [ ] Get the `#infra-issues` channel ID (right-click channel name → View channel details → scroll to bottom)

### 2. Jira Cloud (free tier — up to 10 users)
- [ ] Create a Jira Cloud account at https://www.atlassian.com/software/jira/free
- [ ] Create project with key `INFRA` (or your preferred key)
- [ ] Create Components (Project Settings → Components):
  - BAT GIS Server
  - BAT VM
  - Production GIS Portal
  - Staging GIS Portal
  - Production GIS Server
  - Staging GIS Server
  - (add more as needed for your systems)
- [ ] Create custom fields (Project Settings → Fields):
  - "Reported By" → Short text
  - "Environment" → Select list (BAT, Staging, Production, Unknown)
  - "Slack Thread" → URL
- [ ] Generate API token at https://id.atlassian.com/manage-profile/security/api-tokens
- [ ] Note your Jira domain (e.g., `yourname.atlassian.net`)
- [ ] Note your Jira email (used for API auth)

### 3. Claude API
- [ ] Get API key at https://console.anthropic.com/
- [ ] Add a small amount of credits ($5 is plenty for months of use)
- [ ] Note: each ticket parse costs ~$0.002 with Claude Sonnet

### 4. n8n
- [ ] Option A: n8n Cloud free tier at https://n8n.io (easiest)
- [ ] Option B: Self-host with `npx n8n` (free, needs Node.js)
- [ ] Option C: Docker: `docker run -it --rm -p 5678:5678 n8nio/n8n`


## After import — find and replace these values

Open each node and replace the placeholder values:

| Placeholder              | Where to find it                    | Which nodes         |
|--------------------------|-------------------------------------|----------------------|
| `YOUR_CHANNEL_ID`        | Slack channel details               | Slack Trigger        |
| `YOUR_PROJECT_KEY`       | Jira project settings (e.g. INFRA)  | Jira Create Issue    |
| `YOUR_DOMAIN`            | Your Jira URL prefix                | Build Slack Reply    |


## Credentials to set up in n8n

Go to n8n Settings → Credentials and create:

### Slack credential
- Type: Slack API
- Access Token: your `xoxb-` bot token

### Jira credential  
- Type: Jira Software Cloud
- Email: your Jira account email
- API Token: the token from step 2
- Domain: `yourname.atlassian.net`

### Claude API (manual header)
- The Claude API key is passed as a header in the HTTP Request node
- Replace the `x-api-key` header value with your actual key
- Or create a custom "Header Auth" credential in n8n and reference it


## Testing the workflow

### Test 1: Real ticket
Post in #infra-issues:
> Tim Jones cannot log into the BAT GIS Server. Tried 3 times, keeps timing out.

Expected: Jira ticket created, Slack threaded reply with ticket link.

### Test 2: Non-ticket (should be ignored)
Post in #infra-issues:
> Hey does anyone know the wifi password?

Expected: No Jira ticket. Workflow stops at "Is Ticket?" node.

### Test 3: Bot message (should be filtered)
The bot's own reply should NOT trigger a new ticket.
Expected: Workflow stops at "Filter Bot Messages" node.

### Test 4: Different severity levels
Post:
> Production GIS Portal is completely down. All users affected. Getting 500 errors.

Expected: Priority = Highest (Critical), Component = Production GIS Portal.

Post:
> The staging map is loading a bit slowly today but still works.

Expected: Priority = Medium, Category = Performance.


## Custom fields — Jira API note

Jira's free tier custom fields require the field ID (not the name)
in API calls. After creating your custom fields:

1. Go to: https://yourname.atlassian.net/rest/api/3/field
2. Find your custom fields in the list (e.g., "customfield_10100")
3. Update the Jira Create Issue node to include them:

In the node's "Additional Fields" → "Custom Fields", add:
- customfield_XXXXX (Reported By) = {{ $json.reporter }}
- customfield_XXXXX (Environment) = {{ $json.environment }}  
- customfield_XXXXX (Slack Thread) = {{ $json.slack_permalink }}

Replace XXXXX with your actual field IDs.

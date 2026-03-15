# Slack Confirmation Reply — Block Kit Payload

## n8n Slack Node Configuration

**Node type:** Slack → Post Message
**Channel:** Same channel as the trigger (use expression: `{{ $('Slack Trigger').item.json.channel }}`)
**Thread TS:** `{{ $('Slack Trigger').item.json.ts }}` (posts as threaded reply)
**Block Kit JSON** (paste into the "Blocks" field):

```json
[
  {
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": ":white_check_mark: *Ticket created*"
    }
  },
  {
    "type": "section",
    "fields": [
      {
        "type": "mrkdwn",
        "text": "*Ticket:*\n<{{ $json.jira_url }}|{{ $json.ticket_key }}>"
      },
      {
        "type": "mrkdwn",
        "text": "*Priority:*\n{{ $json.priority }}"
      },
      {
        "type": "mrkdwn",
        "text": "*System:*\n{{ $json.affected_system }}"
      },
      {
        "type": "mrkdwn",
        "text": "*Environment:*\n{{ $json.environment }}"
      },
      {
        "type": "mrkdwn",
        "text": "*Category:*\n{{ $json.symptom_category }}"
      },
      {
        "type": "mrkdwn",
        "text": "*Reporter:*\n{{ $json.reporter }}"
      }
    ]
  },
  {
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": "*Summary:* {{ $json.summary }}"
    }
  },
  {
    "type": "context",
    "elements": [
      {
        "type": "mrkdwn",
        "text": "Something wrong? React with :x: to flag for review."
      }
    ]
  }
]
```

## Priority Color Mapping (for the left border accent)

Slack Block Kit doesn't natively support colored left borders
in the "blocks" format. If you want the colored accent bar,
use an "attachment" alongside the blocks:

```json
{
  "channel": "{{ $('Slack Trigger').item.json.channel }}",
  "thread_ts": "{{ $('Slack Trigger').item.json.ts }}",
  "attachments": [
    {
      "color": "{{ $json.priority === 'Highest' ? '#E24B4A' : $json.priority === 'High' ? '#EF9F27' : $json.priority === 'Medium' ? '#378ADD' : '#888780' }}",
      "blocks": [
        // ... same blocks array from above
      ]
    }
  ]
}
```

Color mapping:
- Highest (Critical) → #E24B4A (red)
- High               → #EF9F27 (amber)
- Medium             → #378ADD (blue)
- Low                → #888780 (gray)


## n8n Expression Reference

These expressions pull data from earlier nodes in the workflow.
Adjust node names to match your actual n8n workflow.

| Value                | n8n Expression                                                    |
|----------------------|-------------------------------------------------------------------|
| Slack channel        | `{{ $('Slack Trigger').item.json.channel }}`                      |
| Thread timestamp     | `{{ $('Slack Trigger').item.json.ts }}`                           |
| Ticket key           | `{{ $('Jira Create Issue').item.json.key }}`                      |
| Jira ticket URL      | `https://your-domain.atlassian.net/browse/{{ $('Jira Create Issue').item.json.key }}` |
| Summary              | `{{ $('JSON Parse').item.json.summary }}`                         |
| Priority             | `{{ $('Priority Map').item.json.priority }}`                      |
| Affected system      | `{{ $('JSON Parse').item.json.affected_system }}`                 |
| Environment          | `{{ $('JSON Parse').item.json.environment }}`                     |
| Symptom category     | `{{ $('JSON Parse').item.json.symptom_category }}`                |
| Reporter             | `{{ $('JSON Parse').item.json.reporter }}`                        |


## The ":x: flag for review" Pattern

This is an optional but powerful addition. If a developer
reacts to the bot's reply with an :x: emoji, you can set up
a second Slack trigger that:

1. Catches the reaction event
2. Adds a "needs-review" label to the Jira ticket
3. Posts in a #ticket-review channel for a human to check

This gives developers a one-click way to say "the bot got
this wrong" without leaving Slack. In your Loom demo, this
is the moment where you say: "I built in a human-in-the-loop
feedback mechanism so the system self-corrects over time."

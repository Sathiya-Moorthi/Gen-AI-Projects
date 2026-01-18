# n8n Automation

[![n8n](https://img.shields.io/badge/n8n-Workflow%20Automation-orange.svg)](https://n8n.io/)

Workflows and scripts for [n8n](https://n8n.io/) - a fair-code licensed workflow automation tool.

## Project Structure

```
n8n automation/
├── workflows/              # JSON workflow definitions
│   ├── Design Request Automation.json
│   ├── Design Request Automation_AI.json
│   ├── Design Request Automation_slack.json
│   ├── Design Request Automation_telegram.json
│   ├── Support Request Notifications.json
│   ├── UI_Automation.json
│   ├── data_flow_workflow.json
│   ├── learning_*.json     # Tutorial workflows
│   └── my_first_*.json     # Starter workflows
├── Projects/               # Complex project implementations
├── output files/           # Data outputs and logs
├── .gitignore
└── README.md
```

## Workflow Catalog

| Workflow | Description | Integrations |
|----------|-------------|--------------|
| **Design Request Automation** | Automates design request processing | Forms, Email |
| **Design Request Automation_AI** | AI-enhanced design requests | OpenAI, Forms |
| **Design Request Automation_slack** | Design requests via Slack | Slack, Forms |
| **Design Request Automation_telegram** | Design requests via Telegram | Telegram, Forms |
| **Support Request Notifications** | Customer support ticket routing | Email, Webhooks |
| **UI_Automation** | UI testing automation workflows | HTTP, Code |
| **data_flow_workflow** | Data transformation pipeline | HTTP, Code |

### Learning Workflows

| Workflow | Concepts Covered |
|----------|-----------------|
| `learning_code_node.json` | JavaScript/Python code execution |
| `learning_HTTP_node.json` | HTTP requests and APIs |
| `learning_trigger_nodes.json` | Workflow triggers |
| `learning_webhook_node.json` | Webhook integrations |
| `my_first_workflow.json` | Basic workflow structure |
| `my_first_scheduled_workflow.json` | Cron-based scheduling |

## Prerequisites

- n8n instance (self-hosted or cloud)
- Access to integrated services (Slack, Telegram, etc.)

## Installation

### Importing Workflows

1. Open your n8n instance
2. Go to **Workflows** > **Import from File**
3. Select a `.json` file from the `workflows/` directory
4. Configure credentials for integrated services

### Step-by-Step Import

```
1. Navigate to: Settings > Workflow > Import
2. Click "Select File" or drag and drop
3. Review imported nodes
4. Update credentials placeholders
5. Activate the workflow
```

## Credentials Configuration

Create credentials in n8n for the following services (as needed):

| Service | Required Credentials |
|---------|---------------------|
| Slack | Bot Token, Signing Secret |
| Telegram | Bot Token |
| OpenAI | API Key |
| Email | SMTP settings or OAuth |

### credentials.json.example

```json
{
  "slack": {
    "botToken": "xoxb-your-token",
    "signingSecret": "your-signing-secret"
  },
  "telegram": {
    "botToken": "your-bot-token"
  },
  "openai": {
    "apiKey": "sk-your-api-key"
  }
}
```

## Usage

1. Import the desired workflow
2. Configure credentials for all nodes
3. Test with sample data using "Execute Workflow"
4. Activate for production use

## Best Practices

- Test workflows in a staging environment first
- Use environment variables for sensitive data
- Set up error handling nodes
- Monitor execution logs regularly

## License

This project is part of [Gen-AI-Projects](../README.md) and is licensed under the MIT License.

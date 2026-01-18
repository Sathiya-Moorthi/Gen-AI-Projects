# Prompt Engineering

[![Prompts](https://img.shields.io/badge/Prompts-Collection-orange.svg)]()
[![LLM](https://img.shields.io/badge/LLM-Compatible-blue.svg)]()

A curated collection of prompts for various LLMs and use cases, including role-based prompts, structured output templates, and RAG-specific prompts.

## Project Structure

```
Prompt Engineering/
├── JSON Prompting/                # Templates for structured JSON outputs
├── Prompt Battle/                 # Comparative prompts for model testing
├── Corrective RAG Prompts/        # Prompts for handling retrieval failures
├── RTCFR Prompting/               # RTCFR methodology prompts
├── n8n workflow building prompts/ # Prompts for n8n automation
├── *.txt                          # Role-based prompt files
├── *.json                         # Structured prompt templates
└── README.md
```

## Prompt Categories

| Category | Description | Files |
|----------|-------------|-------|
| **JSON Prompting** | Templates for structured JSON outputs | `UNIVERSAL JSON PROMPT TEMPLATE.json` |
| **Prompt Battle** | Comparative prompts for testing models | Various comparison prompts |
| **Role-Based** | Prompts for specific professional roles | `Python developer*.txt`, `Data Engineer*.txt` |
| **Corrective RAG** | Handling retrieval failures gracefully | `Fallback RAG Prompt.txt` |
| **n8n Workflows** | Prompts for building n8n automations | Workflow-specific prompts |

## Role-Based Prompts

| Prompt | Description |
|--------|-------------|
| `Prompt Engineer Prompt.txt` | System prompt for prompt engineering tasks |
| `Python and Data Engineer Prompt.txt` | Combined Python and data engineering role |
| `Python developer specializing in Streamlit Prompt.txt` | Streamlit-focused development |

## JSON Templates

| Template | Use Case |
|----------|----------|
| `UNIVERSAL JSON PROMPT TEMPLATE.json` | Generic structured output template |
| `System_Prompt_for_Senior_Prompt_Engineer.json` | Advanced prompt engineering role |

## Usage

### Using a Role Prompt
1. Open the desired `.txt` file
2. Copy the contents
3. Use as a system prompt in your LLM application

### Using JSON Templates
1. Open the `.json` template
2. Customize the structure for your use case
3. Include in your prompt engineering workflow

### Example Integration
```python
with open("Prompt Engineer Prompt.txt", "r") as f:
    system_prompt = f.read()

response = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Your query here"}
    ]
)
```

## Best Practices

1. **Be Specific**: Clear instructions yield better results
2. **Use Examples**: Few-shot prompting improves consistency
3. **Structure Output**: JSON templates ensure parseable responses
4. **Test Iteratively**: Compare results across different prompts
5. **Version Control**: Track prompt changes over time

## License

This project is part of [Gen-AI-Projects](../README.md) and is licensed under the MIT License.

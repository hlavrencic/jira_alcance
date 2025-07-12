# Copilot Instructions

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Context

This is a Python script project for automating Jira sprint data extraction. The main purpose is to:

1. Connect to Jira using API credentials
2. Extract active sprint information from specific projects
3. Gather task details including timetracking information
4. Generate reports in Excel/CSV format

## Key Requirements

- Focus on timetracking data: time spent, original estimate, remaining time
- Handle subtasks and parent-child relationships
- Support multiple sprint extraction
- Generate user-friendly reports
- Error handling for API connections and data processing

## Code Style

- Use Python best practices with proper error handling
- Include comprehensive documentation
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Include logging for debugging and monitoring

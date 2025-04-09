# MCP GitHub Repository Analyzer

A Python-based Model Context Protocol system that bridges AI language models with external content from GitHub repositories and websites. This tool leverages both MCP architecture and OpenAI's powerful language models to provide intelligent code analysis.

With this tool, users can:

- Enter any GitHub repository URL for automatic analysis
- Get comprehensive summaries of codebases and their structure
- Ask specific questions about the repository's code and documentation
- Generate sample code snippets for new features compatible with the existing codebase
- Receive intelligent responses based on the actual repository content combined with OpenAI's language understanding

The system retrieves, processes, and indexes repository content through MCP, then uses OpenAI's intelligent LLM capabilities to generate human-like responses that accurately reflect the specific context of the loaded repository. This creates a personalized AI assistant that understands the unique aspects of any codebase you're working with.
## SETUP AND INSTALLATION

- This will create a Conda environment in a folder named `venv` inside your current directory.

```
conda create -p ./venv python=3.11 -y
```

- If you created it with a path `(-p)`, activate it like this:

```
conda activate ./venv
```

- If you created it using a name, like this:

```
conda create -n taskmanager-env python=3.11 -y
```

- Then activate it with:

```
conda activate taskmanager-env
```

#### IMPORTANT: RUN THIS BEFORE `flask run`

```
pip install -r requirements.txt
```

- 📌 Notes:
- `-p ./venv` creates an `environment` at a `specific path`, `rather than by name.`

- If you use `-n env_name`, `Conda manages` it in its `own envs directory`.

## RUNNING FLASK

- ensure you have this on the headers `from mcp_core import MCPSystem`

```bash
export FLASK_APP=app.py
flask run
```

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

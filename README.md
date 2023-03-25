# DBLP Mining

## Usage

Setup the environment.

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Exact the important information

```bash
python src/parser.py <start> <end>
```

Mine with the FP-tree

```bash
python src/summarize.py
```
# Lab 4: Working with Data in Python

## Duration and alignment

**Duration:** 2 hours  
**Theory alignment:** Chapter 6, Working with Data in Python

You will parse equivalent device inventories from CSV, JSON, YAML, and XML, normalize them, validate them, and confirm equivalence with unit tests. XML is parsed with `xmltodict`.

## Objectives

- Read files with context managers and UTF-8 encoding.
- Parse CSV, JSON, YAML, and XML.
- Use `yaml.safe_load` and `xmltodict.parse`.
- Convert CSV/XML Boolean text explicitly.
- Validate required fields, IP addresses, and duplicates.
- Handle expected errors and run unit tests.
- Publish the project through GitHub.

## Part 1: Prepare and compare data

```bash
mkdir -p ~/devnet-associate/labs
cp -R "/path/to/Lab 04 - Working with Data in Python" ~/devnet-associate/labs/lab04
cd ~/devnet-associate/labs/lab04
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
printf '%s\n' '.venv/' '__pycache__/' '*.py[cod]' 'output/' > .gitignore
git init
git branch -M main
code .
```

Inspect the four files:

```bash
head data/devices.csv
python -m json.tool data/devices.json
head -30 data/devices.yaml
head -40 data/devices.xml
```

CSV fields are text. JSON and YAML provide native Booleans. XML elements also produce text and require conversion. `xmltodict` maps common XML trees into dictionaries and lists.

## Part 2: Implement format parsers

In `data_pipeline.py`, implement the Boolean converter:

```python
def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"Invalid Boolean value: {value!r}")
```

Implement CSV, JSON, and YAML:

```python
def parse_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        records = []
        for row in csv.DictReader(stream):
            row["enabled"] = parse_bool(row["enabled"])
            records.append(row)
    return records


def parse_json(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as stream:
        document = json.load(stream)
    return document["devices"]


def parse_yaml(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as stream:
        document = yaml.safe_load(stream)
    return document["devices"]
```

Implement XML with `xmltodict`:

```python
def required_xml_text(record: dict, name: str) -> str:
    value = record.get(name)
    if not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"XML device requires {name}")
    return value.strip()


def parse_xml(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as stream:
        document = xmltodict.parse(stream.read(), force_list=("device",))
    devices = document["inventory"]["device"]
    return [
        {
            "name": required_xml_text(device, "name"),
            "management_ip": required_xml_text(device, "management_ip"),
            "role": required_xml_text(device, "role"),
            "platform": required_xml_text(device, "platform"),
            "enabled": parse_bool(required_xml_text(device, "enabled")),
            "site": required_xml_text(device, "site"),
        }
        for device in devices
    ]
```

Run parser tests:

```bash
python -m unittest -v \
  tests.test_data_pipeline.CsvTests \
  tests.test_data_pipeline.JsonTests \
  tests.test_data_pipeline.YamlTests \
  tests.test_data_pipeline.XmlTests
```

## Part 3: Validate and normalize

Implement:

```python
def require_text(value: object, field: str) -> str:
    if not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"{field} must be nonempty text")
    return value.strip()


def normalize_device(record: dict) -> dict:
    missing = REQUIRED_FIELDS - record.keys()
    unknown = record.keys() - REQUIRED_FIELDS
    if missing or unknown:
        raise ValueError(f"Invalid fields; missing={missing}, unknown={unknown}")
    if not isinstance(record["enabled"], bool):
        raise ValueError("enabled must be a Boolean")
    return {
        "name": require_text(record["name"], "name").lower(),
        "management_ip": str(ipaddress.ip_address(record["management_ip"])),
        "role": require_text(record["role"], "role").lower(),
        "platform": require_text(record["platform"], "platform").lower(),
        "enabled": record["enabled"],
        "site": require_text(record["site"], "site").lower(),
    }


def validate_devices(records: list[dict]) -> list[dict]:
    normalized = [normalize_device(record) for record in records]
    names = [device["name"] for device in normalized]
    addresses = [device["management_ip"] for device in normalized]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate device name")
    if len(addresses) != len(set(addresses)):
        raise ValueError("Duplicate management IP")
    return normalized
```

Configure and use the parser map:

```python
PARSERS = {
    ".csv": parse_csv,
    ".json": parse_json,
    ".yaml": parse_yaml,
    ".yml": parse_yaml,
    ".xml": parse_xml,
}


def load_devices(path: Path) -> list[dict]:
    parser = PARSERS.get(path.suffix.lower())
    if parser is None:
        raise ValueError(f"Unsupported data format: {path.suffix}")
    return validate_devices(parser(path))
```

Run:

```bash
python -m unittest discover -v
```

## Part 4: Complete output and validate

Implement `write_json()`:

```python
def write_json(path: Path, devices: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        json.dump({"devices": devices}, stream, indent=2, sort_keys=True)
        stream.write("\n")
```

The unit tests validate parsing, normalization, equivalence, failures, and JSON output. The CLI `main()` is optional if class time remains.

```bash
python -m unittest discover -v
python -m py_compile data_pipeline.py
```

Commit and publish:

```bash
git add .gitignore Lab4.md requirements.txt data data_pipeline.py tests observations.md
git diff --staged
git commit -m "Implement multi-format device data pipeline"
gh repo create devnet-associate-lab04 --private --source=. --remote=origin --push
git status
```

## Completion criteria

- CSV, JSON, YAML, and XML parsers pass their tests.
- XML uses `xmltodict` with `force_list`.
- Records are normalized and duplicates rejected.
- All formats produce equivalent validated data.
- JSON output test passes.
- The private GitHub repository contains no environment or cache files.


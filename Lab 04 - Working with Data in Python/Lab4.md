# Lab 4: Working with Data in Python

## Alignment with Chapter 6

This lab applies Chapter 6, **Working with Data in Python**. You will read equivalent network inventory data from CSV, JSON, YAML, and XML; normalize each format into a common Python structure; validate the records; handle expected errors; serialize results; and build unit tests with `unittest`.

## Estimated time

4 to 5 hours.

## Learning objectives

After completing this lab, you should be able to:

- Open text files safely with context managers and explicit encodings.
- Parse CSV, JSON, YAML, and XML using appropriate Python libraries.
- Explain how each format represents records, types, nesting, and metadata.
- Normalize different source formats into a consistent Python data structure.
- Validate required fields, values, IP addresses, and duplicate records.
- Use `try`, `except`, `else`, and `finally` appropriately.
- Serialize validated data to JSON safely.
- Apply the Red-Green-Refactor TDD cycle.
- Build unit tests for normal, boundary, and failure behavior.
- Keep parsing, validation, and output responsibilities separate.
- Submit the completed data pipeline through a private GitHub pull request.

## Project structure

```text
lab04/
├── Lab4.md
├── data_pipeline.py
├── requirements.txt
├── data/
│   ├── devices.csv
│   ├── devices.json
│   ├── devices.yaml
│   └── devices.xml
└── tests/
    ├── __init__.py
    └── test_data_pipeline.py
```

The four data files describe the same three devices. Their syntax differs, but the normalized Python result should be equivalent.

---

## Part 1: Prepare the project

```bash
mkdir -p ~/devnet-associate/labs
cp -R "/path/to/Lab 04 - Working with Data in Python" ~/devnet-associate/labs/lab04
cd ~/devnet-associate/labs/lab04
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Initialize Git and open VS Code:

```bash
printf '%s\n' '.venv/' '__pycache__/' '*.py[cod]' 'output/' > .gitignore
git init
git branch -M main
git add .gitignore Lab4.md requirements.txt data_pipeline.py data tests
git commit -m "Create Lab 4 structured-data pipeline"
code .
```

Select the `.venv` interpreter.

Run the starter tests:

```bash
python -m unittest discover -v
```

Failures are expected because the parser and validation functions contain placeholders.

---

## Part 2: Compare the supplied data formats

Inspect the files:

```bash
sed -n '1,20p' data/devices.csv
python -m json.tool data/devices.json
sed -n '1,40p' data/devices.yaml
sed -n '1,80p' data/devices.xml
```

Complete this comparison in `observations.md`:

| Characteristic | CSV | JSON | YAML | XML |
|---|---|---|---|---|
| Natural top-level structure | | | | |
| Native Boolean representation | | | | |
| Supports nested structures well | | | | |
| Common automation use | | | | |
| Important parser concern | | | | |

Consider these differences:

- CSV fields arrive as text and require explicit conversion.
- JSON distinguishes strings, numbers, Booleans, arrays, objects, and `null`.
- YAML is readable for configuration but whitespace and implicit types require care. Use `yaml.safe_load`, not an unsafe object constructor.
- XML represents a tree of elements, attributes, text, and namespaces. In this lab, `xmltodict` converts that tree into nested Python dictionaries and lists. Applications must still decide how the resulting structure maps to domain objects.

---

## Part 3: Implement CSV parsing

Open `data_pipeline.py` and implement `parse_csv()`:

```python
def parse_csv(path: Path) -> list[dict]:
    """Parse CSV device rows and convert explicit field types."""
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        records = []
        for row in reader:
            records.append(
                {
                    "name": row["name"],
                    "management_ip": row["management_ip"],
                    "role": row["role"],
                    "platform": row["platform"],
                    "enabled": parse_bool(row["enabled"]),
                    "site": row["site"],
                }
            )
    return records
```

Implement the Boolean converter:

```python
def parse_bool(value: str) -> bool:
    """Convert accepted Boolean text or raise ValueError."""
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"Invalid Boolean value: {value!r}")
```

Run the focused tests:

```bash
python -m unittest -v tests.test_data_pipeline.CsvTests
```

`csv.DictReader` uses the header row as dictionary keys. It does not infer Boolean, integer, IP-address, or other domain types.

---

## Part 4: Implement JSON parsing

Implement:

```python
def parse_json(path: Path) -> list[dict]:
    """Parse a JSON object containing a devices array."""
    with path.open(encoding="utf-8") as stream:
        document = json.load(stream)
    if not isinstance(document, dict) or not isinstance(document.get("devices"), list):
        raise ValueError("JSON document requires a devices list")
    return document["devices"]
```

Run:

```bash
python -m unittest -v tests.test_data_pipeline.JsonTests
```

Compare `json.load(stream)` with `json.loads(text)`: the first reads from a file-like object; the second parses an existing string.

Experiment without changing the source file:

```bash
python - <<'PY'
import json
from pathlib import Path

path = Path("data/devices.json")
document = json.loads(path.read_text(encoding="utf-8"))
print(type(document))
print(type(document["devices"]))
print(type(document["devices"][0]["enabled"]))
PY
```

---

## Part 5: Implement safe YAML parsing

Implement:

```python
def parse_yaml(path: Path) -> list[dict]:
    """Safely parse a YAML object containing a devices list."""
    with path.open(encoding="utf-8") as stream:
        document = yaml.safe_load(stream)
    if not isinstance(document, dict) or not isinstance(document.get("devices"), list):
        raise ValueError("YAML document requires a devices list")
    return document["devices"]
```

Run:

```bash
python -m unittest -v tests.test_data_pipeline.YamlTests
```

YAML can construct complex Python objects when unsafe loaders are used. Configuration supplied by users or external systems must be parsed with `safe_load` unless there is a reviewed, specific reason otherwise.

---

## Part 6: Implement XML parsing

The third-party `xmltodict` library makes common XML structures feel similar to parsed JSON. It represents attributes with keys beginning with `@` and mixed element text with `#text`. Repeated elements normally become lists, while a single occurrence may become one dictionary unless `force_list` is used.

Confirm that the library was installed from `requirements.txt`:

```bash
python -m pip show xmltodict
```

Implement:

```python
def parse_xml(path: Path) -> list[dict]:
    """Parse XML with xmltodict and return device dictionaries."""
    with path.open(encoding="utf-8") as stream:
        document = xmltodict.parse(
            stream.read(),
            force_list=("device",),
        )

    inventory = document.get("inventory")
    if not isinstance(inventory, dict):
        raise ValueError("XML document requires an inventory root")

    devices = inventory.get("device")
    if not isinstance(devices, list):
        raise ValueError("XML inventory requires device elements")

    records = []
    for device in devices:
        if not isinstance(device, dict):
            raise ValueError("Each XML device must be an element mapping")
        record = {
            "name": required_xml_text(device, "name"),
            "management_ip": required_xml_text(device, "management_ip"),
            "role": required_xml_text(device, "role"),
            "platform": required_xml_text(device, "platform"),
            "enabled": parse_bool(required_xml_text(device, "enabled")),
            "site": required_xml_text(device, "site"),
        }
        records.append(record)
    return records
```

Implement the helper:

```python
def required_xml_text(record: dict, name: str) -> str:
    """Return a required nonempty scalar from an xmltodict mapping."""
    value = record.get(name)
    if not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"XML device requires {name}")
    return value.strip()
```

Run:

```bash
python -m unittest -v tests.test_data_pipeline.XmlTests
```

`force_list=("device",)` makes collection handling consistent whether the XML contains one device or many. Without it, one `<device>` may become a dictionary while repeated `<device>` elements become a list.

The current `xmltodict.parse()` API disables entity parsing by default. Keep that secure default. XML namespaces, attributes, mixed content, and exact round-trip fidelity still require explicit design; `xmltodict` targets common XML-to-dictionary use cases rather than preserving every XML nuance.

---

## Part 7: Normalize and validate records

Parsing syntax is not the same as validating meaning. Implement `normalize_device()`:

```python
REQUIRED_FIELDS = {
    "name",
    "management_ip",
    "role",
    "platform",
    "enabled",
    "site",
}


def normalize_device(record: dict) -> dict:
    """Validate and normalize one parsed device record."""
    if not isinstance(record, dict):
        raise ValueError("Each device must be an object")

    missing = REQUIRED_FIELDS - record.keys()
    unknown = record.keys() - REQUIRED_FIELDS
    if missing:
        raise ValueError(f"Missing fields: {', '.join(sorted(missing))}")
    if unknown:
        raise ValueError(f"Unknown fields: {', '.join(sorted(unknown))}")

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
```

Implement:

```python
def require_text(value: object, field: str) -> str:
    if not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"{field} must be nonempty text")
    return value.strip()
```

Implement collection validation:

```python
def validate_devices(records: list[dict]) -> list[dict]:
    """Normalize devices and reject duplicate names and addresses."""
    if not isinstance(records, list):
        raise ValueError("Device collection must be a list")

    normalized = []
    names = set()
    addresses = set()

    for record in records:
        device = normalize_device(record)
        if device["name"] in names:
            raise ValueError(f"Duplicate device name: {device['name']}")
        if device["management_ip"] in addresses:
            raise ValueError(
                f"Duplicate management IP: {device['management_ip']}"
            )
        names.add(device["name"])
        addresses.add(device["management_ip"])
        normalized.append(device)

    return normalized
```

Run validation tests:

```bash
python -m unittest -v tests.test_data_pipeline.ValidationTests
```

---

## Part 8: Build a format-independent pipeline

Implement parser selection:

```python
PARSERS = {
    ".csv": parse_csv,
    ".json": parse_json,
    ".yaml": parse_yaml,
    ".yml": parse_yaml,
    ".xml": parse_xml,
}


def load_devices(path: Path) -> list[dict]:
    """Parse and validate devices according to the file suffix."""
    parser = PARSERS.get(path.suffix.lower())
    if parser is None:
        raise ValueError(f"Unsupported data format: {path.suffix}")
    return validate_devices(parser(path))
```

Implement safe JSON output:

```python
def write_json(path: Path, devices: list[dict]) -> None:
    """Write validated devices as readable UTF-8 JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    document = {"devices": devices}
    with path.open("w", encoding="utf-8") as stream:
        json.dump(document, stream, indent=2, sort_keys=True)
        stream.write("\n")
```

Complete the CLI `main()` according to the comments in `data_pipeline.py`. It must:

1. Accept one input path and an optional `--output` path.
2. Call `load_devices()`.
3. Print each device and a summary.
4. Write JSON only when `--output` is provided.
5. Catch expected file, parsing, and validation errors at the program boundary.
6. Return `0` for success and `1` for an expected failure.

Test all inputs:

```bash
python data_pipeline.py data/devices.csv
python data_pipeline.py data/devices.json
python data_pipeline.py data/devices.yaml
python data_pipeline.py data/devices.xml
python data_pipeline.py data/devices.yaml --output output/devices-normalized.json
python -m json.tool output/devices-normalized.json
```

Compare the normalized results programmatically:

```bash
python - <<'PY'
from pathlib import Path
from data_pipeline import load_devices

paths = [
    Path("data/devices.csv"),
    Path("data/devices.json"),
    Path("data/devices.yaml"),
    Path("data/devices.xml"),
]
results = [load_devices(path) for path in paths]
print("All formats equivalent:", all(result == results[0] for result in results[1:]))
PY
```

The result should be `True`.

---

## Part 9: Practice exception handling

Create temporary invalid files under the ignored `output/` directory:

```bash
mkdir -p output
printf '{not valid json}\n' > output/broken.json
printf 'name,management_ip\nr1,999.1.1.1\n' > output/incomplete.csv
```

Run:

```bash
python data_pipeline.py output/broken.json
echo $?
python data_pipeline.py output/incomplete.csv
echo $?
python data_pipeline.py output/missing.yaml
echo $?
```

The CLI should print a concise error and return status `1`, not expose an unhandled traceback for an expected input failure.

Use exception blocks narrowly:

- `try` only the operation expected to fail.
- Catch specific exceptions rather than `except Exception` without justification.
- Use `else` for work that should occur only after success.
- Use `finally` for mandatory cleanup; context managers already close these files.
- Do not hide programmer defects by converting every exception into a generic message.

Record the exception class produced by malformed JSON, malformed YAML, a missing file, invalid XML, and an invalid IP address.

---

## Part 10: Apply TDD and expand the tests

Add a requirement: device names may contain lowercase letters, digits, hyphens, and underscores only.

### Red

Add this test to `ValidationTests` before changing production code:

```python
def test_rejects_invalid_device_name(self):
    record = self.valid_record | {"name": "Edge Router 1!"}
    with self.assertRaisesRegex(ValueError, "Invalid device name"):
        normalize_device(record)
```

Run it and confirm it fails for the expected reason:

```bash
python -m unittest -v \
  tests.test_data_pipeline.ValidationTests.test_rejects_invalid_device_name
```

### Green

Import `re` and add the smallest validation:

```python
name = require_text(record["name"], "name").lower()
if re.fullmatch(r"[a-z0-9_-]+", name) is None:
    raise ValueError(f"Invalid device name: {name}")
```

Use `name` in the returned dictionary. Run the focused test again.

### Refactor

Run the complete suite and remove duplication without changing behavior:

```bash
python -m unittest discover -v
```

Add at least two more tests:

- A boundary test for an empty device list.
- A failure test for duplicate management addresses or an unsupported suffix.

Tests should use temporary directories or in-memory values. They should not depend on a live API, current time, or a learner's home-directory layout.

---

## Part 11: Publish through GitHub review

Run final checks:

```bash
python -m unittest discover -v
python -m py_compile data_pipeline.py
git status
git diff
```

Create the private repository if needed:

```bash
gh repo create devnet-associate-lab04 --private --source=. --remote=origin --push
```

Create a feature branch and commit:

```bash
git switch -c feature/structured-data-pipeline
git add data_pipeline.py data tests Lab4.md requirements.txt observations.md .gitignore
git diff --staged
git commit -m "Implement validated multi-format data pipeline"
git push -u origin feature/structured-data-pipeline
```

Open a pull request:

```bash
gh pr create \
  --base main \
  --head feature/structured-data-pipeline \
  --title "Implement Lab 4 structured-data pipeline" \
  --body "Parses CSV, JSON, YAML, and XML; validates normalized records; writes JSON; and includes unit tests."
```

Review:

- Parser safety and explicit encoding.
- Type conversion and validation boundaries.
- Duplicate detection.
- Specific exception handling.
- Output paths and avoidance of credentials.
- Tests for success, boundary, and failure behavior.

Merge the pull request and synchronize local `main`.

## Completion criteria

- All four input files parse into equivalent normalized records.
- CSV Boolean text is converted explicitly.
- YAML uses `safe_load`.
- XML required elements are validated.
- Unknown, missing, malformed, invalid, and duplicate data is rejected clearly.
- JSON output is readable, deterministic, and newline terminated.
- The learner adds and passes the TDD name-validation test plus two additional tests.
- `python -m unittest discover -v` passes.
- The private GitHub pull request is reviewed and merged.

## Further references

- [Python input and output](https://docs.python.org/3/tutorial/inputoutput.html)
- [Python CSV](https://docs.python.org/3/library/csv.html)
- [Python JSON](https://docs.python.org/3/library/json.html)
- [`xmltodict` documentation](https://pypi.org/project/xmltodict/)
- [Python exceptions](https://docs.python.org/3/tutorial/errors.html)
- [Python unittest](https://docs.python.org/3/library/unittest.html)

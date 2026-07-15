# Lab 2: Introduction to Python for Network Automation

## Alignment with Chapter 4

This lab applies Chapter 4, **Introduction to Python**. You will use the Python interpreter and script files, work inside a virtual environment, select suitable data types, convert user input, and control program flow with conditions and loops. The final program produces a small network-device inventory report without connecting to a live device.

## Estimated time

3 to 4 hours.

## Learning objectives

After completing this lab, you should be able to:

- Run Python interactively and from a script.
- Activate a project-specific virtual environment.
- Use assignments, expressions, comments, and readable names.
- Work with numbers, Booleans, strings, lists, tuples, dictionaries, and sets.
- Explain the effect of mutable and immutable objects.
- Convert text input into validated numeric values.
- Use comparisons and Boolean operators.
- Control execution with `if`, `for`, `while`, `break`, and `continue`.
- Produce formatted output with f-strings.
- Recognize common beginner errors and avoid hard-coded credentials.
- Store the completed program in a private GitHub repository.

## Required resources

- The Ubuntu workstation prepared in Lab 1.
- Python 3, Git, GitHub CLI, and VS Code.
- The supplied `Lab 02 - Introduction to Python` folder.

---

## Part 1: Prepare the Python project

Copy the lab into your course workspace:

```bash
mkdir -p ~/devnet-associate/labs
cp -R "/path/to/Lab 02 - Introduction to Python" ~/devnet-associate/labs/lab02
cd ~/devnet-associate/labs/lab02
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python --version
python -m pip --version
```

This lab uses only the Python standard library, so no third-party package is required. Create `.gitignore` and initialize Git:

```bash
printf '%s\n' '.venv/' '__pycache__/' '*.py[cod]' > .gitignore
git init
git branch -M main
git add Lab2.md inventory_report_starter.py validate_lab2.py .gitignore
git commit -m "Create Lab 2 Python project"
```

Create your working file from the starter:

```bash
cp inventory_report_starter.py inventory_report.py
code .
```

In VS Code, select the interpreter inside `.venv`.

---

## Part 2: Use the interactive interpreter

Start Python:

```bash
python
```

At the `>>>` prompt, evaluate expressions:

```python
2 + 3
10 / 4
10 // 4
10 % 4
2 ** 8
```

Create objects and inspect their types:

```python
hostname = "edge-r1"
port = 443
enabled = True
latency_ms = 12.5
type(hostname)
type(port)
type(enabled)
type(latency_ms)
```

Use built-in help:

```python
help(str.lower)
```

Press `q` if help opens a pager. Exit the interpreter:

```python
exit()
```

Interactive mode is useful for small experiments. A script is preferable when work must be saved, reviewed, tested, and repeated.

---

## Part 3: Work with variables and core data types

Open `inventory_report.py`. Replace the first TODO block with these scalar values:

```python
course_name = "Cisco DevNet Associate"
site_name = "training-campus"
default_timeout = 5
maintenance_mode = False
packet_loss_percent = 0.0
```

Add a tuple for a fixed coordinate and a list of device dictionaries:

```python
site_coordinates = (21.0285, 105.8542)

devices = [
    {
        "name": "edge-r1",
        "role": "router",
        "management_ip": "192.0.2.10",
        "platform": "iosxe",
        "enabled": True,
        "latency_ms": 18.4,
        "tags": ["wan", "critical"],
    },
    {
        "name": "access-sw1",
        "role": "switch",
        "management_ip": "192.0.2.21",
        "platform": "iosxe",
        "enabled": True,
        "latency_ms": 4.8,
        "tags": ["campus", "access"],
    },
    {
        "name": "lab-fw1",
        "role": "firewall",
        "management_ip": "192.0.2.30",
        "platform": "ftd",
        "enabled": False,
        "latency_ms": None,
        "tags": ["security", "maintenance"],
    },
]
```

Explain why these structures fit the data:

- A string represents a name or label.
- An integer represents a whole-number timeout.
- A float represents measured latency.
- A Boolean represents an enabled/disabled decision.
- `None` represents an intentionally absent measurement.
- A tuple represents a coordinate pair that should not be changed in place.
- A list preserves an ordered, mutable collection of devices.
- Each dictionary maps field names to values for one device.

Print the object types temporarily:

```python
print(type(course_name))
print(type(site_coordinates))
print(type(devices))
print(type(devices[0]))
```

Run the script:

```bash
python inventory_report.py
```

Remove the temporary type prints after confirming the results.

---

## Part 4: Observe mutable and immutable behavior

Run this experiment in the interpreter:

```python
hostname = "edge-r1"
original_hostname = hostname
hostname = hostname.upper()
print(original_hostname, hostname)

tags = ["wan", "critical"]
same_tags = tags
same_tags.append("monitored")
print(tags)
print(tags is same_tags)
```

Strings are immutable: calling `upper()` produces a different string. Lists are mutable: both names refer to the same list, so an in-place append is visible through both.

Now compare a shallow copy:

```python
tags = ["wan", "critical"]
copied_tags = tags.copy()
copied_tags.append("monitored")
print(tags)
print(copied_tags)
print(tags == copied_tags)
print(tags is copied_tags)
```

`==` compares values; `is` compares object identity. Do not use `is` as a substitute for normal value comparison.

---

## Part 5: Build the inventory report with a `for` loop

Replace the report TODO with:

```python
print(f"\n{course_name} inventory")
print(f"Site: {site_name}")
print(f"Coordinates: {site_coordinates[0]}, {site_coordinates[1]}")
print("-" * 72)

enabled_count = 0
measured_latencies = []
roles = set()

for device in devices:
    roles.add(device["role"])

    if not device["enabled"]:
        state = "DISABLED"
        latency_text = "not measured"
    else:
        state = "ENABLED"
        enabled_count += 1

        if device["latency_ms"] is None:
            latency_text = "unknown"
        else:
            measured_latencies.append(device["latency_ms"])
            latency_text = f"{device['latency_ms']:.1f} ms"

    tag_text = ", ".join(device["tags"])
    print(
        f"{device['name']:<14} "
        f"{device['role']:<10} "
        f"{device['management_ip']:<15} "
        f"{state:<8} "
        f"{latency_text:<14} "
        f"[{tag_text}]"
    )
```

This loop demonstrates nested dictionary access, Boolean evaluation, an explicit `None` check, numeric formatting, string joining, and aligned f-string fields.

Add the summary:

```python
print("-" * 72)
print(f"Devices: {len(devices)}")
print(f"Enabled: {enabled_count}")
print(f"Roles: {', '.join(sorted(roles))}")

if measured_latencies:
    average_latency = sum(measured_latencies) / len(measured_latencies)
    print(f"Average measured latency: {average_latency:.1f} ms")
else:
    print("Average measured latency: unavailable")
```

Run and inspect the output:

```bash
python inventory_report.py
```

---

## Part 6: Validate user input with conversion and a `while` loop

Automation cannot trust external text. Add this prompt near the beginning of the report code:

```python
while True:
    raw_threshold = input("Latency warning threshold in ms [20]: ").strip()

    if raw_threshold == "":
        warning_threshold = 20.0
        break

    try:
        warning_threshold = float(raw_threshold)
    except ValueError:
        print("Enter a number, such as 20 or 12.5.")
        continue

    if warning_threshold <= 0:
        print("The threshold must be greater than zero.")
        continue

    break
```

Although detailed exception handling is covered later, this small `try`/`except` block is required because `float()` rejects nonnumeric text. The `while` loop continues until input is valid; `continue` starts the next attempt and `break` leaves the loop.

Inside the enabled-device branch, after a real latency is appended, add:

```python
if device["latency_ms"] > warning_threshold:
    latency_text += " WARNING"
```

Test these inputs in separate runs:

- Press `Enter` for the default.
- Enter `10` so `edge-r1` receives a warning.
- Enter `abc`, then a valid value.
- Enter `0`, then a valid value.

---

## Part 7: Use `range`, `break`, and `continue`

Add a retry simulation after the report:

```python
print("\nConnection-attempt simulation")

for attempt in range(1, 4):
    if maintenance_mode:
        print("Maintenance mode is active; skipping connection attempts.")
        break

    print(f"Attempt {attempt} of 3")

    if attempt < 3:
        print("  Simulated timeout; retrying.")
        continue

    print("  Simulated connection succeeded.")
```

`range(1, 4)` produces `1`, `2`, and `3`; the stop value is excluded. Change `maintenance_mode` to `True`, rerun the program, and explain why the loop ends immediately. Restore it to `False`.

---

## Part 8: Explore common errors safely

Run each example in the interpreter and interpret the error before correcting it.

### Mixing text and numbers

```python
port_text = "443"
# port_text + 1             # TypeError
port = int(port_text)
print(port + 1)
```

### Assignment versus comparison

```python
enabled = True
print(enabled == True)
```

Prefer `if enabled:` rather than `if enabled == True:` for a real Boolean. A single `=` assigns; `==` compares.

### Off-by-one behavior

```python
names = ["r1", "r2", "r3"]
print(names[0])
print(names[-1])
print(names[0:2])
```

Indexes begin at zero, and the stop index in a slice is excluded.

### Shadowing a built-in

```python
list = [1, 2, 3]
# list("abc")               # now fails because list refers to the variable
del list
print(list("abc"))
```

Avoid variable names such as `list`, `str`, `set`, `input`, or `id` when they hide useful built-ins.

### Hard-coded credentials

Do not add a password, token, or API key to the program. Later labs will retrieve secrets from protected external sources. A private GitHub repository is not an acceptable secret store.

---

## Part 9: Validate, review, and publish

Run the supplied validation program:

```bash
python validate_lab2.py
```

The validator runs `inventory_report.py` with controlled input and checks important output. If it fails, read the reported missing behavior and correct the learner program.

Review the code and Git diff:

```bash
python -m py_compile inventory_report.py
git status
git diff
```

Commit the completed work:

```bash
git add inventory_report.py Lab2.md
git diff --staged
git commit -m "Build Python device inventory report"
```

Create and push a private GitHub repository:

```bash
gh repo create devnet-associate-lab02 --private --source=. --remote=origin --push
gh repo view --web
```

Confirm that `.venv` and `__pycache__` were not uploaded.

## Completion criteria

- `inventory_report.py` uses the required core data types.
- The report uses conditions, a `for` loop, a validated `while` loop, `break`, and `continue`.
- Invalid threshold input is handled without a traceback.
- Output is readable and includes device and summary information.
- `python validate_lab2.py` passes.
- No credentials appear in code or Git history.
- The completed project is stored in a private GitHub repository.

## Further references

- [Python tutorial](https://docs.python.org/3/tutorial/)
- [Python data structures](https://docs.python.org/3/tutorial/datastructures.html)
- [Python control flow](https://docs.python.org/3/tutorial/controlflow.html)
- [PEP 8](https://peps.python.org/pep-0008/)


# Lab 3: Python Functions, Classes, and Modules

## Alignment with Chapter 5

This lab applies Chapter 5, **Python Functions, Classes, and Modules**. You will refactor network-inventory logic into small functions, model a device with a class, compose an inventory service from device objects, organize code into a package, and verify behavior with unit tests.

## Estimated time

3 to 4 hours.

## Learning objectives

After completing this lab, you should be able to:

- Define and call functions with parameters and return values.
- Use default arguments, keyword arguments, type hints, and docstrings.
- Explain local scope and avoid unnecessary side effects.
- Create a class with instance state and methods.
- Use encapsulation and a readable object representation.
- Prefer composition when an inventory contains device objects.
- Explain when inheritance is and is not appropriate.
- Import standard-library, third-party, and local modules.
- Explain `__name__ == "__main__"` and basic import discovery.
- Organize a small application as a Python package.
- Test functions, classes, and module boundaries.
- Publish work through a GitHub feature branch and pull request.

## Project structure

The supplied project begins with this structure:

```text
lab03/
├── Lab3.md
├── app.py
├── netinventory/
│   ├── __init__.py
│   ├── formatters.py
│   ├── models.py
│   └── services.py
└── tests/
    ├── __init__.py
    └── test_netinventory.py
```

The production files contain deliberate `NotImplementedError` placeholders. The tests describe the required behavior.

---

## Part 1: Prepare the project and observe the failing tests

```bash
mkdir -p ~/devnet-associate/labs
cp -R "/path/to/Lab 03 - Python Functions Classes and Modules" ~/devnet-associate/labs/lab03
cd ~/devnet-associate/labs/lab03
python3 -m venv .venv
source .venv/bin/activate
```

This lab uses the standard library only. Initialize Git:

```bash
printf '%s\n' '.venv/' '__pycache__/' '*.py[cod]' > .gitignore
git init
git branch -M main
git add .gitignore Lab3.md app.py netinventory tests
git commit -m "Create Lab 3 package scaffold"
code .
```

Select the `.venv` interpreter, then run:

```bash
python -m unittest discover -v
```

The tests should fail because the required functions and classes are not implemented. This is the **Red** state. Read the first failure rather than trying to solve all failures simultaneously.

---

## Part 2: Implement reusable formatting functions

Open `netinventory/formatters.py`.

### 2.1 Normalize interface names

Implement:

```python
def normalize_interface(name: str) -> str:
    """Return a compact, lowercase interface name."""
    cleaned = name.strip().lower().replace(" ", "")
    replacements = {
        "gigabitethernet": "gi",
        "tengigabitethernet": "te",
        "fastethernet": "fa",
        "ethernet": "eth",
    }
    for long_name, short_name in replacements.items():
        if cleaned.startswith(long_name):
            return cleaned.replace(long_name, short_name, 1)
    return cleaned
```

The function has one explicit input, returns a string, and does not modify external state. Run only its tests:

```bash
python -m unittest -v tests.test_netinventory.FormatterTests
```

### 2.2 Format a device label

Implement a second function:

```python
def format_device_label(name: str, role: str = "unknown") -> str:
    """Return a consistent label for reports."""
    clean_name = name.strip().lower()
    clean_role = role.strip().lower()
    return f"{clean_name} [{clean_role}]"
```

Call it with positional and keyword arguments in the interpreter:

```python
from netinventory.formatters import format_device_label

print(format_device_label(" EDGE-R1 ", "Router"))
print(format_device_label(name="ACCESS-SW1", role="Switch"))
print(format_device_label("unknown-device"))
```

Default values are evaluated when the function is defined. Avoid mutable defaults such as `tags=[]`; use `None` and create a new list inside the function when mutable state is needed.

Commit the focused change:

```bash
git add netinventory/formatters.py
git commit -m "Implement inventory formatting functions"
```

---

## Part 3: Build a `Device` class

Open `netinventory/models.py`. Implement the initializer:

```python
class Device:
    """A validated network-device record."""

    def __init__(
        self,
        name: str,
        management_ip: str,
        role: str,
        platform: str = "unknown",
        enabled: bool = True,
    ) -> None:
        self.name = name.strip().lower()
        self.management_ip = str(ipaddress.ip_address(management_ip))
        self.role = role.strip().lower()
        self.platform = platform.strip().lower()
        self.enabled = enabled
```

The standard-library `ipaddress` module validates and normalizes the address. Invalid input raises `ValueError`; the class should not silently accept unusable state.

Add a method:

```python
def label(self) -> str:
    """Return the standard display label."""
    return format_device_label(self.name, self.role)
```

Add a readable representation useful during debugging:

```python
def __repr__(self) -> str:
    return (
        f"Device(name={self.name!r}, management_ip={self.management_ip!r}, "
        f"role={self.role!r}, platform={self.platform!r}, "
        f"enabled={self.enabled!r})"
    )
```

Run the class tests:

```bash
python -m unittest -v tests.test_netinventory.DeviceTests
```

Inspect an object interactively:

```bash
python - <<'PY'
from netinventory.models import Device

device = Device(" EDGE-R1 ", "192.0.2.10", "Router", platform="IOSXE")
print(device)
print(device.label())
print(device.management_ip)
PY
```

The class encapsulates data normalization behind a constructor. Callers do not need to repeat the same cleanup and validation.

Commit:

```bash
git add netinventory/models.py
git commit -m "Add validated Device model"
```

---

## Part 4: Use composition in an inventory service

An inventory **has devices**. This is a composition relationship; an inventory is not a specialized kind of device.

Open `netinventory/services.py` and implement:

```python
class Inventory:
    """A collection of Device objects with reporting operations."""

    def __init__(self, devices: list[Device] | None = None) -> None:
        self._devices = list(devices) if devices is not None else []

    def add(self, device: Device) -> None:
        if not isinstance(device, Device):
            raise TypeError("Inventory accepts Device objects only")
        if any(existing.name == device.name for existing in self._devices):
            raise ValueError(f"Duplicate device name: {device.name}")
        self._devices.append(device)

    def enabled(self) -> list[Device]:
        return [device for device in self._devices if device.enabled]

    def by_role(self, role: str) -> list[Device]:
        target = role.strip().lower()
        return [device for device in self._devices if device.role == target]

    def roles(self) -> set[str]:
        return {device.role for device in self._devices}

    def __len__(self) -> int:
        return len(self._devices)
```

Why copy `devices` with `list(devices)`? It prevents the caller from modifying the inventory accidentally through the original list reference.

Run the service tests:

```bash
python -m unittest -v tests.test_netinventory.InventoryTests
```

Add a device to a list supplied to `Inventory`, mutate the original list afterward, and confirm that the inventory length does not change. Record the observation in `notes.md` under **Composition and defensive copying**.

Commit:

```bash
git add netinventory/services.py notes.md
git commit -m "Compose device objects in inventory service"
```

---

## Part 5: Understand inheritance versus composition

Inheritance models an **is-a** relationship. For example, a `ManagedDevice` might be a specialized `Device`, but using subclasses only to store a different role often creates unnecessary complexity.

Do not create `Router`, `Switch`, and `Firewall` subclasses in this lab because their current data and behavior are identical. The `role` attribute is sufficient. Record answers in `notes.md`:

1. When would a subclass become justified?
2. Why would `Inventory(Device)` be conceptually wrong?
3. Why is `Inventory` containing `Device` objects a better design?
4. What could go wrong with a deep inheritance hierarchy in automation code?

---

## Part 6: Organize and import the package

Open `netinventory/__init__.py` and export the stable public interface:

```python
"""Public interface for the netinventory package."""

from .formatters import format_device_label, normalize_interface
from .models import Device
from .services import Inventory

__all__ = [
    "Device",
    "Inventory",
    "format_device_label",
    "normalize_interface",
]
```

Relative imports begin from the current package. External callers can now write:

```python
from netinventory import Device, Inventory
```

Inspect import discovery:

```bash
python - <<'PY'
import netinventory
import sys

print("Package file:", netinventory.__file__)
print("First search path:", sys.path[0])
print("Public names:", netinventory.__all__)
PY
```

Python checks already loaded modules, built-in modules, and directories on `sys.path`. Do not name a local file `json.py`, `ipaddress.py`, or `unittest.py`, because it may shadow the standard-library module you intended to import.

---

## Part 7: Complete the application entry point

Open `app.py` and implement `build_inventory()`:

```python
def build_inventory() -> Inventory:
    inventory = Inventory()
    inventory.add(Device("edge-r1", "192.0.2.10", "router", "iosxe"))
    inventory.add(Device("access-sw1", "192.0.2.21", "switch", "iosxe"))
    inventory.add(
        Device("lab-fw1", "192.0.2.30", "firewall", "ftd", enabled=False)
    )
    return inventory
```

Implement `main()`:

```python
def main() -> int:
    inventory = build_inventory()
    print(f"Inventory devices: {len(inventory)}")
    print(f"Roles: {', '.join(sorted(inventory.roles()))}")
    print("Enabled devices:")
    for device in inventory.enabled():
        print(f"- {device.label()} {device.management_ip} {device.platform}")
    return 0
```

Keep the entry-point guard:

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

When `app.py` is executed, `__name__` is `"__main__"` and the program runs. When imported by a test or another module, definitions load without automatically printing the report.

Run:

```bash
python app.py
python -m unittest discover -v
```

All tests should now pass.

---

## Part 8: Review function and class design

Complete `notes.md` with brief answers:

- Which functions are pure, and why are they easy to test?
- Which methods change object state?
- What inputs are validated at the class boundary?
- Why does `Inventory.enabled()` return a new list?
- Where are default arguments used safely?
- What names form the public package interface?
- Which standard-library modules are imported?
- Where would a third-party SDK be imported in a larger application?

Use VS Code navigation:

- Place the cursor on `Device` and press `F12`.
- Use **Find All References** for `normalize_interface`.
- Use `Ctrl+Shift+F` to find every `NotImplementedError`; none should remain.
- Inspect the test names as executable behavior descriptions.

---

## Part 9: Publish through a branch and pull request

Create the private repository after the scaffold commit if it does not already exist:

```bash
gh repo create devnet-associate-lab03 --private --source=. --remote=origin --push
```

Create a focused documentation branch:

```bash
git switch -c docs/lab3-design-notes
git add netinventory app.py tests notes.md Lab3.md .gitignore
git diff --staged
git commit -m "Complete modular network inventory application"
git push -u origin docs/lab3-design-notes
```

Open a pull request:

```bash
gh pr create \
  --base main \
  --head docs/lab3-design-notes \
  --title "Complete Lab 3 modular inventory" \
  --body "Implements functions, Device and Inventory classes, package exports, and passing unit tests."
```

On GitHub:

1. Review **Files changed**.
2. Confirm no `.venv`, cache, or credential file is present.
3. Confirm the tests passed locally.
4. Merge the pull request.
5. Delete the remote feature branch.

Synchronize locally:

```bash
git switch main
git pull --ff-only
git branch -d docs/lab3-design-notes
git fetch --prune
```

## Completion criteria

- All `NotImplementedError` placeholders are replaced.
- Functions include meaningful names, docstrings, type hints, and return values.
- `Device` validates addresses and normalizes state.
- `Inventory` uses composition and rejects duplicate names.
- Package imports work through `netinventory`.
- `python -m unittest discover -v` passes.
- Design answers are recorded in `notes.md`.
- The private GitHub pull request is reviewed and merged.

## Further references

- [Defining Python functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions)
- [Python classes](https://docs.python.org/3/tutorial/classes.html)
- [Python modules](https://docs.python.org/3/tutorial/modules.html)
- [Python import system](https://docs.python.org/3/reference/import.html)


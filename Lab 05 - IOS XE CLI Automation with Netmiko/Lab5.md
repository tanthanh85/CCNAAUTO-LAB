# Lab 5: IOS XE CLI Automation with Netmiko and TextFSM

## Duration

**2 hours**

In this lab, you will connect to a private Cisco IOS XE reservable sandbox with Netmiko, run `show ip interface brief`, parse the output with TextFSM, and configure ten loopback interfaces from metadata stored in YAML. You will verify the result and remove the lab configuration before the reservation ends.

## Objectives

- Connect to an IOS XE device through SSH using Netmiko.
- Keep device credentials outside source code and Git.
- Parse `show ip interface brief` into structured records with TextFSM.
- Load and validate loopback metadata from YAML.
- Generate interface configuration with a Python `for` loop.
- Perform pre-check, change, post-check, and cleanup operations.
- Store code and non-sensitive evidence in a private GitHub repository.

## Required environment

- Ubuntu workstation prepared in Lab 1.
- A **reservation-based** Cisco IOS XE sandbox with configuration permission.
- The sandbox VPN connected and the reservation status shown as Ready.
- One IOS XE router address, SSH port, username, and password from the current reservation.

Use the current DevNet catalog because sandbox names and versions change. Suitable choices include a reservable **Cisco IOS XE on Catalyst 8kv/CSR** environment. Always-On sandboxes are shared and must not be used for this configuration exercise. Cisco documents reservable IOS XE environments as private labs requiring reservation and VPN access: [IOS XE sandboxes](https://developer.cisco.com/docs/ios-xe-voip/sandbox/) and [DevNet Sandbox getting started](https://developer.cisco.com/docs/sandbox/getting-started/).

Do not erase the device configuration, modify management connectivity, or save this lab configuration to startup configuration.

## Files

```text
lab05/
├── Lab5.md
├── requirements.txt
├── device.yaml
├── common.py
├── show_interfaces.py
├── configure_loopbacks.py
└── cleanup_loopbacks.py
```

## Part 1: Prepare the project and sandbox

Copy the project and install its dependencies:

```bash
mkdir -p ~/devnet-associate/labs
cp -R "/path/to/Lab 05 - IOS XE CLI Automation with Netmiko" \
  ~/devnet-associate/labs/lab05
cd ~/devnet-associate/labs/lab05
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Initialize Git. Runtime evidence and local environment files are excluded:

```bash
printf '%s\n' \
  '.venv/' \
  '__pycache__/' \
  '*.py[cod]' \
  '.env' \
  'artifacts/' > .gitignore
git init
git branch -M main
code .
```

In the sandbox portal:

1. Confirm the reservation is Ready.
2. Open its topology and Instructions panel.
3. Identify one IOS XE router that permits SSH configuration.
4. Connect the workstation to the reservation VPN.
5. Test the assigned address and SSH port only:

```bash
ip route
nc -vz ROUTER_ADDRESS SSH_PORT
```

Replace the placeholders with current reservation values.

## Part 2: Set device metadata and credentials

Open `device.yaml`. Replace only the placeholder `host` and `port` values with the router details from the reservation. Do not add a username or password to YAML.

Export credentials in the current terminal:

```bash
read -rp "Sandbox username: " LAB_USERNAME
read -srp "Sandbox password: " LAB_PASSWORD
echo
export LAB_USERNAME LAB_PASSWORD
```

If the device requires a separate enable secret:

```bash
read -srp "Enable secret: " LAB_SECRET
echo
export LAB_SECRET
```

The variables exist only in this shell and are not committed. Confirm their presence without printing their values:

```bash
test -n "$LAB_USERNAME" && echo "Username is set"
test -n "$LAB_PASSWORD" && echo "Password is set"
```

Review the ten loopbacks in `device.yaml`. They use addresses from the non-public benchmarking range `198.18.0.0/15`, `/32` masks, and a common lab description. If the sandbox instructions prohibit this range or these interface IDs, coordinate an approved alternative with the instructor and update the YAML before running configuration.

## Part 3: Retrieve and parse interface output

Run the read-only collection script:

```bash
python show_interfaces.py --output artifacts/interfaces-before.json
```

The script uses:

```python
parsed = connection.send_command(
    "show ip interface brief",
    use_textfsm=True,
)
```

Netmiko returns a list of dictionaries when the matching NTC TextFSM template is found. For this command, typical fields include `intf`, `ipaddr`, `status`, and `proto`. The exact template controls the keys; the script prints the received keys instead of assuming unverified output.

Inspect the saved structure:

```bash
python -m json.tool artifacts/interfaces-before.json | less
```

If the script reports that it received raw text:

```bash
python -m pip show textfsm ntc-templates
python - <<'PY'
import os
import ntc_templates

template_dir = os.path.join(os.path.dirname(ntc_templates.__file__), "templates")
print(template_dir)
PY
```

Set `NET_TEXTFSM` to the printed template directory and retry:

```bash
export NET_TEXTFSM="PATH_PRINTED_ABOVE"
python show_interfaces.py --output artifacts/interfaces-before.json
```

Do not continue until structured records are produced.

## Part 4: Review the change before execution

Run dry-run mode:

```bash
python configure_loopbacks.py --dry-run
```

The script validates that:

- Exactly ten loopbacks are defined.
- IDs, names, and IPv4 addresses are unique.
- Every address uses a `/32` prefix.
- Every description begins with `LAB5_`.
- None of the requested loopback names already exists.

It then generates commands with a Python loop:

```python
commands = []
for loopback in loopbacks:
    interface_name = f"Loopback{loopback['id']}"
    address = ipaddress.ip_interface(loopback["ipv4"])
    commands.extend(
        [
            f"interface {interface_name}",
            f"description {loopback['description']}",
            f"ip address {address.ip} {address.netmask}",
            "no shutdown",
        ]
    )
```

Read every generated command. Confirm that the script does not modify a physical interface, default route, user account, management service, or existing loopback.

## Part 5: Configure ten loopbacks

Apply the approved change:

```bash
python configure_loopbacks.py --apply
```

The script performs a pre-check again, sends the command list with `send_config_set()`, and displays the IOS XE response. It intentionally does not call `save_config()`.

If an error occurs, stop and inspect the complete message. Do not add `except Exception: pass`, disable validation, or repeatedly rerun a partially understood change.

## Part 6: Verify structured state

Collect the command again:

```bash
python show_interfaces.py --output artifacts/interfaces-after.json
```

Display only the lab loopbacks:

```bash
jq '.[] | select((.intf // .interface) | test("^Loopback5(0[1-9]|10)$"))' \
  artifacts/interfaces-after.json
```

Expected interfaces are `Loopback501` through `Loopback510`. Each should have the address defined in YAML. IOS XE may briefly show protocol state changes; use the parsed status and protocol fields as evidence rather than assuming success from configuration output alone.

Confirm directly from Python:

```bash
python - <<'PY'
import json
from pathlib import Path

records = json.loads(Path("artifacts/interfaces-after.json").read_text())
names = {record.get("intf", record.get("interface")) for record in records}
expected = {f"Loopback{number}" for number in range(501, 511)}
print("Present:", sorted(expected & names))
print("Missing:", sorted(expected - names))
PY
```

`Missing` must be an empty list.

## Part 7: Remove the lab configuration

Run cleanup dry-run first:

```bash
python cleanup_loopbacks.py --dry-run
```

Apply cleanup. Before removing an interface, the script confirms that its running configuration contains the exact `LAB5_` description from YAML:

```bash
python cleanup_loopbacks.py --apply
python show_interfaces.py --output artifacts/interfaces-cleanup.json
```

Verify that the ten lab loopbacks no longer appear. The cleanup script reads the same YAML source of truth and generates only `no interface Loopback<ID>` commands.

Remove credentials from the shell:

```bash
unset LAB_USERNAME LAB_PASSWORD LAB_SECRET
```

Disconnect from the sandbox VPN when no longer needed and release unused reservation time.

## Part 8: Commit and publish

Confirm that artifacts and credentials are not staged:

```bash
git status
git add .gitignore Lab5.md requirements.txt device.yaml \
  common.py show_interfaces.py configure_loopbacks.py cleanup_loopbacks.py
git diff --staged
git commit -m "Automate IOS XE loopbacks with Netmiko and TextFSM"
gh repo create devnet-associate-lab05 --private --source=. --remote=origin --push
```

On GitHub, verify that `.env`, `.venv`, `artifacts`, passwords, and sandbox VPN details are absent.

## Completion criteria

- Netmiko connects to the assigned reservable IOS XE device.
- `show ip interface brief` is returned as TextFSM dictionaries, not raw CLI text.
- YAML contains exactly ten validated loopback definitions.
- Dry-run displays the intended commands before configuration.
- The loop creates and verifies `Loopback501` through `Loopback510`.
- Cleanup removes all ten interfaces.
- Credentials and sandbox-specific evidence are not committed.
- The private GitHub repository contains the Lab 5 code.

## Further references

- [Cisco IOS XE sandboxes](https://developer.cisco.com/docs/ios-xe-voip/sandbox/)
- [Netmiko documentation](https://ktbyers.github.io/netmiko/)
- [NTC Templates](https://github.com/networktocode/ntc-templates)
- [TextFSM](https://github.com/google/textfsm)

# Lab 6: CLI Automation with Ansible

## Duration

**2 hours**

This lab repeats the operational objectives of Lab 5 using Ansible. You will connect to a private IOS XE reservable sandbox, parse `show ip interface brief` with an NTC TextFSM template, configure ten YAML-defined loopbacks with an Ansible loop, verify their state, and remove them safely.

## Objectives

- Use an Ansible `network_cli` connection to manage IOS XE.
- Load credentials from a local `.env` file excluded from Git.
- Parse CLI output with `ansible.utils.cli_parse` and NTC TextFSM templates.
- Store loopback intent in YAML variables.
- Configure repeated resources with an Ansible loop.
- Use assertions, check mode, diffs, post-checks, and bounded cleanup.
- Publish the reusable project to a private GitHub repository.

```mermaid
flowchart LR
    A["Inventory and group variables"] --> B["Ansible playbook"]
    B --> C["network_cli connection"]
    C --> D["IOS XE router"]
    D --> E["Parsed operational state"]
    E --> F["Assertions and local artifacts"]
```

## Required environment

- Ubuntu workstation prepared in Lab 1.
- A private, reservation-based Cisco IOS XE sandbox with configuration permission.
- The sandbox VPN connected and the reservation shown as Ready.
- An IOS XE router address, SSH port, username, and password from that reservation.

Use a reservable IOS XE on Catalyst 8kv/CSR environment currently available in the DevNet catalog. Do not perform this configuration exercise against a shared Always-On sandbox. See [Cisco IOS XE sandboxes](https://developer.cisco.com/docs/ios-xe-voip/sandbox/) and [DevNet Sandbox getting started](https://developer.cisco.com/docs/sandbox/getting-started/).

## Project structure

```text
lab06/
├── Lab6.md
├── ansible.cfg
├── inventory.yml
├── .env.example
├── requirements.txt
├── collections/
│   └── requirements.yml
├── group_vars/
│   └── all.yml
├── playbooks/
│   ├── show_interfaces.yml
│   ├── configure_loopbacks.yml
│   └── cleanup_loopbacks.yml
└── run-playbook.sh
```

## Part 1: Prepare the Ansible project

```bash
mkdir -p ~/devnet-associate/labs
cp -R "/path/to/Lab 06 - CLI Automation with Ansible" \
  ~/devnet-associate/labs/lab06
cd ~/devnet-associate/labs/lab06
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
ansible-galaxy collection install -r collections/requirements.yml
chmod u+x run-playbook.sh
```

Create Git exclusions:

```bash
printf '%s\n' \
  '.venv/' \
  '__pycache__/' \
  '*.py[cod]' \
  '.env' \
  'artifacts/' \
  '*.retry' > .gitignore
git init
git branch -M main
code .
```

Verify Ansible and the required collections:

```bash
ansible --version
ansible-galaxy collection list | grep -E 'ansible.netcommon|ansible.utils|cisco.ios'
```

## Part 2: Set inventory and credentials

Open `inventory.yml` and replace `REPLACE_WITH_RESERVED_ROUTER_ADDRESS` with the assigned router address. Change `ansible_port` only if the reservation specifies a nondefault SSH port.

Create the local credential file:

```bash
cp .env.example .env
chmod 600 .env
code .env
```

Enter the current reservation values:

```dotenv
LAB_USERNAME='your-reservation-username'
LAB_PASSWORD='your-reservation-password'
LAB_SECRET=''
```

Set `LAB_SECRET` only when the router requires a separate enable secret. The wrapper script exports these values for the Ansible process. `.env` is ignored; `.env.example` contains variable names only.

Review `group_vars/all.yml`. It is the desired-state source for exactly ten loopbacks, `Loopback601` through `Loopback610`. Each record contains an ID, `/32` IPv4 address, and `LAB6_` description.

Display the inventory without exposing passwords:

```bash
./run-playbook.sh --inventory inventory.yml --list-hosts playbooks/show_interfaces.yml
```

## Part 3: Retrieve and parse interfaces

Run the read-only playbook:

```bash
./run-playbook.sh playbooks/show_interfaces.yml
```

The core task is:

```yaml
- name: Run and parse show ip interface brief
  ansible.utils.cli_parse:
    command: show ip interface brief
    parser:
      name: ansible.netcommon.ntc_templates
    set_fact: interfaces
```

`ansible_network_os: cisco.ios.ios` is translated to the `cisco_ios` platform name used by NTC Templates. The result is a list of dictionaries rather than unstructured CLI text.

Inspect the local artifact:

```bash
python -m json.tool artifacts/interfaces-before.json | less
```

Identify the actual interface-name, IP-address, status, and protocol keys returned by the installed template. The playbook supports the common `interface`/`intf` naming variants.

Ansible's current parsing guidance recommends `ansible.utils.cli_parse`; the older TextFSM filter is deprecated. See [Ansible CLI parsing](https://docs.ansible.com/projects/ansible/latest/network/user_guide/cli_parsing.html).

## Part 4: Review and check the proposed change

Review the validation and configuration tasks in `playbooks/configure_loopbacks.yml`.

The playbook checks:

- The YAML list contains exactly ten entries.
- IDs and addresses are unique.
- IDs are limited to 601–610.
- Addresses are limited to `198.18.6.1/32` through `198.18.6.10/32`.
- Descriptions begin with `LAB6_`.
- An existing target loopback must already contain the exact lab description.

These checks use basic assertions and regular-expression matching. More advanced Ansible IP-address filters are intentionally omitted so that the focus remains on inventories, variables, tasks, modules, and loops.

The configuration task uses an Ansible loop:

```yaml
- name: Configure YAML-defined loopbacks
  cisco.ios.ios_config:
    parents: "interface Loopback{{ item.id }}"
    lines:
      - "description {{ item.description }}"
      - "ip address {{ item.ipv4.split('/')[0] }} 255.255.255.255"
      - no shutdown
  loop: "{{ loopbacks }}"
  loop_control:
    label: "Loopback{{ item.id }}"
```

Preview with check mode and diff:

```bash
./run-playbook.sh --check --diff playbooks/configure_loopbacks.yml
```

Read the proposed changes before continuing. Do not proceed if the play affects a physical interface, routing, authentication, management reachability, or an existing loopback.

## Part 5: Configure ten loopbacks

Apply the playbook:

```bash
./run-playbook.sh --diff playbooks/configure_loopbacks.yml
```

Review the recap. `failed=0` is required, but it is not sufficient proof that operational state is correct. The playbook intentionally does not save the running configuration to startup configuration.

Run the same playbook again:

```bash
./run-playbook.sh --diff playbooks/configure_loopbacks.yml
```

The second run should report no configuration changes. This demonstrates idempotency: the declared state is already present.

## Part 6: Verify parsed state

Collect the command after configuration:

```bash
./run-playbook.sh \
  -e artifact_name=interfaces-after.json \
  playbooks/show_interfaces.yml
```

Inspect the ten loopbacks:

```bash
jq '.[] | select((.interface // .intf) | test("^Loopback6(0[1-9]|10)$"))' \
  artifacts/interfaces-after.json
```

Expected names are `Loopback601` through `Loopback610`. Compare their addresses with `group_vars/all.yml`. Use parsed status and protocol fields as post-change evidence rather than relying only on Ansible's `changed` result.

## Part 7: Remove the lab configuration

Preview cleanup:

```bash
./run-playbook.sh --check --diff playbooks/cleanup_loopbacks.yml
```

The cleanup playbook retrieves each interface configuration and refuses removal unless the exact YAML description is present. Apply cleanup:

```bash
./run-playbook.sh --diff playbooks/cleanup_loopbacks.yml
./run-playbook.sh \
  -e artifact_name=interfaces-cleanup.json \
  playbooks/show_interfaces.yml
```

Confirm that none of the ten Lab 6 loopbacks remains. Delete the temporary credential file when the reservation ends or when using a shared workstation:

```bash
rm .env
```

Disconnect the sandbox VPN and release unused reservation time.

## Part 8: Commit and publish

```bash
git status --ignored
git add .gitignore .env.example Lab6.md ansible.cfg inventory.yml \
  requirements.txt collections group_vars playbooks run-playbook.sh
git diff --staged
git commit -m "Automate IOS XE loopbacks with Ansible"
gh repo create devnet-associate-lab06 --private --source=. --remote=origin --push
```

Confirm on GitHub that `.env`, `.venv`, artifacts, passwords, and sandbox VPN details are absent.

## Completion criteria

- Ansible connects to the assigned reservable IOS XE router with `network_cli`.
- `show ip interface brief` is parsed into TextFSM dictionaries.
- YAML defines exactly ten loopbacks.
- Assertions prevent conflicts and out-of-scope metadata.
- Check mode and diff show the intended change.
- The first apply creates `Loopback601`–`Loopback610`.
- The second apply is idempotent.
- Post-check verifies the structured operational state.
- Cleanup verifies descriptions before removal.
- Credentials and artifacts are absent from GitHub.

## Further references

- [Cisco IOS XE sandboxes](https://developer.cisco.com/docs/ios-xe-voip/sandbox/)
- [Ansible CLI parsing](https://docs.ansible.com/projects/ansible/latest/network/user_guide/cli_parsing.html)
- [`ansible.utils.cli_parse`](https://docs.ansible.com/projects/ansible/latest/collections/ansible/utils/cli_parse_module.html)
- [`cisco.ios.ios_config`](https://docs.ansible.com/projects/ansible/latest/collections/cisco/ios/ios_config_module.html)

## Key takeaways

- Ansible inventory identifies managed nodes, variables describe intent, and playbooks define ordered tasks.
- Network collections provide device-aware modules instead of requiring learners to script an SSH dialogue.
- Assertions and check mode expose unsafe or unexpected conditions before configuration is applied.
- Idempotent modules describe the desired state and avoid unnecessary changes when that state already exists.
- Parsed post-checks and cleanup ownership checks are as important in Ansible as in Python automation.

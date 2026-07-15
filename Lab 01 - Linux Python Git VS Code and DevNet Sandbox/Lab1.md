# Lab 01: Ubuntu Linux, Python, Git, VS Code, and Cisco DevNet Sandbox

## Lab purpose

Network automation work begins at the workstation. Before learners call an API or configure a device, they need a reliable way to navigate Linux, edit files, isolate Python dependencies, track changes, and connect safely to a lab environment.

In this lab, you will prepare an Ubuntu 26.04 LTS workstation for the rest of the course. You will use common Linux commands and text editors, install the development toolchain, create a Python virtual environment, explore frequently used Visual Studio Code features, and reserve a Cisco DevNet Sandbox.

## Estimated time

3.5 to 4.5 hours, excluding sandbox provisioning time.

## Learning objectives

After completing this lab, you should be able to:

- Navigate the Linux filesystem and manage files and directories.
- Inspect files, processes, network state, permissions, and command output.
- Edit text with Nano and Vim.
- Install and verify Python, pip, Git, Visual Studio Code, and supporting tools.
- Create, activate, use, and remove a Python virtual environment.
- Install Python packages without modifying the system Python environment.
- Create a local Git repository and record a controlled change.
- Create and secure a GitHub account for storing course code.
- Publish, clone, pull, and push a repository using a beginner GitHub workflow.
- Use branches and pull requests to review a change before merging it.
- Use the Explorer, integrated terminal, Command Palette, Source Control view, Python interpreter selector, search, and debugger in VS Code.
- Distinguish an Always-On sandbox from a reservation-based sandbox.
- Reserve a private DevNet Sandbox and locate its topology, instructions, credentials, and VPN access details.

## Required resources

- One Ubuntu 26.04 LTS workstation per learner with internet access.
- A user account with `sudo` privileges.
- A modern web browser.
- A personal email address that can receive GitHub verification messages.
- A Cisco.com account that can sign in to Cisco DevNet.
- This complete `Lab 01 - Linux Python Git VS Code and DevNet Sandbox` folder.

Use only the workstation and sandbox assigned to you. Do not scan, probe, or attempt to access systems outside the lab instructions.

---

## Part 1: Become familiar with the Linux terminal

Open the Terminal application. A prompt similar to the following appears:

```text
learner@ubuntu:~$
```

The text before `@` is normally the user name, the text after it is the host name, and `~` represents the current user's home directory. The `$` prompt indicates an unprivileged shell. Commands that require administrative privileges will be run explicitly with `sudo`.

### 1.1 Identify the workstation and shell

Run the following commands one at a time:

```bash
whoami
hostnamectl
uname -a
cat /etc/os-release
echo "$SHELL"
pwd
```

`whoami` identifies the current user. `hostnamectl`, `uname`, and `/etc/os-release` describe the operating system and kernel. `pwd` prints the absolute path of the current working directory.

Create a workspace for this course:

```bash
mkdir -p ~/devnet-associate/labs
cd ~/devnet-associate/labs
pwd
```

The `-p` option creates missing parent directories and does not report an error if the directory already exists.

### 1.2 List, create, copy, move, and remove files

Create a practice directory and enter it:

```bash
mkdir linux-practice
cd linux-practice
touch router-a.txt router-b.txt
ls
ls -la
```

`ls -la` includes hidden entries and shows permissions, ownership, size, and modification time.

Add content, copy a file, and rename the copy:

```bash
printf 'hostname: router-a\nmanagement_ip: 192.0.2.10\n' > router-a.txt
cp router-a.txt router-a-backup.txt
mv router-a-backup.txt router-a-copy.txt
ls -l
```

The `>` operator replaces a file's content. The `>>` operator appends instead:

```bash
printf 'site: training-lab\n' >> router-a.txt
cat router-a.txt
```

Create and inspect a nested directory:

```bash
mkdir -p backups/daily
cp router-*.txt backups/daily/
find . -maxdepth 3 -type f -print
tree .
```

Remove only the copied practice file and confirm the result:

```bash
rm router-a-copy.txt
ls -l
```

Before using `rm`, verify the current directory with `pwd` and inspect the target with `ls`. Files removed from a terminal may not enter the desktop Trash.

### 1.3 Read and search text

Create a short log file:

```bash
printf '%s\n' \
  'INFO connected to router-a' \
  'WARNING latency above threshold' \
  'ERROR authentication failed' \
  'INFO session closed' > automation.log
```

Read and search it:

```bash
cat automation.log
head -n 2 automation.log
tail -n 2 automation.log
less automation.log
grep 'ERROR' automation.log
grep -n -E 'WARNING|ERROR' automation.log
wc -l automation.log
```

Press `q` to exit `less`. The `-n` option to `grep` shows matching line numbers, and `-E` enables an extended regular expression.

Use a pipeline to pass the output of one command to another:

```bash
grep -E 'WARNING|ERROR' automation.log | sort
```

Redirect a filtered result to a new file:

```bash
grep -E 'WARNING|ERROR' automation.log > exceptions.log
cat exceptions.log
```

### 1.4 Work with paths and command help

Compare absolute and relative paths:

```bash
cd ~/devnet-associate/labs/linux-practice
pwd
ls ./backups
ls ~/devnet-associate/labs/linux-practice/backups
cd ..
pwd
cd -
```

Use built-in help before guessing at command options:

```bash
ls --help | less
man find
```

Press `q` to exit either viewer.

### 1.5 Inspect permissions and use `sudo` safely

Inspect the permissions of the practice files:

```bash
ls -l
stat router-a.txt
```

Linux permissions are shown for the owner, group, and others. Add execute permission to a new shell script, run it, and then remove the permission:

```bash
printf '#!/usr/bin/env bash\necho "Workstation check complete"\n' > check.sh
chmod u+x check.sh
./check.sh
chmod u-x check.sh
```

Check whether your account may use `sudo`:

```bash
sudo -v
sudo -l
```

Use `sudo` for the individual administrative command that needs it. Do not work from a permanently privileged shell, and do not use `sudo` with `pip` later in this lab.

### 1.6 Inspect processes, storage, and network state

Run these read-only inspection commands:

```bash
ps aux | head
top
df -h
du -sh ~/devnet-associate
ip -brief address
ip route
ss -tuln
getent hosts developer.cisco.com
ping -c 4 developer.cisco.com
curl -I https://developer.cisco.com/
```

Press `q` to exit `top`. A failed `ping` does not always mean a service is unavailable because some networks block ICMP. An HTTPS response from `curl` may still prove application connectivity.

### 1.7 Useful command-line shortcuts

Practice the following shell features:

- Press `Tab` to complete a command or path.
- Press the Up and Down arrows to browse command history.
- Press `Ctrl+C` to interrupt a foreground command.
- Press `Ctrl+L` to clear the visible terminal.
- Run `history` to inspect recent commands.
- Run `history | grep python` later to find Python-related commands.

---

## Part 2: Edit text with Nano and Vim

Graphical editors are convenient, but terminal editors remain useful on remote Linux systems and network automation hosts.

### 2.1 Use Nano

Open the router file:

```bash
cd ~/devnet-associate/labs/linux-practice
nano router-a.txt
```

Add the following line:

```text
role: access-switch
```

Nano displays keyboard shortcuts at the bottom of the screen. The caret means the `Ctrl` key. Save with `Ctrl+O`, press `Enter` to confirm the file name, and exit with `Ctrl+X`.

Confirm the change:

```bash
cat router-a.txt
```

### 2.2 Use Vim

Open the second file:

```bash
vim router-b.txt
```

Vim starts in Normal mode. Press `i` to enter Insert mode, then type:

```text
hostname: router-b
management_ip: 192.0.2.11
role: edge-router
```

Press `Esc` to return to Normal mode. Type `:wq` and press `Enter` to write the file and quit.

Reopen the file and practice these common operations:

```bash
vim router-b.txt
```

- `/router` searches forward for `router`; press `n` for the next match.
- `dd` deletes the current line.
- `u` undoes the previous edit.
- `:w` saves without exiting.
- `:q!` exits and discards unsaved changes.

Use Nano when you want an immediately discoverable interface. Use Vim when efficient keyboard-driven editing is valuable or when it is the available remote editor.

---

## Part 3: Install the development toolchain

Update package metadata and install the course tools:

```bash
sudo apt update
sudo apt install -y \
  python3 python3-pip python3-venv python3-dev \
  git gh curl wget jq tree nano vim openssh-client build-essential
```

Install Visual Studio Code through Snap, which is normally available on Ubuntu desktop:

```bash
sudo snap install code --classic
```

If the workstation image does not provide Snap, use the current Debian/Ubuntu installation procedure from the [official Visual Studio Code documentation](https://code.visualstudio.com/docs/setup/linux) instead of downloading packages from an unverified site.

Verify the tools:

```bash
python3 --version
python3 -m pip --version
git --version
gh --version
code --version
ssh -V
curl --version | head -n 1
jq --version
```

Use `python3 -m pip` rather than relying on a separate `pip` command. This makes it explicit which Python interpreter will receive a package.

Configure Git with your own identity:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.name@example.com"
git config --global init.defaultBranch main
git config --global core.editor "code --wait"
git config --global --list
```

The email may be a classroom address; it does not need to be a public personal address for a local repository.

---

## Part 4: Create and use a Python virtual environment

Ubuntu protects its system-managed Python packages. A virtual environment gives each project an isolated interpreter and package set, preventing one lab's dependencies from changing another lab or the operating system.

### 4.1 Create a project

Copy this entire lab folder into the course workspace if it is not already there. Then enter it:

```bash
cd ~/devnet-associate/labs
cp -R "/path/to/Lab 01 - Linux Python Git VS Code and DevNet Sandbox" lab01
cd lab01
ls -la
```

Replace `/path/to/...` with the actual location supplied by your instructor. If the files are already in `~/devnet-associate/labs/lab01`, simply enter that directory.

Create the environment in a hidden `.venv` directory:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

The prompt normally begins with `(.venv)`. Confirm which executables are active:

```bash
which python
which pip
python --version
python -m pip --version
```

Both paths should point inside the project directory's `.venv` folder.

### 4.2 Install packages inside the environment

Upgrade the environment's packaging tools and install the supplied dependencies:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

Inspect the installed packages:

```bash
python -m pip list
python -m pip show requests PyYAML
python -m pip check
```

Record the exact environment for troubleshooting:

```bash
python -m pip freeze > installed-packages.txt
cat installed-packages.txt
```

`requirements.txt` expresses the direct packages needed by the project. `installed-packages.txt` captures the complete resolved environment, including transitive dependencies. In a larger project, teams may use a dependency-locking tool rather than manually maintaining both files.

### 4.3 Run the verification program

Run the supplied program:

```bash
python verify_workstation.py
```

The program reads `inventory.yaml`, converts the YAML document into Python dictionaries and lists, prints a summary, and displays the installed library versions. A successful run ends with:

```text
Lab 01 Python environment is ready.
```

Review the exit status:

```bash
echo $?
```

An exit status of `0` normally indicates success.

### 4.4 Deactivate and recreate the environment

Leave the virtual environment:

```bash
deactivate
```

Confirm that `python` no longer points to `.venv`:

```bash
command -v python || true
command -v python3
```

Reactivate the environment before continuing:

```bash
source .venv/bin/activate
```

Virtual environments are disposable. If one becomes damaged, deactivate it, remove only the project's `.venv` directory, recreate it, and reinstall the declared requirements:

```bash
deactivate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Never place source files inside `.venv`; the directory may be deleted at any time.

---

## Part 5: Track the project with Git

Remain in the `lab01` project directory.

Create a `.gitignore` file so generated and local-only files are not committed:

```bash
printf '%s\n' \
  '.venv/' \
  '__pycache__/' \
  '*.py[cod]' \
  '.vscode/' \
  'installed-packages.txt' > .gitignore
```

Initialize and inspect the repository:

```bash
git init
git status
git diff
```

Stage the learner files and create the first commit:

```bash
git add Lab1.md requirements.txt verify_workstation.py inventory.yaml .gitignore
git status
git diff --staged
git commit -m "Create Lab 01 workstation project"
git log --oneline --decorate
```

Make a controlled change:

```bash
printf '\n  - name: switch-02\n    management_ip: 192.0.2.22\n    platform: iosxe\n' >> inventory.yaml
git diff
python verify_workstation.py
git add inventory.yaml
git commit -m "Add a second training switch"
git log --oneline --graph --decorate --all
```

Git records meaningful project states. Review `git diff` before staging and `git diff --staged` before committing so that secrets, generated files, and unintended changes do not enter history.

---

## Part 6: Store course code on GitHub

Git and GitHub are related but different. **Git** is the version-control program running on your workstation. **GitHub** hosts remote Git repositories and adds collaboration features such as issues, pull requests, reviews, and repository permissions.

For this course, each learner will use a personal GitHub account and a **private repository** to store lab code. Never upload passwords, API keys, tokens, VPN credentials, private keys, cookies, production configurations, or customer data. Deleting a secret in a later commit does not reliably remove it from Git history.

### 6.1 Register and secure a GitHub account

1. Open [GitHub](https://github.com/) and select **Sign up**.
2. Register a personal account using an email address you can access. Do not create a shared team account.
3. Choose a professional user name that you will be comfortable using in repository URLs.
4. Use a unique password stored in an approved password manager.
5. Open the verification message from GitHub and verify the email address.
6. Enable two-factor authentication when prompted. Save the recovery codes in a secure location separate from the workstation.
7. In **Settings > Emails**, review whether your email should remain private. GitHub can provide a `noreply` address for commits.
8. Review the public profile. Do not publish personal information that is unnecessary for the course.

GitHub currently requires contributors to use two-factor authentication. Its onboarding documentation also identifies email verification and account security as initial setup tasks. Follow the current [GitHub account setup guide](https://docs.github.com/en/get-started/onboarding/getting-started-with-your-github-account) if the interface differs from these steps.

### 6.2 Understand the GitHub vocabulary

| Term | Meaning |
|---|---|
| Repository | A project and its version history. A repository may be local, remote, or both. |
| Remote | A named connection from a local repository to another repository; `origin` is the conventional name for the primary GitHub remote. |
| Clone | A new local copy of a remote repository, including its history and remote configuration. |
| Commit | A recorded snapshot with an author, time, message, and parent history. |
| Push | Send local commits to a remote branch. |
| Fetch | Download remote branch information without merging it into the current branch. |
| Pull | Fetch remote changes and integrate them into the current branch. |
| Branch | A movable line of development. `main` is normally the stable default branch. |
| Pull request | A GitHub proposal to review and merge one branch into another. It is not the same operation as `git pull`. |
| Issue | A GitHub item for tracking a task, defect, question, or planned improvement. |
| Fork | A GitHub-hosted copy under a different account, commonly used to contribute to a repository you cannot modify directly. |

### 6.3 Authenticate safely from Ubuntu

GitHub no longer accepts an account password for Git operations over HTTPS. For this beginner lab, use GitHub CLI to authenticate through the browser and let it configure Git securely.

Confirm that GitHub CLI was installed in Part 3:

```bash
gh --version
```

Start authentication:

```bash
gh auth login
```

Select these answers when offered:

1. **GitHub.com**
2. **HTTPS**
3. Authenticate Git with your GitHub credentials: **Yes**
4. **Login with a web browser**

Copy the one-time code, press `Enter` to open the browser, sign in, and authorize GitHub CLI. Then return to the terminal and verify the result:

```bash
gh auth status
```

Do not put a personal access token in a command, source file, `.env` file, shell history, screenshot, or Git repository. If a later environment requires a token, create the minimum permissions and expiration needed, use it only as a secret, and revoke it when it is no longer required. GitHub's [authentication documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github) explains the supported methods.

### 6.4 Publish the Lab 01 repository

Return to the Git repository created in Part 5 and ensure it is ready to publish:

```bash
cd ~/devnet-associate/labs/lab01
git status
git branch --show-current
git log --oneline --decorate -n 5
```

The working tree should be clean and the current branch should be `main`. Search for common secret material before publishing:

```bash
git grep -n -E 'password|token|secret|private.key' || true
```

Review every match in context. A word such as `token` in documentation is not necessarily a credential, but an actual value must not be committed.

Create a private GitHub repository from the current local repository:

```bash
gh repo create devnet-associate-lab01 \
  --private \
  --source=. \
  --remote=origin \
  --push
```

Verify the connection and tracking branch:

```bash
git remote -v
git branch -vv
gh repo view --web
```

In the browser, examine these common repository features:

- **Code** shows the current files, branch selector, commit history, and clone URL.
- **Issues** tracks work that should be discussed or completed.
- **Pull requests** shows proposed changes and their reviews.
- **Actions** shows automated workflows when a repository defines them.
- **Settings** controls visibility, collaborators, security options, and other repository behavior.

Keep the repository private unless the instructor explicitly approves publication. Private does not mean secret: collaborators and authorized services can still access it, so credentials never belong in the repository.

### 6.5 Clone a repository

`git clone` is normally used once, when placing an existing remote repository on a workstation. It creates the project directory, downloads its history, checks out the default branch, and configures `origin`.

Practice cloning your repository into a separate directory:

```bash
mkdir -p ~/devnet-associate/github-clones
cd ~/devnet-associate/github-clones
git clone https://github.com/YOUR-GITHUB-USERNAME/devnet-associate-lab01.git
cd devnet-associate-lab01
git remote -v
git status
git log --oneline --decorate -n 5
```

Replace `YOUR-GITHUB-USERNAME` with your account name. Copying the HTTPS URL from the repository's **Code** button avoids typing errors. Do not run `git clone` repeatedly to update an existing copy; use `git pull` from inside that copy.

### 6.6 Use the everyday pull-edit-commit-push workflow

Use the original working copy for the following steps:

```bash
cd ~/devnet-associate/labs/lab01
git switch main
git pull --ff-only
git status
```

`git pull --ff-only` updates the local branch only when Git can move it forward without creating an unexpected merge commit. If it refuses, stop and inspect the local and remote history rather than forcing the update.

Create a small learner record that contains no sensitive information:

```bash
printf '%s\n' \
  '# Lab Progress' \
  '' \
  '- Lab 01 workstation setup completed.' > PROGRESS.md
```

Review, stage, commit, and push the change:

```bash
git status
git diff
git add PROGRESS.md
git diff --staged
git commit -m "Document completion of Lab 01 setup"
git push origin main
```

Refresh the repository page in the browser. Open `PROGRESS.md`, then open the latest commit to see the files and exact lines changed.

The regular individual workflow is:

```text
git pull --ff-only
      ↓
edit and test files
      ↓
git status and git diff
      ↓
git add and git commit
      ↓
git push
```

Pull before beginning work, commit one meaningful change at a time, and push frequently enough that reviewed work is available remotely.

### 6.7 Fetch and inspect before integrating

`git fetch` downloads remote information without modifying the current files. It is useful when you want to inspect first:

```bash
git fetch origin
git status
git log --oneline --graph --decorate --all -n 12
git diff main..origin/main
```

If the local `main` branch is simply behind `origin/main`, update it:

```bash
git pull --ff-only origin main
```

Never use `git push --force` in this course unless the instructor is deliberately teaching history repair in an isolated repository. Force-pushing can remove commits that other people depend on.

### 6.8 Create a branch and pull request

Even when working alone, a branch and pull request provide a review boundary before changing `main`.

Start from an updated `main` branch:

```bash
git switch main
git pull --ff-only
git switch -c docs/add-course-purpose
```

Add a short statement:

```bash
printf '\nThis repository stores my DevNet Associate course lab code.\n' >> PROGRESS.md
git diff
git add PROGRESS.md
git commit -m "Explain the purpose of the course repository"
git push -u origin docs/add-course-purpose
```

Create a pull request in the browser:

1. Open the repository on GitHub.
2. Select **Compare & pull request** for `docs/add-course-purpose`, or open **Pull requests > New pull request**.
3. Confirm that the base branch is `main` and the compare branch is `docs/add-course-purpose`.
4. Review the **Files changed** tab.
5. Enter a clear title and describe why the change is needed and how it was validated.
6. Create the pull request.
7. If working with an instructor or team, request a review and wait for approval.
8. Merge the pull request and delete the remote feature branch.

Update the local repository after the browser merge:

```bash
git switch main
git pull --ff-only
git branch -d docs/add-course-purpose
git fetch --prune
git log --oneline --graph --decorate --all -n 12
```

GitHub's [Hello World exercise](https://docs.github.com/en/get-started/start-your-journey/hello-world) provides an additional beginner walkthrough of repositories, branches, commits, and pull requests.

### 6.9 Avoid common beginner problems

- Run `git status` before and after each important operation.
- Pull before editing shared branches and push completed commits before switching workstations.
- Do not edit the same lines concurrently in multiple copies of the repository.
- Do not commit `.venv`, caches, generated files, credentials, or sandbox connection details.
- Do not download a repository as a ZIP when you need Git history and future synchronization; clone it instead.
- Do not confuse **commit** with **push**. A commit exists locally until it is pushed.
- Do not confuse `git pull` with a **pull request**. The command updates a local branch; the GitHub feature proposes a reviewed merge.
- Read an error message before retrying. Repeating `push`, `pull`, or authentication commands rarely corrects an unexplained problem.

Use these inspection commands when uncertain:

```bash
git status
git remote -v
git branch -vv
git log --oneline --graph --decorate --all -n 20
gh auth status
```

---

## Part 7: Use common Visual Studio Code features

Start VS Code with the project folder as the workspace:

```bash
code .
```

If VS Code asks whether you trust the authors, confirm only because this lab folder came from your instructor and you have already reviewed its files.

### 7.1 Install course extensions

Open Extensions with `Ctrl+Shift+X`. Search for and install:

- **Python**, published by Microsoft (`ms-python.python`).
- **Pylance**, published by Microsoft (`ms-python.vscode-pylance`).

You may also install them from the terminal:

```bash
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
```

Install extensions only from publishers approved for the course. Extensions run code with the permissions of your user account.

### 7.2 Explore the interface

Use the Activity Bar on the left to open these views:

- **Explorer**: browse, create, rename, and organize files.
- **Search**: search across the project; open it with `Ctrl+Shift+F`.
- **Source Control**: inspect Git changes, stage files, and review diffs.
- **Run and Debug**: start a program with a debugger and inspect state.
- **Extensions**: add and manage approved editor capabilities.

Toggle the integrated terminal with ``Ctrl+` ``. Confirm that it opens in the project directory:

```bash
pwd
git status
```

### 7.3 Select the project interpreter

Open the Command Palette with `Ctrl+Shift+P`. Run **Python: Select Interpreter** and choose the interpreter inside `.venv`.

Open a new integrated terminal. VS Code should activate the environment automatically. Confirm:

```bash
python -c "import sys; print(sys.executable)"
```

The printed path must contain the current project and `.venv`.

### 7.4 Edit, search, format, and navigate

Open `verify_workstation.py` and practice:

- `Ctrl+P`: quickly open a file by name.
- `Ctrl+Shift+P`: run an editor command.
- `Ctrl+F`: search in the current file.
- `Ctrl+Shift+F`: search throughout the project.
- `F2`: rename a symbol with language awareness.
- `F12`: go to a definition when one is available.
- `Shift+Alt+F`: format the current document.
- `Ctrl+S`: save the current file.
- **View > Problems**: inspect diagnostics reported by the Python tools.

Hover over `yaml.safe_load` and `requests.__version__` to view type and documentation information supplied by the language service.

### 7.5 Run and debug Python

Open `verify_workstation.py`. Click in the margin beside the line:

```python
device_names = [device["name"] for device in inventory["devices"]]
```

A red breakpoint marker appears. Press `F5`, choose **Python File** if prompted, and observe the program pause.

While paused:

1. Inspect variables in the Run and Debug view.
2. Add `inventory` to the Watch area.
3. Hover over local variables to inspect their values.
4. Press `F10` to step over the current line.
5. Use the Debug Console to evaluate `len(inventory["devices"])`.
6. Press `F5` to continue.

Remove the breakpoint by clicking it again.

### 7.6 Review Git changes visually

In `inventory.yaml`, change `training-lab` to `devnet-classroom` and save the file. Open Source Control with `Ctrl+Shift+G`, then select the changed file to see a side-by-side diff.

Do not commit the change yet. Open the Command Palette and run **Git: Revert Selected Ranges** or use the Source Control discard action to restore it. Confirm in the integrated terminal:

```bash
git status
```

The working tree should be clean.

---

## Part 8: Introduction to Cisco DevNet Sandbox

Cisco DevNet Sandbox provides hosted Cisco products and topologies for learning, development, API testing, and automation. The catalog and specific lab versions change over time, so search the current catalog rather than relying only on a remembered lab name.

Two access models are common:

| Sandbox type | Access | Advantages | Constraints |
|---|---|---|---|
| Always-On | Shared and immediately available | No provisioning delay; useful for a quick API call | Shared state; restricted administrative access |
| Reservation | Private for the reservation period, normally through VPN | Administrative access and a controlled environment | Must be scheduled; provisioning takes time; state is not retained after the reservation |

For this course, use a **reservation-based sandbox whenever the exercise changes state, requires administrative access, or needs predictable data**. An Always-On sandbox remains useful for short, read-only API exercises.

Cisco's current documentation states that reservation labs are private, usually require VPN access, and cannot be saved for a later reservation. Availability and provisioning time vary. See the [DevNet Sandbox getting-started guide](https://developer.cisco.com/docs/sandbox/getting-started/), [first reservation guide](https://developer.cisco.com/docs/sandbox/first-reservation-guide/), and [sandbox FAQ](https://developer.cisco.com/docs/sandbox/faqs/).

### 8.1 Sign in and inspect the catalog

1. Open [Cisco DevNet Sandbox](https://developer.cisco.com/sandbox/).
2. Select **Get Started with Sandbox** and sign in with your Cisco.com account.
3. Set the account's current location or time zone so scheduled reservations use the expected local time.
4. Inspect the catalog filters and identify entries labeled **Reserve** and **Always-On**.
5. Search for **Catalyst Center**.

For the enterprise-networking and API portions of this course, prefer the current **Cisco Catalyst Center reservation sandbox** when it is available. Cisco currently documents both an Always-On option and a reservable Catalyst Center environment. The reservable environment supports controlled API automation against a private lab. Review the current version and capabilities on the [official Catalyst Center sandbox page](https://developer.cisco.com/docs/catalyst-center/sandboxes/) before reserving.

If that sandbox is unavailable, select another reservable environment that supports the learning objective, such as a current model-driven networking or Cisco platform sandbox. Record the exact sandbox name and version because endpoints and credentials differ between environments.

### 8.2 Make a reservation

1. Select the chosen sandbox's **Reserve** action.
2. Choose a start time that allows for provisioning before the class activity.
3. Choose only the duration you need so that the shared resource becomes available to another learner afterward.
4. Review the reservation time zone, start time, end time, and lab description.
5. Submit the reservation.
6. Wait for the separate **Lab Ready** notification before attempting to connect. A message saying that provisioning has started does not mean the environment is ready.

Reservation capacity is finite. Coordinate times with the instructor and cancel reservations that will not be used.

### 8.3 Locate the lab information

Open the active reservation from **Lab Management > Reservations**. Locate and review:

- The topology or blueprint and the role of each resource.
- The **Instructions** panel.
- The **Output** window, including provisioning status.
- Device or controller IP addresses and resource attributes.
- Administrative credentials supplied for the reservation.
- The VPN server, user name, and temporary password in the Lab Ready email or output window.
- The reservation end time.

Do not copy sandbox credentials into source code, screenshots, Git commits, chat systems, or shared documents.

### 8.4 Connect through the VPN

Most reservable environments use a VPN because their resources have private addresses. Use the Cisco Secure Client/AnyConnect download and instructions provided with the reservation when available.

Cisco also documents OpenConnect as a community alternative for Linux but states that it is not officially supported. If your instructor authorizes it, install it with:

```bash
sudo apt update
sudo apt install -y openconnect
```

Connect using the VPN server from the Lab Ready message, not a value copied from another learner:

```bash
sudo openconnect VPN_SERVER_FROM_LAB_READY_MESSAGE
```

Enter the temporary reservation user name and password when prompted. Leave the process running while using the lab. See Cisco's [Linux OpenConnect guidance](https://developer.cisco.com/docs/sandbox/tips-tricks/) for the current caveat and workflow.

After the VPN connects, open a second terminal and inspect the resulting routes:

```bash
ip -brief address
ip route
```

Test only a resource listed in your reservation topology:

```bash
ping -c 3 SANDBOX_RESOURCE_IP
curl -kI https://SANDBOX_RESOURCE_IP/
```

Replace the placeholder with an assigned address. `-k` permits a temporary lab's self-signed HTTPS certificate for this connectivity check. Do not make certificate verification globally insecure and do not use `verify=False` as a default in later Python programs.

If connectivity fails, check in this order:

1. The reservation shows **Ready**, not Setup, Teardown, or Ended.
2. The VPN client reports a connected state.
3. The VPN server and credentials came from your current reservation.
4. `ip route` contains routes for the sandbox networks.
5. The destination address matches a resource in the active topology.
6. A local or organizational firewall is not blocking the required VPN or application traffic.
7. The Instructions and Output panels do not report a provisioning failure.

### 8.5 Record a safe sandbox profile

Create a file that records non-secret context only:

```bash
cd ~/devnet-associate/labs/lab01
cat > sandbox-profile.txt <<'EOF'
Sandbox name:
Sandbox version:
Reservation start:
Reservation end:
Primary controller or platform:
VPN required: yes/no
Lab instructions reviewed: yes/no
EOF
```

Complete the fields without adding passwords, tokens, cookies, or private keys. Add the file to `.gitignore` because reservation details are temporary:

```bash
printf 'sandbox-profile.txt\n' >> .gitignore
git diff
git add .gitignore
git commit -m "Ignore temporary sandbox profile"
```

### 8.6 Disconnect and release resources

When the exploration is complete:

1. Close controller or device sessions.
2. Stop the VPN client cleanly. For a foreground OpenConnect session, press `Ctrl+C` in its terminal.
3. Confirm that temporary sandbox routes have disappeared with `ip route`.
4. Cancel or end the reservation if you no longer need the remaining time and the portal offers that action.
5. Remove any temporary credential files. Do not attempt to preserve the sandbox state; reservation environments are designed to be disposable.

---

## Part 9: Final validation

From the project directory, activate the environment and run the final checks:

```bash
cd ~/devnet-associate/labs/lab01
source .venv/bin/activate
python verify_workstation.py
python -m pip check
git status
git log --oneline --graph --decorate --all
git remote -v
gh auth status
code --version
```

Your lab is complete when all of the following are true:

- Ubuntu, Python, pip, Git, SSH, `curl`, `jq`, and VS Code report versions.
- The project uses the Python executable inside `.venv`.
- `verify_workstation.py` runs successfully.
- Git contains the intended commits and reports a clean working tree.
- The private GitHub repository contains the pushed Lab 01 commits.
- You can explain and perform clone, pull, status, add, commit, push, branch, and pull-request operations.
- VS Code uses the `.venv` interpreter and can run the program under the debugger.
- You can explain where to find a reservation's topology, instructions, output, credentials, and end time.
- You reserved or identified a suitable reservable DevNet Sandbox and understand its VPN requirement.
- No credential or token has been stored in the project or Git history.

Deactivate the environment when finished:

```bash
deactivate
```

## Command reference

| Task | Command |
|---|---|
| Print working directory | `pwd` |
| List detailed directory contents | `ls -la` |
| Change directory | `cd PATH` |
| Create directories | `mkdir -p PATH` |
| Copy a file or directory | `cp SOURCE DESTINATION`, `cp -R SOURCE DESTINATION` |
| Rename or move | `mv SOURCE DESTINATION` |
| Remove a file | `rm FILE` |
| Read/search text | `cat`, `less`, `head`, `tail`, `grep` |
| Find filesystem entries | `find PATH ...` |
| Inspect addresses and routes | `ip -brief address`, `ip route` |
| Inspect listening sockets | `ss -tuln` |
| Install Ubuntu packages | `sudo apt install PACKAGE` |
| Create a virtual environment | `python3 -m venv .venv` |
| Activate the environment | `source .venv/bin/activate` |
| Install Python dependencies | `python -m pip install -r requirements.txt` |
| Leave the environment | `deactivate` |
| Inspect Git state | `git status`, `git diff`, `git log` |
| Clone a GitHub repository | `git clone HTTPS_URL` |
| Download remote information | `git fetch origin` |
| Update the current branch | `git pull --ff-only` |
| Publish local commits | `git push` |
| Create and switch to a branch | `git switch -c BRANCH_NAME` |
| Check GitHub authentication | `gh auth status` |
| Open the current folder in VS Code | `code .` |

## Further references

- [Ubuntu command-line tutorial](https://ubuntu.com/tutorials/command-line-for-beginners)
- [Python virtual environments](https://docs.python.org/3/library/venv.html)
- [pip user guide](https://pip.pypa.io/en/stable/user_guide/)
- [Git reference](https://git-scm.com/docs)
- [GitHub account setup](https://docs.github.com/en/get-started/onboarding/getting-started-with-your-github-account)
- [GitHub Git basics](https://docs.github.com/en/get-started/git-basics)
- [GitHub pull requests](https://docs.github.com/en/pull-requests)
- [Visual Studio Code documentation](https://code.visualstudio.com/docs)
- [Cisco DevNet Sandbox getting started](https://developer.cisco.com/docs/sandbox/getting-started/)
- [Cisco DevNet first reservation guide](https://developer.cisco.com/docs/sandbox/first-reservation-guide/)
- [Cisco Catalyst Center sandboxes](https://developer.cisco.com/docs/catalyst-center/sandboxes/)

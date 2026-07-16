#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
env_file="${project_dir}/.env"

if [[ ! -f "${env_file}" ]]; then
  echo "Create .env from .env.example before running Ansible." >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "${env_file}"
set +a

exec ansible-playbook "$@"


#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-https://repository.qtpyvcp.com/buildbot}"
API_BUILDERS="${BASE_URL%/}/api/v2/builders?limit=500"
API_SCHEDULERS="${BASE_URL%/}/api/v2/schedulers?limit=500"

expected_builders=(
  "probe_basic-pyside6-x86"
  "probe_basic-pyside6-x86-dev"
  "probe_basic-pyside6-arm64"
  "probe_basic-pyside6-arm64-dev"
)

expected_schedulers=(
  "probe_basic_pyside6_x86_stable"
  "probe_basic_pyside6_x86_dev"
  "probe_basic_pyside6_arm64_stable"
  "probe_basic_pyside6_arm64_dev"
)

echo "Checking Buildbot runtime at: ${BASE_URL}"
echo

builders_json="$(curl -fsSL "${API_BUILDERS}")"
schedulers_json="$(curl -fsSL "${API_SCHEDULERS}")"

missing=0

echo "Builders:"
for name in "${expected_builders[@]}"; do
  if grep -Fq "\"name\": \"${name}\"" <<<"${builders_json}"; then
    echo "  [ok] ${name}"
  else
    echo "  [missing] ${name}"
    missing=$((missing + 1))
  fi
done

echo
echo "Schedulers:"
for name in "${expected_schedulers[@]}"; do
  if grep -Fq "\"name\": \"${name}\"" <<<"${schedulers_json}"; then
    echo "  [ok] ${name}"
  else
    echo "  [missing] ${name}"
    missing=$((missing + 1))
  fi
done

echo
if [[ ${missing} -eq 0 ]]; then
  echo "Result: runtime matches expected Probe Basic PySide6 wiring."
  exit 0
fi

echo "Result: ${missing} expected names are still missing in runtime config."
echo "Hint: maintainer should reload/restart Buildbot master and re-run this script."
exit 2

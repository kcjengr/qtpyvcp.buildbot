#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-https://repository.qtpyvcp.com/buildbot}"
API_BUILDERS="${BASE_URL%/}/api/v2/builders?limit=500"
API_SCHEDULERS="${BASE_URL%/}/api/v2/schedulers?limit=500"

# Expected builder names from current master.cfg matrix.
expected_builders=(
  "qtpyvcp-pyqt5-x86"
  "qtpyvcp-pyqt5-x86-dev"
  "qtpyvcp-pyqt5-arm64"
  "qtpyvcp-pyqt5-arm64-dev"
  "qtpyvcp-pyside6-x86"
  "qtpyvcp-pyside6-x86-dev"
  "qtpyvcp-pyside6-arm64"
  "qtpyvcp-pyside6-arm64-dev"
  "probe_basic-pyqt5-x86"
  "probe_basic-pyqt5-x86-dev"
  "probe_basic-pyqt5-arm64"
  "probe_basic-pyqt5-arm64-dev"
  "probe_basic-pyside6-x86"
  "probe_basic-pyside6-x86-dev"
  "probe_basic-pyside6-arm64"
  "probe_basic-pyside6-arm64-dev"
  "turbonc-pyqt5-x86"
  "turbonc-pyqt5-x86-dev"
  "turbonc-pyqt5-arm64"
  "turbonc-pyqt5-arm64-dev"
  "turbonc-pyside6-x86"
  "turbonc-pyside6-x86-dev"
  "turbonc-pyside6-arm64"
  "turbonc-pyside6-arm64-dev"
  "monokrom-pyqt5-x86"
  "monokrom-pyqt5-x86-dev"
  "monokrom-pyqt5-arm64"
  "monokrom-pyqt5-arm64-dev"
  "monokrom-pyside6-x86"
  "monokrom-pyside6-x86-dev"
  "monokrom-pyside6-arm64"
  "monokrom-pyside6-arm64-dev"
)

# Expected scheduler names from current master.cfg matrix.
expected_schedulers=(
  "qtpyvcp_pyqt5_x86_stable"
  "qtpyvcp_pyqt5_x86_dev"
  "qtpyvcp_pyqt5_arm64_stable"
  "qtpyvcp_pyqt5_arm64_dev"
  "qtpyvcp_pyside6_x86_stable"
  "qtpyvcp_pyside6_x86_dev"
  "qtpyvcp_pyside6_arm64_stable"
  "qtpyvcp_pyside6_arm64_dev"
  "probe_basic_x86_stable"
  "probe_basic_x86_dev"
  "probe_basic_arm64_stable"
  "probe_basic_arm64_dev"
  "probe_basic_pyside6_x86_stable"
  "probe_basic_pyside6_x86_dev"
  "probe_basic_pyside6_arm64_stable"
  "probe_basic_pyside6_arm64_dev"
  "tnc_pyqt5_x86_stable"
  "tnc_pyqt5_x86_dev"
  "tnc_pyqt5_arm64_stable"
  "tnc_pyqt5_arm64_dev"
  "tnc_pyside6_x86_stable"
  "tnc_pyside6_x86_dev"
  "tnc_pyside6_arm64_stable"
  "tnc_pyside6_arm64_dev"
  "monokrom_pyqt5_x86_stable"
  "monokrom_pyqt5_x86_dev"
  "monokrom_pyqt5_arm64_stable"
  "monokrom_pyqt5_arm64_dev"
  "monokrom_pyside6_x86_stable"
  "monokrom_pyside6_x86_dev"
  "monokrom_pyside6_arm64_stable"
  "monokrom_pyside6_arm64_dev"
)

contains_name() {
  local name="$1"
  local payload="$2"
  grep -Fq "\"name\": \"${name}\"" <<<"${payload}"
}

print_check_section() {
  local label="$1"
  local payload="$2"
  shift 2
  local names=("$@")
  local section_missing=0

  echo "${label}:"
  for name in "${names[@]}"; do
    if contains_name "${name}" "${payload}"; then
      echo "  [ok] ${name}"
    else
      echo "  [missing] ${name}"
      section_missing=$((section_missing + 1))
    fi
  done
  echo

  return ${section_missing}
}

echo "Checking Buildbot matrix runtime at: ${BASE_URL}"
echo

builders_json="$(curl -fsSL "${API_BUILDERS}")"
schedulers_json="$(curl -fsSL "${API_SCHEDULERS}")"

missing_total=0

if print_check_section "Builders" "${builders_json}" "${expected_builders[@]}"; then
  section_missing=0
else
  section_missing=$?
fi
missing_total=$((missing_total + section_missing))

if print_check_section "Schedulers" "${schedulers_json}" "${expected_schedulers[@]}"; then
  section_missing=0
else
  section_missing=$?
fi
missing_total=$((missing_total + section_missing))

echo "Summary:"
echo "  Expected builders:   ${#expected_builders[@]}"
echo "  Expected schedulers: ${#expected_schedulers[@]}"

echo
if [[ ${missing_total} -eq 0 ]]; then
  echo "Result: runtime matches full matrix from master.cfg."
  exit 0
fi

echo "Result: ${missing_total} expected names are missing in runtime config."
echo "Hint: maintainer should reconfig/restart Buildbot master, then re-run this script."
exit 2

#!/usr/bin/env bash
# Exercise install.sh and with-helm3 against a fake release served from a local directory. No network.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
failures=0

check() {
  local name="$1"
  shift
  if ("$@") >/dev/null 2>&1; then
    echo "ok   $name"
  else
    echo "FAIL $name"
    failures=$((failures + 1))
  fi
}

fake_release() {
  local version="$1" dir="$2"
  mkdir -p "$dir" "$WORK/pkg/linux-amd64"
  cat >"$WORK/pkg/linux-amd64/helm" <<EOF
#!/bin/sh
[ "\$1" = version ] && { echo v$version; exit 0; }
echo "helm \$*"
EOF
  chmod +x "$WORK/pkg/linux-amd64/helm"
  local archive="helm-v$version-linux-amd64.tar.gz"
  tar -czf "$dir/$archive" -C "$WORK/pkg" linux-amd64
  echo "$(shasum -a 256 "$dir/$archive" | cut -d' ' -f1)  $archive" >"$dir/$archive.sha256sum"
}

run_install() {
  local release="$1" prefix="$2"
  shift 2
  HELM3_BASE_URL="file://$release" HELM3_HOME="$prefix/home" HELM3_BIN_DIR="$prefix/bin" \
    HELM3_OS=Linux HELM3_ARCH=amd64 "$HERE/install.sh" "$@"
}

fails_with() {
  local pattern="$1"
  shift
  local output status
  output="$("$@" 2>&1)"
  status=$?
  [ "$status" -ne 0 ] && echo "$output" | grep -q "$pattern"
}

t_install_layout() {
  run_install "$WORK/release" "$WORK/ok" &&
    [ -x "$WORK/ok/home/v3.21.3/bin/helm" ] &&
    [ "$(readlink "$WORK/ok/home/current")" = v3.21.3 ] &&
    [ -x "$WORK/ok/bin/with-helm3" ] && [ ! -L "$WORK/ok/bin/with-helm3" ] &&
    [ ! -e "$WORK/ok/bin/helm" ]
}

t_wrapper_status_and_path() {
  local out status
  out="$(HELM3_HOME="$WORK/ok/home" "$WORK/ok/bin/with-helm3" sh -c 'helm foo; exit 7')"
  status=$?
  [ "$status" -eq 7 ] && [ "$out" = "helm foo" ]
}

t_wrapper_missing() {
  fails_with install.sh env HELM3_HOME="$WORK/none" "$WORK/ok/bin/with-helm3" true &&
    HELM3_HOME="$WORK/none" "$WORK/ok/bin/with-helm3" true 2>/dev/null
  [ $? -eq 69 ]
}

t_wrapper_rejects_helm4() {
  printf '#!/bin/sh\necho v4.2.2\n' >"$WORK/helm4"
  chmod +x "$WORK/helm4"
  HELM3_BIN="$WORK/helm4" "$WORK/ok/bin/with-helm3" true 2>/dev/null
  [ $? -eq 69 ]
}

t_wrapper_rejects_alternate_name() {
  # A valid Helm 3 under another name must not run: PATH lookup of `helm` would find a different Helm.
  ln -s "$WORK/ok/home/current/bin/helm" "$WORK/helm3"
  HELM3_BIN="$WORK/helm3" "$WORK/ok/bin/with-helm3" touch "$WORK/ran" 2>/dev/null
  [ $? -eq 69 ] && [ ! -e "$WORK/ran" ]
}

t_wrapper_usage() {
  "$WORK/ok/bin/with-helm3" 2>/dev/null
  [ $? -eq 64 ]
}

t_checksum_mismatch() {
  fails_with "checksum mismatch" run_install "$WORK/bad" "$WORK/bad-out" &&
    [ ! -e "$WORK/bad-out/home" ] && [ ! -e "$WORK/bad-out/bin" ]
}

t_unsupported_arch() {
  fails_with "unsupported architecture" env HELM3_ARCH=riscv64 HELM3_HOME="$WORK/rv" "$HERE/install.sh" &&
    [ ! -e "$WORK/rv" ]
}

t_unsupported_os() {
  fails_with "unsupported OS" env HELM3_OS=Plan9 "$HERE/install.sh"
}

t_rejects_helm4_version() {
  fails_with "not a Helm 3" "$HERE/install.sh" --version 4.2.2
}

t_dry_run() {
  run_install "$WORK/release" "$WORK/dry" --dry-run && [ ! -e "$WORK/dry" ]
}

fake_release 3.21.3 "$WORK/release"
fake_release 3.21.3 "$WORK/bad"
echo "0000000000000000000000000000000000000000000000000000000000000000  helm-v3.21.3-linux-amd64.tar.gz" \
  >"$WORK/bad/helm-v3.21.3-linux-amd64.tar.gz.sha256sum"

check "install lays out a versioned helm and a copied wrapper" t_install_layout
check "wrapper puts helm 3 first on PATH and returns the command's status" t_wrapper_status_and_path
check "wrapper refuses a missing install with status 69 and setup advice" t_wrapper_missing
check "wrapper refuses a helm that is not v3" t_wrapper_rejects_helm4
check "wrapper refuses a HELM3_BIN not named helm and runs nothing" t_wrapper_rejects_alternate_name
check "wrapper without a command is a usage error" t_wrapper_usage
check "checksum mismatch installs nothing" t_checksum_mismatch
check "unsupported architecture fails before any download" t_unsupported_arch
check "unsupported OS fails" t_unsupported_os
check "a Helm 4 version is rejected" t_rejects_helm4_version
check "dry run touches nothing" t_dry_run

[ "$failures" -eq 0 ] || {
  echo "$failures failed"
  exit 1
}
echo "all passed"

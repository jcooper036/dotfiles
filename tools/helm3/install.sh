#!/usr/bin/env bash
# Install a versioned Helm 3 and the with-helm3 wrapper into user-local directories.
set -euo pipefail

DEFAULT_VERSION="3.21.3"
BASE_URL="${HELM3_BASE_URL:-https://get.helm.sh}"
HELM3_HOME="${HELM3_HOME:-$HOME/.local/share/helm3}"
BIN_DIR="${HELM3_BIN_DIR:-$HOME/.local/bin}"
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<EOF
Usage: install.sh [--version X.Y.Z] [--dry-run]

Installs Helm $DEFAULT_VERSION (or --version, which must be a 3.x release) and the with-helm3 wrapper.

  Helm binary   \$HELM3_HOME/v<version>/bin/helm   (default: ~/.local/share/helm3)
  Current link  \$HELM3_HOME/current -> v<version>
  Wrapper       \$HELM3_BIN_DIR/with-helm3          (default: ~/.local/bin; a copy, not a link)

The archive's published .sha256sum is fetched from \$HELM3_BASE_URL (default https://get.helm.sh)
and must match before anything is installed. A helm already on your PATH is never touched.
Supported platforms: Darwin and Linux on arm64 and amd64. Rerunning is safe.

  --dry-run   print what would be fetched and installed, and touch nothing
EOF
}

die() {
  echo "install.sh: $*" >&2
  exit 1
}

detect_os() {
  case "${HELM3_OS:-$(uname -s)}" in
    Darwin) echo darwin ;;
    Linux) echo linux ;;
    *) die "unsupported OS '${HELM3_OS:-$(uname -s)}' (supported: Darwin, Linux)" ;;
  esac
}

detect_arch() {
  case "${HELM3_ARCH:-$(uname -m)}" in
    arm64 | aarch64) echo arm64 ;;
    x86_64 | amd64) echo amd64 ;;
    *) die "unsupported architecture '${HELM3_ARCH:-$(uname -m)}' (supported: arm64, amd64)" ;;
  esac
}

sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | cut -d' ' -f1
  else
    shasum -a 256 "$1" | cut -d' ' -f1
  fi
}

version="$DEFAULT_VERSION"
dry_run=0
while [ $# -gt 0 ]; do
  case "$1" in
    --version)
      [ $# -ge 2 ] || die "--version needs a value"
      version="${2#v}"
      shift 2
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      usage >&2
      exit 64
      ;;
  esac
done

[[ "$version" =~ ^3\.[0-9]+\.[0-9]+$ ]] || die "version '$version' is not a Helm 3.x.y release"

os="$(detect_os)"
arch="$(detect_arch)"
archive="helm-v${version}-${os}-${arch}.tar.gz"
destination="$HELM3_HOME/v$version"

if [ "$dry_run" -eq 1 ]; then
  echo "fetch    $BASE_URL/$archive"
  echo "verify   $BASE_URL/$archive.sha256sum"
  echo "install  $destination/bin/helm"
  echo "link     $HELM3_HOME/current -> v$version"
  echo "wrapper  $BIN_DIR/with-helm3"
  exit 0
fi

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

curl -fsSL "$BASE_URL/$archive" -o "$work/$archive" || die "could not download $BASE_URL/$archive"
curl -fsSL "$BASE_URL/$archive.sha256sum" -o "$work/expected" || die "could not download $BASE_URL/$archive.sha256sum"

expected="$(awk '{print $1; exit}' "$work/expected")"
actual="$(sha256_of "$work/$archive")"
[ -n "$expected" ] || die "published checksum for $archive is empty"
[ "$expected" = "$actual" ] || die "checksum mismatch for $archive: expected $expected, got $actual; nothing installed"

tar -xzf "$work/$archive" -C "$work" "$os-$arch/helm" || die "$archive does not contain $os-$arch/helm"
reported="$("$work/$os-$arch/helm" version --template '{{.Version}}')" || die "the downloaded helm does not run"
[ "$reported" = "v$version" ] || die "downloaded helm reports '$reported', expected v$version"

mkdir -p "$destination/bin" "$BIN_DIR"
install -m 0755 "$work/$os-$arch/helm" "$destination/bin/helm"
ln -sfn "v$version" "$HELM3_HOME/current"
install -m 0755 "$SELF_DIR/with-helm3" "$BIN_DIR/with-helm3"

echo "installed Helm v$version at $destination/bin/helm"
echo "installed $BIN_DIR/with-helm3"
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) echo "note: $BIN_DIR is not on PATH" >&2 ;;
esac

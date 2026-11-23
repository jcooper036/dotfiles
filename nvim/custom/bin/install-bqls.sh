#!/bin/sh
# Install a pinned, checksum-verified bqls (BigQuery language server) binary.
# Usage: install-bqls.sh <dest_dir>
# To upgrade: bump VERSION and replace the checksums from
# https://github.com/kitagry/bqls/releases/download/v<VERSION>/bqls_<VERSION>_checksums.txt
set -eu

VERSION="0.8.8"

DEST="${1:?usage: install-bqls.sh <dest_dir>}"

case "$(uname -s)_$(uname -m)" in
  Darwin_arm64)  PLATFORM="darwin_arm64"; SHA="36801ac970c872084ca996bb2b9f04b1f846a2a14f7026d7c383996d65e38fef" ;;
  Darwin_x86_64) PLATFORM="darwin_amd64"; SHA="2d512bc9ca2cccc6604d1101580ee7c5be270ad0061dd764340dd2f0b634a074" ;;
  Linux_x86_64)  PLATFORM="linux_amd64";  SHA="92049fecf9acb09424c236fdcfc74fd99001b5bdcf430588ec66e523ee952894" ;;
  Linux_aarch64) PLATFORM="linux_arm64";  SHA="975297a1b77e3d7343f4a8890abf54cd87fd5e5ead2e37a29d156ef722c53c66" ;;
  *) echo "bqls: unsupported platform $(uname -s) $(uname -m)" >&2; exit 1 ;;
esac

URL="https://github.com/kitagry/bqls/releases/download/v${VERSION}/bqls_${VERSION}_${PLATFORM}.tar.gz"
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

curl -fsSL "$URL" -o "$TMP"

if command -v sha256sum >/dev/null 2>&1; then
  ACTUAL="$(sha256sum "$TMP" | cut -d' ' -f1)"
else
  ACTUAL="$(shasum -a 256 "$TMP" | cut -d' ' -f1)"
fi
if [ "$ACTUAL" != "$SHA" ]; then
  echo "bqls: checksum mismatch for $URL (got $ACTUAL, want $SHA)" >&2
  exit 1
fi

mkdir -p "$DEST"
tar -xzf "$TMP" -C "$DEST" bqls
chmod +x "$DEST/bqls"
echo "bqls v${VERSION} installed to $DEST/bqls"

"""Attachment screening: a type blocklist applied to the bytes before anything touches disk.

This is not antivirus. It refuses file types that execute or run macros when opened, archives it
cannot see inside, and anything whose content contradicts a harmless-looking name. Gmail's own
server-side malware scanning is the other layer.
"""

import io
import re
import unicodedata
import zipfile
from pathlib import PurePosixPath, PureWindowsPath

BLOCKED_EXTENSIONS = frozenset(
    {
        # Windows executables, installers, scripts, shortcuts
        "exe", "dll", "com", "scr", "pif", "cpl", "msi", "msp", "mst", "msc", "bat", "cmd", "ps1", "psm1",
        "vbs", "vbe", "js", "jse", "wsf", "wsh", "hta", "lnk", "reg", "inf", "gadget", "appx", "msix",
        "application", "appref-ms", "xll", "url", "scf", "settingcontent-ms",
        # macOS / Unix
        "app", "pkg", "mpkg", "dmg", "command", "tool", "workflow", "scpt", "applescript", "sh", "bash",
        "zsh", "csh", "ksh", "run", "bin", "elf", "dylib", "so", "terminal", "webloc", "inetloc",
        # Cross-platform code
        "jar", "class", "py", "pyc", "pyw", "pl", "rb", "php", "lua",
        # Macro-enabled Office formats
        "docm", "dotm", "xlsm", "xltm", "xlam", "xlsb", "pptm", "potm", "ppam", "ppsm", "sldm",
        # Markup that runs script when opened locally
        "html", "htm", "xhtml", "shtml", "mht", "mhtml", "svg", "svgz",
        # Disk images and archives we cannot inspect
        "iso", "img", "vhd", "vhdx", "rar", "7z", "cab", "ace", "arj", "tar", "gz", "tgz", "bz2", "xz", "lzh",
    }
)

BLOCKED_MIME_TYPES = frozenset(
    {
        "application/x-msdownload", "application/x-msdos-program", "application/x-ms-installer",
        "application/x-msi", "application/vnd.microsoft.portable-executable", "application/x-executable",
        "application/x-mach-binary", "application/x-sh", "application/x-csh", "application/x-shellscript",
        "application/java-archive", "application/x-java-archive", "application/x-apple-diskimage",
        "application/javascript", "text/javascript", "application/hta", "text/html", "image/svg+xml",
        "application/x-rar-compressed", "application/vnd.rar", "application/x-7z-compressed",
        "application/vnd.ms-word.document.macroenabled.12", "application/vnd.ms-excel.sheet.macroenabled.12",
        "application/vnd.ms-excel.sheet.binary.macroenabled.12", "application/vnd.ms-powerpoint.presentation.macroenabled.12",
    }
)

# Leading bytes of formats that are executable or uninspectable no matter what the file is named.
BLOCKED_MAGIC = {
    b"MZ": "Windows executable",
    b"\x7fELF": "Linux executable",
    b"\xfe\xed\xfa\xce": "Mach-O executable",
    b"\xfe\xed\xfa\xcf": "Mach-O executable",
    b"\xce\xfa\xed\xfe": "Mach-O executable",
    b"\xcf\xfa\xed\xfe": "Mach-O executable",
    b"\xca\xfe\xba\xbe": "Mach-O universal binary or Java class",
    b"#!": "script with an interpreter line",
    b"Rar!": "RAR archive",
    b"7z\xbc\xaf\x27\x1c": "7-Zip archive",
    b"\x1f\x8b": "gzip archive",
    b"BZh": "bzip2 archive",
    b"\xfd7zXZ\x00": "xz archive",
    b"MSCF": "Windows cabinet archive",
    b"koly": "disk image",
}
OLE_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"  # legacy .doc/.xls/.ppt/.msg container
OLE_VBA_MARKER = "_VBA_PROJECT".encode("utf-16-le")
ZIP_MAGIC = b"PK\x03\x04"
ZIP_MAX_UNCOMPRESSED = 1 << 30  # refuse zip bombs


class BlockedAttachment(ValueError):
    pass


def extension(name: str) -> str:
    return PurePosixPath(name).suffix.lower().lstrip(".")


def safe_filename(name: str) -> str:
    """Reduce an attacker-controlled filename to a single harmless path component."""
    name = unicodedata.normalize("NFKC", name)
    name = PureWindowsPath(PurePosixPath(name).name).name  # drop any directory part, either separator
    name = "".join(c for c in name if unicodedata.category(c)[0] != "C")  # control and bidi-override chars
    name = re.sub(r'[<>:"|?*]', "_", name).strip().lstrip(".")
    return name[:200] or "attachment"


def _check_zip(data: bytes) -> None:
    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
        members = archive.infolist()
    except zipfile.BadZipFile as exc:
        raise BlockedAttachment(f"looks like a zip archive but cannot be read ({exc})") from exc
    if sum(m.file_size for m in members) > ZIP_MAX_UNCOMPRESSED:
        raise BlockedAttachment("archive expands to more than 1 GiB")
    for member in members:
        if member.flag_bits & 0x1:
            raise BlockedAttachment("archive is password-protected, so its contents cannot be checked")
        if PurePosixPath(member.filename).name.lower() == "vbaproject.bin":
            raise BlockedAttachment("Office document contains macros")
        ext = extension(member.filename)
        if ext in BLOCKED_EXTENSIONS or ext == "zip":
            raise BlockedAttachment(f"archive contains a blocked file: {member.filename}")


def check(filename: str, mime_type: str, data: bytes) -> None:
    """Raise BlockedAttachment if this attachment should not be written to disk."""
    ext = extension(filename)
    if ext in BLOCKED_EXTENSIONS:
        raise BlockedAttachment(f".{ext} files are blocked")
    if mime_type.lower() in BLOCKED_MIME_TYPES:
        raise BlockedAttachment(f"{mime_type} attachments are blocked")
    for magic, kind in BLOCKED_MAGIC.items():
        if data.startswith(magic):
            raise BlockedAttachment(f"content is a {kind}")
    if data.startswith(ZIP_MAGIC):
        _check_zip(data)
    elif data.startswith(OLE_MAGIC) and OLE_VBA_MARKER in data:
        raise BlockedAttachment("Office document contains macros")

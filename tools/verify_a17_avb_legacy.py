#!/usr/bin/env python3
"""Inventory archived AVB signing-key risks. No key operations, no Android build."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
avbtool = (root / "avbtool.py").read_text(encoding="utf-8")
bp = (root / "Android.bp").read_text(encoding="utf-8")
vbmeta = (root / "libavb/avb_vbmeta_image.h").read_text(encoding="utf-8")
checks = {
    "historical secure storage env command": "ANDROID_SECURE_STORAGE_CMD" in avbtool,
    "legacy shell execution in signing path": "subprocess.Popen(secure_storage_cmd, shell=True" in avbtool,
    "secret passed using OpenSSL --passin argv": "'--passin', 'pass:' + key_password" in avbtool,
    "legacy temp key filename environment": "TMP__KEY_FILE_NAME" in avbtool,
    "separate signing helper entry points exist": "signing_helper_with_files" in avbtool and "signing_helper" in avbtool,
    "historical libavb_atx exists": (root / "libavb_atx").is_dir(),
    "modern libavb_cert is absent": not (root / "libavb_cert").exists(),
    "modern Rust interface is absent": not (root / "rust").exists(),
    "libavb build target remains present": 'name: "libavb"' in bp,
    "hashtree and verification flags are distinct": "AVB_VBMETA_IMAGE_FLAGS_HASHTREE_DISABLED" in vbmeta and "AVB_VBMETA_IMAGE_FLAGS_VERIFICATION_DISABLED" in vbmeta,
}
for label, passed in checks.items():
    print(f"{'PASS' if passed else 'FAIL'}: {label}")
if not all(checks.values()):
    raise SystemExit("Archived AVB source inventory drift detected; manual review required.")
print("PASS: archived source inventory only; no signing, build, vbmeta or boot test.")

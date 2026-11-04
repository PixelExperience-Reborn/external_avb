# P2 — archived PixelExperience external/avb: Android 17 verified boot / mondrian

**Date:** 2026-11-04. **Status:** archived source-only security audit. **Do not activate the historical AVB fork.** No Android 17 AVB build, signed target-files, device boot or rollback test has been performed.

## Source provenance and incompatible history

- PE-Reborn archive `external_avb` [`seventeen` commit `46a2e996260f7acf6c4d87d2702c8b208d24fb5f`](https://github.com/PixelExperience-Reborn/external_avb/commit/46a2e996260f7acf6c4d87d2702c8b208d24fb5f) merged `android-14.0.0_r21` in January 2024. It is not an AOSP 17 fork.
- Verified official [Android 17 tag `android-17.0.0_r1`](https://android.googlesource.com/platform/external/avb/+/refs/tags/android-17.0.0_r1): commit `ba2dec4b035b0a3b61c5f8f8a74d86bcd450b1ee`, tree `03312e0570b5893b9ac940e5ec3148287e4130e6`. This source includes `libavb_cert` and `rust` directories which are absent in the Android 14-era PE archive (the archive instead has `libavb_atx`). Keep the official Android 17 source in the staged manifest until there is a justified, reviewed AVB delta.
- Historical [PE commit `4400f585a341`](https://github.com/PixelExperience-Reborn/external_avb/commit/4400f585a341c55e1e86a6fce931776adabc761c) modifies `avbtool.py` to fetch an RSA key password from `ANDROID_SECURE_STORAGE_CMD`. It executes the command with `subprocess.Popen(..., shell=True)`, writes the key path to `TMP__KEY_FILE_NAME` environment, then passes the password to OpenSSL as `--passin pass:<password>`. Do **not** cherry-pick this signing pathway into Android 17: arbitrary shell command execution inherited from the environment and passphrases passed in process arguments pose signing-key exposure risks. The archive also exposes explicit `signing_helper` / `signing_helper_with_files` entry points; choose a separately reviewed signing design rather than patching cryptographic primitives blindly.

## Concrete mondrian boot-chain blockers from the hardware reference

- Existing (Lineage-derived, **not native PE-Reborn**) [sm8450-common BoardConfigCommon.mk](https://github.com/LF52406/mondrian_android_device_xiaomi_sm8450-common/blob/lineage-24.0/BoardConfigCommon.mk) sets `BOARD_AVB_ENABLE := true`, but points `BOARD_AVB_KEY_PATH`, `BOARD_AVB_RECOVERY_KEY_PATH` and `BOARD_AVB_VBMETA_SYSTEM_KEY_PATH` at **public repository test keys** in `external/avb/test/data/`. These are not release signing credentials.
- That reference also sets `BOARD_AVB_MAKE_VBMETA_IMAGE_ARGS += --flags 3`. In `libavb/avb_vbmeta_image.h`, bit 0 is `AVB_VBMETA_IMAGE_FLAGS_HASHTREE_DISABLED` and bit 1 is `AVB_VBMETA_IMAGE_FLAGS_VERIFICATION_DISABLED`. Combined value 3 disables both checks in vbmeta. This may be appropriate to an explicitly unlocked development build, but **must not silently become a release verified-boot policy**.
- Recovery uses its own AVB key, algorithm, rollback index/location; `vbmeta_system` has a security-patch-derived rollback index and location 2. The exact recovery/partition chain, key provenance and rollback locations must be checked against the eventual **independent PE-Reborn** board configuration and device bootloader, not guessed from a Lineage-based reference tree.
- Existing P0 `system/update_engine` and recovery audits already reject signature-verification and downgrade bypasses. External AVB may not reintroduce these through separate image/signing logic.

## Cross-base reuse policy

This audit **does not prohibit taking good solutions from modern LineageOS**. The PE-Reborn product is separate, but the proven mondrian/SM8450 hardware work can be adapted with scoped changes, upstream attribution, and Android17 build/runtime checks. The security issue here is **specific to public test keys, disabled verification flags and the old AVB signing helper**, not to LineageOS as a base. A safe configuration or a useful hardware fix from the LineageOS tree remains a candidate for the native PE-Reborn port.

## Acceptance gates

1. Preserve official AOSP17 `external/avb` source (commit/tree pinned above). Do not add the old PE repo to opt-in `aosp17_pe_*.xml` manifests.
2. Build **independently maintained PE-Reborn** `device/xiaomi/mondrian` and `device/xiaomi/sm8450-common` integration on AOSP17. The existing LineageOS 24.0 device/common trees are **current, valuable technical implementations of another Android base**, not obsolete code. Reuse or port suitable hardware configuration, boot/partition descriptions, board flags, HAL wiring and patches selectively, preserving relevant upstream attribution and licences. For each change, check source/API/Make/Soong dependencies, remove LineageOS-only product/namespace assumptions, and verify AOSP17 behaviour; never inherit incompatible pieces wholesale. Establish explicit developer versus release AVB policy, production signing-key custody, vbmeta chain and rollback indices. Do not commit private keys or put plaintext passphrases in process arguments.
3. Test `avbtool` and `libavb` on an actual Android17 Linux build; validate vbmeta descriptors, key hashes, rollback protection, AVB chained partitions, recovery/fastbootd and OTA signature enforcement.
4. Perform physical-device locked/unlocked-state checks only with a verified safe recovery plan. Never claim locked-boot support from a static source scan, and never bypass AVB to make an incomplete ROM appear bootable.

## Source-only CI

- `tools/verify_a17_avb_legacy.py` checks the exact archived signing-extension and old AVB directory layout without running signing helpers or processing any key material.
- **No historical AVB implementation has been ported.** `seventeen` is preserved.

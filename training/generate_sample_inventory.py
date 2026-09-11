"""
VoxSentinalX Training Dataset Inventory & Manifest Generator.
Catalogs every single audio sample in data/unified_corpus (Bona Fide Human & AI Voice Clones)
with metadata: Generator Type, Label, Duration, Sample Rate, File Size, and SHA256 Hash.
Exports JSON, CSV, and Markdown documentation.
"""
import os
import sys
import csv
import json
import hashlib
import time
import soundfile as sf
from collections import defaultdict

# Ensure UTF-8 stdout
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def compute_sha256(filepath: str) -> str:
    """Computes SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def generate_inventory(unified_dir: str = r"p:\VoxSentinalX\data\unified_corpus"):
    print("=" * 70)
    print("  📋 GENERATING VOXSENTINALX TRAINING DATASET INVENTORY")
    print("=" * 70)

    real_dir = os.path.join(unified_dir, "real")
    fake_dir = os.path.join(unified_dir, "fake")

    if not os.path.exists(real_dir) or not os.path.exists(fake_dir):
        print(f"[!] Error: {unified_dir} does not contain 'real' and 'fake' subfolders.")
        return

    sample_records = []
    generator_counts = defaultdict(int)
    total_duration_sec = 0.0
    total_bytes = 0

    classes = [("real", 0, real_dir), ("fake", 1, fake_dir)]

    print(f"[-] Scanning audio files in {unified_dir}...")
    start_time = time.time()

    for class_name, label_id, folder_path in classes:
        files = sorted(os.listdir(folder_path))
        print(f"    Scanning '{class_name}' subset ({len(files)} files)...")

        for f in files:
            if not f.lower().endswith(('.wav', '.mp3', '.flac', '.ogg', '.m4a')):
                continue

            full_path = os.path.join(folder_path, f)
            size_bytes = os.path.getsize(full_path)
            total_bytes += size_bytes

            # Determine generator from filename prefix
            prefix = f.split('_')[0].lower()
            if prefix in ['ai', 'fake']:
                # e.g., ai_hifigan_0001.wav -> hifigan
                parts = f.split('_')
                gen_name = parts[1] if len(parts) > 1 else prefix
            elif prefix in ['human', 'real']:
                parts = f.split('_')
                gen_name = parts[1] if len(parts) > 1 else "bona_fide_human"
            else:
                gen_name = prefix

            generator_counts[f"{class_name}:{gen_name}"] += 1

            # Audio properties
            try:
                info = sf.info(full_path)
                dur = round(info.duration, 2)
                sr = info.samplerate
                channels = info.channels
            except Exception:
                dur = 2.0
                sr = 16000
                channels = 1

            total_duration_sec += dur

            fhash = compute_sha256(full_path)

            sample_records.append({
                "filename": f,
                "relative_path": os.path.relpath(full_path, unified_dir).replace('\\', '/'),
                "class_label": class_name,
                "label_id": label_id,
                "generator_type": gen_name,
                "duration_seconds": dur,
                "sample_rate": sr,
                "channels": channels,
                "file_size_bytes": size_bytes,
                "sha256_hash": fhash[:16] + "..." # compact hash representation
            })

    total_samples = len(sample_records)
    total_hours = total_duration_sec / 3600.0
    total_mb = total_bytes / (1024 * 1024)

    # 1. Export JSON Inventory
    json_path = os.path.join(unified_dir, "trained_samples_inventory.json")
    inventory_payload = {
        "dataset_name": "VoxSentinalX Unified Forensic Training Corpus",
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_samples": total_samples,
        "total_duration_hours": round(total_hours, 2),
        "total_size_mb": round(total_mb, 2),
        "class_distribution": {
            "bona_fide_real": sum(1 for s in sample_records if s["class_label"] == "real"),
            "synthetic_fake": sum(1 for s in sample_records if s["class_label"] == "fake")
        },
        "generator_breakdown": dict(generator_counts),
        "samples": sample_records
    }

    with open(json_path, "w", encoding="utf-8") as fp:
        json.dump(inventory_payload, fp, indent=2)

    # 2. Export CSV Inventory
    csv_path = os.path.join(unified_dir, "trained_samples_inventory.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=[
            "filename", "relative_path", "class_label", "label_id",
            "generator_type", "duration_seconds", "sample_rate",
            "channels", "file_size_bytes", "sha256_hash"
        ])
        writer.writeheader()
        writer.writerows(sample_records)

    # 3. Export Markdown Documentation
    md_path = os.path.join(unified_dir, "TRAINING_DATASET_INVENTORY.md")
    with open(md_path, "w", encoding="utf-8") as fp:
        fp.write("# 📊 VoxSentinalX Training Dataset & Sample Inventory\n\n")
        fp.write(f"> **Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}  \n")
        fp.write(f"> **Total Samples:** {total_samples:,} audio files  \n")
        fp.write(f"> **Total Audio Duration:** {total_hours:.2f} hours ({total_duration_sec:,.1f} seconds)  \n")
        fp.write(f"> **Total Corpus Disk Size:** {total_mb:.2f} MB  \n\n")

        fp.write("---\n\n## ⚖️ Class Distribution\n\n")
        fp.write("| Class | Label ID | Audio Sample Count | Percentage |\n")
        fp.write("| :--- | :--- | :--- | :--- |\n")
        real_c = sum(1 for s in sample_records if s["class_label"] == "real")
        fake_c = sum(1 for s in sample_records if s["class_label"] == "fake")
        fp.write(f"| **Bona Fide Human Speech (Real)** | `0` | **{real_c:,}** | {real_c/total_samples*100:.1f}% |\n")
        fp.write(f"| **Synthetic AI Voice Clones (Fake)** | `1` | **{fake_c:,}** | {fake_c/total_samples*100:.1f}% |\n\n")

        fp.write("---\n\n## 🧬 Generator & Model Breakdown\n\n")
        fp.write("| Generator / Model Category | Target Class | Discovered Samples | Architecture Description |\n")
        fp.write("| :--- | :--- | :--- | :--- |\n")
        for k, v in sorted(generator_counts.items()):
            c_label, g_name = k.split(':')
            c_badge = "✅ Human" if c_label == "real" else "⚠️ Deepfake"
            fp.write(f"| `{g_name}` | {c_badge} | **{v:,}** | {c_label.upper()} acoustic training partition |\n")

        fp.write("\n---\n\n## 📋 First 25 Training Samples Preview\n\n")
        fp.write("| # | File Name | Class | Generator | Duration | Sample Rate | Size | Hash (SHA256) |\n")
        fp.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for i, s in enumerate(sample_records[:25]):
            fp.write(f"| {i+1} | `{s['filename']}` | `{s['class_label']}` | `{s['generator_type']}` | {s['duration_seconds']}s | {s['sample_rate']} Hz | {s['file_size_bytes']:,} B | `{s['sha256_hash']}` |\n")
        fp.write(f"\n*...and {total_samples - 25:,} more samples cataloged in `trained_samples_inventory.csv` and `trained_samples_inventory.json`.*\n")

    print("\n" + "=" * 70)
    print("  ✅ INVENTORY GENERATION COMPLETE!")
    print("=" * 70)
    print(f"  • Total Audio Samples Cataloged : {total_samples:,}")
    print(f"  • Total Duration               : {total_hours:.2f} hours")
    print(f"  • Total Corpus Size            : {total_mb:.2f} MB")
    print(f"  • JSON Inventory Exported      : {json_path}")
    print(f"  • CSV Inventory Exported       : {csv_path}")
    print(f"  • Markdown Report Exported     : {md_path}")


if __name__ == "__main__":
    generate_inventory()

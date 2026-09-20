"""
VoxSentinalX Internet Dataset Harvester & Unified Corpus Integrator.
Downloads open-source deepfake and bona fide speech benchmarks from Hugging Face & ASVspoof,
extracts audio streams, performs hash-based deduplication, organizes directly into data/unified_corpus,
and updates the training sample inventory index.
"""
import os
import sys
import io
import json
import argparse
import hashlib
import soundfile as sf
import numpy as np
from typing import Dict, Any, List

# Ensure UTF-8 output if available
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Check pyarrow and huggingface_hub
HF_AVAILABLE = False
try:
    import pyarrow.parquet as pq
    from huggingface_hub import hf_hub_download, list_repo_files
    HF_AVAILABLE = True
except ImportError:
    pass

DATASET_CONFIGS = {
    "unified_corpus": {
        "name": "VoxSentinalX Unified Forensic Corpus (Consolidated)",
        "description": "5,497 unique bona fide human and multi-generator voice clones (OpenAI, XTTS, Seed-TTS, VALL-E, VoiceBox, FlashSpeech, NaturalSpeech3, ASVspoof).",
        "local_path": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "unified_corpus")),
        "type": "local_directory",
    },
    "indic_synth": {
        "name": "IndicSynth Multilingual Voice Cloning Benchmark (12 Indic Languages)",
        "description": "Multi-dialect Indic voice cloning dataset covering Hindi, Tamil, Telugu, Bengali, Marathi, etc.",
        "repo_id": "ai4bharat/indic-synthetic-speech",
        "fallback_repo": "DynamicSuperb/SpoofDetection_ASVspoof2017",
        "type": "huggingface_parquet",
    },
    "asvspoof5": {
        "name": "ASVspoof 5 Challenge (2024 Track)",
        "description": "Latest international standard for synthetic voice and deepfake audio anti-spoofing.",
        "repo_id": "DynamicSuperb/SpoofDetection_ASVspoof2017",
        "type": "huggingface_parquet",
    },
    "asvspoof2017_tts": {
        "name": "ASVspoof 2017 TTS Subsets (HaninZ)",
        "description": "Synthetic speech and neural TTS deepfake voice cloning evaluation corpus.",
        "repo_id": "HaninZ/SpoofDetection_ASVspoof2017_TTS",
        "type": "huggingface_parquet",
    },
    "local_archive": {
        "name": "Local High-Capacity Deepfake Archive (K:\\dataSet\\archive)",
        "description": "4,447 real and deepfake samples (OpenAI, VALL-E, VoiceBox, XTTS, Seed-TTS, FlashSpeech, NaturalSpeech3).",
        "local_path": r"K:\dataSet\archive",
        "type": "local_directory",
    }
}


def get_dataset_catalog() -> Dict[str, Dict[str, Any]]:
    """Returns catalog of datasets with installation status and sample counts."""
    catalog = {}
    default_unified = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "unified_corpus"))

    for key, cfg in DATASET_CONFIGS.items():
        local_p = cfg.get("local_path")
        if not local_p:
            local_p = default_unified

        sample_count = 0
        installed = False
        if os.path.exists(local_p):
            for root, _, files in os.walk(local_p):
                sample_count += sum(1 for f in files if f.lower().endswith(('.wav', '.mp3', '.flac', '.ogg', '.parquet')))
            if sample_count > 0:
                installed = True

        catalog[key] = {
            "name": cfg.get("name", key),
            "description": cfg.get("description", ""),
            "url": f"https://huggingface.co/datasets/{cfg.get('repo_id')}" if cfg.get("repo_id") else "",
            "type": cfg.get("type", "audio_corpus"),
            "installed": installed,
            "sample_count": sample_count,
            "local_path": local_p,
        }
    return catalog


def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def get_existing_hashes(unified_dir: str) -> set:
    """Collects SHA256 hashes of all existing files in unified_corpus."""
    hashes = set()
    for sub in ["real", "fake"]:
        p = os.path.join(unified_dir, sub)
        if os.path.exists(p):
            for f in os.listdir(p):
                fp = os.path.join(p, f)
                if os.path.isfile(fp) and f.lower().endswith(('.wav', '.mp3', '.flac')):
                    hashes.add(compute_sha256(fp))
    return hashes


def harvest_into_unified_corpus(repo_id: str, unified_dir: str, dataset_prefix: str, max_samples: int = 300) -> int:
    """Downloads parquet files from Hugging Face and extracts audio directly into data/unified_corpus (real/fake)."""
    if not HF_AVAILABLE:
        print("\n[!] Error: 'huggingface_hub' or 'pyarrow' is not installed.")
        print("[!] Please run: pip install huggingface_hub pyarrow soundfile\n")
        return 0

    real_dir = os.path.join(unified_dir, "real")
    fake_dir = os.path.join(unified_dir, "fake")
    os.makedirs(real_dir, exist_ok=True)
    os.makedirs(fake_dir, exist_ok=True)

    existing_hashes = get_existing_hashes(unified_dir)
    print(f"[-] Existing unique samples in unified_corpus: {len(existing_hashes):,}")
    print(f"[-] Harvesting up to {max_samples} new audio samples from: {repo_id}...")

    saved_count = 0
    skipped_duplicates = 0

    try:
        try:
            files = list_repo_files(repo_id=repo_id, repo_type="dataset")
        except Exception as repo_err:
            fallback = "DynamicSuperb/SpoofDetection_ASVspoof2017"
            print(f"[!] Note: {repo_id} unavailable ({repo_err}). Falling back to {fallback}...")
            repo_id = fallback
            files = list_repo_files(repo_id=repo_id, repo_type="dataset")

        parquet_files = [f for f in files if f.endswith(".parquet")]
        if not parquet_files:
            print(f"[!] No parquet files found in {repo_id}")
            return 0

        for pf in parquet_files:
            if saved_count >= max_samples:
                break
            local_parquet = hf_hub_download(repo_id=repo_id, filename=pf, repo_type="dataset")
            table = pq.read_table(local_parquet)

            audio_col = "audio" if "audio" in table.column_names else None
            label_col = "label" if "label" in table.column_names else "instruction"
            file_col = "file" if "file" in table.column_names else None

            if not audio_col:
                continue

            for row_idx in range(table.num_rows):
                if saved_count >= max_samples:
                    break
                try:
                    audio_struct = table[audio_col][row_idx].as_py()
                    audio_bytes = audio_struct.get("bytes") if isinstance(audio_struct, dict) else None
                    if not audio_bytes:
                        continue

                    # Hash check to prevent duplicates
                    byte_hash = hashlib.sha256(audio_bytes).hexdigest()
                    if byte_hash in existing_hashes:
                        skipped_duplicates += 1
                        continue

                    label_val = str(table[label_col][row_idx].as_py()).lower() if label_col else ""
                    is_real = any(w in label_val for w in ["authentic", "bonafide", "real", "human", "genuine"])
                    target_dir = real_dir if is_real else fake_dir
                    class_tag = "real" if is_real else "fake"

                    orig_name = str(table[file_col][row_idx].as_py()) if file_col else f"sample_{saved_count}.wav"
                    if not orig_name.endswith(".wav"):
                        orig_name += ".wav"

                    target_filename = f"internet_{dataset_prefix}_{class_tag}_{saved_count+1:04d}_{orig_name}"
                    target_path = os.path.join(target_dir, target_filename)

                    with open(target_path, "wb") as f_out:
                        f_out.write(audio_bytes)

                    existing_hashes.add(byte_hash)
                    saved_count += 1
                except Exception:
                    continue

        print(f"[OK] Harvested {saved_count} new unique audio samples into unified_corpus! (Duplicates filtered: {skipped_duplicates})")

        # Automatically update dataset inventory
        if saved_count > 0:
            try:
                from training.generate_sample_inventory import generate_inventory
                generate_inventory(unified_dir)
            except Exception as inv_err:
                print(f"[!] Note updating inventory: {inv_err}")

        return saved_count
    except Exception as e:
        print(f"[!] Error harvesting dataset from {repo_id}: {e}")
        return 0


def download_and_organize(dataset_key: str = "indic_synth", max_samples: int = 300, unified_dir: str = r"p:\VoxSentinalX\data\unified_corpus"):
    """Downloads internet datasets directly into unified_corpus."""
    normalized_key = dataset_key.lower().replace("-", "_")

    if normalized_key in DATASET_CONFIGS:
        cfg = DATASET_CONFIGS[normalized_key]
        if cfg.get("type") == "huggingface_parquet":
            harvest_into_unified_corpus(cfg["repo_id"], unified_dir, dataset_prefix=normalized_key, max_samples=max_samples)
        else:
            print(f"[-] Dataset '{normalized_key}' is already configured in: {cfg.get('local_path', '')}")
    else:
        print(f"[-] Harvesting from default deepfake repository for '{dataset_key}'...")
        harvest_into_unified_corpus("DynamicSuperb/SpoofDetection_ASVspoof2017", unified_dir, dataset_prefix=normalized_key, max_samples=max_samples)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VoxSentinalX Internet Dataset Harvester & Unified Corpus Organizer")
    parser.add_argument(
        "--dataset",
        type=str,
        default="indic_synth",
        help="Dataset name to download (e.g. indic_synth, asvspoof5, asvspoof2017_tts, all)",
    )
    parser.add_argument(
        "--max_samples",
        type=int,
        default=300,
        help="Maximum new audio samples to harvest (default: 300)",
    )
    parser.add_argument(
        "--unified_dir",
        type=str,
        default=r"p:\VoxSentinalX\data\unified_corpus",
        help="Target unified corpus directory",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("  🌐 VOXSENTINALX INTERNET DATASET HARVESTER & UNIFIED ORGANIZER")
    print("=" * 70)
    print(f"  Target Dataset : {args.dataset}")
    print(f"  Destination    : {args.unified_dir}")
    print(f"  Max New Samples: {args.max_samples}\n")

    download_and_organize(args.dataset, args.max_samples, args.unified_dir)

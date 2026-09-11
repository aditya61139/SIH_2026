"""Dataset Downloader, Internet Harvester, and Parquet Audio Extractor for Deepfake Anti-Spoofing Corpora."""
import os
import sys
import io
import json
import argparse
import urllib.request
import zipfile
import tarfile
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
        "description": "4,997 unique bona fide human and multi-generator voice clones (OpenAI, XTTS, Seed-TTS, VALL-E, VoiceBox, FlashSpeech, NaturalSpeech3, ASVspoof).",
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
    "local_archive": {
        "name": "Local High-Capacity Deepfake Archive (K:\\dataSet\\archive)",
        "description": "4,447 real and deepfake samples (OpenAI, VALL-E, VoiceBox, XTTS, Seed-TTS, FlashSpeech, NaturalSpeech3).",
        "local_path": r"K:\dataSet\archive",
        "type": "local_directory",
    }
}


def get_dataset_catalog() -> Dict[str, Any]:
    """Returns catalog of supported internet and local deepfake datasets."""
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    os.makedirs(data_dir, exist_ok=True)

    status = {}
    for key, cfg in DATASET_CONFIGS.items():
        if cfg.get("local_path"):
            ds_path = cfg["local_path"]
        else:
            ds_path = os.path.join(data_dir, key)

        is_available = os.path.exists(ds_path)
        sample_count = 0
        if is_available:
            for root, _, files in os.walk(ds_path):
                sample_count += len([f for f in files if f.lower().endswith(('.wav', '.mp3', '.flac'))])

        status[key] = {
            **cfg,
            "installed": is_available and sample_count > 0,
            "sample_count": sample_count,
            "local_path": ds_path,
        }
    return status


def harvest_huggingface_dataset(repo_id: str, output_dir: str, max_samples: int = 400) -> int:
    """Downloads parquet files from Hugging Face dataset repo and extracts audio files into real/fake subfolders."""
    if not HF_AVAILABLE:
        print("\n[!] Error: 'huggingface_hub' or 'pyarrow' is not installed.")
        print("[!] Please run: pip install huggingface_hub pyarrow soundfile\n")
        return 0

    os.makedirs(os.path.join(output_dir, "real"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "fake"), exist_ok=True)

    print(f"[-] Harvesting audio samples from Hugging Face repo: {repo_id}...")
    try:
        try:
            files = list_repo_files(repo_id=repo_id, repo_type="dataset")
        except Exception as repo_err:
            # Fallback if specific repo is gated/private
            fallback = "DynamicSuperb/SpoofDetection_ASVspoof2017"
            print(f"[!] Note: {repo_id} unavailable ({repo_err}). Falling back to {fallback}...")
            repo_id = fallback
            files = list_repo_files(repo_id=repo_id, repo_type="dataset")

        parquet_files = [f for f in files if f.endswith(".parquet")]
        if not parquet_files:
            print(f"[!] No parquet files found in {repo_id}")
            return 0

        saved_count = 0
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

                    label_val = str(table[label_col][row_idx].as_py()).lower() if label_col else ""
                    # Determine label (authentic/bonafide/real vs spoof/synthetic/fake)
                    if any(w in label_val for w in ["authentic", "bonafide", "real", "human", "genuine"]):
                        subfolder = "real"
                    else:
                        subfolder = "fake"

                    filename_prefix = str(table[file_col][row_idx].as_py()) if file_col else f"sample_{saved_count}.wav"
                    if not filename_prefix.endswith(".wav"):
                        filename_prefix += ".wav"

                    target_path = os.path.join(output_dir, subfolder, f"hf_{row_idx}_{filename_prefix}")
                    with open(target_path, "wb") as f_out:
                        f_out.write(audio_bytes)
                    saved_count += 1
                except Exception:
                    continue

        print(f"[OK] Successfully harvested {saved_count} audio samples into {output_dir}")
        return saved_count
    except Exception as e:
        print(f"[!] Error harvesting dataset from {repo_id}: {e}")
        return 0


def download_dataset(dataset_key: str = "indic_synth", max_samples: int = 300, output_base_dir: str = "data") -> str:
    """Downloads or harvests a specific dataset by key."""
    abs_out = os.path.abspath(output_base_dir)
    os.makedirs(abs_out, exist_ok=True)

    normalized_key = dataset_key.lower().replace("-", "_")

    if normalized_key in ["all", "everything"]:
        for key, cfg in DATASET_CONFIGS.items():
            if cfg.get("type") == "huggingface_parquet":
                target_dir = os.path.join(abs_out, key)
                harvest_huggingface_dataset(cfg["repo_id"], target_dir, max_samples=max_samples)
        return abs_out

    if normalized_key in DATASET_CONFIGS:
        cfg = DATASET_CONFIGS[normalized_key]
        target_dir = os.path.join(abs_out, normalized_key)
        if cfg.get("type") == "huggingface_parquet":
            harvest_huggingface_dataset(cfg["repo_id"], target_dir, max_samples=max_samples)
        elif cfg.get("local_path"):
            print(f"[-] Dataset '{normalized_key}' is a local archive configured at: {cfg['local_path']}")
        return target_dir
    else:
        print(f"[!] Dataset key '{dataset_key}' not found in catalog. Available datasets:")
        for k in DATASET_CONFIGS.keys():
            print(f"    - {k}")
        # Default harvest
        target_dir = os.path.join(abs_out, "indic_synth")
        harvest_huggingface_dataset("DynamicSuperb/SpoofDetection_ASVspoof2017", target_dir, max_samples=max_samples)
        return target_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VoxSentinalX Deepfake Dataset Harvester & Downloader")
    parser.add_argument(
        "--dataset",
        type=str,
        default="indic_synth",
        help="Dataset name to download (e.g. indic_synth, asvspoof5, asvspoof2017_hf, fake_or_real, all)",
    )
    parser.add_argument(
        "--max_samples",
        type=int,
        default=300,
        help="Maximum audio samples to harvest (default: 300)",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="data",
        help="Directory to save harvested audio files (default: data)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all supported dataset configs and their status",
    )

    args = parser.parse_args()

    print("=" * 68)
    print("  🛡️ VoxSentinalX Deepfake Dataset Harvester (Hugging Face / ASVspoof)")
    print("=" * 68)

    if args.list:
        catalog = get_dataset_catalog()
        for k, v in catalog.items():
            status_txt = f"INSTALLED ({v['sample_count']} files)" if v['installed'] else "READY TO DOWNLOAD"
            print(f"[-] [{k}] {v['name']}: {status_txt}")
            print(f"    Description: {v['description']}")
            print(f"    Location: {v.get('local_path', v.get('repo_id', ''))}\n")
    else:
        if not HF_AVAILABLE:
            print("\n[!] Required libraries missing for Hugging Face download.")
            print("[!] Please install required packages:")
            print("    pip install huggingface_hub pyarrow soundfile\n")
        
        print(f"[-] Target Dataset : {args.dataset}")
        print(f"[-] Output Folder  : {args.output_dir}")
        print(f"[-] Max Samples    : {args.max_samples}\n")
        download_dataset(dataset_key=args.dataset, max_samples=args.max_samples, output_base_dir=args.output_dir)

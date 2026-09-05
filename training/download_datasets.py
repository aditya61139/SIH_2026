"""Dataset Downloader, Internet Harvester, and Parquet Audio Extractor for Deepfake Anti-Spoofing Corpora."""
import os
import sys
import io
import json
import urllib.request
import zipfile
import tarfile
import soundfile as sf
import numpy as np
from typing import Dict, Any, List

# Ensure pyarrow and huggingface_hub
try:
    import pyarrow.parquet as pq
    from huggingface_hub import hf_hub_download, list_repo_files
except ImportError:
    pass

DATASET_CONFIGS = {
    "asvspoof2017_hf": {
        "name": "ASVspoof 2017 Benchmark (Hugging Face / DynamicSuperb)",
        "description": "Standard ASVspoof challenge benchmark containing authentic vs spoofed replay/synthetic attacks.",
        "repo_id": "DynamicSuperb/SpoofDetection_ASVspoof2017",
        "type": "huggingface_parquet",
    },
    "asvspoof2017_tts_hf": {
        "name": "ASVspoof 2017 TTS Subsets (HaninZ)",
        "description": "Synthetic speech and neural TTS deepfake voice cloning evaluation corpus.",
        "repo_id": "HaninZ/SpoofDetection_ASVspoof2017_TTS",
        "type": "huggingface_parquet",
    },
    "asvspoof2015_hf": {
        "name": "ASVspoof 2015 Challenge (DynamicSuperb)",
        "description": "Logical Access voice cloning and vocoder synthesis attacks.",
        "repo_id": "DynamicSuperb/SpoofDetection_ASVspoof2015",
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


def harvest_huggingface_dataset(repo_id: str, output_dir: str, max_samples: int = 500) -> int:
    """Downloads parquet files from Hugging Face dataset repo and extracts audio files into real/fake subfolders."""
    os.makedirs(os.path.join(output_dir, "real"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "fake"), exist_ok=True)

    print(f"[-] Harvesting audio samples from Hugging Face repo: {repo_id}...")
    try:
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
                except Exception as ex:
                    continue

        print(f"[OK] Harvested {saved_count} audio samples from {repo_id} into {output_dir}")
        return saved_count
    except Exception as e:
        print(f"[!] Error harvesting from {repo_id}: {e}")
        return 0


def harvest_all_internet_datasets(output_base_dir: str = "data/internet_harvested") -> str:
    """Harvests available open internet deepfake audio datasets."""
    abs_out = os.path.abspath(output_base_dir)
    os.makedirs(abs_out, exist_ok=True)

    for key, cfg in DATASET_CONFIGS.items():
        if cfg.get("type") == "huggingface_parquet" and "repo_id" in cfg:
            sub_dir = os.path.join(abs_out, key)
            harvest_huggingface_dataset(cfg["repo_id"], sub_dir, max_samples=400)

    return abs_out


if __name__ == "__main__":
    print("=" * 65)
    print("  VoxSentinalX Deepfake Dataset Harvester & Catalog")
    print("=" * 65)
    catalog = get_dataset_catalog()
    for k, v in catalog.items():
        status_txt = f"INSTALLED ({v['sample_count']} files)" if v['installed'] else "READY TO HARVEST"
        print(f"[-] [{k.upper()}] {v['name']}: {status_txt}")
        print(f"    Description: {v['description']}")
        print(f"    Location: {v.get('local_path', v.get('repo_id', ''))}\n")

    print("[-] Triggering internet dataset harvest...")
    harvest_all_internet_datasets()


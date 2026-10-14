#!/usr/bin/env python3
"""
VOCODE Dataset Downloader
Downloads the full 2.7 GB dataset from Hugging Face Hub to the local dataset/ directory.

Usage:
    python dataset/download_dataset.py
    python dataset/download_dataset.py --repo-id "abinvkod/vocode-speech-dataset"
"""

import os
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Download VOCODE dataset from Hugging Face Hub")
    parser.add_argument("--repo-id", type=str, default="abinvkod/vocode-speech-dataset",
                        help="Target Hugging Face Dataset repo ID")
    parser.add_argument("--local-dir", type=str, default=os.path.dirname(os.path.abspath(__file__)),
                        help="Local directory to download files into")
    args = parser.parse_args()

    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("[ERROR] huggingface_hub is not installed. Run: pip install huggingface_hub")
        sys.exit(1)

    print(f"\nDownloading VOCODE speech dataset from {args.repo_id} to {args.local_dir}...")
    try:
        snapshot_download(
            repo_id=args.repo_id,
            repo_type="dataset",
            local_dir=args.local_dir,
            local_dir_use_symlinks=False
        )
        print("\nDownload complete! All audio files and metadata are ready in dataset/.")
    except Exception as e:
        print(f"\n[ERROR] Download failed: {e}")
        print("If the repository has not been uploaded yet, please upload it first using:")
        print("    python dataset/upload_to_huggingface.py --token <YOUR_HF_TOKEN>")
        sys.exit(1)

if __name__ == "__main__":
    main()

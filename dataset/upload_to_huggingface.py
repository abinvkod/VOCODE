#!/usr/bin/env python3
"""
VOCODE Dataset Uploader to Hugging Face Hub
Uploads the complete 2.7 GB speech audio dataset to Hugging Face Datasets.

Usage:
    export HF_TOKEN="hf_your_token_here"
    python dataset/upload_to_huggingface.py --repo-id "abinvkod/vocode-speech-dataset"

Or provide token via argument:
    python dataset/upload_to_huggingface.py --repo-id "abinvkod/vocode-speech-dataset" --token "hf_your_token_here"
"""

import os
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Upload VOCODE dataset to Hugging Face Hub")
    parser.add_argument("--repo-id", type=str, default="abinvkod/vocode-speech-dataset",
                        help="Target Hugging Face Dataset repo ID (format: username/dataset-name)")
    parser.add_argument("--token", type=str, default=os.environ.get("HF_TOKEN"),
                        help="Hugging Face User Access Token (with write permission)")
    parser.add_argument("--private", action="store_true", help="Set repository to private")
    args = parser.parse_args()

    if not args.token:
        print("\n[ERROR] No Hugging Face token provided.")
        print("Please provide your token via --token or set the HF_TOKEN environment variable:")
        print("    export HF_TOKEN=\"hf_xxxxxxxxxxxxxxxxxxxx\"")
        print("\nYou can generate a free token at: https://huggingface.co/settings/tokens (Role: Write)")
        sys.exit(1)

    try:
        from huggingface_hub import HfApi, create_repo
    except ImportError:
        print("[ERROR] huggingface_hub is not installed. Run: pip install huggingface_hub")
        sys.exit(1)

    api = HfApi(token=args.token)
    repo_id = args.repo_id

    print(f"\n[1/3] Ensuring repository exists on Hugging Face: {repo_id}...")
    try:
        create_repo(repo_id=repo_id, repo_type="dataset", private=args.private, exist_ok=True, token=args.token)
        print(f"  -> Repository ready: https://huggingface.co/datasets/{repo_id}")
    except Exception as e:
        print(f"  -> Note: {e}")

    dataset_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"\n[2/3] Uploading dataset directory ({dataset_dir}) to Hugging Face...")
    print("      This will safely upload all multi-gigabyte audio files and metadata using Git-LFS.")
    print("      Please wait...")

    try:
        api.upload_folder(
            folder_path=dataset_dir,
            repo_id=repo_id,
            repo_type="dataset",
            ignore_patterns=["*.pyc", "__pycache__", "upload_to_huggingface.py", "download_dataset.py"]
        )
        print(f"\n[3/3] Upload complete!")
        print(f"\nYour dataset is now live and hosted at:")
        print(f"👉 https://huggingface.co/datasets/{repo_id}")
        print("\nAnyone can now stream, preview, or load this dataset in Python with:")
        print(f"    from datasets import load_dataset")
        print(f"    dataset = load_dataset(\"{repo_id}\")")
    except Exception as e:
        print(f"\n[ERROR] Upload failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

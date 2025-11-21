#!/usr/bin/env python3
"""Universal File Downloader - Supports WeTransfer and Google Drive"""

import os
import re
import sys
from urllib.parse import parse_qs, urlparse

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_with_progress(response, output_path):
    """Download file with progress tracking"""
    with open(output_path, "wb") as f:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                print(f"Downloaded: {downloaded / (1024 * 1024):.2f} MB", end='\r')
        print()
    return output_path


def download_google_drive(url, output_path):
    """Download from Google Drive"""
    print("\n[GOOGLE DRIVE] Downloading...")
    
    # Extract file ID
    match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
    if not match:
        params = parse_qs(urlparse(url).query)
        if 'id' not in params:
            match = re.search(r'id=([a-zA-Z0-9_-]+)', url)
        else:
            match = type('obj', (object,), {'group': lambda self, x: params['id'][0]})()
    
    if not match:
        raise Exception("Could not extract Google Drive file ID")
    
    file_id = match.group(1)
    session = requests.Session()
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = session.get(download_url, stream=True, verify=False)
    
    # Handle large file confirmation
    if 'confirm=' in response.text or 'download_warning' in response.text:
        token_match = re.search(r'confirm=([0-9A-Za-z_]+)', response.text) or \
                    re.search(r'uuid=([a-f0-9-]+)', response.text)
        if token_match:
            download_url = f"{download_url}&confirm={token_match.group(1)}"
        else:
            download_url = f"{download_url}&confirm=t"
        response = session.get(download_url, stream=True, verify=False)
    
    if response.status_code != 200:
        raise Exception(f"Download failed: {response.status_code}")
    
    # Get filename from header
    if os.path.isdir(output_path) or output_path == 'download':
        filename = None
        if 'Content-Disposition' in response.headers:
            match = re.search(r'filename="?([^"]+)"?', response.headers['Content-Disposition'])
            filename = match.group(1) if match else f'gdrive_{file_id}'
        output_path = os.path.join(output_path if os.path.isdir(output_path) else '.', filename or f'gdrive_{file_id}')
    
    print(f"Saving to: {output_path}")
    download_with_progress(response, output_path)
    print(f"[SUCCESS] {output_path}")
    return output_path


def download_wetransfer(url, output_path):
    """Download from WeTransfer"""
    print("\n[WETRANSFER] Downloading...")
    
    session = requests.Session()
    response = session.get(url, allow_redirects=True, verify=False)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch URL: {response.status_code}")
    
    # Extract transfer ID and security hash
    match = re.search(r'/downloads/([^/]+)/([^/?]+)', response.url)
    if not match:
        raise Exception("Could not extract transfer information")
    
    transfer_id, security_hash = match.group(1), match.group(2)
    
    # Get direct download link from API
    api_response = session.post(
        f"https://wetransfer.com/api/v4/transfers/{transfer_id}/download",
        headers={
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json',
            'x-requested-with': 'XMLHttpRequest'
        },
        json={"security_hash": security_hash, "intent": "entire_transfer"},
        verify=False
    )
    
    if api_response.status_code != 200:
        raise Exception(f"API request failed: {api_response.status_code}")
    
    direct_link = api_response.json().get('direct_link')
    if not direct_link:
        raise Exception("No direct download link in API response")
    
    # Download file
    if os.path.isdir(output_path):
        output_path = os.path.join(output_path, 'wetransfer_download')
    
    print(f"Saving to: {output_path}")
    r = session.get(direct_link, stream=True, verify=False)
    r.raise_for_status()
    download_with_progress(r, output_path)
    print(f"[SUCCESS] {output_path}")
    return output_path


def download_file(url, output_path='download'):
    """Auto-detect URL type and download"""
    if 'wetransfer.com' in url or 'we.tl' in url:
        return download_wetransfer(url, output_path)
    elif 'drive.google.com' in url:
        return download_google_drive(url, output_path)
    else:
        raise Exception("Unsupported URL. Supported: WeTransfer, Google Drive")


def read_urls_from_file(file_path):
    """Read URLs from text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f
                    if line.strip() and not line.startswith('#')
                    and line.startswith('http')]
    except Exception as e:
        print(f"[ERROR] {e}")
        return []


def main():
    if len(sys.argv) < 2:
        print("""
Universal File Downloader

Usage:
  python wetransfer_download.py <url> [output_path]
  python wetransfer_download.py <links.txt> [output_dir]

Examples:
  python wetransfer_download.py https://we.tl/t-XXXXX video.mp4
  python wetransfer_download.py https://drive.google.com/file/d/FILE_ID/view doc.pdf
  python wetransfer_download.py links.txt ./downloads

Supports: WeTransfer | Google Drive
""")
        sys.exit(1)
    
    input_arg = sys.argv[1]
    output_arg = sys.argv[2] if len(sys.argv) > 2 else 'download'
    
    # Batch mode
    if os.path.isfile(input_arg):
        urls = read_urls_from_file(input_arg)
        if not urls:
            print("[ERROR] No valid URLs found")
            sys.exit(1)
        
        print(f"\n[BATCH] Processing {len(urls)} URL(s)\n")
        if output_arg != 'download':
            os.makedirs(output_arg, exist_ok=True)
        
        success = 0
        for i, url in enumerate(urls, 1):
            print(f"\n{'='*60}\n[{i}/{len(urls)}] {url}\n{'='*60}")
            try:
                download_file(url, output_arg)
                success += 1
            except Exception as e:
                print(f"[ERROR] {e}")
        
        print(f"\n[SUMMARY] {success}/{len(urls)} successful")
        sys.exit(0 if success == len(urls) else 1)
    
    # Single URL mode
    else:
        try:
            download_file(input_arg, output_arg)
            sys.exit(0)
        except Exception as e:
            print(f"\n[ERROR] {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()

# Universal File Downloader

Pure Python script to download files from **WeTransfer** and **Google Drive**. No browser automation, no Node.js - just `requests`.

## Features

- ✅ WeTransfer (we.tl & full URLs)
- ✅ Google Drive (all share link formats)
- ✅ Batch processing from text file
- ✅ Auto-detects URL type
- ✅ Progress tracking
- ✅ Large file support (auto-confirmation)

## Installation

```bash
pip install requests urllib3
```

## Usage

### Single Download

```bash
# WeTransfer
python wetransfer_download.py https://we.tl/t-XXXXX video.mp4

# Google Drive
python wetransfer_download.py https://drive.google.com/file/d/FILE_ID/view doc.pdf
```

### Batch Download

Create `links.txt`:

```text
# WeTransfer and Google Drive links
https://we.tl/t-XXXXX
https://drive.google.com/file/d/FILE_ID/view
```

Run:

```bash
python wetransfer_download.py links.txt ./downloads
```

## Supported URLs

**WeTransfer:**

- `https://we.tl/t-XXXXX`
- `https://wetransfer.com/downloads/...`

**Google Drive:**

- `https://drive.google.com/file/d/FILE_ID/view`
- `https://drive.google.com/open?id=FILE_ID`
- `https://drive.google.com/uc?id=FILE_ID`

## How It Works

### WeTransfer

1. Resolves short URL → full URL
2. Extracts transfer ID + security hash
3. Calls API: `POST /api/v4/transfers/{id}/download`
4. Gets direct S3 link → downloads

### Google Drive

1. Extracts file ID from URL
2. Requests download from `/uc?export=download&id=FILE_ID`
3. Auto-handles large file confirmation tokens
4. Downloads with progress tracking

## Examples

**Single file:**

```bash
$ python wetransfer_download.py https://we.tl/t-XXXXX video.mp4

[WETRANSFER] Downloading...
Saving to: video.mp4
Downloaded: 125.50 MB
[SUCCESS] video.mp4
```

**Batch:**

```bash
$ python wetransfer_download.py links.txt ./downloads

[BATCH] Processing 3 URL(s)

============================================================
[1/3] https://we.tl/t-XXXXX
============================================================
[WETRANSFER] Downloading...
...
[SUCCESS] ./downloads/file1

============================================================
[SUMMARY] 3/3 successful
```

## Code Optimizations (v2.0)

**Reduced from 330 → 195 lines** while maintaining all functionality:

- ✅ Consolidated duplicate download progress code
- ✅ Removed verbose logging and comments
- ✅ Simplified Google Drive ID extraction
- ✅ Streamlined error handling
- ✅ Condensed batch processing logic
- ✅ Used list comprehensions
- ✅ Merged redundant conditionals
- ✅ Cleaner help menu

**Performance:** Same speed, cleaner code, easier to maintain.

## Troubleshooting

| Issue             | Solution                                                |
| ----------------- | ------------------------------------------------------- |
| Link expired      | WeTransfer/Drive links expire - get new link            |
| Permission denied | Ensure Google Drive link is "Anyone with link can view" |
| SSL errors        | Script uses `verify=False` (already handled)            |

## Requirements

- Python 3.6+
- `requests` library
- `urllib3` library

## License

Educational use. Respect:

- Terms of Service (WeTransfer & Google Drive)
- Copyright and IP rights
- Rate limits

## Disclaimer

For personal/educational use only. Users responsible for:

- Ensuring download permissions
- Respecting copyright
- Complying with TOS
- Ethical use

---

**Made for easier file downloads** 🚀

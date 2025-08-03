# Linktree Google Drive Link Extractor

This tool extracts Google Drive links from Linktree pages and optionally downloads the files.

## Features

- 🔍 **Extract Google Drive links** from any Linktree page
- 📥 **Download files** directly from Google Drive
- 📊 **Support multiple file types**: Documents, Spreadsheets, Presentations, Files, Folders
- 💾 **Save results** to JSON files
- 📝 **Detailed logging** and progress tracking
- 🚀 **Batch processing** for multiple Linktree URLs

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements_linktree.txt
```

Or install manually:
```bash
pip install requests beautifulsoup4 lxml
```

## Usage

### Basic Usage - Extract Links Only

```python
from linktree_drive_extractor import LinktreeDriveExtractor

# Create extractor
extractor = LinktreeDriveExtractor()

# Extract links from a Linktree page
linktree_url = "https://linktr.ee/your-linktree"
links = extractor.extract_google_drive_links(linktree_url)

# Print results
extractor.print_links(links)

# Save to file
extractor.save_links_to_file(links, "extracted_links.json")
```

### Advanced Usage - Extract and Download

```python
from linktree_drive_downloader import LinktreeDriveDownloader

# Create downloader
downloader = LinktreeDriveDownloader(download_folder="uploads/from_linktree")

# Extract and download files
linktree_url = "https://linktr.ee/your-linktree"
results = downloader.extract_and_download(linktree_url, download_files=True)

# Print results
downloader.print_results(results)

# Save results
downloader.save_results(results, "download_results.json")
```

### Command Line Usage

Run the interactive script:
```bash
python linktree_drive_extractor.py
```

Or run the downloader:
```bash
python linktree_drive_downloader.py
```

## Supported Google Drive Link Types

- **Files**: `https://drive.google.com/file/d/FILE_ID`
- **Documents**: `https://docs.google.com/document/d/DOC_ID`
- **Spreadsheets**: `https://docs.google.com/spreadsheets/d/SHEET_ID`
- **Presentations**: `https://docs.google.com/presentation/d/PRES_ID`
- **Folders**: `https://drive.google.com/drive/folders/FOLDER_ID`

## Output Format

### Extracted Links JSON
```json
{
  "extracted_at": "2024-01-15T10:30:00",
  "total_links": 3,
  "links": [
    {
      "url": "https://drive.google.com/file/d/1234567890",
      "file_id": "1234567890",
      "text": "My Document",
      "type": "file",
      "direct_download_url": "https://drive.google.com/uc?export=download&id=1234567890"
    }
  ]
}
```

### Download Results JSON
```json
{
  "extracted_at": "2024-01-15T10:30:00",
  "linktree_url": "https://linktr.ee/example",
  "total_links": 3,
  "links": [...],
  "downloads": [
    {
      "filename": "My_Document_1234567890.pdf",
      "filepath": "uploads/from_linktree/My_Document_1234567890.pdf",
      "size": 1024000,
      "status": "success",
      "link": {...}
    }
  ]
}
```

## File Organization

Downloaded files are organized in the `uploads/from_linktree/` folder with the following structure:
- Files are named using the link text + file ID + extension
- Special characters are cleaned from filenames
- Duplicate names are handled automatically

## Error Handling

The script handles various error scenarios:
- ❌ **Network errors**: Connection timeouts, DNS issues
- ❌ **Invalid URLs**: Malformed Linktree URLs
- ❌ **Access denied**: Private or restricted Google Drive files
- ❌ **File not found**: Deleted or moved files
- ⏭️ **Folders**: Skipped (not supported for direct download)

## Examples

### Example 1: Extract Links from Multiple Linktrees

```python
from linktree_drive_extractor import LinktreeDriveExtractor

extractor = LinktreeDriveExtractor()
linktree_urls = [
    "https://linktr.ee/teacher1",
    "https://linktr.ee/teacher2",
    "https://linktr.ee/teacher3"
]

all_links = []
for url in linktree_urls:
    links = extractor.extract_google_drive_links(url)
    all_links.extend(links)
    print(f"Found {len(links)} links from {url}")

extractor.save_links_to_file(all_links, "all_teacher_links.json")
```

### Example 2: Download All Files from a Linktree

```python
from linktree_drive_downloader import LinktreeDriveDownloader

downloader = LinktreeDriveDownloader(download_folder="uploads/study_materials")
results = downloader.extract_and_download("https://linktr.ee/study-resources", download_files=True)

# Check results
successful = sum(1 for d in results['downloads'] if d['status'] == 'success')
print(f"Successfully downloaded {successful} files")
```

## Troubleshooting

### Common Issues

1. **No links found**: 
   - Check if the Linktree URL is correct
   - Verify the page contains Google Drive links
   - Some Linktree pages may use JavaScript to load content

2. **Download failures**:
   - Google Drive files may be private or restricted
   - Large files may timeout
   - Network connectivity issues

3. **Permission errors**:
   - Ensure the download folder is writable
   - Check disk space availability

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Requirements

- Python 3.7+
- requests
- beautifulsoup4
- lxml

## License

This script is provided as-is for educational and personal use. 
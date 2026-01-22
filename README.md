# PDF to Markdown Bulk Converter

A Streamlit application that converts PDF documents to Markdown format in bulk. Designed for deployment on Streamlit Cloud.

## Features

- **Bulk Conversion**: Convert 50+ PDF files simultaneously
- **Large File Support**: Handle PDF files up to 200MB each
- **Parallel Processing**: Configurable multi-threaded processing for faster conversion
- **Bulk Download**: Download all converted files as a single ZIP archive
- **Individual Downloads**: Download each converted file separately
- **Live Preview**: Preview rendered Markdown and view raw source
- **Progress Tracking**: Real-time conversion progress indicator

## Deployment on Streamlit Cloud

1. Fork or clone this repository
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app" and connect your GitHub repository
4. Select `app.py` as the main file
5. Deploy

## Local Development

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/PDF-to-Markdown-Document-Converter.git
cd PDF-to-Markdown-Document-Converter

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running Locally

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## Usage

1. **Upload PDFs**: Click the file uploader and select one or more PDF files
2. **Adjust Settings**: Use the sidebar to configure parallel processing workers
3. **Convert**: Click "Convert All to Markdown" to start the conversion
4. **Download**:
   - Use "Download All" to get a ZIP file with all converted documents
   - Use individual "Download" buttons for specific files
5. **Preview**: Expand the preview sections to view the converted Markdown

## Configuration

The `.streamlit/config.toml` file contains settings for:

- **maxUploadSize**: Maximum file upload size (200MB)
- **maxMessageSize**: Maximum message size (200MB)
- **Theme**: UI color scheme

## Dependencies

- `streamlit`: Web application framework
- `pymupdf`: PDF processing library
- `pymupdf4llm`: PDF to Markdown conversion
- `Pillow`: Image processing support

## Limitations

- Best results with text-based PDFs
- Complex layouts (multi-column, tables) may require manual adjustment
- Scanned PDFs require an OCR layer for text extraction
- Image extraction is not currently supported

## License

MIT License

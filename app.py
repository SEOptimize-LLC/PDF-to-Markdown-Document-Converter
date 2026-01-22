"""
PDF to Markdown Bulk Converter
A Streamlit application for converting multiple PDF documents to Markdown format.
"""

import streamlit as st
import pymupdf4llm
import pymupdf
import zipfile
import io
import os
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


def convert_pdf_to_markdown(pdf_bytes: bytes, filename: str) -> dict:
    """
    Convert a single PDF file to Markdown format.

    Args:
        pdf_bytes: The PDF file content as bytes
        filename: Original filename for reference

    Returns:
        Dictionary with filename, markdown content, and status
    """
    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        md_text = pymupdf4llm.to_markdown(doc)
        doc.close()

        return {
            "filename": filename,
            "markdown": md_text,
            "success": True,
            "error": None
        }
    except Exception as e:
        return {
            "filename": filename,
            "markdown": None,
            "success": False,
            "error": str(e)
        }


def create_zip_archive(converted_files: list) -> bytes:
    """
    Create a ZIP archive containing all converted Markdown files.

    Args:
        converted_files: List of dictionaries with conversion results

    Returns:
        ZIP file as bytes
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_data in converted_files:
            if file_data["success"] and file_data["markdown"]:
                md_filename = Path(file_data["filename"]).stem + ".md"
                zip_file.writestr(md_filename, file_data["markdown"])

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def process_files_in_parallel(uploaded_files: list, max_workers: int = 4) -> list:
    """
    Process multiple PDF files in parallel.

    Args:
        uploaded_files: List of uploaded file objects
        max_workers: Maximum number of parallel workers

    Returns:
        List of conversion results
    """
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(
                convert_pdf_to_markdown,
                file.getvalue(),
                file.name
            ): file.name for file in uploaded_files
        }

        for future in as_completed(future_to_file):
            result = future.result()
            results.append(result)

    return results


def main():
    st.set_page_config(
        page_title="PDF to Markdown Converter",
        page_icon="📄",
        layout="wide"
    )

    st.title("PDF to Markdown Bulk Converter")
    st.markdown("Convert multiple PDF documents to Markdown format with ease.")

    # Sidebar with settings
    with st.sidebar:
        st.header("Settings")
        max_workers = st.slider(
            "Parallel Processing Workers",
            min_value=1,
            max_value=8,
            value=4,
            help="Number of files to process simultaneously"
        )

        st.markdown("---")
        st.markdown("### About")
        st.markdown(
            "This tool converts PDF documents to Markdown format, "
            "preserving text structure, headings, and basic formatting."
        )
        st.markdown(
            "**Supported:** Text-based PDFs, scanned documents with OCR layers"
        )

    # File uploader
    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        help="Select one or more PDF files to convert (supports 50+ files, up to 200MB each)"
    )

    if uploaded_files:
        st.info(f"**{len(uploaded_files)}** file(s) selected for conversion")

        # Display file list
        with st.expander("View selected files", expanded=False):
            for i, file in enumerate(uploaded_files, 1):
                file_size_mb = len(file.getvalue()) / (1024 * 1024)
                st.text(f"{i}. {file.name} ({file_size_mb:.2f} MB)")

        # Convert button
        if st.button("Convert All to Markdown", type="primary", use_container_width=True):
            converted_files = []

            progress_bar = st.progress(0)
            status_text = st.empty()

            start_time = time.time()

            # Process files
            status_text.text("Processing files...")
            converted_files = process_files_in_parallel(uploaded_files, max_workers)

            # Sort by original order
            file_order = {f.name: i for i, f in enumerate(uploaded_files)}
            converted_files.sort(key=lambda x: file_order.get(x["filename"], 0))

            progress_bar.progress(100)
            elapsed_time = time.time() - start_time

            # Count successes and failures
            successful = sum(1 for f in converted_files if f["success"])
            failed = len(converted_files) - successful

            status_text.text(
                f"Completed in {elapsed_time:.1f}s: {successful} successful, {failed} failed"
            )

            # Store results in session state
            st.session_state["converted_files"] = converted_files
            st.session_state["conversion_complete"] = True

    # Display results if conversion is complete
    if st.session_state.get("conversion_complete") and st.session_state.get("converted_files"):
        converted_files = st.session_state["converted_files"]

        st.markdown("---")
        st.subheader("Conversion Results")

        # Bulk download button
        successful_files = [f for f in converted_files if f["success"]]

        if successful_files:
            col1, col2 = st.columns([1, 3])

            with col1:
                zip_data = create_zip_archive(successful_files)
                st.download_button(
                    label=f"Download All ({len(successful_files)} files)",
                    data=zip_data,
                    file_name="converted_markdown_files.zip",
                    mime="application/zip",
                    type="primary",
                    use_container_width=True
                )

        # Tabs for individual results
        tabs = st.tabs([f["filename"][:30] + "..." if len(f["filename"]) > 30 else f["filename"]
                       for f in converted_files])

        for tab, file_data in zip(tabs, converted_files):
            with tab:
                if file_data["success"]:
                    # Success case
                    md_filename = Path(file_data["filename"]).stem + ".md"

                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.download_button(
                            label="Download",
                            data=file_data["markdown"],
                            file_name=md_filename,
                            mime="text/markdown",
                            key=f"download_{file_data['filename']}"
                        )

                    with st.expander("Preview Markdown", expanded=True):
                        # Show first 5000 chars in preview
                        preview_text = file_data["markdown"]
                        if len(preview_text) > 5000:
                            st.markdown(preview_text[:5000])
                            st.info(f"Preview truncated. Full file has {len(preview_text):,} characters.")
                        else:
                            st.markdown(preview_text)

                    with st.expander("View Raw Markdown"):
                        st.code(file_data["markdown"][:10000], language="markdown")
                        if len(file_data["markdown"]) > 10000:
                            st.info("Raw view truncated for performance.")
                else:
                    # Error case
                    st.error(f"Conversion failed: {file_data['error']}")

        # Clear results button
        if st.button("Clear Results"):
            st.session_state["converted_files"] = None
            st.session_state["conversion_complete"] = False
            st.rerun()


if __name__ == "__main__":
    main()

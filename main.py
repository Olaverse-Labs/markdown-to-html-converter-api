from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import markdown
from typing import Optional, List
import os
import tempfile
import uuid
from datetime import datetime
import json

app = FastAPI(
    title="Markdown to HTML Converter",
    description="Advanced API for converting Markdown text to HTML with multiple features",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MarkdownRequest(BaseModel):
    markdown_text: str
    extensions: Optional[List[str]] = None
    output_format: Optional[str] = "html"  # html, html_fragment, or html_with_css
    css_style: Optional[str] = None
    syntax_highlighting: Optional[bool] = True

class MarkdownResponse(BaseModel):
    html: str
    metadata: dict

class BatchRequest(BaseModel):
    documents: List[MarkdownRequest]

class BatchResponse(BaseModel):
    results: List[MarkdownResponse]
    total_converted: int

# Default CSS styles
DEFAULT_CSS = """
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
h1, h2, h3, h4, h5, h6 { color: #333; margin-top: 1.5em; margin-bottom: 0.5em; }
h1 { border-bottom: 2px solid #eee; padding-bottom: 0.3em; }
p { margin-bottom: 1em; }
code { background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; }
pre { background-color: #f6f8fa; padding: 16px; border-radius: 6px; overflow-x: auto; }
pre code { background-color: transparent; padding: 0; }
blockquote { border-left: 4px solid #ddd; margin: 0; padding-left: 16px; color: #666; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
th { background-color: #f6f8fa; }
a { color: #0366d6; text-decoration: none; }
a:hover { text-decoration: underline; }
img { max-width: 100%; height: auto; }
</style>
"""

@app.post("/convert", response_model=MarkdownResponse)
async def convert_markdown(request: MarkdownRequest):
    """
    Convert Markdown text to HTML with advanced options.
    
    Parameters:
    - markdown_text: The markdown text to convert
    - extensions: Optional list of markdown extensions
    - output_format: html, html_fragment, or html_with_css
    - css_style: Custom CSS to apply
    - syntax_highlighting: Enable/disable syntax highlighting
    
    Returns:
    - html: The converted HTML text
    - metadata: Conversion metadata
    """
    try:
        # Configure extensions
        extensions = request.extensions or ['extra', 'codehilite', 'tables', 'toc']
        if request.syntax_highlighting:
            extensions.append('codehilite')
        
        # Initialize markdown converter
        md = markdown.Markdown(extensions=extensions)
        html_content = md.convert(request.markdown_text)
        
        # Apply CSS based on output format
        if request.output_format == "html_with_css":
            css = request.css_style or DEFAULT_CSS
            html_content = f"<!DOCTYPE html><html><head><meta charset='utf-8'>{css}</head><body>{html_content}</body></html>"
        elif request.output_format == "html_fragment":
            # Return just the converted content without HTML structure
            pass
        else:  # html
            html_content = f"<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>{html_content}</body></html>"
        
        metadata = {
            "conversion_time": datetime.now().isoformat(),
            "extensions_used": extensions,
            "output_format": request.output_format,
            "input_length": len(request.markdown_text),
            "output_length": len(html_content)
        }
        
        return MarkdownResponse(html=html_content, metadata=metadata)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/convert/file", response_model=MarkdownResponse)
async def convert_markdown_file(
    file: UploadFile = File(...),
    extensions: Optional[str] = Form(None),
    output_format: Optional[str] = Form("html"),
    css_style: Optional[str] = Form(None),
    syntax_highlighting: Optional[bool] = Form(True)
):
    """
    Convert a Markdown file to HTML.
    
    Parameters:
    - file: Uploaded markdown file
    - extensions: Comma-separated list of extensions
    - output_format: html, html_fragment, or html_with_css
    - css_style: Custom CSS to apply
    - syntax_highlighting: Enable/disable syntax highlighting
    """
    if not file.filename.endswith(('.md', '.markdown')):
        raise HTTPException(status_code=400, detail="File must be a markdown file (.md or .markdown)")
    
    try:
        content = await file.read()
        markdown_text = content.decode('utf-8')
        
        # Parse extensions
        ext_list = extensions.split(',') if extensions else None
        
        request = MarkdownRequest(
            markdown_text=markdown_text,
            extensions=ext_list,
            output_format=output_format,
            css_style=css_style,
            syntax_highlighting=syntax_highlighting
        )
        
        return await convert_markdown(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/convert/batch", response_model=BatchResponse)
async def convert_markdown_batch(request: BatchRequest):
    """
    Convert multiple Markdown documents to HTML in a single request.
    
    Parameters:
    - documents: List of markdown conversion requests
    
    Returns:
    - results: List of conversion results
    - total_converted: Number of successfully converted documents
    """
    results = []
    for doc_request in request.documents:
        try:
            result = await convert_markdown(doc_request)
            results.append(result)
        except Exception as e:
            # Add error result
            results.append(MarkdownResponse(
                html="",
                metadata={"error": str(e), "conversion_time": datetime.now().isoformat()}
            ))
    
    return BatchResponse(
        results=results,
        total_converted=len([r for r in results if not r.metadata.get("error")])
    )

@app.get("/preview/{conversion_id}")
async def preview_conversion(conversion_id: str):
    """
    Preview a previously converted document (placeholder for future implementation).
    """
    return {"message": "Preview feature coming soon", "conversion_id": conversion_id}

@app.get("/extensions")
async def get_available_extensions():
    """
    Get list of available Markdown extensions.
    """
    return {
        "extensions": [
            "extra", "codehilite", "tables", "toc", "fenced_code", 
            "footnotes", "attr_list", "def_list", "abbr", "md_in_html"
        ],
        "description": "Available markdown extensions for enhanced conversion"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

@app.get("/")
async def root():
    """
    Root endpoint that returns API information
    """
    return {
        "name": "Advanced Markdown to HTML Converter API",
        "version": "2.0.0",
        "description": "Convert Markdown text to HTML with advanced features",
        "endpoints": {
            "/convert": "POST - Convert markdown text to HTML",
            "/convert/file": "POST - Convert uploaded markdown file to HTML",
            "/convert/batch": "POST - Convert multiple markdown documents",
            "/preview/{id}": "GET - Preview converted document",
            "/extensions": "GET - List available extensions",
            "/health": "GET - Health check",
            "/": "GET - This information"
        },
        "features": [
            "Text and file conversion",
            "Batch processing",
            "Custom CSS styling",
            "Syntax highlighting",
            "Multiple output formats",
            "Extension support",
            "Health monitoring"
        ]
    } 
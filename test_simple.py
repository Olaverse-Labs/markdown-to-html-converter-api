import requests
import json

# Test the conversion endpoint
markdown_text = """# Hello World

This is a **test** document with `code` and *italic* text.

## Features
- Text conversion
- File upload
- Batch processing
- Custom styling

## Code Example
```python
def hello():
    print("Hello, World!")
```
"""

response = requests.post(
    "http://localhost:8000/convert",
    json={
        "markdown_text": markdown_text,
        "output_format": "html_with_css"
    }
)

if response.status_code == 200:
    result = response.json()
    print("✅ Conversion successful!")
    print(f"Input length: {result['metadata']['input_length']} characters")
    print(f"Output length: {result['metadata']['output_length']} characters")
    print(f"Extensions used: {result['metadata']['extensions_used']}")
    print("\n📄 Converted HTML (first 500 chars):")
    print(result['html'][:500] + "...")
else:
    print(f"❌ Conversion failed: {response.text}") 
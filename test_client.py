import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_basic_conversion():
    """Test basic markdown to HTML conversion"""
    print("=== Testing Basic Conversion ===")
    
    markdown_text = """
# Hello World

This is a **bold** text and *italic* text.

## Code Example
```python
def hello():
    print("Hello, World!")
```

## List Example
- Item 1
- Item 2
  - Subitem 2.1
  - Subitem 2.2

## Table Example
| Name | Age | City |
|------|-----|------|
| John | 25  | NYC  |
| Jane | 30  | LA   |
"""
    
    response = requests.post(
        f"{BASE_URL}/convert",
        json={
            "markdown_text": markdown_text,
            "output_format": "html_with_css"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Basic conversion successful")
        print(f"Input length: {result['metadata']['input_length']}")
        print(f"Output length: {result['metadata']['output_length']}")
        print(f"Extensions used: {result['metadata']['extensions_used']}")
    else:
        print(f"❌ Basic conversion failed: {response.text}")

def test_custom_css():
    """Test conversion with custom CSS"""
    print("\n=== Testing Custom CSS ===")
    
    custom_css = """
    <style>
    body { 
        font-family: 'Courier New', monospace; 
        background-color: #1a1a1a; 
        color: #00ff00; 
        padding: 20px; 
    }
    h1 { color: #ff0000; text-align: center; }
    h2 { color: #ffff00; }
    code { background-color: #333; color: #00ffff; }
    </style>
    """
    
    markdown_text = "# Custom Styled Document\n\nThis has a **dark theme** with custom colors."
    
    response = requests.post(
        f"{BASE_URL}/convert",
        json={
            "markdown_text": markdown_text,
            "output_format": "html_with_css",
            "css_style": custom_css
        }
    )
    
    if response.status_code == 200:
        print("✅ Custom CSS conversion successful")
    else:
        print(f"❌ Custom CSS conversion failed: {response.text}")

def test_batch_conversion():
    """Test batch conversion of multiple documents"""
    print("\n=== Testing Batch Conversion ===")
    
    documents = [
        {
            "markdown_text": "# Document 1\n\nThis is the first document.",
            "output_format": "html_fragment"
        },
        {
            "markdown_text": "## Document 2\n\nThis is the second document with **bold** text.",
            "output_format": "html_fragment"
        },
        {
            "markdown_text": "### Document 3\n\n```python\nprint('Hello from doc 3')\n```",
            "output_format": "html_fragment"
        }
    ]
    
    response = requests.post(
        f"{BASE_URL}/convert/batch",
        json={"documents": documents}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Batch conversion successful")
        print(f"Total documents: {len(result['results'])}")
        print(f"Successfully converted: {result['total_converted']}")
        
        for i, doc_result in enumerate(result['results']):
            if 'error' not in doc_result['metadata']:
                print(f"  Document {i+1}: {doc_result['metadata']['output_length']} chars")
            else:
                print(f"  Document {i+1}: Error - {doc_result['metadata']['error']}")
    else:
        print(f"❌ Batch conversion failed: {response.text}")

def test_extensions():
    """Test available extensions endpoint"""
    print("\n=== Testing Extensions Endpoint ===")
    
    response = requests.get(f"{BASE_URL}/extensions")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Extensions endpoint successful")
        print(f"Available extensions: {', '.join(result['extensions'])}")
    else:
        print(f"❌ Extensions endpoint failed: {response.text}")

def test_health_check():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Health check successful")
        print(f"Status: {result['status']}")
        print(f"Version: {result['version']}")
        print(f"Timestamp: {result['timestamp']}")
    else:
        print(f"❌ Health check failed: {response.text}")

def test_api_info():
    """Test root endpoint for API information"""
    print("\n=== Testing API Info ===")
    
    response = requests.get(f"{BASE_URL}/")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ API info successful")
        print(f"Name: {result['name']}")
        print(f"Version: {result['version']}")
        print(f"Description: {result['description']}")
        print("Features:")
        for feature in result['features']:
            print(f"  - {feature}")
    else:
        print(f"❌ API info failed: {response.text}")

if __name__ == "__main__":
    print("🚀 Starting API Tests...\n")
    
    try:
        test_api_info()
        test_health_check()
        test_extensions()
        test_basic_conversion()
        test_custom_css()
        test_batch_conversion()
        
        print("\n🎉 All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running on http://localhost:8000")
        print("Run: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Test failed with error: {e}") 
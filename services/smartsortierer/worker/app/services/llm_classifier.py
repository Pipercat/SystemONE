"""
SmartSortierer Pro - LLM Classification Service
Uses Ollama for intelligent document categorization
"""
import json
from typing import Dict, Any, Optional
import httpx

from app.core.config import settings
from app.models.document import Document


class LLMClassifier:
    """
    Classifies documents using Ollama LLM.
    Extracts: category, suggested_filename, target_path, confidence, tags
    """
    
    def __init__(self):
        self.ollama_url = settings.ollama_base_url
        self.model = settings.OLLAMA_MODEL_CHAT
        self.available = False
        
        # Check if Ollama is available
        try:
            response = httpx.get(f"{self.ollama_url}/api/tags", timeout=5.0)
            self.available = response.status_code == 200
        except:
            self.available = False
    
    def build_prompt(self, document: Document) -> str:
        """
        Build classification prompt with document metadata and content preview.
        
        Args:
            document: Document to classify
            
        Returns:
            Prompt string for LLM
        """
        # Extract metadata
        filename = document.original_filename
        mime_type = document.mime_type or "unknown"
        file_size = document.file_size_bytes or 0
        
        # Text preview (first 2000 chars)
        text_preview = ""
        if document.extracted_text:
            text_preview = document.extracted_text[:2000]
            if len(document.extracted_text) > 2000:
                text_preview += "\n\n[... text truncated ...]"
        
        prompt = f"""You are a document classification assistant. Analyze the following document and provide a structured classification.

**Document Metadata:**
- Filename: {filename}
- MIME Type: {mime_type}
- File Size: {file_size} bytes

**Document Content Preview:**
{text_preview if text_preview else "(No text extracted)"}

**Task:**
Classify this document and provide:
1. **Category**: A descriptive category (e.g., "Invoice", "Contract", "Report", "Personal Document")
2. **Suggested Filename**: A clean, descriptive filename (keep extension, use underscore_case)
3. **Target Path**: Relative path under 03_sorted/ (e.g., "Finance/Invoices", "Projects/2024", "Personal/Medical")
4. **Confidence**: Your confidence level (0.0 to 1.0)
5. **Tags**: List of relevant tags (max 5)

**Output Format (JSON only, no explanations):**
{{
  "category": "Invoice",
  "suggested_filename": "invoice_company_2024_01.pdf",
  "target_path": "Finance/Invoices/2024",
  "confidence": 0.95,
  "tags": ["invoice", "finance", "2024"]
}}

Respond with JSON only:"""
        
        return prompt
    
    def parse_llm_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse LLM response and extract classification data.
        Handles both pure JSON and markdown-wrapped JSON.
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            Classification dict or None if parsing fails
        """
        try:
            # Try direct JSON parse
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown code block
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find any JSON object in text
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        return None
    
    def classify(self, document: Document) -> Optional[Dict[str, Any]]:
        """
        Classify a document using Ollama LLM.
        
        Args:
            document: Document to classify
            
        Returns:
            Classification result dict with:
            - category, suggested_filename, target_path, confidence, tags
            - llm_trace: Full LLM response for debugging
            Or None if classification fails or LLM unavailable
        """
        if not self.available:
            print(f"  ⚠ Ollama not available, skipping LLM classification")
            return None
        
        # Build prompt
        prompt = self.build_prompt(document)
        
        try:
            # Call Ollama generate API
            response = httpx.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Lower = more deterministic
                        "top_p": 0.9,
                    }
                },
                timeout=60.0,  # LLM can take time
            )
            
            if response.status_code != 200:
                print(f"  ✗ Ollama API error: {response.status_code}")
                return None
            
            # Parse response
            ollama_response = response.json()
            llm_text = ollama_response.get("response", "")
            
            # Extract classification data
            classification = self.parse_llm_response(llm_text)
            
            if not classification:
                print(f"  ✗ Failed to parse LLM response")
                return None
            
            # Validate required fields
            required_fields = ["category", "confidence"]
            if not all(field in classification for field in required_fields):
                print(f"  ✗ Missing required fields in LLM response")
                return None
            
            # Add full LLM response for tracing
            classification["llm_trace"] = {
                "model": self.model,
                "prompt_length": len(prompt),
                "response": llm_text[:500],  # Truncated
            }
            
            return classification
        
        except httpx.TimeoutException:
            print(f"  ✗ Ollama request timeout")
            return None
        
        except Exception as e:
            print(f"  ✗ LLM classification error: {e}")
            return None

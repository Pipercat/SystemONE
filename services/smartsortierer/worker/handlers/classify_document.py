"""
SmartSortierer Pro - Document Classification Handler
Applies rules engine and LLM classification
"""
import sys
import logging
from pathlib import Path
from typing import Dict, Any

# Add API path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "api"))

from app.core.database import SessionLocal
from app.models.document import Document, DocStatus
from app.services.rules_engine import RulesEngine
from app.services.llm_classifier import LLMClassifier

logger = logging.getLogger(__name__)


class ClassifyDocumentHandler:
    """
    Classify document using rules engine (priority) and LLM (fallback).
    
    Process:
    1. Try rules engine first (hard rules, high confidence)
    2. If no rule matches, try LLM classification
    3. Update document with classification results
    4. Set status to NEEDS_REVIEW or ANALYZED based on confidence
    """
    
    def __init__(self):
        self.llm = LLMClassifier()
    
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute classification job.
        
        Payload:
            - document_id: int
        
        Returns:
            - method: "rules" or "llm" or "none"
            - confidence: float
            - category: str
        """
        document_id = payload["document_id"]
        
        logger.info(f"Classifying document {document_id}")
        
        db = SessionLocal()
        try:
            # Get document
            document = db.query(Document).filter(Document.id == document_id).first()
            
            if not document:
                raise Exception(f"Document {document_id} not found")
            
            # 1. Try rules engine first
            rules_engine = RulesEngine(db)
            rule_result = rules_engine.classify_document(document)
            
            if rule_result:
                # Rule matched! Apply changes
                logger.info(f"Matched rule: {rule_result['rule_name']} (priority {rule_result['priority']})")
                
                # Rules have high confidence
                document.classification_confidence = 1.0
                
                # Store rule trace
                document.llm_trace = {
                    "method": "rules",
                    "rule_id": rule_result["rule_id"],
                    "rule_name": rule_result["rule_name"],
                    "changes": rule_result["changes"],
                }
                
                # Status: Rules are deterministic, mark as ANALYZED
                document.status = DocStatus.ANALYZED
                document.analyzed_at = db.execute(db.query(db.func.now())).scalar()
                
                db.commit()
                
                return {
                    "method": "rules",
                    "confidence": 1.0,
                    "category": document.category,
                    "rule_name": rule_result["rule_name"],
                }
            
            # 2. No rule matched, try LLM
            logger.info(f"No rule matched, trying LLM classification...")
            
            llm_result = self.llm.classify(document)
            
            if llm_result:
                # LLM classification successful
                logger.info(f"LLM classified: {llm_result.get('category')} (confidence {llm_result.get('confidence')})")
                
                # Apply LLM suggestions
                document.category = llm_result.get("category")
                document.suggested_filename = llm_result.get("suggested_filename")
                document.suggested_target_path = llm_result.get("target_path")
                document.classification_confidence = llm_result.get("confidence", 0.5)
                
                # Store LLM trace
                document.llm_trace = {
                    "method": "llm",
                    "model": self.llm.model,
                    **llm_result.get("llm_trace", {}),
                }
                
                # Status: LLM needs review if confidence < 0.8
                confidence = llm_result.get("confidence", 0.5)
                if confidence >= 0.8:
                    document.status = DocStatus.ANALYZED
                else:
                    document.status = DocStatus.NEEDS_REVIEW
                
                document.analyzed_at = db.execute(db.query(db.func.now())).scalar()
                
                db.commit()
                
                return {
                    "method": "llm",
                    "confidence": confidence,
                    "category": document.category,
                }
            
            # 3. No classification possible
            logger.warning(f"Could not classify (no rules, LLM unavailable)")
            
            document.status = DocStatus.NEEDS_REVIEW
            document.analyzed_at = db.execute(db.query(db.func.now())).scalar()
            db.commit()
            
            return {
                "method": "none",
                "confidence": 0.0,
                "category": None,
                "reason": "No rules matched and LLM unavailable",
            }
        
        finally:
            db.close()

"""
SmartSortierer Pro - Rules Engine
Evaluates classification rules based on priority
"""
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.document import Document


class RulesEngine:
    """
    Evaluates rules against documents for automatic classification.
    Rules are evaluated in priority order (lower number = higher priority).
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_active_rules(self) -> List[Dict[str, Any]]:
        """
        Get all active rules ordered by priority.
        
        Returns:
            List of rule dicts
        """
        query = text("""
            SELECT id, name, priority, conditions, actions
            FROM rules
            WHERE is_active = TRUE
            ORDER BY priority ASC
        """)
        
        result = self.db.execute(query)
        rules = []
        
        for row in result:
            rules.append({
                "id": row[0],
                "name": row[1],
                "priority": row[2],
                "conditions": row[3],  # JSONB
                "actions": row[4],      # JSONB
            })
        
        return rules
    
    def evaluate_condition(self, document: Document, condition: Dict[str, Any]) -> bool:
        """
        Evaluate a single condition against a document.
        
        Supported conditions:
            - filename_regex: Regex pattern for filename
            - mime_type: Exact mime type match
            - mime_type_contains: Partial mime type match
            - file_size_min: Minimum file size in bytes
            - file_size_max: Maximum file size in bytes
            - text_contains: Search in extracted text
        
        Args:
            document: Document to evaluate
            condition: Condition dict
            
        Returns:
            True if condition matches, False otherwise
        """
        # Filename regex
        if "filename_regex" in condition:
            pattern = condition["filename_regex"]
            if not re.search(pattern, document.original_filename, re.IGNORECASE):
                return False
        
        # Mime type exact match
        if "mime_type" in condition:
            if document.mime_type != condition["mime_type"]:
                return False
        
        # Mime type partial match
        if "mime_type_contains" in condition:
            if not document.mime_type or condition["mime_type_contains"].lower() not in document.mime_type.lower():
                return False
        
        # File size min
        if "file_size_min" in condition:
            if not document.file_size_bytes or document.file_size_bytes < condition["file_size_min"]:
                return False
        
        # File size max
        if "file_size_max" in condition:
            if not document.file_size_bytes or document.file_size_bytes > condition["file_size_max"]:
                return False
        
        # Text contains
        if "text_contains" in condition:
            if not document.extracted_text or condition["text_contains"].lower() not in document.extracted_text.lower():
                return False
        
        return True
    
    def evaluate_rule(self, document: Document, rule: Dict[str, Any]) -> bool:
        """
        Evaluate all conditions of a rule (AND logic).
        
        Args:
            document: Document to evaluate
            rule: Rule dict with conditions
            
        Returns:
            True if all conditions match, False otherwise
        """
        conditions = rule.get("conditions", {})
        
        # Empty conditions = match all
        if not conditions:
            return True
        
        # Evaluate each condition (AND logic)
        for key, value in conditions.items():
            condition = {key: value}
            if not self.evaluate_condition(document, condition):
                return False
        
        return True
    
    def apply_actions(self, document: Document, actions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply rule actions to document (doesn't save to DB).
        
        Actions:
            - category: Set category
            - target_path: Set target path
            - suggested_filename: Set suggested filename
            - tags: Add tags (list of tag names)
        
        Args:
            document: Document to modify
            actions: Actions dict
            
        Returns:
            Dict of applied changes for logging
        """
        changes = {}
        
        if "category" in actions:
            document.category = actions["category"]
            changes["category"] = actions["category"]
        
        if "target_path" in actions:
            document.suggested_target_path = actions["target_path"]
            changes["target_path"] = actions["target_path"]
        
        if "suggested_filename" in actions:
            document.suggested_filename = actions["suggested_filename"]
            changes["suggested_filename"] = actions["suggested_filename"]
        
        if "tags" in actions:
            changes["tags"] = actions["tags"]
            # Tag application handled separately (requires Tag model access)
        
        return changes
    
    def classify_document(self, document: Document) -> Optional[Dict[str, Any]]:
        """
        Classify a document by evaluating all rules.
        First matching rule wins (priority order).
        
        Args:
            document: Document to classify
            
        Returns:
            Dict with rule_id, rule_name, and applied changes, or None if no match
        """
        rules = self.get_active_rules()
        
        for rule in rules:
            if self.evaluate_rule(document, rule):
                # Rule matches, apply actions
                changes = self.apply_actions(document, rule["actions"])
                
                return {
                    "rule_id": rule["id"],
                    "rule_name": rule["name"],
                    "priority": rule["priority"],
                    "changes": changes,
                }
        
        return None

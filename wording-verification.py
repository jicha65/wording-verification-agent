#!/usr/bin/env python3
"""
Automatic Wording Verification Agent
Validates wording entries for linguistic accuracy, consistency, and cultural appropriateness
"""

import csv
import re
import sys
from pathlib import Path

class WordingVerifier:
    def __init__(self):
        self.common_typos = {
            'voide': 'voided',
            'excute': 'execute',
            'acitivate': 'activate',
            'succss': 'success',
            'reject': 'rejected',
        }
        
        self.status_patterns = {
            'ongoing': r'(ing|izing|ating)$',  # Executing, Processing, etc.
            'completed': r'(d|ed|ated|ed)$',  # Completed, Released, etc.
        }
        
        # ===== CONFIGURABLE RULES SECTION =====
        # Easy to add new rules here without changing verify logic
        
        # Rule 1: Toast message word replacements
        # If sub_category contains "Toast", replace these words with "successfully"
        self.toast_word_replacements = {
            'success': 'successfully',
            'succeed': 'successfully',
            'succeeded': 'successfully',
        }
        
        # Rule 2: Toast punctuation rules
        # Toast messages should end with "." not "!"
        self.toast_punctuation_rule = {
            'should_end_with': '.',
            'replace_exclamation': True,  # Convert ! to .
        }
        
        # Rule 3: Category-specific rules
        # Define rules that apply to specific categories/sub_categories
        self.category_rules = {
            'Toast': {
                'rules': ['use_successfully', 'use_period_punctuation'],
                'description': 'Toast messages should use "successfully" and end with period'
            },
            'Success Toast': {
                'rules': ['use_successfully', 'use_period_punctuation'],
                'description': 'Success toasts should use past participle + successfully, with period'
            },
            'Error Toast': {
                'rules': ['use_period_punctuation'],
                'description': 'Error messages should end with period'
            }
        }
        # ===== END RULES SECTION =====
    
    def check_spelling(self, word):
        """Check for common typos and misspellings"""
        word_lower = word.lower().replace(' ', '')
        for typo, correction in self.common_typos.items():
            if typo in word_lower:
                return True, correction
        return False, None
    
    def check_grammar(self, text):
        """Check for common grammar issues"""
        issues = []
        
        # Check for "Successed" or similar incorrect verb forms
        if re.search(r'\bSuccessed\b', text):
            issues.append(('grammar', 'Successfully', 'Incorrect verb form "Successed"'))
        
        # Check incomplete words
        if text.endswith('e') and len(text) > 2:
            base = text[:-1]
            if base + 'ed' in str(self.common_typos.values()):
                issues.append(('typo', base + 'ed', 'Incomplete word'))
        
        # Check verb-adverb word order
        if re.search(r'\bsuccessfully\s+\w+ed\b', text, re.IGNORECASE):
            issues.append(('grammar', None, 'Awkward word order for adverb placement'))
        
        # Check comma splice
        if re.search(r'[a-z]\,\s+[A-Z]', text):
            issues.append(('punctuation', None, 'Comma splice error'))
        
        return issues
    
    def check_consistency(self, text, category):
        """Check consistency with category standards"""
        issues = []
        
        # Success messages should be consistent
        if category == 'Success Toast':
            # Should start with capital letter
            if text and text[0].islower():
                issues.append(('consistency', text[0].upper() + text[1:], 'Messages should start with capital letter'))
            
            # Should use consistent success format
            if ' success' in text.lower() and 'successfully' not in text.lower():
                if not re.search(r'Successful[ly]?', text):
                    issues.append(('consistency', None, 'Use consistent success terminology (Successful/Successfully)'))
        
        # Status messages should be consistent
        if category == 'Status':
            if text and text[0].islower():
                issues.append(('consistency', text[0].upper() + text[1:], 'Statuses should start with capital letter'))
        
        return issues
    
    def check_clarity(self, text):
        """Check for clarity and vagueness"""
        issues = []
        
        # Vague terms
        vague_terms = ['data', 'thing', 'stuff', 'it']
        for term in vague_terms:
            if f' {term}' in text.lower() or text.lower().endswith(term):
                if term == 'data':
                    issues.append(('clarity', 'report', 'Vague term, use specific alternative'))
        
        # Incomplete messages
        if text.lower() == 'succeed' or text.lower() == 'success':
            issues.append(('clarity', 'Operation successful', 'Incomplete message, clarify what succeeded'))
        
        # Check for abbreviations that might be unclear
        if re.search(r'\bSync\b|\bGM\b|\bInit\b', text):
            if text == 'Init':
                issues.append(('clarity', 'Initialized', 'Technical jargon, use full word'))
            elif 'Sync' in text and text == 'Sync successfully':
                issues.append(('clarity', 'Sync Successful', 'Abbreviation may be unclear'))
        
        return issues
    
    def apply_toast_word_replacements(self, text, sub_category):
        """Replace common words with 'successfully' in toast messages"""
        issues = []
        
        # Check if this is a toast message
        if 'toast' in sub_category.lower():
            for old_word, replacement in self.toast_word_replacements.items():
                # Look for the word as a whole word (not part of another word)
                pattern = r'\b' + old_word + r'\b'
                if re.search(pattern, text, re.IGNORECASE):
                    # Replace it
                    corrected = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
                    issues.append(('rule', corrected, f'Toast: Use "{replacement}" instead of "{old_word}"'))
        
        return issues
    
    def apply_toast_punctuation_rules(self, text, sub_category):
        """Apply punctuation rules for toast messages"""
        issues = []
        
        # Check if this is a toast message
        if 'toast' in sub_category.lower():
            # Rule: Toast should end with period, not exclamation mark
            if text.endswith('!'):
                corrected = text[:-1] + '.'
                issues.append(('rule', corrected, 'Toast: Should end with period (.) not exclamation mark (!)'))
            elif not text.endswith('.') and not text.endswith('!'):
                # If doesn't end with punctuation, add period
                corrected = text + '.'
                issues.append(('rule', corrected, 'Toast: Should end with period (.)'))
        
        return issues
    
    def apply_category_rules(self, text, category, sub_category):
        """Apply rules based on category/sub_category"""
        issues = []
        
        # Check against category_rules
        for rule_category, rule_config in self.category_rules.items():
            # Match by sub_category or category
            if rule_category.lower() in sub_category.lower() or rule_category.lower() in category.lower():
                for rule_name in rule_config['rules']:
                    if rule_name == 'use_successfully':
                        toast_issues = self.apply_toast_word_replacements(text, sub_category)
                        issues.extend(toast_issues)
                    elif rule_name == 'use_period_punctuation':
                        punct_issues = self.apply_toast_punctuation_rules(text, sub_category)
                        issues.extend(punct_issues)
        
        return issues
    
    def verify_entry(self, category, sub_category, wording):
        """Main verification function for a single entry"""
        
        if not wording or not wording.strip():
            return 'Yes', 'N/A', 'Empty entry'
        
        is_correct = True
        suggestions = []
        reasons = []
        
        # Run all checks
        has_typo, typo_fix = self.check_spelling(wording)
        if has_typo:
            is_correct = False
            suggestions.append(typo_fix)
            reasons.append('Typo detected')
        
        grammar_issues = self.check_grammar(wording)
        if grammar_issues:
            is_correct = False
            for issue_type, fix, reason in grammar_issues:
                if fix:
                    suggestions.append(fix)
                reasons.append(reason)
        
        consistency_issues = self.check_consistency(wording, sub_category)
        if consistency_issues:
            is_correct = False
            for issue_type, fix, reason in consistency_issues:
                if fix:
                    suggestions.append(fix)
                reasons.append(reason)
        
        clarity_issues = self.check_clarity(wording)
        if clarity_issues:
            is_correct = False
            for issue_type, fix, reason in clarity_issues:
                if fix:
                    suggestions.append(fix)
                reasons.append(reason)
        
        # NEW: Apply configurable category rules
        rule_issues = self.apply_category_rules(wording, category, sub_category)
        if rule_issues:
            is_correct = False
            for issue_type, fix, reason in rule_issues:
                if fix:
                    suggestions.append(fix)
                reasons.append(reason)
        
        # Format results
        is_right = 'Yes' if is_correct else 'No'
        suggested_fix = suggestions[0] if suggestions else 'N/A'
        why_suggest = ' | '.join(set(reasons)) if reasons else 'No issues found'
        
        return is_right, suggested_fix, why_suggest
    
    
    def process_csv(self, csv_path):
        """Process CSV file and fill validation columns"""
        
        try:
            # Read existing CSV
            rows = []
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            # Process each row
            updated_rows = []
            changes_made = 0
            
            for row in rows:
                # Only process if validation columns are empty
                if not row.get('Is the word right', '').strip():
                    category = row.get('Words Category', '')
                    sub_category = row.get('Sub Category', '')
                    wording = row.get('Current Wording', '')
                    
                    is_right, suggestion, reason = self.verify_entry(category, sub_category, wording)
                    
                    row['Is the word right'] = is_right
                    row['If not right, what is suggested'] = suggestion
                    row['Why suggest this word'] = reason
                    
                    if is_right == 'No':
                        changes_made += 1
                
                updated_rows.append(row)
            
            # Write back to CSV
            if changes_made > 0 or any(row.get('Is the word right', '').strip() for row in updated_rows):
                with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                    fieldnames = rows[0].keys() if rows else []
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(updated_rows)
                
                print(f"✓ Verification complete: {changes_made} issues found and corrected")
                return True
            else:
                print("✓ No new issues found")
                return False
        
        except Exception as e:
            print(f"✗ Error processing CSV: {e}")
            return False

if __name__ == '__main__':
    # Default CSV path
    csv_file = 'Wording Criterias-Wording.csv'
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    # Run verification
    verifier = WordingVerifier()
    success = verifier.process_csv(csv_file)
    
    sys.exit(0 if success else 1)

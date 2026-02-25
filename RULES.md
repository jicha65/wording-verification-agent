# 📋 Wording Verification Rules Guide

## Overview

The wording verification agent uses a **configurable rules system** that makes it easy to add, modify, and manage verification rules without touching the core logic.

---

## Current Rules

### Rule 1: "Successfully" Format ✅

**When to use:** For all action verbs + "successfully" statements

**Requirement:**
- ✗ Bad: "Save Successful" or "Save Successfully" (base verb)
- ✓ Good: "Saved Successfully" (past participle)

**Examples:**
```
Saved Successfully     ✓
Deleted Successfully   ✓
Updated Successfully   ✓
Exported Successfully  ✓
Processing...          ✓ (ongoing verb form is okay)
```

**Why:** Consistency - completed actions use past participle form for clarity

---

### Rule 2: "Not" Prefix (NOT "Un-") ✅

**When to use:** To indicate negation/opposite meaning

**Requirement:**
- ✗ Bad: Unopened, Unconfirmed, Unavailable, Unbound, Unsubscribe
- ✓ Good: Not Opened, Not Confirmed, Not Available, Not Bound, Not Subscribed

**Examples:**
```
Not Available         ✓
Not Found            ✓
Not Scheduled        ✓
Not Configured       ✓
```

**Why:** Consistency and clarity - "Not" is more explicit than "Un-" prefix

---

### Rule 3: Toast Punctuation ✅ (NEW)

**When to use:** For all toast notification messages

**Requirement:**
- ✗ Bad: "Saved Successfully!"
- ✓ Good: "Saved Successfully."

**Why:** Professional and consistent - periods for declarative statements

---

### Rule 4: Toast Word Replacements ✅ (NEW)

**When to use:** In toast message categories (any sub_category containing "Toast")

**Requirement:**
- ✗ Bad: "Operation Success" or "Operation Succeed"
- ✓ Good: "Operation Successfully Completed"

**Word Replacements:**
```
success    → successfully
succeed    → successfully
succeeded  → successfully
```

**Why:** Toasts should use adverbs (-ly) for better grammar flow

---

## How to Add New Rules

### Step 1: Edit the Rules Configuration

Open `wording-verification.py` and find the `__init__` method of the `WordingVerifier` class.

Locate this section:
```python
# ===== CONFIGURABLE RULES SECTION =====
```

### Step 2: Add Your Rule

**Example 1: Add a New Word Replacement Rule**

```python
# In __init__ method, add to toast_word_replacements:
self.toast_word_replacements = {
    'success': 'successfully',
    'succeed': 'successfully',
    'succeeded': 'successfully',
    'complete': 'completed',  # NEW RULE
}
```

**Example 2: Add a Category-Specific Rule**

```python
# Add to category_rules dictionary:
self.category_rules = {
    'Toast': {...},
    'Warning Toast': {  # NEW CATEGORY
        'rules': ['use_period_punctuation'],
        'description': 'Warning messages should end with period'
    }
}
```

### Step 3: Create the Check Method

If adding a new type of rule, create a corresponding method.

**Example:**
```python
def apply_custom_rule(self, text, category):
    """Apply your new custom rule"""
    issues = []
    
    if 'Email' in category:
        if not '@' in text:
            issues.append('Email addresses should contain @')
    
    return issues
```

### Step 4: Call the Method in verify_entry

Add your method call in the `verify_entry` function:

```python
# Add with other rule checks
custom_issues = self.apply_custom_rule(wording, category)
if custom_issues:
    is_correct = False
    for issue_type, fix, reason in custom_issues:
        if fix:
            suggestions.append(fix)
        reasons.append(reason)
```

### Step 5: Test the Rule

Test with a sample entry:
```bash
python wording-verification.py
```

Or use the web app: Submit an entry that should trigger your new rule.

---

## Rule Structure

All rules follow this structure:

```python
{
    'trigger': 'When rule applies',
    'check': 'What to validate',
    'fix': 'Suggested correction',
    'reason': 'Why this rule exists'
}
```

---

## Common Rule Patterns

### Pattern 1: Word Replacement

```python
self.word_replacements = {
    'old_word': 'new_word',
    'another_bad': 'another_good',
}

def check_word_replacement(self, text):
    for old, new in self.word_replacements.items():
        if old in text.lower():
            return True, new, f'Use "{new}" instead of "{old}"'
    return False, None, None
```

### Pattern 2: Grammar Check

```python
def check_custom_grammar(self, text):
    issues = []
    
    if some_condition(text):
        issues.append((
            'grammar',
            suggested_fix,
            'reason for suggestion'
        ))
    
    return issues
```

### Pattern 3: Category-Specific Rule

```python
def check_by_category(self, text, category):
    issues = []
    
    if 'CategoryName' in category:
        if not expected_pattern(text):
            issues.append((
                'rule',
                correction,
                'reason'
            ))
    
    return issues
```

---

## Rule Examples You Can Add

### Example: Required Punctuation

```python
def apply_punctuation_rule(self, text, category):
    """Ensure messages end with appropriate punctuation"""
    issues = []
    
    if 'Message' in category:
        if not text.endswith(('.', '!', '?')):
            corrected = text + '.'
            issues.append(('rule', corrected, 'Messages should end with punctuation'))
    
    return issues
```

### Example: Length Validation

```python
def check_length_constraint(self, text, category):
    """Ensure text meets length requirements"""
    issues = []
    
    if 'Button Label' in category:
        if len(text) > 25:
            issues.append(('rule', None, 'Button labels should be under 25 characters'))
    
    return issues
```

### Example: Format Validation

```python
def check_date_format(self, text, category):
    """Ensure dates follow consistent format"""
    issues = []
    
    if 'Date' in category:
        # Check for YYYY-MM-DD format
        if not re.match(r'\d{4}-\d{2}-\d{2}', text):
            issues.append(('rule', None, 'Use YYYY-MM-DD format for dates'))
    
    return issues
```

---

## Managing Multiple Rules

### Priority & Conflicts

If multiple rules apply to the same entry:
1. All rules are checked
2. First issue found is suggested
3. All reasons are displayed

### Disable a Rule

Comment out or remove the check call:

```python
# This rule is disabled:
# rule_issues = self.apply_custom_rule(wording, category)
```

### Override a Rule

Create a more specific rule that takes precedence:

```python
# More specific: Only for certain sub-categories
if 'Success Toast' in sub_category:
    # Apply special rule for success toasts
elif 'Error Toast' in sub_category:
    # Apply different rule for error toasts
```

---

## Rule Testing Checklist

When adding a new rule:

- [ ] Rule is documented in RULES.md
- [ ] Test case added to CSV with expected result
- [ ] Run verification on test case
- [ ] Rule correctly identifies issue
- [ ] Rule suggests appropriate fix
- [ ] Rule explanation is clear
- [ ] Reason message is helpful
- [ ] No false positives on unrelated entries
- [ ] Works in both web app and CLI

---

## File Locations

**Rules are defined in:**
- `wording-verification.py` - Main verification engine
- `app.py` - Web app version of rules

**Both files must be kept in sync** for consistent behavior.

---

## Quick Reference

| Rule | Type | Category | Applies To |
|------|------|----------|-----------|
| Successfully Format | Grammar | All | Action verbs |
| Not Prefix | Consistency | All | Negations |
| Toast Punctuation | Format | Toast | Toast messages |
| Toast Words | Word Replace | Toast | Toast messages |

---

## Need Help?

**To create a new rule:**
1. Define rule in Rules Configuration section
2. Create check method
3. Call method in verify_entry
4. Test with sample entry
5. Document in RULES.md

**Questions?** Check the examples above or review existing rules in the code!

---

**Last Updated:** February 25, 2026
**Version:** 2.0 (with configurable rules)

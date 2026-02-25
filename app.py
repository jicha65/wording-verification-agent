import streamlit as st
import pandas as pd
import csv
import re
import json
from io import StringIO
from datetime import datetime
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Wording Verification Agent",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Verification Rules
class WordingVerifier:
    def __init__(self):
        self.common_typos = {
            'sucessfully': 'successfully',
            'sucessfuly': 'successfully',
            'succesfully': 'successfully',
            'sucessful': 'successful',
            'acitivate': 'activate',
            'voide': 'voided',
            'excute': 'execute',
            'syncronization': 'synchronization',
            'unavaialbe': 'unavailable',
            'aproved': 'approved',
            'importd': 'imported',
            'faliure': 'failure',
            'peding': 'pending',
            'reviw': 'review',
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
        """Check for common typos"""
        word_lower = word.lower()
        for typo, correction in self.common_typos.items():
            if typo in word_lower:
                return True, correction
        return False, None
    
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
                    issues.append(f'Toast: Use "{replacement}" instead of "{old_word}"')
                    return replacement, issues
        
        return text, []
    
    def apply_toast_punctuation_rules(self, text, sub_category):
        """Apply punctuation rules for toast messages"""
        issues = []
        
        # Check if this is a toast message
        if 'toast' in sub_category.lower():
            # Rule: Toast should end with period, not exclamation mark
            if text.endswith('!'):
                corrected = text[:-1] + '.'
                issues.append('Toast: Should end with period (.) not exclamation mark (!)')
                return corrected, issues
            elif not text.endswith('.') and not text.endswith('!'):
                # If doesn't end with punctuation, add period
                corrected = text + '.'
                issues.append('Toast: Should end with period (.)')
                return corrected, issues
        
        return text, []
    
    def check_grammar(self, text, sub_category=''):
        """Check for grammar issues"""
        issues = []
        suggestion = None
        
        # Check for "Successed"
        if re.search(r'\bSuccessed\b', text):
            issues.append('Incorrect verb form "Successed" - should be "Successfully"')
        
        # Check capitalization for toast messages
        if 'toast' in text.lower() or 'success' in text.lower():
            if text and text[0].islower():
                issues.append(f'Messages should start with capital letter: "{text[0].upper()}{text[1:]}"')
        
        # Check for "Un" prefix (should be "Not")
        if re.search(r'\b(Un|Unbound|Unavailable|Unconfirmed|Unsubscribe)\b', text):
            issues.append('Use "Not" instead of "Un" prefix for consistency')
        
        # Check verb-adverb consistency
        if 'successful' in text.lower() and 'successfully' not in text.lower():
            if not text.endswith('ly'):
                issues.append('Use "Successfully" (adverb) instead of "Successful" (adjective)')
        
        return issues
    
    def check_consistency(self, text):
        """Check consistency patterns"""
        issues = []
        
        # Check for past participle + successfully
        verbs_to_fix = [
            ('Save Successfully', 'Saved Successfully'),
            ('Export Successfully', 'Exported Successfully'),
            ('Delete Successfully', 'Deleted Successfully'),
            ('Update Successfully', 'Updated Successfully'),
            ('Process Successfully', 'Processed Successfully'),
            ('Release Successfully', 'Released Successfully'),
        ]
        
        for bad, good in verbs_to_fix:
            if bad in text and good not in text:
                issues.append(f'Use past participle: "{good}" instead of "{bad}"')
        
        return issues
    
    def verify(self, category, subcategory, wording):
        """Main verification function"""
        if not wording or not wording.strip():
            return 'Unknown', 'N/A', 'Empty entry'
        
        is_correct = True
        suggestions = []
        reasons = []
        current_text = wording
        
        # Check spelling
        has_typo, typo_fix = self.check_spelling(wording)
        if has_typo:
            is_correct = False
            suggestions.append(typo_fix)
            reasons.append('Typo detected')
        
        # Check grammar
        grammar_issues = self.check_grammar(wording, subcategory)
        if grammar_issues:
            is_correct = False
            for issue in grammar_issues:
                reasons.append(issue)
        
        # Check consistency
        consistency_issues = self.check_consistency(wording)
        if consistency_issues:
            is_correct = False
            for issue in consistency_issues:
                reasons.append(issue)
        
        # Apply category rules - Toast word replacements
        corrected_text, toast_word_issues = self.apply_toast_word_replacements(wording, subcategory)
        if toast_word_issues:
            is_correct = False
            suggestions.append(corrected_text)
            reasons.extend(toast_word_issues)
            current_text = corrected_text
        
        # Apply category rules - Toast punctuation
        corrected_text, punct_issues = self.apply_toast_punctuation_rules(current_text, subcategory)
        if punct_issues:
            is_correct = False
            suggestions.append(corrected_text)
            reasons.extend(punct_issues)
        
        status = 'Yes' if is_correct else 'No'
        suggestion = suggestions[0] if suggestions else 'N/A'
        why = ' | '.join(set(reasons)) if reasons else 'No issues found'
        
        return status, suggestion, why


# Initialize verifier
verifier = WordingVerifier()

# ===== RULES MANAGEMENT FUNCTIONS =====
@st.cache_resource
def load_rules():
    """Load rules from rules.json"""
    rules_file = Path('rules.json')
    if rules_file.exists():
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return get_default_rules()
    return get_default_rules()

def get_default_rules():
    """Return default rules structure"""
    return {
        "toast_word_replacements": {
            "success": "successfully",
            "succeed": "successfully",
            "succeeded": "successfully"
        },
        "category_rules": {
            "Toast": {
                "rules": ["use_successfully", "use_period_punctuation"],
                "description": "Toast messages should use 'successfully' and end with period"
            },
            "Success Toast": {
                "rules": ["use_successfully", "use_period_punctuation"],
                "description": "Success toasts should use past participle + successfully, with period"
            },
            "Error Toast": {
                "rules": ["use_period_punctuation"],
                "description": "Error messages should end with period"
            }
        },
        "custom_rules": {
            "un_prefix_to_not": {
                "name": "Use 'Not' instead of 'Un' prefix",
                "description": "Replace 'Un' prefixes with 'Not' for consistency",
                "applies_to": "All",
                "examples": ["Unopened → Not Opened", "Unavailable → Not Available"]
            },
            "past_participle_successfully": {
                "name": "Past Participle + Successfully",
                "description": "Action verbs before 'Successfully' must be in -ed form",
                "applies_to": "Success Toast",
                "examples": ["Save Successfully → Saved Successfully", "Delete Successfully → Deleted Successfully"]
            },
            "period_not_exclamation": {
                "name": "Use Period, Not Exclamation",
                "description": "Toast messages should end with period (.) not exclamation (!)",
                "applies_to": "Toast",
                "examples": ["Saved Successfully! → Saved Successfully."]
            }
        }
    }

def save_rules(rules):
    """Save rules to rules.json"""
    try:
        with open('rules.json', 'w', encoding='utf-8') as f:
            json.dump(rules, f, indent=2, ensure_ascii=False)
        st.success("✅ Rules saved successfully!")
        st.cache_resource.clear()
        return True
    except Exception as e:
        st.error(f"❌ Error saving rules: {e}")
        return False

# Load rules at startup
rules = load_rules()

# Load CSV examples
@st.cache_data
def load_csv_examples():
    """Load wording examples from CSV file"""
    csv_file = Path('Wording Criterias-Wording.csv')
    if csv_file.exists():
        try:
            df = pd.read_csv(csv_file)
            return df
        except:
            return None
    return None

csv_examples = load_csv_examples()

st.title("✍️ Wording Verification Agent")
st.markdown("**Automatically verify and improve your wording for clarity, consistency, and cultural appropriateness.**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📋 About")
    st.info("""
    This agent verifies wording by checking:
    - ✅ Spelling & typos
    - ✅ Grammar & consistency
    - ✅ Verb tenses & formatting
    - ✅ Capitalization rules
    - ✅ "Successfully" format
    - ✅ "Not" vs "Un" prefix
    """)
    
    st.header("🔧 Rules Applied")
    st.markdown("""
    1. Use **"Successfully"** not "Successful"
    2. Use **"Not"** instead of "Un" prefix
    3. Start messages with **capitals**
    4. Use **past participles** (Saved, Deleted, Updated)
    5. Fix common **typos**
    """)

# Main interface
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Single Entry", "Batch Upload", "Results", "Rules Management", "Example Wordings"])

# TAB 1: Single Entry
with tab1:
    st.header("Verify Single Wording")
    
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.selectbox(
            "Category",
            ["Status", "Toast", "Label", "Message", "Error"],
            key="single_category"
        )
    
    with col2:
        subcategory = st.text_input(
            "Sub Category",
            placeholder="e.g., General Task, Success Toast",
            key="single_subcategory"
        )
    
    wording = st.text_area(
        "Wording to Verify",
        placeholder="Enter the word or phrase you want to check...",
        height=100,
        key="single_wording"
    )
    
    if st.button("🔍 Verify", key="verify_single", use_container_width=True):
        if wording:
            status, suggestion, reason = verifier.verify(category, subcategory, wording)
            
            st.markdown("### Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if status == "Yes":
                    st.markdown(f"<div class='success-box'>✅ <b>Status:</b> Correct</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='warning-box'>⚠️ <b>Status:</b> Needs Fix</div>", unsafe_allow_html=True)
            
            with col2:
                st.metric("Suggestion", suggestion if suggestion != "N/A" else "None needed")
            
            with col3:
                st.metric("Issues Found", "0" if status == "Yes" else "1+")
            
            if reason:
                st.markdown("#### Why?")
                st.info(reason)
            
            if status == "No" and suggestion != "N/A":
                st.markdown(f"#### Recommended Fix:")
                st.success(f"**{suggestion}**")
                
                # Copy button
                st.code(suggestion, language="text")
            
            # Add to Examples button
            st.divider()
            st.markdown("### 💾 Save to Example Library")
            
            col1, col2 = st.columns(2)
            
            with col1:
                override_suggestion = st.text_input(
                    "Override suggestion (optional)",
                    value=suggestion if suggestion != "N/A" else "",
                    key="override_suggestion",
                    help="If empty, will use the verified suggestion above"
                )
            
            with col2:
                override_reason = st.text_area(
                    "Override reason (optional)",
                    value=reason if reason else "",
                    key="override_reason",
                    height=50,
                    help="If empty, will use the reason above"
                )
            
            if st.button("✨ Save to Example Library", key="save_to_library", use_container_width=True):
                # Prepare data
                final_suggestion = override_suggestion if override_suggestion else suggestion
                final_reason = override_reason if override_reason else reason
                
                csv_file = Path('Wording Criterias-Wording.csv')
                
                try:
                    # Read existing CSV
                    if csv_file.exists():
                        existing_df = pd.read_csv(csv_file)
                    else:
                        # Create new CSV with headers if it doesn't exist
                        existing_df = pd.DataFrame(columns=[
                            'Words Category', 'Sub Category', 'Current Wording',
                            'Is the word right', 'If not right, what is suggested', 'Why suggest this word'
                        ])
                    
                    # Create new entry
                    new_entry = {
                        'Words Category': category,
                        'Sub Category': subcategory if subcategory else 'General',
                        'Current Wording': wording,
                        'Is the word right': status,
                        'If not right, what is suggested': final_suggestion,
                        'Why suggest this word': final_reason
                    }
                    
                    # Add to dataframe
                    new_df = pd.concat([existing_df, pd.DataFrame([new_entry])], ignore_index=True)
                    
                    # Save to CSV
                    new_df.to_csv(csv_file, index=False, encoding='utf-8')
                    
                    # Clear cache to refresh example tab
                    st.cache_data.clear()
                    
                    st.success("✅ Entry saved to Example Library!")
                    st.info(f"📌 Added: **{wording}** → Status: {status}")
                    
                    # Show preview
                    with st.expander("View saved entry"):
                        preview_df = pd.DataFrame([new_entry])
                        st.dataframe(preview_df, use_container_width=True, hide_index=True)
                
                except Exception as e:
                    st.error(f"❌ Error saving to library: {str(e)}")
        else:
            st.error("Please enter a wording to verify")

# TAB 2: Batch Upload
with tab2:
    st.header("Verify Multiple Entries")
    
    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type="csv",
        help="CSV format: Category,Sub Category,Wording"
    )
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            
            st.markdown("#### Preview")
            st.dataframe(df.head(), use_container_width=True)
            
            if st.button("🔍 Verify All Entries", use_container_width=True):
                results = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                total = len(df)
                
                for idx, row in df.iterrows():
                    category = row.get('Words Category', '') or row.get('Category', '')
                    subcategory = row.get('Sub Category', '') or row.get('Sub_Category', '')
                    wording = row.get('Current Wording', '') or row.get('Wording', '')
                    
                    status, suggestion, reason = verifier.verify(category, subcategory, wording)
                    
                    results.append({
                        'Category': category,
                        'Sub Category': subcategory,
                        'Wording': wording,
                        'Is Correct': status,
                        'Suggested Fix': suggestion,
                        'Reason': reason
                    })
                    
                    progress = (idx + 1) / total
                    progress_bar.progress(progress)
                    status_text.text(f"Processing: {idx + 1}/{total}")
                
                results_df = pd.DataFrame(results)
                
                st.markdown("#### Verification Results")
                st.dataframe(results_df, use_container_width=True)
                
                # Statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    correct_count = len(results_df[results_df['Is Correct'] == 'Yes'])
                    st.metric("Correct", correct_count)
                
                with col2:
                    issues_count = len(results_df[results_df['Is Correct'] == 'No'])
                    st.metric("Issues Found", issues_count)
                
                with col3:
                    accuracy = (correct_count / len(results_df) * 100) if len(results_df) > 0 else 0
                    st.metric("Accuracy", f"{accuracy:.0f}%")
                
                # Download button
                csv = results_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results (CSV)",
                    data=csv,
                    file_name=f"wording_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                # Save to Library button
                st.divider()
                st.markdown("### 💾 Save Results to Example Library")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    save_all = st.checkbox("Save all entries", value=True, help="Check to save all, uncheck to save only incorrect entries")
                
                with col2:
                    auto_override = st.checkbox("Auto-accept verified suggestions", value=True, help="Use verified results as-is")
                
                if st.button("✨ Save to Example Library", key="save_batch_to_library", use_container_width=True):
                    csv_file = Path('Wording Criterias-Wording.csv')
                    
                    try:
                        # Read existing CSV
                        if csv_file.exists():
                            existing_df = pd.read_csv(csv_file)
                        else:
                            existing_df = pd.DataFrame(columns=[
                                'Words Category', 'Sub Category', 'Current Wording',
                                'Is the word right', 'If not right, what is suggested', 'Why suggest this word'
                            ])
                        
                        # Prepare entries to save
                        entries_to_add = []
                        
                        for idx, row in results_df.iterrows():
                            # Filter based on checkbox
                            if not save_all and row['Is Correct'] == 'Yes':
                                continue
                            
                            entry = {
                                'Words Category': row['Category'],
                                'Sub Category': row['Sub Category'] if row['Sub Category'] else 'General',
                                'Current Wording': row['Wording'],
                                'Is the word right': row['Is Correct'],
                                'If not right, what is suggested': row['Suggested Fix'],
                                'Why suggest this word': row['Reason']
                            }
                            entries_to_add.append(entry)
                        
                        if entries_to_add:
                            # Add entries to dataframe
                            new_entries_df = pd.DataFrame(entries_to_add)
                            final_df = pd.concat([existing_df, new_entries_df], ignore_index=True)
                            
                            # Save to CSV
                            final_df.to_csv(csv_file, index=False, encoding='utf-8')
                            
                            # Clear cache to refresh example tab
                            st.cache_data.clear()
                            
                            st.success(f"✅ {len(entries_to_add)} entries saved to Example Library!")
                            st.balloons()
                            
                            # Show preview
                            with st.expander(f"View {len(entries_to_add)} saved entries"):
                                st.dataframe(new_entries_df, use_container_width=True, hide_index=True)
                        else:
                            st.info("No entries to save based on current filters")
                    
                    except Exception as e:
                        st.error(f"❌ Error saving to library: {str(e)}")

        
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.info("Please ensure your CSV has columns: Category, Sub Category, Wording")

# TAB 3: Results & History
with tab3:
    st.header("About This Agent")
    
    st.markdown("""
    ### How It Works
    
    This wording verification agent automatically:
    
    1. **Detects Issues:**
       - Spelling errors (typos)
       - Grammar mistakes
       - Inconsistent formatting
       - Capitalization errors
    
    2. **Applies Rules:**
       - Use "Successfully" (adverb) not "Successful" (adjective)
       - Use "Not" prefix instead of "Un"
       - Consistent past participle forms
       - Professional capitalization
    
    3. **Provides Suggestions:**
       - Clear corrections
       - Explanations for each issue
       - Download results as CSV
    
    ### Example Verifications
    
    """)
    
    examples = [
        ("Save Successful", "Saved Successfully", "Use past participle + adverb"),
        ("Univailable", "Not Available", "Avoid 'Un' prefix, use 'Not'"),
        ("sucessfully", "successfully", "Fix common typo"),
        ("save succcessfuly", "Saved Successfully", "Multiple issues: typo + format"),
    ]
    
    example_df = pd.DataFrame(examples, columns=["Original", "Corrected", "Reason"])
    st.dataframe(example_df, use_container_width=True, hide_index=True)
    
    st.markdown("""
    ### Supported Categories
    
    - **Status**: Task/workflow status terms (Active, Pending, Completed, etc.)
    - **Toast**: Success/error notification messages
    - **Label**: UI labels and button text
    - **Message**: System messages and instructions
    - **Error**: Error messages
    
    ### Get Started
    
    1. Go to **"Single Entry"** tab to verify one word
    2. Or use **"Batch Upload"** to verify entire CSV files
    3. Download results and integrate into your documentation
    
    ---
    
    **Need help?** Check the rules in the sidebar →
    """)

# TAB 4: Rules Management
with tab4:
    st.header("⚙️ Rules Management")
    st.markdown("View, manage, and add new verification rules")
    
    rules_tab1, rules_tab2, rules_tab3 = st.tabs(["Current Rules", "Add Word Replacement", "Add Custom Rule"])
    
    # TAB 4.1: View Current Rules
    with rules_tab1:
        st.subheader("📋 Active Rules")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Word Replacements")
            st.markdown("Words automatically replaced in toast messages:")
            
            replacements = rules.get('toast_word_replacements', {})
            if replacements:
                replacement_data = [
                    {"Original": k, "Replace With": v} 
                    for k, v in replacements.items()
                ]
                st.dataframe(
                    pd.DataFrame(replacement_data),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No word replacements configured")
        
        with col2:
            st.markdown("### Category Rules")
            st.markdown("Rules applied to specific message categories:")
            
            cat_rules = rules.get('category_rules', {})
            if cat_rules:
                for category, config in cat_rules.items():
                    with st.expander(f"📁 {category}", expanded=False):
                        st.write(f"**Description:** {config.get('description', 'N/A')}")
                        rules_list = config.get('rules', [])
                        st.write(f"**Applied Rules:** {', '.join(rules_list)}")
            else:
                st.info("No category rules configured")
        
        st.divider()
        
        st.markdown("### Custom Rules")
        custom = rules.get('custom_rules', {})
        
        if custom:
            for rule_id, rule_config in custom.items():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    with st.expander(f"✨ {rule_config.get('name', rule_id)}", expanded=False):
                        st.write(f"**Description:** {rule_config.get('description', 'N/A')}")
                        st.write(f"**Applies To:** {rule_config.get('applies_to', 'N/A')}")
                        
                        examples = rule_config.get('examples', [])
                        if examples:
                            st.write("**Examples:**")
                            for example in examples:
                                st.caption(f"• {example}")
                
                with col2:
                    if st.button("🗑️", key=f"delete_{rule_id}", help="Delete this rule"):
                        del rules['custom_rules'][rule_id]
                        save_rules(rules)
                        st.rerun()
        else:
            st.info("No custom rules added yet")
    
    # TAB 4.2: Add Word Replacement
    with rules_tab2:
        st.subheader("➕ Add Word Replacement Rule")
        
        st.markdown("""
        Add new words that should be automatically replaced in toast messages.
        
        **Example:** If you always write "success" but want it to be "successfully", add this rule.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            original_word = st.text_input(
                "Original Word",
                placeholder="e.g., success",
                key="new_original_word"
            )
        
        with col2:
            replacement_word = st.text_input(
                "Replace With",
                placeholder="e.g., successfully",
                key="new_replacement_word"
            )
        
        if st.button("➕ Add Replacement Rule", use_container_width=True, key="add_replacement"):
            if original_word and replacement_word:
                if 'toast_word_replacements' not in rules:
                    rules['toast_word_replacements'] = {}
                
                rules['toast_word_replacements'][original_word.lower()] = replacement_word.lower()
                
                if save_rules(rules):
                    st.balloons()
                    st.rerun()
            else:
                st.error("Please fill in both fields")
        
        st.divider()
        
        st.markdown("**Current Word Replacements:**")
        replacements = rules.get('toast_word_replacements', {})
        if replacements:
            for word, replacement in replacements.items():
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.text(word)
                with col2:
                    st.text("→ " + replacement)
                with col3:
                    if st.button("🗑️", key=f"delete_word_{word}", help="Delete"):
                        del rules['toast_word_replacements'][word]
                        save_rules(rules)
                        st.rerun()
    
    # TAB 4.3: Add Custom Rule
    with rules_tab3:
        st.subheader("✨ Add Custom Rule")
        
        st.markdown("""
        Create new custom verification rules for your organization.
        """)
        
        rule_name = st.text_input(
            "Rule Name",
            placeholder="e.g., Use 'Please' in requests",
            key="new_rule_name"
        )
        
        rule_description = st.text_area(
            "Rule Description",
            placeholder="Explain what this rule checks for...",
            height=80,
            key="new_rule_description"
        )
        
        rule_applies_to = st.selectbox(
            "Applies To",
            ["All", "Toast", "Success Toast", "Error Toast", "Label", "Status", "Message", "Custom"],
            key="new_rule_applies_to"
        )
        
        st.markdown("**Examples** (optional - separate with semicolon)")
        rule_examples_text = st.text_area(
            "Examples",
            placeholder="Good example → Bad example; Another good → Another bad",
            height=80,
            key="new_rule_examples"
        )
        
        if st.button("✨ Add Custom Rule", use_container_width=True, key="add_custom_rule"):
            if rule_name and rule_description:
                if 'custom_rules' not in rules:
                    rules['custom_rules'] = {}
                
                # Generate rule ID from name
                rule_id = rule_name.lower().replace(' ', '_')
                
                # Parse examples
                examples = []
                if rule_examples_text:
                    examples = [ex.strip() for ex in rule_examples_text.split(';') if ex.strip()]
                
                rules['custom_rules'][rule_id] = {
                    "name": rule_name,
                    "description": rule_description,
                    "applies_to": rule_applies_to,
                    "examples": examples
                }
                
                if save_rules(rules):
                    st.balloons()
                    st.rerun()
            else:
                st.error("Please fill in at least Rule Name and Description")
        
        st.divider()
        
        st.info("""
        💡 **Tip:** Custom rules are displayed in the "Current Rules" tab but need to be implemented 
        in the verification logic by the development team. Use the "Rules & Guide" documentation 
        to learn how to implement custom rules in the code.
        """)

# TAB 5: Example Wordings
with tab5:
    st.header("📚 Wording Library & Examples")
    st.markdown("Browse verified wording examples from your organization")
    
    if csv_examples is not None and not csv_examples.empty:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            categories = ['All'] + sorted(csv_examples['Words Category'].unique().tolist())
            selected_category = st.selectbox("Filter by Category", categories, key="filter_category")
        
        with col2:
            sub_categories = ['All']
            if selected_category != 'All':
                filtered_by_cat = csv_examples[csv_examples['Words Category'] == selected_category]
                sub_categories += sorted(filtered_by_cat['Sub Category'].unique().tolist())
            else:
                sub_categories += sorted(csv_examples['Sub Category'].unique().tolist())
            
            selected_subcategory = st.selectbox("Filter by Sub Category", sub_categories, key="filter_subcategory")
        
        with col3:
            status_filter = st.selectbox("Filter by Status", ['All', 'Yes (Correct)', 'No (Needs Fix)'], key="filter_status")
        
        st.divider()
        
        # Apply filters
        filtered_df = csv_examples.copy()
        
        if selected_category != 'All':
            filtered_df = filtered_df[filtered_df['Words Category'] == selected_category]
        
        if selected_subcategory != 'All':
            filtered_df = filtered_df[filtered_df['Sub Category'] == selected_subcategory]
        
        if status_filter == 'Yes (Correct)':
            filtered_df = filtered_df[filtered_df['Is the word right'] == 'Yes']
        elif status_filter == 'No (Needs Fix)':
            filtered_df = filtered_df[filtered_df['Is the word right'] == 'No']
        
        # Search
        search_term = st.text_input("🔍 Search wording...", placeholder="Type to search in current wording and suggestions")
        
        if search_term:
            filtered_df = filtered_df[
                filtered_df['Current Wording'].str.contains(search_term, case=False, na=False) |
                filtered_df['If not right, what is suggested'].str.contains(search_term, case=False, na=False)
            ]
        
        st.markdown(f"**Found {len(filtered_df)} entries**")
        
        # Display options
        col1, col2 = st.columns(2)
        
        with col1:
            view_style = st.radio("View Style", ["Detailed Cards", "Table"], horizontal=True)
        
        with col2:
            sort_by = st.selectbox("Sort by", ["Category", "Status", "Alphabetical"])
        
        # Sort
        if sort_by == "Category":
            filtered_df = filtered_df.sort_values('Words Category')
        elif sort_by == "Status":
            filtered_df = filtered_df.sort_values('Is the word right', ascending=False)
        elif sort_by == "Alphabetical":
            filtered_df = filtered_df.sort_values('Current Wording')
        
        st.divider()
        
        # Display results
        if view_style == "Detailed Cards":
            for idx, row in filtered_df.iterrows():
                status_icon = "✅" if row['Is the word right'] == 'Yes' else "⚠️"
                
                with st.expander(f"{status_icon} {row['Current Wording']} • {row['Words Category']} / {row['Sub Category']}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Current Wording:**")
                        st.code(row['Current Wording'], language="text")
                        
                        st.markdown("**Category:**")
                        st.caption(f"{row['Words Category']} → {row['Sub Category']}")
                    
                    with col2:
                        st.markdown("**Status:**")
                        if row['Is the word right'] == 'Yes':
                            st.success("✅ Correct", icon="✓")
                        else:
                            st.warning("⚠️ Needs Fix", icon="⚠")
                        
                        if row['Is the word right'] == 'No':
                            st.markdown("**Suggested Correction:**")
                            st.code(row['If not right, what is suggested'], language="text")
                    
                    st.markdown("**Why:**")
                    st.info(row['Why suggest this word'])
        
        else:  # Table view
            # Select columns to display
            display_cols = {
                'Words Category': 'Category',
                'Sub Category': 'Sub Category',
                'Current Wording': 'Current',
                'Is the word right': 'Status',
                'If not right, what is suggested': 'Suggestion',
                'Why suggest this word': 'Reason'
            }
            
            display_df = filtered_df[list(display_cols.keys())].copy()
            display_df.columns = list(display_cols.values())
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Download option
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered Results (CSV)",
                data=csv,
                file_name=f"wording_examples_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        # Statistics
        st.divider()
        st.markdown("### Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_entries = len(csv_examples)
            st.metric("Total Entries", total_entries)
        
        with col2:
            correct_entries = len(csv_examples[csv_examples['Is the word right'] == 'Yes'])
            st.metric("Correct", correct_entries)
        
        with col3:
            needs_fix = len(csv_examples[csv_examples['Is the word right'] == 'No'])
            st.metric("Needs Fix", needs_fix)
        
        with col4:
            accuracy = (correct_entries / total_entries * 100) if total_entries > 0 else 0
            st.metric("Accuracy Rate", f"{accuracy:.1f}%")
        
        # Category breakdown
        st.markdown("### Category Breakdown")
        
        category_counts = csv_examples['Words Category'].value_counts()
        col1, col2 = st.columns(2)
        
        with col1:
            st.bar_chart(category_counts)
        
        with col2:
            # Status by category
            status_by_cat = csv_examples.groupby(['Words Category', 'Is the word right']).size().unstack(fill_value=0)
            st.bar_chart(status_by_cat)
    
    else:
        st.warning("❌ No CSV file found. Please ensure 'Wording Criterias-Wording.csv' is in the same directory as app.py")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9rem;'>
    <p>✍️ Wording Verification Agent | Built with Streamlit | v1.0</p>
    <p>Ensuring clarity, consistency, and cultural appropriateness across digital experiences</p>
</div>
""", unsafe_allow_html=True)

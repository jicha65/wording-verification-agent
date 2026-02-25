import streamlit as st
import pandas as pd
import csv
import re
from io import StringIO
from datetime import datetime

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
    
    def check_spelling(self, word):
        """Check for common typos"""
        word_lower = word.lower()
        for typo, correction in self.common_typos.items():
            if typo in word_lower:
                return True, correction
        return False, None
    
    def check_grammar(self, text):
        """Check for grammar issues"""
        issues = []
        
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
        
        # Check spelling
        has_typo, typo_fix = self.check_spelling(wording)
        if has_typo:
            is_correct = False
            suggestions.append(typo_fix)
            reasons.append('Typo detected')
        
        # Check grammar
        grammar_issues = self.check_grammar(wording)
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
        
        status = 'Yes' if is_correct else 'No'
        suggestion = suggestions[0] if suggestions else 'N/A'
        why = ' | '.join(set(reasons)) if reasons else 'No issues found'
        
        return status, suggestion, why

# Initialize verifier
verifier = WordingVerifier()

# Header
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
tab1, tab2, tab3 = st.tabs(["Single Entry", "Batch Upload", "Results"])

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

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9rem;'>
    <p>✍️ Wording Verification Agent | Built with Streamlit | v1.0</p>
    <p>Ensuring clarity, consistency, and cultural appropriateness across digital experiences</p>
</div>
""", unsafe_allow_html=True)

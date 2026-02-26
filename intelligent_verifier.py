#!/usr/bin/env python3
"""
Intelligent Wording Verifier - Hybrid AI + Rules Engine
Combines rule-based verification with Claude AI for semantic understanding
"""

import json
from pathlib import Path
from anthropic import Anthropic

class IntelligentWordingVerifier:
    """Hybrid verifier combining rules + Claude AI"""
    
    def __init__(self, rules_verifier=None, api_key=None):
        """
        Initialize intelligent verifier
        
        Args:
            rules_verifier: WordingVerifier instance for rule-based checks
            api_key: Anthropic API key (can be None for rules-only mode)
        """
        self.rules_verifier = rules_verifier
        self.api_key = api_key
        self.client = None
        self.use_ai = False
        
        if api_key:
            try:
                self.client = Anthropic(api_key=api_key)
                self.use_ai = True
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize Claude API: {e}")
                self.use_ai = False
    
    def load_csv_examples(self, csv_path='Wording Criterias-Wording.csv'):
        """Load verified examples for context"""
        try:
            import pandas as pd
            if Path(csv_path).exists():
                return pd.read_csv(csv_path)
        except:
            pass
        return None
    
    def _get_similar_examples(self, wording, category, csv_df=None, limit=3):
        """Find similar verified examples"""
        if csv_df is None or csv_df.empty:
            return ""
        
        # Filter by category
        filtered = csv_df[csv_df['Words Category'] == category]
        
        if filtered.empty:
            return ""
        
        # Get examples with good suggestions
        good_examples = filtered[filtered['Is the word right'] == 'No'].head(limit)
        
        if good_examples.empty:
            return ""
        
        examples_text = "📚 Similar verified examples:\n"
        for idx, row in good_examples.iterrows():
            examples_text += f"  • '{row['Current Wording']}' → '{row['If not right, what is suggested']}'\n"
            examples_text += f"    Reason: {row['Why suggest this word']}\n"
        
        return examples_text
    
    def verify_intelligent(self, category, subcategory, wording, use_ai=True):
        """
        Intelligent verification combining rules and AI
        
        Returns:
            {
                'rule_status': 'Yes'/'No',
                'rule_suggestion': 'suggestion',
                'rule_reason': 'reason',
                'ai_suggestion': 'AI suggestion or None',
                'ai_reason': 'Why AI suggests this',
                'semantic_issues': ['issue1', 'issue2'],
                'final_suggestion': 'Best suggestion',
                'final_reason': 'Combined reasoning',
                'confidence': 'High/Medium/Low',
                'ai_used': True/False
            }
        """
        
        result = {
            'rule_status': 'Unknown',
            'rule_suggestion': 'N/A',
            'rule_reason': 'N/A',
            'ai_suggestion': None,
            'ai_reason': None,
            'semantic_issues': [],
            'final_suggestion': 'N/A',
            'final_reason': 'N/A',
            'confidence': 'Unknown',
            'ai_used': False
        }
        
        # Step 1: Get rules-based verification
        if self.rules_verifier:
            rule_status, rule_suggestion, rule_reason = self.rules_verifier.verify(
                category, subcategory, wording
            )
            result['rule_status'] = rule_status
            result['rule_suggestion'] = rule_suggestion
            result['rule_reason'] = rule_reason
        
        # Step 2: Get AI verification if enabled
        if use_ai and self.use_ai and self.client:
            ai_result = self._get_ai_verification(
                category, subcategory, wording,
                result['rule_status'], result['rule_suggestion'], result['rule_reason']
            )
            
            result['ai_suggestion'] = ai_result.get('suggestion')
            result['ai_reason'] = ai_result.get('reason')
            result['semantic_issues'] = ai_result.get('issues', [])
            result['ai_used'] = True
        
        # Step 3: Combine suggestions
        result['final_suggestion'] = result['ai_suggestion'] or result['rule_suggestion']
        
        # Build final reason
        reasons = []
        if result['rule_reason'] and result['rule_reason'] != 'No issues found':
            reasons.append(f"Rules: {result['rule_reason']}")
        if result['ai_reason']:
            reasons.append(f"AI Analysis: {result['ai_reason']}")
        
        result['final_reason'] = ' | '.join(reasons) if reasons else 'No issues found'
        
        # Determine confidence
        if result['ai_used'] and result['ai_suggestion']:
            result['confidence'] = 'High' if result['ai_suggestion'] == result['rule_suggestion'] else 'Medium'
        elif result['rule_status'] == 'Yes':
            result['confidence'] = 'High'
        else:
            result['confidence'] = 'Medium'
        
        return result
    
    def _get_ai_verification(self, category, subcategory, wording, 
                            rule_status, rule_suggestion, rule_reason):
        """Get Claude AI verification"""
        
        try:
            # Load examples for context
            csv_df = self.load_csv_examples()
            examples_context = self._get_similar_examples(wording, category, csv_df)
            
            # Build context
            context = f"""You are an expert wording verification specialist. Your role is to verify and improve wording for:
- Clarity and conciseness
- Consistency with organizational standards
- Cultural appropriateness
- Professional tone
- User experience

Current organizational rules:
1. Use "successfully" (adverb) not "successful" (adjective)
2. Use "Not" prefix instead of "Un" prefix
3. Action verbs before "successfully" should be in past participle form (e.g., "Saved Successfully")
4. Toast messages should end with period (.) not exclamation (!)

{examples_context}"""
            
            # Create prompt
            prompt = f"""Verify this wording for the {category} / {subcategory} category:

Current wording: "{wording}"

Existing verification:
- Rule engine status: {rule_status}
- Rule suggestion: {rule_suggestion}
- Rule reason: {rule_reason}

Please analyze this wording and provide:
1. Your assessment (Correct/Needs improvement)
2. Semantic analysis (clarity, tone, professionalism)
3. Cultural/audience considerations
4. Better suggestion if needed
5. Why your suggestion is better

Respond ONLY as valid JSON in this format, no markdown:
{{
    "assessment": "Correct" or "Needs improvement",
    "suggestion": "Better wording or null",
    "reason": "Why this suggestion is better",
    "issues": ["clarity issue", "tone issue"],
    "tone": "professional/friendly/formal",
    "audience_fit": "appropriate/needs adjustment"
}}"""
            
            # Call Claude
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                system=context
            )
            
            # Parse response
            response_text = message.content[0].text
            
            # Try to extract JSON
            try:
                # Handle markdown code blocks
                if '```json' in response_text:
                    response_text = response_text.split('```json')[1].split('```')[0]
                elif '```' in response_text:
                    response_text = response_text.split('```')[1].split('```')[0]
                
                ai_result = json.loads(response_text.strip())
                return {
                    'suggestion': ai_result.get('suggestion'),
                    'reason': ai_result.get('reason'),
                    'issues': ai_result.get('issues', []),
                    'tone': ai_result.get('tone'),
                    'audience_fit': ai_result.get('audience_fit')
                }
            except json.JSONDecodeError:
                # Fallback: return raw response
                return {
                    'suggestion': None,
                    'reason': response_text[:200],
                    'issues': [],
                    'tone': None,
                    'audience_fit': None
                }
        
        except Exception as e:
            print(f"⚠️ AI verification error: {e}")
            return {
                'suggestion': None,
                'reason': f'AI unavailable: {str(e)[:50]}',
                'issues': [],
                'tone': None,
                'audience_fit': None
            }


def create_intelligent_verifier(rules_verifier, api_key=None):
    """Factory function to create intelligent verifier"""
    return IntelligentWordingVerifier(rules_verifier, api_key)

#!/usr/bin/env python3
"""
Intelligent Wording Verifier - Hybrid AI + Rules Engine
Supports: Claude API (global), Google Gemini (global), Local Models (Ollama, China-friendly)
"""

import json
from pathlib import Path

class IntelligentWordingVerifier:
    """Hybrid verifier combining rules + AI"""
    
    def __init__(self, rules_verifier=None, ai_provider=None, api_key=None, model_name=None):
        """
        Initialize intelligent verifier
        
        Args:
            rules_verifier: WordingVerifier instance for rule-based checks
            ai_provider: 'claude', 'gemini', 'ollama', or None
            api_key: API key (for Claude/Gemini)
            model_name: Model name for Ollama (default: 'mistral')
        """
        self.rules_verifier = rules_verifier
        self.ai_provider = ai_provider
        self.api_key = api_key
        self.model_name = model_name or 'mistral'
        self.client = None
        self.use_ai = False
        
        self._initialize_ai()
    
    def _initialize_ai(self):
        """Initialize AI client based on provider"""
        if not self.ai_provider:
            return
        
        try:
            if self.ai_provider == 'claude':
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
                self.use_ai = True
            
            elif self.ai_provider == 'gemini':
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel('gemini-1.5-flash')
                self.use_ai = True
            
            elif self.ai_provider == 'ollama':
                # Don't initialize here - import fresh in verify method
                # Just mark as available
                self.use_ai = True
                print(f"✅ Ollama mode enabled (model: {self.model_name})")
        
        except ImportError as e:
            print(f"⚠️ Library not installed: {e}")
            self.use_ai = False
        except Exception as e:
            print(f"⚠️ AI initialization error: {e}")
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
        """Get AI verification from configured provider"""
        
        try:
            if self.ai_provider == 'claude':
                return self._get_claude_verification(category, subcategory, wording, 
                                                     rule_status, rule_suggestion, rule_reason)
            elif self.ai_provider == 'gemini':
                return self._get_gemini_verification(category, subcategory, wording,
                                                     rule_status, rule_suggestion, rule_reason)
            elif self.ai_provider == 'ollama':
                return self._get_ollama_verification(category, subcategory, wording,
                                                     rule_status, rule_suggestion, rule_reason)
            else:
                return {'suggestion': None, 'reason': 'No AI provider configured', 'issues': []}
        
        except Exception as e:
            print(f"⚠️ AI verification error: {e}")
            return {'suggestion': None, 'reason': f'AI error: {str(e)[:50]}', 'issues': []}
    
    def _get_claude_verification(self, category, subcategory, wording, 
                                 rule_status, rule_suggestion, rule_reason):
        """Get verification from Claude API"""
        try:
            csv_df = self.load_csv_examples()
            examples_context = self._get_similar_examples(wording, category, csv_df)
            
            context = f"""You are an expert wording verification specialist. Your role is to verify and improve wording for:
- Clarity and conciseness
- Consistency with organizational standards
- Cultural appropriateness
- Professional tone
- User experience

Current organizational rules:
1. Use "successfully" (adverb) not "successful" (adjective)
2. Use "Not" prefix instead of "Un" prefix
3. Action verbs before "successfully" should be in past participle form
4. Toast messages should end with period (.) not exclamation (!)

{examples_context}"""
            
            prompt = f"""Verify this wording for {category} / {subcategory}:
Current: "{wording}"
Rule status: {rule_status}
Rule suggestion: {rule_suggestion}

Provide as JSON:
{{
    "assessment": "Correct/Needs improvement",
    "suggestion": "Better wording or null",
    "reason": "Why",
    "issues": ["issue1"],
    "tone": "professional/friendly",
    "audience_fit": "appropriate/needs adjustment"
}}"""
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
                system=context
            )
            
            response_text = message.content[0].text
            return self._parse_json_response(response_text)
        
        except Exception as e:
            return {'suggestion': None, 'reason': f'Claude error: {str(e)[:50]}', 'issues': []}
    
    def _get_gemini_verification(self, category, subcategory, wording,
                                rule_status, rule_suggestion, rule_reason):
        """Get verification from Google Gemini API"""
        try:
            csv_df = self.load_csv_examples()
            examples_context = self._get_similar_examples(wording, category, csv_df)
            
            system_prompt = f"""Expert wording verification specialist.
Rules: Use "successfully", "Not" not "Un", past participles, periods in toasts.
{examples_context}"""
            
            prompt = f"""Verify: "{wording}" (Category: {category})
Current status: {rule_status}
Current suggestion: {rule_suggestion}

Provide JSON: {{"assessment": "...", "suggestion": "...", "reason": "...", "issues": [...], "tone": "...", "audience_fit": "..."}}"""
            
            response = self.client.generate_content(
                f"{system_prompt}\n\n{prompt}",
                generation_config={'temperature': 0.3, 'max_output_tokens': 500}
            )
            
            return self._parse_json_response(response.text)
        
        except Exception as e:
            return {'suggestion': None, 'reason': f'Gemini error: {str(e)[:50]}', 'issues': []}
    
    def _get_ollama_verification(self, category, subcategory, wording,
                                rule_status, rule_suggestion, rule_reason):
        """Get verification from local Ollama model"""
        try:
            import ollama
            
            # Create simple prompt
            prompt = f"""You are a wording expert. Verify this text for a {category} message:

Text: "{wording}"
Current rule status: {rule_status}
Current suggestion: {rule_suggestion}

RESPOND ONLY with valid JSON (no markdown, no explanation):
{{"assessment": "Correct or Needs improvement", "suggestion": "better wording or null", "reason": "why", "issues": [], "tone": "professional", "audience_fit": "appropriate"}}"""
            
            # Call Ollama - response is a dict-like object
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt
            )
            
            # Extract text from response
            if isinstance(response, dict) and 'response' in response:
                response_text = response['response']
            else:
                # Handle Pydantic model response
                response_text = str(getattr(response, 'response', str(response)))
            
            return self._parse_json_response(response_text)
        
        except ImportError:
            return {
                'suggestion': None, 
                'reason': 'ollama library not installed', 
                'issues': []
            }
        except ConnectionError:
            return {
                'suggestion': None, 
                'reason': 'Cannot connect to Ollama. Run: ollama serve', 
                'issues': []
            }
        except KeyError as e:
            # Handle NameError/'name' errors from response parsing
            return {
                'suggestion': None, 
                'reason': f'Error parsing Ollama response: {str(e)}', 
                'issues': []
            }
        except Exception as e:
            return {
                'suggestion': None, 
                'reason': f'Ollama error: {str(e)[:80]}', 
                'issues': []
            }
    
    def _parse_json_response(self, response_text):
        """Parse JSON response from AI"""
        try:
            # Remove markdown code blocks if present
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            # Clean up the text
            response_text = response_text.strip()
            
            ai_result = json.loads(response_text)
            
            # Safely extract fields
            return {
                'suggestion': ai_result.get('suggestion'),
                'reason': ai_result.get('reason', 'No additional feedback'),
                'issues': ai_result.get('issues', []),
                'tone': ai_result.get('tone'),
                'audience_fit': ai_result.get('audience_fit')
            }
        except json.JSONDecodeError as e:
            # If JSON fails, just return the text as reason
            return {
                'suggestion': None,
                'reason': response_text[:200] if response_text else 'No response',
                'issues': []
            }
        except (KeyError, TypeError) as e:
            return {
                'suggestion': None,
                'reason': f'Parse error: {str(e)}',
                'issues': []
            }
        except Exception as e:
            return {
                'suggestion': None,
                'reason': f'Unexpected error: {str(e)[:100]}',
                'issues': []
            }
    


def create_intelligent_verifier(rules_verifier, api_key=None):
    """Factory function to create intelligent verifier"""
    return IntelligentWordingVerifier(rules_verifier, api_key)

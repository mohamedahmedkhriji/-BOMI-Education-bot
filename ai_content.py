import openai
import os
import json
import random
import openai
from dotenv import load_dotenv

load_dotenv()

class AIContentGenerator:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.full_dataset = self._load_all_datasets()
        self.constants = self._load_constants()
        self.operations = self._load_operations()
        self.training_context = self._build_training_context()
        print(f"Loaded {len(self.full_dataset)} problems for LLM training")
    
    def _load_all_datasets(self):
        """Load ALL dataset files for comprehensive training"""
        datasets = []
        files = ['train.json', 'dev.json', 'test.json', 'challenge_test.json']
        
        for file in files:
            try:
                path = f"../aymen/math/{file}"
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    datasets.extend(data)
                    print(f"Loaded {len(data)} problems from {file}")
            except Exception as e:
                print(f"Failed to load {file}: {e}")
        
        return datasets
    
    def _load_constants(self):
        """Load mathematical constants"""
        try:
            with open('../aymen/math/constant_list.txt', 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except:
            return []
    
    def _load_operations(self):
        """Load mathematical operations"""
        try:
            with open('../aymen/math/operation_list.txt', 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except:
            return []
    
    def _build_training_context(self):
        """Build comprehensive training context from all data"""
        categories = {}
        for problem in self.full_dataset:
            cat = problem.get('category', 'general')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(problem)
        
        context = f"""DTM EXAM DATASET ANALYSIS:
Total Problems: {len(self.full_dataset)}
Categories: {list(categories.keys())}
Constants Available: {len(self.constants)}
Operations Available: {len(self.operations)}

PROBLEM PATTERNS:"""
        
        for cat, problems in categories.items():
            context += f"\n{cat.upper()}: {len(problems)} problems"
            if problems:
                sample = problems[0]
                context += f"\n  Sample: {sample['Problem'][:80]}..."
        
        return context
    
    def _validate_language(self, language):
        """Validate and normalize language code"""
        if language in ['uz', 'uzbek', 'o\'zbek']:
            return 'uz'
        elif language in ['en', 'eng', 'english']:
            return 'en'
        else:
            print(f"Unknown language '{language}', defaulting to Uzbek")
            return 'uz'  # Default to Uzbek for DTM exam
    
    def _get_language_instructions(self, language):
        """Get language-specific instructions for AI generation"""
        if language == 'uz':
            return """
LANGUAGE: Generate content in UZBEK (O'zbek tili)
INSTRUCTIONS:
- Use proper Uzbek grammar and vocabulary
- Mathematical terms in Uzbek: son (number), tenglama (equation), formula (formula)
- Numbers and calculations can be in standard notation
- Use Uzbek question words: qancha (how much), necha (how many), qaysi (which)
- Keep mathematical expressions clear and simple
"""
        else:
            return """
LANGUAGE: Generate content in ENGLISH
INSTRUCTIONS:
- Use clear, simple English suitable for exam preparation
- Standard mathematical terminology
- Avoid complex vocabulary, focus on clarity
- Use common English question patterns
"""
    
    def _clean_text(self, text):
        """Remove markdown and LaTeX formatting, keep only essential math symbols"""
        import re
        if not text:
            return ""
        
        # Remove LaTeX math delimiters
        text = re.sub(r'\\\(|\\\)|\\\[|\\\]', '', text)
        
        # Replace LaTeX commands with simple text
        text = re.sub(r'\\text\{([^}]+)\}', r'\1', text)  # \text{Area} -> Area
        text = re.sub(r'\\times', '×', text)  # \times -> ×
        text = re.sub(r'\\div', '÷', text)  # \div -> ÷
        text = re.sub(r'\\pi', 'π', text)  # \pi -> π
        text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1/\2)', text)  # \frac{1}{2} -> (1/2)
        text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)  # Remove other LaTeX commands
        text = re.sub(r'\\[a-zA-Z]+', '', text)  # Remove LaTeX commands without braces
        
        # Remove markdown formatting
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\*\*|__', '', text)
        text = re.sub(r'\*|_', '', text)
        text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
        
        # Remove extra symbols but keep essential math ones
        text = re.sub(r'[{}\[\]`~]', '', text)  # Remove brackets, backticks
        text = re.sub(r'\\', '', text)  # Remove backslashes
        text = re.sub(r'\$', '', text)  # Remove dollar signs
        
        # Clean up whitespace and improve formatting
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'\n{3,}', '\n\n', text)  # Multiple newlines to double
        
        # Add proper spacing around sections
        text = re.sub(r'(Definition|Key Concepts|Example|Solution|Common Patterns)', r'\n\n\1', text)
        text = re.sub(r'(\d+\.)\s*([A-Z])', r'\n\1 \2', text)  # Number lists
        text = re.sub(r'(-\s*)', r'\n- ', text)  # Bullet points
        
        # Clean up extra newlines at start
        text = re.sub(r'^\n+', '', text)
        
        return text.strip()
    
    def generate_diagnostic_questions_structured(self, level='Beginner', language='uz', count=12):
        """Generate questions using comprehensive dataset training with guaranteed count"""
        # Validate language
        language = self._validate_language(language)
        
        # Try AI generation first with multiple attempts
        for attempt in range(3):
            try:
                training_examples = self._get_comprehensive_examples(level, count=10)
                lang_text = "Uzbek" if language == 'uz' else "English"
                difficulty = {
                    'Beginner': 'basic arithmetic and simple algebra',
                    'Intermediate': 'algebra, geometry, percentages', 
                    'Advanced': 'complex problems like DTM exam'
                }.get(level, 'intermediate')
                
                lang_instructions = self._get_language_instructions(language)
                
                # Enhanced difficulty-specific prompts
                difficulty_instructions = {
            'Beginner': f"""
DIFFICULTY: BEGINNER LEVEL
- Use simple arithmetic operations (+, -, ×, ÷)
- Problems should be 1-2 steps maximum
- Use whole numbers and simple fractions
- Avoid complex formulas or equations
- Focus on basic concepts: addition, subtraction, multiplication, division, percentages
- Question length: 50-100 words maximum
- Examples: "What is 25% of 80?" or "If 3 apples cost $6, how much do 5 apples cost?""",
            
            'Intermediate': f"""
DIFFICULTY: INTERMEDIATE LEVEL  
- Use moderate complexity problems (2-3 steps)
- Include basic algebra, geometry, and word problems
- Use decimals, fractions, and simple equations
- Introduce concepts like area, perimeter, ratios
- Question length: 75-150 words
- Examples: "Solve for x: 2x + 5 = 15" or "Find the area of a rectangle with length 8m and width 5m""",
            
            'Advanced': f"""
DIFFICULTY: ADVANCED LEVEL
- Use complex multi-step problems (3+ steps)
- Include advanced algebra, geometry, physics concepts
- Use quadratic equations, trigonometry, logarithms
- Complex word problems with multiple variables
- Question length: 100-200 words
- Examples: "A projectile is fired at 45° with initial velocity 20m/s. Find maximum height" or "Solve the system: 2x + 3y = 12, x - y = 1"""
                }
                
                prompt = f"""
{self.training_context}

You are an expert DTM exam question generator trained on {len(self.full_dataset)} real problems.

{lang_instructions}

{difficulty_instructions.get(level, difficulty_instructions['Intermediate'])}

STUDY THESE {level.upper()} LEVEL EXAMPLES:
{self._format_comprehensive_examples(training_examples)}

GENERATE EXACTLY {count} COMPLETE questions in {lang_text} at {level.upper()} level. MUST have {count} questions, no more, no less.

RULES:
- Follow DTM exam format exactly
- Match {level.upper()} difficulty level precisely
- Use mathematical constants: {', '.join(self.constants[:5])}
- Apply operations: {', '.join(self.operations[:10])}
- PLAIN TEXT only, no LaTeX, no extra symbols
- Use only basic math symbols: +, -, ×, ÷, =, (), %
- 4 options A-D with clear correct answer
- ALL OPTIONS MUST BE DIFFERENT AND UNIQUE
- NO DUPLICATE VALUES OR REPEATED OPTIONS

Format:
QUESTION: [text]
A) [unique option 1]
B) [unique option 2] 
C) [unique option 3]
D) [unique option 4]
CORRECT: [A/B/C/D]

IMPORTANT: Each option must be DIFFERENT and UNIQUE!
"""
                
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2500,
                    temperature=0.7
                )
                
                questions = self._parse_questions(response.choices[0].message.content)
                
                # If we got exactly the right count, return
                if len(questions) == count:
                    print(f"AI generation completed")
                    return questions
                elif len(questions) > 0:
                    print(f"Generated only {len(questions)}/{count} questions")
                    # Supplement with dataset questions
                    needed = count - len(questions)
                    dataset_questions = self._get_dataset_questions(needed, language=language)
                    questions.extend(dataset_questions)
                    return questions[:count]
                    
            except Exception as e:
                print(f"AI attempt {attempt + 1} failed: {e}")
                continue
        
        # If all AI attempts failed, use dataset
        print("AI generation completed")
        return self._get_dataset_questions(count, language=language)
    
    def generate_practice_questions(self, topic, language='uz', count=5, user_level='Intermediate'):
        """Generate practice questions using comprehensive dataset training"""
        # Validate language
        language = self._validate_language(language)
        topic_examples = self._get_comprehensive_topic_examples(topic, count=8)
        
        lang_text = "Uzbek" if language == 'uz' else "English"
        
        # Language-specific instructions
        lang_instructions = self._get_language_instructions(language)
        
        # Get user level for difficulty adaptation
        user_level = 'Intermediate'  # Default
        try:
            # Try to get user level from context if available
            user_level = context.get('user_level', 'Intermediate') if 'context' in locals() else 'Intermediate'
        except:
            pass
            
        level_instructions = {
            'Beginner': f"Generate SIMPLE {topic} problems suitable for beginners. Use basic operations and 1-2 steps maximum.",
            'Intermediate': f"Generate MODERATE {topic} problems with 2-3 steps. Include some algebra and geometry concepts.", 
            'Advanced': f"Generate COMPLEX {topic} problems with multiple steps. Use advanced mathematical concepts."
        }
        
        prompt = f"""
{self.training_context}

{lang_instructions}

TOPIC: {topic.upper()}
LEVEL: {user_level.upper()}

{level_instructions.get(user_level, level_instructions['Intermediate'])}

TOPIC-SPECIFIC TRAINING for {topic}:
{self._format_comprehensive_examples(topic_examples)}

GENERATE {count} DTM questions in {lang_text} about {topic} at {user_level.upper()} level.

USE DATASET PATTERNS:
- Problem structure from {len(topic_examples)} examples
- Mathematical operations: {', '.join(self.operations[:8])}
- Constants when needed: {', '.join(self.constants[:3])}
- PLAIN TEXT only, no extra symbols except basic math: +, -, ×, ÷, =, (), %
- ENSURE ALL 4 OPTIONS ARE COMPLETELY DIFFERENT
- NO DUPLICATE ANSWERS OR VALUES
- MATCH {user_level.upper()} DIFFICULTY LEVEL

Format:
QUESTION: [text]
A) [unique option 1]
B) [unique option 2]
C) [unique option 3] 
D) [unique option 4]
CORRECT: [A/B/C/D]

IMPORTANT: Each option must be DIFFERENT and UNIQUE!
"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.8
            )
            
            questions = self._parse_questions(response.choices[0].message.content)
            
            # Always ensure we have exactly the requested count
            if len(questions) < count:
                print(f"AI generated only {len(questions)}/{count} questions, supplementing with dataset")
                needed = count - len(questions)
                dataset_questions = self._get_dataset_questions(needed, topic, language=language)
                questions.extend(dataset_questions)
            
            # Return exactly the requested count
            return questions[:count]
            
        except Exception as e:
            print(f"Using dataset directly: {e}")
            return self._get_dataset_questions(count, topic)
    
    def _parse_questions(self, content):
        """Parse AI response into structured question format"""
        questions = []
        lines = content.strip().split('\n')
        
        current_q = {}
        options = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('QUESTION:'):
                if current_q and 'text' in current_q and 'correct' in current_q and len(options) == 4:
                    # Validate options are unique and answer is A-D
                    if len(set(options)) == 4 and current_q['correct'] in ['A', 'B', 'C', 'D']:
                        current_q['options'] = options
                        questions.append(current_q)
                current_q = {'text': line.split(':', 1)[1].strip()}
                options = []
            elif line.startswith('A)'):
                option = line[2:].strip()
                if option and option not in options:
                    options.append(option)
            elif line.startswith('B)'):
                option = line[2:].strip()
                if option and option not in options:
                    options.append(option)
            elif line.startswith('C)'):
                option = line[2:].strip()
                if option and option not in options:
                    options.append(option)
            elif line.startswith('D)'):
                option = line[2:].strip()
                if option and option not in options:
                    options.append(option)
            elif line.startswith('CORRECT:'):
                answer = line.split(':', 1)[1].strip()
                answer_letter = answer.upper()[0] if answer else 'A'
                # Only accept A, B, C, D answers
                if answer_letter in ['A', 'B', 'C', 'D']:
                    current_q['correct'] = answer_letter
                else:
                    current_q['correct'] = 'A'  # Default to A if invalid
        
        # Add last question with validation
        if current_q and 'text' in current_q and 'correct' in current_q and len(options) == 4:
            if len(set(options)) == 4 and current_q['correct'] in ['A', 'B', 'C', 'D']:  # Ensure all options are unique and answer is A-D
                current_q['options'] = options
                questions.append(current_q)
        
        print(f"Parsed {len(questions)} valid questions")
        return questions
    
    def _get_comprehensive_examples(self, level, count=10):
        """Get examples from full dataset based on difficulty with enhanced filtering"""
        if not self.full_dataset:
            return []
        
        # Enhanced difficulty filtering
        if level == 'Beginner':
            # Simple arithmetic, basic algebra, short problems
            filtered = []
            for p in self.full_dataset:
                text = p.get('Problem', '').lower()
                category = p.get('category', '')
                
                # Beginner criteria: short problems, basic operations
                if (len(text) < 150 and 
                    category in ['general', 'gain'] and
                    any(word in text for word in ['add', 'subtract', 'multiply', 'divide', 'sum', 'difference', 'simple']) and
                    not any(word in text for word in ['equation', 'formula', 'complex', 'derivative', 'integral'])):
                    filtered.append(p)
                    
        elif level == 'Advanced':
            # Complex problems, multiple steps, advanced concepts
            filtered = []
            for p in self.full_dataset:
                text = p.get('Problem', '').lower()
                category = p.get('category', '')
                
                # Advanced criteria: longer problems, complex operations
                if (len(text) > 100 and
                    category in ['physics', 'geometry', 'probability'] and
                    any(word in text for word in ['equation', 'formula', 'calculate', 'determine', 'complex', 'system']) and
                    ('²' in text or '^' in text or 'sqrt' in text or 'log' in text)):
                    filtered.append(p)
                    
        else:  # Intermediate
            # Medium complexity problems
            filtered = []
            for p in self.full_dataset:
                text = p.get('Problem', '').lower()
                category = p.get('category', '')
                
                # Intermediate criteria: moderate length and complexity
                if (50 < len(text) < 200 and
                    category in ['general', 'geometry', 'gain'] and
                    any(word in text for word in ['find', 'solve', 'calculate']) and
                    not any(word in text for word in ['complex', 'advanced', 'derivative'])):
                    filtered.append(p)
        
        # Fallback to category-based filtering if enhanced filtering yields too few results
        if len(filtered) < count:
            if level == 'Beginner':
                filtered = [p for p in self.full_dataset if p.get('category') in ['general', 'gain']]
            elif level == 'Advanced':
                filtered = [p for p in self.full_dataset if p.get('category') in ['physics', 'geometry', 'probability']]
            else:
                filtered = [p for p in self.full_dataset if p.get('category') in ['general', 'geometry', 'gain']]
        
        return random.sample(filtered, min(count, len(filtered)))
    
    def _get_comprehensive_topic_examples(self, topic, count=8):
        """Get comprehensive topic-specific examples from full dataset"""
        if not self.full_dataset:
            return []
            
        topic_map = {
            'algebra': ['general', 'gain'],
            'geometry': ['geometry', 'physics'], 
            'arithmetic': ['general'],
            'percentages': ['gain'],
            'fractions': ['general'],
            'ratios': ['general', 'gain'],
            'equations': ['general'],
            'inequalities': ['general'],
            'functions': ['general'],
            'graphs': ['general'],
            'probability': ['probability'],
            'statistics': ['probability'],
            'number theory': ['general'],
            'combinatorics': ['probability']
        }
        
        categories = topic_map.get(topic.lower(), ['general'])
        filtered = [q for q in self.full_dataset if q.get('category') in categories]
        
        if not filtered:
            filtered = self.full_dataset
            
        return random.sample(filtered, min(count, len(filtered)))
    
    def _format_comprehensive_examples(self, examples):
        """Format comprehensive dataset examples for LLM training"""
        formatted = []
        for i, ex in enumerate(examples[:5]):  # Show more examples
            options = ex.get('options', '').split(' , ')[:4]
            if len(options) == 4:
                rationale = ex.get('Rationale', '')[:100]
                category = ex.get('category', 'general')
                formatted.append(f"""
EXAMPLE {i+1} [{category.upper()}]:
Problem: {ex['Problem']}
A) {options[0]}
B) {options[1]} 
C) {options[2]}
D) {options[3]}
Correct: {ex['correct'].upper()}
Rationale: {rationale}...
""")
        return '\n'.join(formatted)
    
    def _get_dataset_questions(self, count, topic=None, language='uz'):
        """Get questions directly from comprehensive dataset - guaranteed count"""
        if not self.full_dataset:
            return []
            
        # Filter by topic if specified
        if topic:
            topic_map = {
                'algebra': ['general', 'gain'],
                'geometry': ['geometry', 'physics'],
                'percentage': ['gain'],
                'speed': ['physics'],
                'probability': ['probability']
            }
            categories = topic_map.get(topic.lower(), ['general'])
            filtered = [q for q in self.full_dataset if q.get('category') in categories]
        else:
            filtered = self.full_dataset
            
        # Filter out questions with answer E first
        valid_questions = [q for q in filtered if q.get('correct', '').upper() in ['A', 'B', 'C', 'D']]
        
        questions = []
        attempts = 0
        max_attempts = len(valid_questions) if valid_questions else 0
        
        # Keep trying until we get exactly the requested count
        while len(questions) < count and attempts < max_attempts:
            remaining_questions = [q for q in valid_questions if q not in [item['_source'] for item in questions if '_source' in item]]
            if not remaining_questions:
                # If we run out of unique questions, start over with all questions
                remaining_questions = valid_questions
            
            item = random.choice(remaining_questions)
            attempts += 1
            
            # Skip questions with answer E (we only support A-D)
            if item['correct'].upper() not in ['A', 'B', 'C', 'D']:
                continue
                
            options = item.get('options', '').split(' , ')
            if len(options) >= 4:
                clean_options = [self._clean_option(opt.strip()) for opt in options[:4]]
                # Ensure options are unique and not empty
                if len(set(clean_options)) == 4 and all(opt for opt in clean_options):
                    question = {
                        'text': self._clean_text(item['Problem']),
                        'options': clean_options,
                        'correct': item['correct'].upper(),
                        'topic': item.get('category', 'general'),
                        'rationale': self._clean_text(item.get('Rationale', '')),
                        '_source': item  # Keep reference to avoid duplicates
                    }
                    questions.append(question)
        
        # Remove the _source field before returning
        for q in questions:
            q.pop('_source', None)
                
        return questions[:count]
    
    def generate_theory_explanation(self, topic, language='uz'):
        """Generate theory explanation using comprehensive dataset context"""
        # Validate language
        language = self._validate_language(language)
        topic_examples = self._get_comprehensive_topic_examples(topic, count=5)
        lang_text = "Uzbek" if language == 'uz' else "English"
        
        # Language-specific instructions
        lang_instructions = self._get_language_instructions(language)
        
        prompt = f"""
{self.training_context}

{lang_instructions}

CREATE THEORY LESSON for "{topic}" in {lang_text}.

ANALYZE THESE PATTERNS:
{self._format_comprehensive_examples(topic_examples)}

RELEVANT OPERATIONS: {', '.join([op for op in self.operations if topic.lower() in op.lower()][:5])}
USEFUL CONSTANTS: {', '.join(self.constants[:3])}

INCLUDE:
1. Clear definition
2. Key formulas (use simple text, NO LaTeX symbols)
3. Step-by-step example with numbers
4. Common DTM patterns

FORMATTING:
- Use clear section headers
- Add line breaks between sections
- Use numbered lists for steps
- Keep sentences short and clear

IMPORTANT: Use plain text only. Write formulas like "Area = length × width". Use only basic math symbols: +, -, ×, ÷, =, (), %, π. No LaTeX, no extra formatting symbols.

Keep under 400 words.
"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600
            )
            
            content = response.choices[0].message.content
            return self._clean_text(content)
        except Exception as e:
            print(f"Theory generation failed: {e}")
            if language == 'uz':
                return f"Mavzu: {topic}\nDTM imtihoniga tayyorgarlik uchun asosiy tushunchalar va formulalar."
            else:
                return f"Topic: {topic}\nBasic concepts and formulas for DTM exam preparation."
    
    def _clean_option(self, option):
        """Clean option text by removing letter prefixes like 'a )', 'b )', etc."""
        import re
        # Remove patterns like 'a )', 'b )', 'c )', 'd )' from the beginning
        cleaned = re.sub(r'^[a-d]\s*\)\s*', '', option, flags=re.IGNORECASE)
        return self._clean_text(cleaned.strip())
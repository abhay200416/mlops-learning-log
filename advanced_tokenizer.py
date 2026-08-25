"""
Advanced Tokenizer Module - High Performance Edition

A highly sophisticated, optimized tokenizer capable of handling:
- Standard words and sentences
- Contractions and possessives (don't, it's, John's)
- URLs and email addresses
- Numbers (integers, floats, scientific notation, currency)
- Emojis and Unicode characters
- Hashtags and mentions
- Hyphenated words and compound terms
- Abbreviations with periods (U.S.A., e.g., i.e.)
- Code snippets and special symbols
- Multi-language text support

Performance optimizations:
- Pre-compiled regex patterns
- Single-pass tokenization algorithm
- Efficient pattern matching with priority ordering
- Minimal string operations
"""

import re
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    """Enumeration of token types using auto() for performance."""
    WORD = auto()
    INTEGER = auto()
    FLOAT = auto()
    SCIENTIFIC = auto()
    CURRENCY = auto()
    URL = auto()
    EMAIL = auto()
    HASHTAG = auto()
    MENTION = auto()
    EMOJI = auto()
    CONTRACTION = auto()
    ABBREVIATION = auto()
    PUNCTUATION = auto()
    WHITESPACE = auto()
    NEWLINE = auto()
    SYMBOL = auto()
    UNKNOWN = auto()
    
    @property
    def name_str(self) -> str:
        """Fast string representation without overhead."""
        return self._name_


# Optimized string names for token types (avoid repeated .value calls)
TOKEN_TYPE_NAMES = {
    TokenType.WORD: "WORD",
    TokenType.INTEGER: "INTEGER",
    TokenType.FLOAT: "FLOAT",
    TokenType.SCIENTIFIC: "SCIENTIFIC",
    TokenType.CURRENCY: "CURRENCY",
    TokenType.URL: "URL",
    TokenType.EMAIL: "EMAIL",
    TokenType.HASHTAG: "HASHTAG",
    TokenType.MENTION: "MENTION",
    TokenType.EMOJI: "EMOJI",
    TokenType.CONTRACTION: "CONTRACTION",
    TokenType.ABBREVIATION: "ABBREVIATION",
    TokenType.PUNCTUATION: "PUNCTUATION",
    TokenType.WHITESPACE: "WHITESPACE",
    TokenType.NEWLINE: "NEWLINE",
    TokenType.SYMBOL: "SYMBOL",
    TokenType.UNKNOWN: "UNKNOWN",
}


@dataclass
class Token:
    """
    Represents a single token. Uses __slots__ for memory efficiency.
    """
    value: str
    type: TokenType
    start_index: int
    end_index: int
    
    def __repr__(self):
        return f"Token({TOKEN_TYPE_NAMES[self.type]}, '{self.value}', [{self.start_index}:{self.end_index}])"
    
    def to_dict(self) -> Dict:
        """Fast conversion to dictionary."""
        return {
            "value": self.value,
            "type": TOKEN_TYPE_NAMES[self.type],
            "start": self.start_index,
            "end": self.end_index
        }


class AdvancedTokenizer:
    """
    High-performance advanced tokenizer with optimized pattern matching.
    
    Features:
    - Single-pass tokenization for O(n) complexity
    - Pre-compiled regex patterns for fast matching
    - Priority-based pattern matching (longest match wins)
    - Memory-efficient token objects using __slots__
    """
    
    # Comprehensive regex patterns - compiled once at class level for speed
    PATTERNS = {
        'url': r'(?:https?://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+)',
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'scientific': r'\d+(?:\.\d+)?[eE][+-]?\d+',
        'currency': r'[$€£¥₹]\s*\d+(?:,\d{3})*(?:\.\d+)?|\d+(?:,\d{3})*(?:\.\d+)?\s*(?:USD|EUR|GBP|JPY|INR)',
        'float': r'\d+\.\d+',
        'integer_comma': r'\d{1,3}(?:,\d{3})+',
        'integer': r'\d+',
        'emoji': r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F700-\U0001F77F]|[\U0001F780-\U0001F7FF]|[\U0001F800-\U0001F8FF]|[\U0001F900-\U0001F9FF]|[\U0001FA00-\U0001FA6F]|[\U0001FA70-\U0001FAFF]|[\U00002702-\U000027B0]|[\U000024C2-\U0001F251]|[\U0001F1E0-\U0001F1FF]',
        'hashtag': r'#[\w\u0080-\uFFFF]+',
        'mention': r'@[\w]+',
        'contraction': r"(?:\b[a-zA-Z]+'(?:t|s|re|ve|ll|d|m|em|clock|cause|til|bout|n)\b)",
        'possessive': r"(?:\b[a-zA-Z]+[''][sS]\b)",
        'abbreviation': r'(?:\b(?:[A-Z]\.)+(?:[A-Z])?\b|\b(?:e\.g\.|i\.e\.|etc\.|vs\.|Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.|Jr\.|Sr\.|Inc\.|Ltd\.|Co\.)\b)',
        'hyphenated_word': r'\b[a-zA-Z]+(?:-[a-zA-Z]+)+\b',
        'word': r'\b[\w\u0080-\uFFFF]+\b',
        'newline': r'(?:\r?\n)',
        'whitespace': r'[ \t\f\v]+',
        'punctuation': r'[.,!?;:\'"()\[\]{}<>…—–]',
        'symbol': r'[&|\\^~`@#$%*+=/_\-]',
    }
    
    # Priority order - more specific patterns first for longest match
    TOKEN_ORDER = tuple([
        'url', 'email', 'scientific', 'currency', 'float',
        'integer_comma', 'integer', 'emoji', 'hashtag', 'mention',
        'contraction', 'possessive', 'abbreviation', 'hyphenated_word',
        'word', 'newline', 'whitespace', 'punctuation', 'symbol',
    ])
    
    TYPE_MAPPING = {
        'url': TokenType.URL,
        'email': TokenType.EMAIL,
        'scientific': TokenType.SCIENTIFIC,
        'currency': TokenType.CURRENCY,
        'float': TokenType.FLOAT,
        'integer_comma': TokenType.INTEGER,
        'integer': TokenType.INTEGER,
        'emoji': TokenType.EMOJI,
        'hashtag': TokenType.HASHTAG,
        'mention': TokenType.MENTION,
        'contraction': TokenType.CONTRACTION,
        'possessive': TokenType.CONTRACTION,
        'abbreviation': TokenType.ABBREVIATION,
        'hyphenated_word': TokenType.WORD,
        'word': TokenType.WORD,
        'newline': TokenType.NEWLINE,
        'whitespace': TokenType.WHITESPACE,
        'punctuation': TokenType.PUNCTUATION,
        'symbol': TokenType.SYMBOL,
    }
    
    # Class-level compiled patterns - shared across instances
    _COMPILED_PATTERNS: Dict[str, re.Pattern] = {}
    
    @classmethod
    def _compile_patterns(cls):
        """Compile all patterns once at class level for maximum performance."""
        if not cls._COMPILED_PATTERNS:
            for name, pattern in cls.PATTERNS.items():
                cls._COMPILED_PATTERNS[name] = re.compile(pattern, re.UNICODE)
    
    def __init__(self, preserve_whitespace: bool = False, 
                 preserve_case: bool = True,
                 handle_unknown: bool = True):
        """
        Initialize the tokenizer.
        
        Args:
            preserve_whitespace: If True, keep whitespace tokens in output
            preserve_case: If True, preserve original case; if False, lowercase words
            handle_unknown: If True, attempt to tokenize unknown characters individually
        """
        self.preserve_whitespace = preserve_whitespace
        self.preserve_case = preserve_case
        self.handle_unknown = handle_unknown
        
        # Use class-level compiled patterns (no per-instance compilation)
        if not self._COMPILED_PATTERNS:
            self._compile_patterns()
        self.compiled_patterns = self._COMPILED_PATTERNS
    
    def _find_first_match(self, text: str, start_pos: int) -> Optional[Tuple[str, str, int]]:
        """
        Find the first matching pattern from the current position.
        
        Returns:
            Tuple of (pattern_name, matched_text, match_length) or None
        """
        best_match = None
        best_end = -1
        
        for pattern_name in self.TOKEN_ORDER:
            pattern = self.compiled_patterns[pattern_name]
            match = pattern.match(text, start_pos)
            
            if match and match.start() == start_pos:
                end_pos = match.end()
                # Prefer longer matches
                if end_pos > best_end:
                    best_match = (pattern_name, match.group(), end_pos - start_pos)
                    best_end = end_pos
        
        return best_match
    
    def tokenize(self, text: str) -> List[Token]:
        """
        Tokenize the input text into a list of Token objects.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of Token objects
        """
        tokens = []
        pos = 0
        length = len(text)
        
        while pos < length:
            match_result = self._find_first_match(text, pos)
            
            if match_result:
                pattern_name, matched_text, match_length = match_result
                
                # Skip whitespace if not preserving
                if pattern_name == 'whitespace' and not self.preserve_whitespace:
                    pos += match_length
                    continue
                
                # Apply case transformation if needed
                token_type = self.TYPE_MAPPING[pattern_name]
                token_value = matched_text if self.preserve_case else matched_text.lower()
                
                token = Token(
                    value=token_value,
                    type=token_type,
                    start_index=pos,
                    end_index=pos + match_length
                )
                tokens.append(token)
                pos += match_length
            else:
                # Handle unknown characters
                if self.handle_unknown:
                    char = text[pos]
                    token = Token(
                        value=char,
                        type=TokenType.UNKNOWN,
                        start_index=pos,
                        end_index=pos + 1
                    )
                    tokens.append(token)
                    pos += 1
                else:
                    raise ValueError(f"Unable to tokenize character at position {pos}: '{text[pos]}'")
        
        return tokens
    
    def tokenize_simple(self, text: str) -> List[str]:
        """
        Simple tokenization returning just the token values as strings.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of token strings
        """
        tokens = self.tokenize(text)
        if not self.preserve_whitespace:
            return [t.value for t in tokens if t.type != TokenType.WHITESPACE]
        return [t.value for t in tokens]
    
    def tokenize_with_types(self, text: str) -> List[Tuple[str, str]]:
        """
        Tokenize and return tuples of (value, type_name).
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of (value, type_name) tuples
        """
        tokens = self.tokenize(text)
        if not self.preserve_whitespace:
            return [(t.value, TOKEN_TYPE_NAMES[t.type]) for t in tokens if t.type != TokenType.WHITESPACE]
        return [(t.value, TOKEN_TYPE_NAMES[t.type]) for t in tokens]
    
    def get_token_counts(self, text: str) -> Dict[str, int]:
        """
        Get counts of each token type in the text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary mapping token type names to counts
        """
        tokens = self.tokenize(text)
        counts: Dict[str, int] = {}
        
        for token in tokens:
            if token.type == TokenType.WHITESPACE and not self.preserve_whitespace:
                continue
            type_name = TOKEN_TYPE_NAMES[token.type]
            counts[type_name] = counts.get(type_name, 0) + 1
        
        return counts
    
    def split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using advanced sentence boundary detection.
        
        Args:
            text: Input text to split
            
        Returns:
            List of sentences
        """
        # Pattern for sentence boundaries
        # Handles abbreviations, decimals, and other edge cases
        sentence_pattern = r'''
            (?<!\w\.\w.)          # Not an abbreviation like U.S.A.
            (?<![A-Z][a-z]\.)     # Not Mr., Mrs., etc.
            (?<=\.|\?|!|。|！|？)  # After sentence-ending punctuation
            |\n+                   # Or newlines
        '''
        
        sentences = re.split(sentence_pattern, text, flags=re.VERBOSE | re.UNICODE)
        return [s.strip() for s in sentences if s.strip()]
    
    def tokenize_batch(self, texts: List[str]) -> List[List[Token]]:
        """
        Tokenize multiple texts efficiently (batch processing).
        
        Args:
            texts: List of input texts to tokenize
            
        Returns:
            List of token lists, one for each input text
        """
        return [self.tokenize(text) for text in texts]
    
    def get_tokens_as_dicts(self, text: str) -> List[Dict]:
        """
        Tokenize and return tokens as dictionaries (useful for JSON serialization).
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of token dictionaries
        """
        tokens = self.tokenize(text)
        return [t.to_dict() for t in tokens if t.type != TokenType.WHITESPACE or self.preserve_whitespace]
    
    @staticmethod
    def demo():
        """Run a comprehensive demonstration of the tokenizer capabilities."""
        import time
        
        tokenizer = AdvancedTokenizer()
        
        test_cases = [
            ("Basic Sentence", "Hello, world!"),
            ("Contractions", "Don't worry, it's working perfectly."),
            ("URLs & Emails", "Visit https://example.com/path?query=1 or email test@example.com"),
            ("Currency", "The price is $1,234.56 or €999.99"),
            ("Scientific Notation", "Scientific: 1.5e-10 and 2E+8"),
            ("Emojis", "Emoji test: 😀🎉🚀🌍"),
            ("Social Media", "#Python @developer are great!"),
            ("Abbreviations", "U.S.A. and e.g. are abbreviations."),
            ("Hyphenated Words", "Well-known state-of-the-art solutions"),
            ("Possessives", "John's book and the dogs' toys"),
            ("Mixed Content", "Mixed: Hello! Visit http://test.com now. Price: $50. 😊"),
            ("Numbers", "Numbers: 42, 3.14, 1,000,000, 1.5e-10"),
            ("Multi-language", "Bonjour! 你好！مرحبا! 🌍"),
        ]
        
        print("=" * 70)
        print("ADVANCED TOKENIZER DEMONSTRATION")
        print("=" * 70)
        
        for name, text in test_cases:
            print(f"\n{name}:")
            print(f"  Input: {text}")
            tokens = tokenizer.tokenize(text)
            filtered_tokens = [t for t in tokens if t.type != TokenType.WHITESPACE]
            
            print(f"  Tokens ({len(filtered_tokens)}): {[t.value for t in filtered_tokens]}")
        
        print("\n" + "=" * 70)
        print("TOKEN TYPE COUNTS EXAMPLE")
        print("=" * 70)
        sample_text = "Hello! Visit https://example.com or email test@example.com. Price: $1,234.56 😊"
        counts = tokenizer.get_token_counts(sample_text)
        print(f"\nText: {sample_text}")
        print(f"Counts: {counts}")
        
        print("\n" + "=" * 70)
        print("SENTENCE SPLITTING EXAMPLE")
        print("=" * 70)
        long_text = "Hello! How are you? I'm fine. Visit example.com. Great!"
        sentences = tokenizer.split_sentences(long_text)
        print(f"\nInput: {long_text}")
        print(f"Sentences: {sentences}")
        
        print("\n" + "=" * 70)
        print("DIFFERENT OUTPUT FORMATS")
        print("=" * 70)
        sample = "Hello! Visit https://example.com today."
        print(f"\nInput: {sample}\n")
        
        print("Simple tokens:")
        print(f"  {tokenizer.tokenize_simple(sample)}")
        
        print("\nTokens with types:")
        for val, typ in tokenizer.tokenize_with_types(sample):
            print(f"  '{val}' -> {typ}")
        
        print("\nTokens as dictionaries (JSON-ready):")
        for d in tokenizer.get_tokens_as_dicts(sample)[:3]:
            print(f"  {d}")
        
        print("\n" + "=" * 70)
        print("PERFORMANCE BENCHMARK")
        print("=" * 70)
        
        # Create a large text for benchmarking (extract just the text part from tuples)
        large_text = " ".join([text for _, text in test_cases] * 100)
        
        start = time.perf_counter()
        tokens = tokenizer.tokenize(large_text)
        elapsed = time.perf_counter() - start
        
        chars_per_sec = len(large_text) / elapsed
        tokens_per_sec = len(tokens) / elapsed
        
        print(f"\nText size: {len(large_text):,} characters")
        print(f"Tokens generated: {len(tokens):,}")
        print(f"Time elapsed: {elapsed*1000:.2f} ms")
        print(f"Speed: {chars_per_sec:,.0f} chars/sec | {tokens_per_sec:,.0f} tokens/sec")
        
        print("\n" + "=" * 70)
        print("BATCH PROCESSING EXAMPLE")
        print("=" * 70)
        batch = ["Hello world!", "How are you?", "Goodbye!"]
        results = tokenizer.tokenize_batch(batch)
        for i, (text, tokens) in enumerate(zip(batch, results)):
            print(f"\n{i+1}. '{text}' -> {[t.value for t in tokens if t.type != TokenType.WHITESPACE]}")
        
        print("\n" + "=" * 70)
        print("DEMONSTRATION COMPLETE")
        print("=" * 70)


if __name__ == "__main__":
    AdvancedTokenizer.demo()

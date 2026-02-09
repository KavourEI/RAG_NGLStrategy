#!/usr/bin/env python
"""Test the text cleaning function"""
import re

def clean_text(text):
    """Comprehensive text cleaning to fix OCR and formatting issues"""
    # Remove asterisks used for emphasis
    text = re.sub(r'\*+', '', text)

    # Fix severely spaced-out text (e.g., "6 3 9" -> "639", "/ m t" -> "/mt")
    text = re.sub(r'(\d)\s+(?=\d)', r'\1', text)  # Fix spaced numbers
    text = re.sub(r'([/$])\s+', r'\1', text)  # Fix "/ " or "$ "
    text = re.sub(r'\s+([/$])', r'\1', text)  # Fix " /" or " $"

    # Fix common unit patterns
    text = re.sub(r'/\s*m\s*t\b', '/mt', text, flags=re.IGNORECASE)
    text = re.sub(r'U\s*S\s*\$?\s*', 'US$', text)
    text = re.sub(r'\$\s+(\d)', r'$\1', text)

    # Fix spaced letters in common words
    def fix_spaced_word(match):
        return match.group(0).replace(' ', '')

    text = re.sub(r'\b([a-z])\s+([a-z])\s+([a-z](?:\s+[a-z])*)\b', fix_spaced_word, text, flags=re.IGNORECASE)

    # Normalize multiple spaces to single space
    text = re.sub(r' +', ' ', text)

    # Normalize line breaks - max 2 newlines
    text = re.sub(r'\n\s*\n+', '\n\n', text)

    # Clean up extra whitespace around punctuation
    text = re.sub(r'\s+([,;:.!?)])', r'\1', text)
    text = re.sub(r'([(])\s+', r'\1', text)
    text = re.sub(r'([,;:.!?])\s+', r'\1 ', text)

    # Fix common number-dash patterns
    text = re.sub(r'(\d+)\s*-\s*(\d+)', r'\1-\2', text)

    return text.strip()

# Test with the problematic text from the user
test_text = """* CFR Vietnam* – For cargoes with a 30 % propane / 70 % butane split, July 2nd‑half spot prices were US 
639
‑
649
 
/
 
m
t
,
c
a
r
r
y
i
n
g
a
p
r
e
m
i
u
m
o
f
a
b
o
u
t
U
S
 
639‑649 / mt,carryingapremiumofaboutUS 85‑95 / mt over the July contract price (CP). August 1st‑half prices were US $621‑631 / mt with the same premium range."""

print("BEFORE CLEANING:")
print("-" * 80)
print(test_text)
print("\n")

cleaned = clean_text(test_text)

print("AFTER CLEANING:")
print("-" * 80)
print(cleaned)


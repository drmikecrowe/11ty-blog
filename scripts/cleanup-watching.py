#!/usr/bin/env python3
"""
Clean up watching posts:
1. Remove tags that duplicate genres
2. Fix spelling/grammar in "Our Thoughts" section (preserving tone/style)
"""

import re
import sys
from pathlib import Path

# Simple spelling fixes - common typos only
SPELLING_FIXES = {
    r'\bteh\b': 'the',
    r'\brecieve\b': 'receive',
    r'\boccured\b': 'occurred',
    r'\bseperate\b': 'separate',
    r'\bdefinately\b': 'definitely',
    r'\boccasion\b': 'occasion',
    r'\buntil\b': 'until',
    r'\balot\b': 'a lot',
    r"its'": "its",
    r'\bwont\b': "won't",
    r'\bdont\b': "don't",
    r'\bcant\b': "can't",
    r'\bwouldnt\b': "wouldn't",
    r'\bcouldnt\b': "couldn't",
    r'\bshouldnt\b': "shouldn't",
    r'\bdidnt\b': "didn't",
    r'\bisnt\b': "isn't",
    r'\barent\b': "aren't",
    r'\bwasnt\b': "wasn't",
    r'\bwerent\b': "weren't",
    r'\bhasnt\b': "hasn't",
    r'\bhavent\b': "haven't",
    r'\bhadnt\b': "hadn't",
    r'\bthats\b': "that's",
    r'\bwhats\b': "what's",
    r'\bheres\b': "here's",
    r'\btheres\b': "there's",
    r'\bwhos\b': "who's",
    r'\blets\b(?!\s+[a-z])': "let's",  # "lets" alone, not "lets go"
    r'\byoure\b': "you're",
    r'\btheyre\b': "they're",
    r'\bwere\b(?=\s+(?:going|doing|watching|looking))': "we're",
    r'\bIve\b': "I've",
    r'\bId\b(?=\s+(?:say|think|recommend|love|hate))': "I'd",
    r'\bIll\b': "I'll",
    r'\bIm\b': "I'm",
}

def fix_grammar(text: str) -> str:
    """Fix common spelling/grammar issues while preserving tone."""
    if not text.strip():
        return text

    result = text

    # Apply spelling fixes
    for pattern, replacement in SPELLING_FIXES.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Fix double spaces
    result = re.sub(r'  +', ' ', result)

    # Fix spacing around punctuation
    result = re.sub(r'\s+([.,!?;:])', r'\1', result)
    result = re.sub(r'([.,!?;:])([A-Za-z])', r'\1 \2', result)

    # Capitalize first letter of sentences
    result = re.sub(r'([.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), result)

    # Capitalize "I" when standalone
    result = re.sub(r'\bi\b(?=[^a-zA-Z]|$)', 'I', result)

    return result


def process_file(file_path: Path) -> bool:
    """Process a single file. Returns True if changes were made."""
    content = file_path.read_text()
    original = content

    # Parse frontmatter and body
    if not content.startswith("---"):
        return False

    parts = content.split("---", 2)
    if len(parts) < 3:
        return False

    frontmatter = parts[1]
    body = parts[2]

    # Extract genres from frontmatter
    genres = set()
    genres_match = re.search(r'genres:\s*\[([^\]]*)\]', frontmatter)
    if genres_match:
        genres_str = genres_match.group(1)
        # Parse genres like ["Action", "Sci-Fi"]
        for g in re.findall(r'"([^"]+)"', genres_str):
            genres.add(g.lower())

    # Remove tags that duplicate genres
    frontmatter_lines = frontmatter.split("\n")
    new_frontmatter_lines = []
    in_tags = False
    for line in frontmatter_lines:
        if line.strip().startswith("tags:"):
            in_tags = True
            new_frontmatter_lines.append(line)
            continue
        if in_tags:
            if line.strip().startswith("- "):
                tag = line.strip()[2:].strip()
                # Keep tag if it's not a genre duplicate
                if tag.lower() not in genres:
                    new_frontmatter_lines.append(line)
                # else: skip this tag (it duplicates a genre)
            elif line.strip() and not line.startswith(" "):
                in_tags = False
                new_frontmatter_lines.append(line)
            else:
                new_frontmatter_lines.append(line)
        else:
            new_frontmatter_lines.append(line)

    new_frontmatter = "\n".join(new_frontmatter_lines)

    # Fix grammar in "Our Thoughts" section
    if "## Our Thoughts" in body:
        before_thoughts, thoughts_and_rest = body.split("## Our Thoughts", 1)

        # Find where thoughts section ends (next ## or end of file)
        if "\n## " in thoughts_and_rest:
            thoughts_content, rest = thoughts_and_rest.split("\n## ", 1)
            rest = "\n## " + rest
        else:
            thoughts_content = thoughts_and_rest
            rest = ""

        # Fix grammar in thoughts
        fixed_thoughts = fix_grammar(thoughts_content)

        body = before_thoughts + "## Our Thoughts" + fixed_thoughts + rest

    # Reconstruct file
    new_content = f"---{new_frontmatter}---{body}"

    if new_content != original:
        file_path.write_text(new_content)
        return True
    return False


def main():
    script_dir = Path(__file__).parent
    content_dir = script_dir.parent / "content" / "watching"

    if not content_dir.exists():
        print(f"Error: Content directory not found: {content_dir}")
        sys.exit(1)

    # Find all index.md files
    files = list(content_dir.glob("**/index.md"))
    files = [f for f in files if "_index.md" not in f.name]

    print(f"Processing {len(files)} files...")

    changed = 0
    for file_path in sorted(files):
        rel_path = file_path.relative_to(content_dir)
        if process_file(file_path):
            print(f"  Updated: {rel_path}")
            changed += 1

    print(f"\nDone. {changed} files updated.")


if __name__ == "__main__":
    main()

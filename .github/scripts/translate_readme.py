#!/usr/bin/env python3
"""
Script to translate README.md to Chinese using Step AI's translation API.
"""
import os
import sys
import textwrap
from openai import OpenAI


def main():
    """Translate README.md to Chinese (Simplified)."""
    api_key = os.environ.get('STEPFUN_API_KEY')
    if not api_key:
        print('STEPFUN_API_KEY is not set; skipping README translation step.', file=sys.stderr)
        sys.exit(0)

    client = OpenAI(
        api_key=api_key,
        base_url='https://api.stepfun.com/v1'
    )
    
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print('ERROR: README.md not found in current directory.', file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f'ERROR: Failed to read README.md: {e}', file=sys.stderr)
        sys.exit(1)
        
    system_prompt = textwrap.dedent("""
        You are a professional technical translator. 
        Translate the following Markdown content from English to Chinese (Simplified). 
        Maintain all formatting, links, and code blocks exactly as they are. 
        Only translate the text content.
        The file is a README for an AI model named 'Step 3.5 Flash'.
    """).strip()

    response = client.chat.completions.create(
        model='step-3.5-flash',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': content}
        ]
    )
    
    if not response.choices or len(response.choices) == 0:
        print('ERROR: API returned empty response.', file=sys.stderr)
        sys.exit(1)
        
    translated_content = response.choices[0].message.content
    if not translated_content:
        print('ERROR: API returned empty translation.', file=sys.stderr)
        sys.exit(1)
    
    try:
        with open('README.zh-CN.md', 'w', encoding='utf-8') as f:
            f.write(translated_content)
    except IOError as e:
        print(f'ERROR: Failed to write README.zh-CN.md: {e}', file=sys.stderr)
        sys.exit(1)
    
    print('README.md successfully translated to README.zh-CN.md')


if __name__ == '__main__':
    main()

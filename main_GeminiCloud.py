        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    engine = get_query_engine()
                    response = engine.query(prompt)
                    
                    if hasattr(response, 'response'):
                        response_text = response.response
                    elif hasattr(response, 'text'):
                        response_text = response.text
                    else:
                        response_text = str(response)
                    
                    # Apply multiple cleaning passes
                    response_text = clean_text(response_text)
                    
                    # Additional fix for common LLM formatting issues
                    response_text = fix_llm_formatting(response_text)
                    
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})


def fix_llm_formatting(text):
    """Additional formatting fixes for LLM output"""
    import re
    
    # Fix: number newline - number pattern
    text = re.sub(r'(\d+)\s*\n\s*([−‑–—])\s*(\d+)', r'\1\2\3', text)
    
    # Fix: /mt on new line
    text = re.sub(r'(\d+)\s*\n\s*/\s*(mt|ton)', r'\1/\2', text, flags=re.IGNORECASE)
    
    # Fix: $ on new line
    text = re.sub(r'([A-Za-z])\s*\n\s*\$', r'\1 $', text)
    
    # Fix hyphenated words broken across lines
    text = re.sub(r'([a-zA-Z])-\s*\n\s*([a-zA-Z])', r'\1-\2', text)
    
    # Remove excessive newlines but keep paragraphs
    lines = text.split('\n')
    cleaned = []
    for i, line in enumerate(lines):
        line = line.strip()
        if line:
            # If next line starts with lowercase, merge them
            if i < len(lines) - 1 and lines[i+1].strip() and lines[i+1].strip()[0].islower():
                cleaned.append(line + ' ' + lines[i+1].strip())
                lines[i+1] = ''
            else:
                cleaned.append(line)
    
    text = '\n'.join(cleaned)
    
    return text

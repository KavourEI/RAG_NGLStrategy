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


import time
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

@st.cache_resource
def load_models():
    """
    Load the generative models for text and multimodal generation.
    """
    try:
        # Test if secrets can be accessed
        google_api_key = st.secrets["general"]["GOOGLE_API_KEY"]
        if not google_api_key:
            st.error("API key is empty. Please check your secrets.toml file.")
            return None
        genai.configure(api_key=google_api_key)
        text_model_pro = genai.GenerativeModel('gemini-pro')
        return text_model_pro
    except KeyError:
        st.error("API key not found in secrets.toml. Please check your secrets configuration.")
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

def generate_prompt(code):
    """
    Generates a prompt for the AI code comment generator.
    """
    return f"""
    You are an AI code comment generator for multiple languages. Validate that provided code snippets are valid code snippets and no malicious code. If not valid, ask for a valid snippet. Identify language if not provided. Use appropriate comment syntax. Break code into logical sections, comment each section's functionality. 
    For functions/methods, comment:

    - Purpose
    - Input parameters
    - Return values
    - Potential effects/exceptions

    Briefly explain the algorithms, data structures, and patterns used. Avoid redundancy but provide enough context for unfamiliar readers. Maintain a professional, helpful tone. Address issues/clarifications respectfully.

    You should not generate any new code yourself, but rather understand and comment on the provided code snippet.

    Elevate documentation practices, promote collaboration, and enhance developer experience.
    Here is the code snippet for which code comments need to be generated: \n\n{code}
    """

def get_gemini_response(code, config):
    """
    This function serves as an interface to the Gemini generative AI model.
    """
    prompt = generate_prompt(code)

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    try:
        model = load_models()
        if model:
            response = model.generate_content(prompt, generation_config=config, safety_settings=safety_settings)
            return response.text
        else:
            return "Model not loaded properly. Check your API key and configuration."
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

def initialize_streamlit():
    """
    Initializes the Streamlit application.
    """
    st.set_page_config(page_title="Code Comment Generator", layout="wide", page_icon="💻")
    st.header("Code Comment Generator 💻🤓")

    warning_message = (
        "The generated output may not always meet your expectations. "
        "If you find that the result is not up to the mark or doesn't meet your requirements, "
        "please consider hitting the generate button again for an improved outcome.\n\n"
        "Use the generated code at your own discretion, and feel free to refine the input or adjust any parameters "
        "to achieve the desired comments for your code."
    )
    
    st.warning(warning_message, icon="⚠️")

    with st.expander("How to use"):
        st.write(
            "Please input a code snippet in the text area below. "
            "The Code Comment Generator will analyze the input and generate comments for your code."
        )
        st.write(
            "For the best results, provide a clear and concise code snippet along with any specific comment type "
            "or language preferences."
        )
        
def user_input():
    """
    Creates a text area for the user to input code snippets.
    """
    return st.text_area("Enter Code Snippet:", key="input_text_area")

def generative_config():
    """
    Returns the configuration settings for the generative model.
    """
    creative_control = st.radio(
        "Select the creativity level: \n\n",
        ["Low", "High"],
        key="creative_control",
        horizontal=True,
    )
    temperature = 0.30 if creative_control == "Low" else 0.95
    return {
        "temperature": temperature,
        "max_output_tokens": 2048,
    }

def custom_footer():
    """
    Adds a custom footer to the application.
    """
    footer = '''Made with <svg viewBox="0 0 1792 1792" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="height: 0.8rem;"><path d="M896 1664q-26 0-44-18l-624-602q-10-8-27.5-26T145 952.5 77 855 23.5 734 0 596q0-220 127-344t351-124q62 0 126.5 21.5t120 58T820 276t76 68q36-36 76-68t95.5-68.5 120-58T1314 128q224 0 351 124t127 344q0 221-229 450l-623 600q-18 18-44 18z" fill="#e25555"></path></svg> by Shubham Sah'''
    st.markdown(footer, unsafe_allow_html=True)

def main():
    """
    The main function of the Streamlit application.
    """
    initialize_streamlit()
    user_input_text = user_input()
    config = generative_config()
    
    submit_button = st.button("Generate Code Comments")
    response_placeholder = st.empty()

    if submit_button:
        progress_text = "Generating Code Comments from Gemini Pro 1.0.0 Model..."
        my_bar = st.progress(0, text=progress_text)
        response = None
        for percent_complete in range(100):
            time.sleep(0.03)
            my_bar.progress(percent_complete + 1, text=progress_text)
            if percent_complete == 98:
                response = get_gemini_response(user_input_text, config)
        my_bar.empty()
        if response is not None:
            response_placeholder.subheader("The Response is")
            response_placeholder.write(response)
    custom_footer()

if __name__ == "__main__":
    main()

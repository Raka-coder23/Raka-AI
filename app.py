# =========================================================
# RAKA AI - PREMIUM AI CHAT + IMAGE GENERATOR
# =========================================================

import streamlit as st
import google.generativeai as genai
from huggingface_hub import InferenceClient
import io
import time

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Raka AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# API CONFIG
# =========================================================

genai.configure(
    api_key=st.secrets["gemini"]["api_key"]
)

chat_model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

HF_TOKEN = st.secrets["huggingface"]["token"]

IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"

# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "mode" not in st.session_state:
    st.session_state.mode = "chat"

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

/* =======================================================
GLOBAL
======================================================= */

.stApp{
    background:#0f0f0f;
    color:white;
    font-family:Inter,sans-serif;
}

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

/* =======================================================
SIDEBAR
======================================================= */

section[data-testid="stSidebar"]{
    background:#171717;
    border-right:1px solid #2d2d2d;
}

section[data-testid="stSidebar"] *{
    color:white !important;
}

/* =======================================================
TITLE
======================================================= */

.main-title{
    text-align:center;
    font-size:56px;
    font-weight:800;
    margin-top:10px;
    background:linear-gradient(90deg,#60a5fa,#a855f7);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    letter-spacing:-2px;
}

.sub-title{
    text-align:center;
    color:#9ca3af;
    margin-bottom:30px;
    font-size:18px;
}

/* =======================================================
BUTTONS
======================================================= */

.stButton button{
    width:100%;
    background:#262626;
    color:white;
    border:1px solid #3a3a3a;
    border-radius:16px;
    padding:14px;
    font-weight:600;
    transition:0.3s;
}

.stButton button:hover{
    border:1px solid #2563eb;
    background:#2f2f2f;
}

/* =======================================================
CHAT MESSAGES
======================================================= */

.user-msg{
    background:linear-gradient(135deg,#2563eb,#1d4ed8);
    padding:16px 20px;
    border-radius:22px 22px 8px 22px;
    width:fit-content;
    max-width:75%;
    margin-left:auto;
    margin-top:18px;
    color:white;
    font-size:16px;
    line-height:1.8;
    box-shadow:0 8px 24px rgba(37,99,235,0.25);
}

.ai-msg{
    background:#1e1e1e;
    border:1px solid #2f2f2f;
    padding:18px 22px;
    border-radius:22px 22px 22px 8px;
    width:fit-content;
    max-width:75%;
    margin-top:18px;
    color:white;
    font-size:16px;
    line-height:1.9;
    box-shadow:0 8px 24px rgba(0,0,0,0.2);
}

/* =======================================================
IMAGE CARD
======================================================= */

.image-card{
    background:#1e1e1e;
    border:1px solid #2f2f2f;
    padding:18px;
    border-radius:24px;
    margin-top:20px;
}

/* =======================================================
CHAT INPUT
======================================================= */

.stChatInput{
    position:fixed;
    bottom:20px;
    left:26%;
    width:48%;
}

.stChatInput input{
    background:#1e1e1e !important;
    color:white !important;
    border-radius:24px !important;
    border:1px solid #333 !important;
    padding:18px !important;
    font-size:16px !important;
}

/* =======================================================
DOWNLOAD BUTTON
======================================================= */

.stDownloadButton button{
    background:#16a34a !important;
    border:none !important;
}

/* =======================================================
SCROLLBAR
======================================================= */

::-webkit-scrollbar{
    width:8px;
}

::-webkit-scrollbar-thumb{
    background:#333;
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("# ✨ Raka AI")

    st.caption("Next Generation AI Experience")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💬 Chat"):
            st.session_state.mode = "chat"

    with col2:
        if st.button("🎨 Image"):
            st.session_state.mode = "image"

    st.divider()

    st.markdown("""
    ### Features

    ✨ AI Chat Assistant  
    🎨 AI Image Generation  
    """)

    st.divider()

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.caption("Powered by Gemini + FLUX AI")

# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">Raka AI</div>',
    unsafe_allow_html=True
)

if st.session_state.mode == "chat":

    st.markdown(
        '<div class="sub-title">Professional AI Conversation Experience</div>',
        unsafe_allow_html=True
    )

else:

    st.markdown(
        '<div class="sub-title">Generate Stunning AI Images</div>',
        unsafe_allow_html=True
    )

# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for msg in st.session_state.messages:

    # USER MESSAGE
    if msg["role"] == "user":

        st.markdown(
            f'<div class="user-msg">{msg["content"]}</div>',
            unsafe_allow_html=True
        )

    # AI MESSAGE
    elif msg["role"] == "assistant":

        st.markdown(
            f'<div class="ai-msg">{msg["content"]}</div>',
            unsafe_allow_html=True
        )

    # IMAGE MESSAGE
    elif msg["role"] == "image":

        st.markdown(
            '<div class="image-card">',
            unsafe_allow_html=True
        )

        st.image(
            msg["image"],
            use_container_width=True
        )

        st.markdown(
            f"**Prompt:** {msg['prompt']}"
        )

        # DOWNLOAD BUTTON
        buf = io.BytesIO()

        msg["image"].save(
            buf,
            format="PNG"
        )

        st.download_button(
            label="⬇ Download Image",
            data=buf.getvalue(),
            file_name=f"raka_ai_{int(time.time())}.png",
            mime="image/png",
            use_container_width=True,
            key=f"download_{time.time()}"
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

# =========================================================
# CHAT MODE
# =========================================================

if st.session_state.mode == "chat":

    prompt = st.chat_input(
        "Message Raka AI..."
    )

    if prompt:

        # SAVE USER
        st.session_state.messages.append({
            "role":"user",
            "content":prompt
        })

        st.markdown(
            f'<div class="user-msg">{prompt}</div>',
            unsafe_allow_html=True
        )

        # AI RESPONSE
        with st.spinner("Thinking..."):

            response = chat_model.generate_content(
                prompt
            )

            ai_response = response.text

            placeholder = st.empty()

            typed = ""

            for char in ai_response:

                typed += char

                placeholder.markdown(
                    f'<div class="ai-msg">{typed}</div>',
                    unsafe_allow_html=True
                )

                time.sleep(0.002)

        # SAVE AI RESPONSE
        st.session_state.messages.append({
            "role":"assistant",
            "content":ai_response
        })

# =========================================================
# IMAGE MODE
# =========================================================

else:

    image_prompt = st.chat_input(
        "Describe the image you want..."
    )

    if image_prompt:

        # SAVE USER MESSAGE
        st.session_state.messages.append({
            "role":"user",
            "content":image_prompt
        })

        st.markdown(
            f'<div class="user-msg">{image_prompt}</div>',
            unsafe_allow_html=True
        )

        with st.spinner("Generating Image..."):

            try:

                # NEW CLIENT EVERY REQUEST
                image_client = InferenceClient(
                    token=HF_TOKEN,
                    timeout=300
                )

                time.sleep(1)

                # GENERATE IMAGE
                image = image_client.text_to_image(
                    prompt=image_prompt,
                    model=IMAGE_MODEL
                )

                # SAVE IMAGE
                st.session_state.messages.append({
                    "role":"image",
                    "image":image,
                    "prompt":image_prompt
                })

                # SHOW IMAGE CARD
                st.markdown(
                    '<div class="image-card">',
                    unsafe_allow_html=True
                )

                st.image(
                    image,
                    use_container_width=True
                )

                st.markdown(
                    f"**Prompt:** {image_prompt}"
                )

                # DOWNLOAD BUTTON
                buf = io.BytesIO()

                image.save(
                    buf,
                    format="PNG"
                )

                st.download_button(
                    label="⬇ Download Image",
                    data=buf.getvalue(),
                    file_name=f"raka_ai_{int(time.time())}.png",
                    mime="image/png",
                    use_container_width=True,
                    key=f"download_new_{time.time()}"
                )

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

                st.success(
                    "Image Generated Successfully!"
                )

            except Exception as e:

                st.error(
                    f"Generation Failed: {e}"
                )

                if st.button("🔄 Retry Generation"):
                    st.rerun()
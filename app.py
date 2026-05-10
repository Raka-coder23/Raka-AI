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
    layout="centered",
    initial_sidebar_state="collapsed"   # sidebar starts collapsed but toggle icon visible
)

# =========================================================
# API CONFIG
# =========================================================
genai.configure(api_key=st.secrets["gemini"]["api_key"])
chat_model = genai.GenerativeModel("gemini-2.5-flash")

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
# CUSTOM CSS (header visible so sidebar icon shows)
# =========================================================
st.markdown("""
<style>
.stApp {background:#0f0f0f;color:white;font-family:Inter,sans-serif;}
#MainMenu, footer {visibility:hidden;}   /* hide menu + footer only, keep header visible */

.main-title {
    text-align:center;
    font-size:48px;
    font-weight:800;
    margin-top:20px;
    margin-bottom:10px;
    background:linear-gradient(90deg,#60a5fa,#a855f7);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.sub-title {
    text-align:center;
    font-size:18px;
    color:#9ca3af;
    margin-bottom:30px;
}
.user-msg,.ai-msg {
    max-width:100% !important;
    border-radius:18px;
    padding:14px 18px;
    margin:8px auto;
    font-size:15px;
    line-height:1.6;
}
.user-msg {background:#2563eb;color:white;}
.ai-msg {background:#1e1e1e;border:1px solid #333;}
.image-card {
    background:#1e1e1e;
    border:1px solid #2f2f2f;
    padding:14px;
    border-radius:18px;
    margin:12px auto;
}
.stChatInput {
    position:sticky;
    bottom:0;
    left:0;
    width:100% !important;
    padding:10px;
    background:#0f0f0f;
    border-top:1px solid #333;
    z-index:100;
}
.stChatInput input {
    width:100% !important;
    max-width:800px;
    margin:auto;
    display:block;
    background:#1e1e1e !important;
    color:white !important;
    border-radius:18px !important;
    border:1px solid #333 !important;
    padding:14px !important;
    font-size:15px !important;
}
.stDownloadButton button {background:#16a34a !important;border:none !important;}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER (Logo + Subtitle Centered)
# =========================================================
st.markdown('<div class="main-title">✨ Raka AI</div>', unsafe_allow_html=True)
if st.session_state.mode == "chat":
    st.markdown('<div class="sub-title">Professional AI Conversation Experience</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="sub-title">Generate Stunning AI Images</div>', unsafe_allow_html=True)

# =========================================================
# SIDEBAR CONTENT (Mode Selector + Info)
# =========================================================
with st.sidebar:
    st.markdown("# ✨ Raka AI")
    st.caption("Next Generation AI Experience")
    st.divider()
    st.markdown("### Features\n\n✨ AI Chat Assistant  \n🎨 AI Image Generation")
    mode_option = st.selectbox(
        "✨ Mode",
        ["💬 Chat", "🎨 Image", "🗑 Clear Chat"],
        index=0,
        key="mode_selector"
    )

if mode_option == "💬 Chat":
    st.session_state.mode = "chat"
elif mode_option == "🎨 Image":
    st.session_state.mode = "image"
elif mode_option == "🗑 Clear Chat":
    st.session_state.messages = []
    st.rerun()

# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f'<div class="ai-msg">{msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "image":
        st.markdown('<div class="image-card">', unsafe_allow_html=True)
        st.image(msg["image"], use_container_width=True)
        st.markdown(f"**Prompt:** {msg['prompt']}")
        buf = io.BytesIO()
        msg["image"].save(buf, format="PNG")
        st.download_button(
            label="⬇ Download Image",
            data=buf.getvalue(),
            file_name=f"raka_ai_{int(time.time())}.png",
            mime="image/png",
            use_container_width=True,
            key=f"download_{time.time()}"
        )
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# CHAT MODE (with quota error handling)
# =========================================================
if st.session_state.mode == "chat":
    prompt = st.chat_input("Message Raka AI...")
    if prompt:
        st.session_state.messages.append({"role":"user","content":prompt})
        st.markdown(f'<div class="user-msg">{prompt}</div>', unsafe_allow_html=True)
        with st.spinner("Thinking..."):
            try:
                response = chat_model.generate_content(prompt)
                ai_response = response.text
                placeholder = st.empty()
                typed = ""
                for char in ai_response:
                    typed += char
                    placeholder.markdown(f'<div class="ai-msg">{typed}</div>', unsafe_allow_html=True)
                    time.sleep(0.002)
                st.session_state.messages.append({"role":"assistant","content":ai_response})
            except Exception as e:
                st.error("⚠️ Gemini API quota exceeded. Please wait for reset or upgrade your plan.")
                st.session_state.messages.append({"role":"assistant","content":"[Quota exceeded – please retry later or upgrade your plan]"})


# =========================================================
# IMAGE MODE
# =========================================================
else:
    image_prompt = st.chat_input("Describe the image you want...")
    if image_prompt:
        st.session_state.messages.append({"role":"user","content":image_prompt})
        st.markdown(f'<div class="user-msg">{image_prompt}</div>', unsafe_allow_html=True)
        with st.spinner("Generating Image..."):
            try:
                image_client = InferenceClient(token=HF_TOKEN, timeout=300)
                time.sleep(1)
                image = image_client.text_to_image(prompt=image_prompt, model=IMAGE_MODEL)
                st.session_state.messages.append({"role":"image","image":image,"prompt":image_prompt})
                st.markdown('<div class="image-card">', unsafe_allow_html=True)
                st.image(image, use_container_width=True)
                st.markdown(f"**Prompt:** {image_prompt}")
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                st.download_button(
                    label="⬇ Download Image",
                    data=buf.getvalue(),
                    file_name=f"raka_ai_{int(time.time())}.png",
                    mime="image/png",
                    use_container_width=True,
                    key=f"download_new_{time.time()}"
                )
                st.markdown('</div>', unsafe_allow_html=True)
                st.success("Image Generated Successfully!")
            except Exception as e:
                st.error(f"Image generation failed: {e}")

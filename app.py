import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import csv
import zipfile

# --- আপনার API KEY ---
API_KEY = "AIzaSyDggNlQsVZ_io62gHZQXn5fQYYwC4W_vXI"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="EPS to AI SEO Tool", layout="wide")

st.markdown("""
    <style>
    .stButton>button {
        background-color: #7F27FF;
        color: white;
        border-radius: 8px;
        width: 100%;
    }
    .stDownloadButton>button {
        background-color: #00C853;
        color: white;
        border-radius: 8px;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🖼️ EPS to JPG & AI Metadata Generator")
st.write("আপনার EPS ফাইল আপলোড করুন, JPG কনভার্ট করুন এবং AI দিয়ে SEO তথ্য তৈরি করুন।")

col1, col2 = st.columns([2, 1])
with col1:
    uploaded_file = st.file_uploader("আপনার EPS ফাইলটি এখানে আপলোড করুন", type=["eps"])
with col2:
    num_keywords = st.number_input("কতটি Keywords প্রয়োজন?", min_value=1, max_value=100, value=20)

if uploaded_file is not None:
    try:
        with st.spinner("কাজ চলছে... দয়া করে অপেক্ষা করুন।"):
            image = Image.open(uploaded_file)
            rgb_image = image.convert("RGB")
            
            jpg_buffer = io.BytesIO()
            rgb_image.save(jpg_buffer, format="JPEG", quality=95)
            st.image(rgb_image, caption="ইমেজ প্রিভিউ", width=400)
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            Analyze this image and provide:
            1. Title: A professional SEO title.
            2. Description: A short SEO-friendly description (max 2 sentences).
            3. Keywords: Exactly {num_keywords} relevant SEO keywords separated by commas.
            
            Format exactly like this:
            Title: [Title here]
            Description: [Description here]
            Keywords: [Keywords here]
            """
            
            response = model.generate_content([prompt, rgb_image])
            ai_text = response.text
            
            st.subheader("AI জেনারেটেড মেটাডেটা:")
            st.text_area("আউটপুট:", ai_text, height=200)
            
            lines = ai_text.strip().split('\n')
            title, description, keywords = "N/A", "N/A", "N/A"
            for line in lines:
                if line.lower().startswith("title:"): title = line.split(":", 1)[1].strip()
                elif line.lower().startswith("description:"): description = line.split(":", 1)[1].strip()
                elif line.lower().startswith("keywords:"): keywords = line.split(":", 1)[1].strip()

            csv_buffer = io.StringIO()
            writer = csv.writer(csv_buffer)
            writer.writerow(["Title", "Description", "Keywords"])
            writer.writerow([title, description, keywords])
            
            zip_output = io.BytesIO()
            base_name = uploaded_file.name.rsplit('.', 1)[0]
            
            with zipfile.ZipFile(zip_output, "w") as zf:
                zf.writestr(f"{uploaded_file.name}", uploaded_file.getvalue())
                zf.writestr(f"{base_name}.jpg", jpg_buffer.getvalue())
                zf.writestr(f"{base_name}_metadata.csv", csv_buffer.getvalue())
            
            st.success("তৈরি হয়ে গেছে! নিচের বাটন থেকে ডাউনলোড করুন।")
            st.download_button(
                label="📥 ডাউনলোড করুন (EPS + JPG + CSV)",
                data=zip_output.getvalue(),
                file_name=f"{base_name}_package.zip",
                mime="application/zip"
            )
    except Exception as e:
        st.error(f"দুঃখিত, একটি সমস্যা হয়েছে: {e}")

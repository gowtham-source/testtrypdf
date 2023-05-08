
import os
import streamlit as st
# import pyperclip


import textwrap
from transformers import AutoProcessor, Wav2Vec2ForCTC
import torch
import librosa
from googletrans import Translator, LANGUAGES
from reportlab.pdfgen import canvas
from PIL import Image
# from datasets import load_dataset
import base64


def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


img = get_img_as_base64("assets/sampletest.jpg")


page_bg = f'''
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("data:image/png;base64,{img}");
background-size: 100%;
background-position: top left;
background-repeat: no-repeat;
background-attachment: fixed;
}}
[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}
[data-testid="stToolbar"] {{
right: 2rem;
}}
</style>
'''
st.markdown(page_bg, unsafe_allow_html=True)


@st.cache_resource
def load_model():
    processor = AutoProcessor.from_pretrained("facebook/wav2vec2-base-960h")
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
    return model, processor


model, processor = load_model()

# Function to check if the uploaded file is an audio file


def is_audio_file(file):
    audio_formats = ['.wav', '.opus', '.mp3']
    _, file_extension = os.path.splitext(file.name)
    if file_extension in audio_formats:
        return True
    else:
        return False


# def get_image_download_link(pdf_bytes):
#     b64 = base64.b64encode(pdf_bytes).decode()
#     href = f'<a href="data:application/octet-stream;base64,{b64}" download="image.pdf">Download PDF</a>'
#     return href

# @st.cache_data
# def copy_to_clipboard(text):
#     pyperclip.copy(text)


@st.cache_data
def generate_pdf(text):
    pdf = canvas.Canvas("output.pdf")

    # set up the font and font size
    pdf.setFont("Helvetica", 12)

    # set the margins of the page
    left_margin = 50
    right_margin = 50
    top_margin = 50
    bottom_margin = 50

    # split the text into lines based on the margins
    text_lines = []
    current_line = ""
    for word in text.split():
        word_width = pdf.stringWidth(current_line + word)
        if word_width > (pdf._pagesize[0] - left_margin - right_margin):
            text_lines.append(current_line)
            current_line = ""
        current_line += f"{word} "
    if current_line:
        text_lines.append(current_line)

    # add the lines of text to the PDF document, justified
    y = pdf._pagesize[1] - top_margin
    line_height = 15
    for line in text_lines:
        words = line.strip().split(" ")
        space_count = len(words) - 1
        total_word_width = sum([pdf.stringWidth(word) for word in words])
        remaining_space = pdf._pagesize[0] - \
            left_margin - right_margin - total_word_width
        if space_count > 0:
            space_width = remaining_space / space_count
        else:
            space_width = 0
        x = left_margin
        for word in words:
            pdf.drawString(x, y, word)
            x += pdf.stringWidth(word) + space_width
        y -= line_height

    # save the PDF document
    pdf.save()


# def load_image(img):
#     im = Image.open(img)
#     return im


@st.cache_data
def translate(text, dest_language):
    translator = Translator()

    # Translate the text
    translated_text = translator.translate(text, dest=list(LANGUAGES.keys())[
                                           list(LANGUAGES.values()).index(dest_language)]).text
    return translated_text


# Streamlit app
st.markdown("<center><h1>NoteZ✨</h1></center>", unsafe_allow_html=True)
st.title("Audio to Pdf Converter...")
st.write("Upload your audio files here")

uploaded_file = st.file_uploader("Choose an audio file", type=[
    'wav', 'opus', 'mp3'], accept_multiple_files=False)

if uploaded_file is not None and is_audio_file(uploaded_file):
    audio_array, sr = librosa.load(uploaded_file, sr=16000)
    inputs = processor(audio_array, sampling_rate=sr, return_tensors="pt")
    col133, col144, col155 = st.columns(3)
    with col144:
        st.audio(uploaded_file, format='audio/wav', start_time=0)

    # audio file is decoded on the fly
    # inputs = processor(dataset[0]["audio"]["array"], sampling_rate=sampling_rate, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
    predicted_ids = torch.argmax(logits, dim=-1)

    # transcribe speech
    transcription = processor.batch_decode(predicted_ids)
    text = transcription[0]
    if text:
        st.write("#### The Transcribed text:-")
        with st.container():
            wrapper = textwrap.TextWrapper(width=75)
            wrapped_text = wrapper.fill(text)
            st.code(wrapped_text, language='c#')
    if text:
        col1, col2, col3 = st.columns(3)
        # with col1:
        #     if st.button('Copy to clipboard'):
        #         copy_to_clipboard(text)
        #         st.success("Copied to clipboard")
        with col1:

            if st.button("Generate Pdf"):
                generate_pdf(text)

                with open("output.pdf", "rb") as f:
                    bytes = f.read()
                    st.download_button(
                        label="Download Pdf", data=bytes, file_name="output.pdf", mime="application/pdf")

                    # link = get_image_download_link(bytes)
                    # generate_qr(link)
                    # img = load_image('qr.png')
                    # st.image(img, width=290)
                # with col22:
                    # download as text file

            st.download_button('Download as text', text)
        # if st.button('Translate'):
        # Create an instance of the Translator class
    dest_language = st.selectbox(
        "Select language to translate to:", options=list(LANGUAGES.values()))

    # translator = Translator()

    # # Translate the text
    # translated_text = translator.translate(text, dest=list(LANGUAGES.keys())[
    #     list(LANGUAGES.values()).index(dest_language)]).text
    if dest_language:
        translated_text = translate(text, dest_language)
    # Display the translated text
        st.write("#### Translated Content: ({})".format(dest_language))
        with st.container():
            wrapper = textwrap.TextWrapper(width=75)
            wrapped_text = wrapper.fill(translated_text)
            st.code(wrapped_text, language='c#')

            if st.button(f"Generate Pdf in {dest_language}"):
                generate_pdf(translated_text)
                col12, col22 = st.columns(2)
                with col12:
                    with open("output.pdf", "rb") as f:
                        bytes = f.read()
                        st.download_button(
                            label="Download Pdf", data=bytes, file_name="output.pdf", mime="application/pdf")

            st.download_button('Download as text', translated_text)
            st.info(
                "Note: The generated pdf(for translated text) doesnot support some languages(for eg. Tamil, hindi etc..).")

    # st.code(translated_text)

    # Use the uploaded file for further processing or analysis
else:
    if st.button("Try test file"):
        col33, col44, col55 = st.columns(3)
        with col44:
            st.audio("test.opus", format='audio/wav', start_time=0)
        path = "test.opus"
        audio_file = "test"
        audio_array, sr = librosa.load(path, sr=16000)
        inputs = processor(audio_array, sampling_rate=sr, return_tensors="pt")

        # audio file is decoded on the fly
        # inputs = processor(dataset[0]["audio"]["array"], sampling_rate=sampling_rate, return_tensors="pt")
        with torch.no_grad():
            logits = model(**inputs).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)
        text = transcription[0]
        if text:
            st.write("#### The Transcribed text:-")
            with st.container():
                wrapper = textwrap.TextWrapper(width=75)
                wrapped_text = wrapper.fill(text)
                st.code(wrapped_text, language='c#')
        if text:
            col1, col2, col3 = st.columns(3)
            # with col1:
            #     if st.button('Copy to clipboard'):
            #         copy_to_clipboard(text)
            #         st.success("Copied to clipboard")
            with col1:

                if st.button("Generate Pdf"):
                    generate_pdf(text)

                    with open("output.pdf", "rb") as f:
                        bytes = f.read()
                        st.download_button(
                            label="Download Pdf", data=bytes, file_name="output.pdf", mime="application/pdf")

                        # link = get_image_download_link(bytes)
                        # generate_qr(link)
                        # img = load_image('qr.png')
                        # st.image(img, width=290)
                    # with col22:
                        # download as text file

                st.download_button('Download as text', text)
            # if st.button('Translate'):
            # Create an instance of the Translator class
        dest_language = st.selectbox(
            "Select language to translate to:", options=list(LANGUAGES.values()))

        # translator = Translator()

        # # Translate the text
        # translated_text = translator.translate(text, dest=list(LANGUAGES.keys())[
        #     list(LANGUAGES.values()).index(dest_language)]).text
        if dest_language:
            translated_text = translate(text, dest_language)
        # Display the translated text
            st.write("#### Translated Content: ({})".format(dest_language))
            with st.container():
                wrapper = textwrap.TextWrapper(width=75)
                wrapped_text = wrapper.fill(translated_text)
                st.code(wrapped_text, language='c#')

                if st.button(f"Generate Pdf in {dest_language}"):
                    generate_pdf(translated_text)
                    col12, col22 = st.columns(2)
                    with col12:
                        with open("output.pdf", "rb") as f:
                            bytes = f.read()
                            st.download_button(
                                label="Download Pdf", data=bytes, file_name="output.pdf", mime="application/pdf")

# elif uploaded_file is not None:
#     st.write("Please upload an audio file in .wav, .opus, or .mp3 format.")

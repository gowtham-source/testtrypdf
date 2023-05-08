import streamlit as st
import pandas as pd
import tabula
from PIL import Image

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


col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    image = Image.open('assets/pdfexcel.png')
    st.image(image, width=150)
with col2:
    st.write("## PDF to Excel")


uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
# pdf_path = "https://sedl.org/afterschool/toolkits/science/pdf/ast_sci_data_tables_sample.pdf"

if uploaded_file is not None:

    dfs = tabula.read_pdf(uploaded_file, pages='all')

    st.write(f"#### There are {len(dfs)} tables available in this pdf")

    selected_table = st.selectbox("Select a table", list(range(len(dfs))))

    st.write(dfs[selected_table])
    st.download_button(
        label=f"Download table {selected_table+1} as CSV",
        data=dfs[selected_table].to_csv(index=False).encode(),
        file_name=f"table_{selected_table}.csv",
        mime="text/csv",
    )

    if st.button("Generate a python code"):
        # df_concatenated = pd.concat(dfs[selected_table])
        data_dict = dfs[selected_table].to_dict()
        code_gen = f'''import pandas as pd
df = pd.DataFrame.from_dict({data_dict})
print(df)'''
        st.code(code_gen, language="python")

    st.write("----")

    with st.expander("See all tables"):
        for i, df in enumerate(dfs):
            st.write(f"### Table {i}")
            st.write(df)

    all_tables_df = pd.concat(dfs)

    csv_data = all_tables_df.to_csv(index=False).encode()
    st.download_button(
        label="Download all tables as CSV",
        data=csv_data,
        file_name="all_tables.csv",
        mime="text/csv",
    )

    # dfs[0].to_csv("first_table.csv")

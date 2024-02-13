import streamlit as st
import pandas as pd
import numpy as np
import pandas as pd
import fitz  # PyMuPDF
import pdf2image
from datetime import date
import random
def calculate_statistics(scores):
    mean = scores.mean()
    median = scores.median()
    mode = scores.mode()[0] if not scores.mode().empty else None
    _range = scores.max() - scores.min()
    return mean, median, mode, _range

def main():
    st.set_page_config(layout="wide")
    st.title("Marking App")

    # Sidebar
    st.sidebar.header("Settings")
    pdf1_path = st.sidebar.file_uploader("Upload Student Answer PDF 1", type=["pdf"])
    start_page_pdf1 = st.sidebar.number_input("Start Page - PDF 1", min_value=0, value=0)
    pdf2_path = st.sidebar.file_uploader("Upload Student Answer PDF 2", type=["pdf"])
    start_page_pdf2 = st.sidebar.number_input("Start Page - PDF 2", min_value=0, value=0)
    solution_pdf_path = st.sidebar.file_uploader("Upload Solution PDF", type=["pdf"])
    start_page_solution_pdf = st.sidebar.number_input("Start Page - Solution PDF", min_value=0, value=0)

    export_format = st.sidebar.selectbox("Export Format", ["CSV", "Markdown"])
    export_path = st.sidebar.text_input("Export Path")
    students = st.sidebar.text_area("Students (comma-separated)").split(',')
    num_mcq = int(st.sidebar.number_input("Number of MCQ"))
    num_short_answer = int(st.sidebar.number_input("Number of Short Answer"))

    # Main content
    if pdf1_path and pdf2_path and solution_pdf_path:

        # Load PDFs
        st.subheader("PDF Viewer")

        pdf1 = fitz.open(stream=pdf1_path.read(), filetype="pdf")
        pdf2 = fitz.open(stream=pdf2_path.read(), filetype="pdf")
        solution_pdf = fitz.open(stream=solution_pdf_path.read(), filetype="pdf")

        pdf1_path.seek(0, 0)
        images_pdf1 = pdf2image.convert_from_bytes(pdf1_path.read(), poppler_path=r'poppler-23.11.0/Library/bin')
        pdf2_path.seek(0, 0)
        images_pdf2 = pdf2image.convert_from_bytes(pdf2_path.read(), poppler_path=r'poppler-23.11.0/Library/bin')
        solution_pdf_path.seek(0, 0)
        images_solution_pdf = pdf2image.convert_from_bytes(solution_pdf_path.read(), poppler_path=r'poppler-23.11.0/Library/bin')

        max_pages = max(len(images_pdf1), len(images_pdf2), len(images_solution_pdf))
        min_pages = 0

        page_number = st.slider("Select Page", min_value=min_pages, max_value=max_pages-1, value=min_pages)

        st.subheader(f"Page {page_number}")

        columns = st.columns(3)

        with columns[0]:
            if page_number + start_page_pdf1 < len(images_pdf1):
                st.image(images_pdf1[page_number + start_page_pdf1], use_column_width=True, caption="Student 1 Answer")

        with columns[1]:
            if page_number + start_page_pdf2 < len(images_pdf2):
                st.image(images_pdf2[page_number + start_page_pdf2], use_column_width=True, caption="Student 2 Answer")

        with columns[2]:
            if page_number + start_page_solution_pdf < len(images_solution_pdf):
                st.image(images_solution_pdf[page_number + start_page_solution_pdf], use_column_width=True, caption="Solution")

        # Marking Table
        @st.cache_data
        def get_profile_dataset(number_of_items: int = 100, seed: int = 0) -> pd.DataFrame:
            new_data = []

            def calculate_age(born):
                today = date.today()
                return (
                    today.year - born.year - ((today.month, today.day) < (born.month, born.day))
                )

            from faker import Faker

            fake = Faker()
            random.seed(seed)
            Faker.seed(seed)

            for i in range(number_of_items):
                profile = fake.profile()
                new_data.append(
                    {
                        "avatar": f"https://picsum.photos/400/200?lock={i}",
                        "name": profile["name"],
                        "age": calculate_age(profile["birthdate"]),
                        "active": random.choice([True, False]),
                        "daily_activity": np.random.rand(25),
                        "homepage": profile["website"][0],
                        "email": profile["mail"],
                        "activity": np.random.randint(2, 90, size=25),
                        "gender": random.choice(["male", "female", "other", None]),
                        "birthdate": profile["birthdate"],
                        "status": round(random.uniform(0, 1), 2),
                    }
                )

            profile_df = pd.DataFrame(new_data)
            profile_df["gender"] = profile_df["gender"].astype("category")
            return profile_df


        column_configuration = {
            "name": st.column_config.TextColumn(
                "Name", help="The name of the user", max_chars=100
            ),
            "avatar": st.column_config.ImageColumn("Avatar", help="The user's avatar"),
            "active": st.column_config.CheckboxColumn("Is Active?", help="Is the user active?"),
            "homepage": st.column_config.LinkColumn(
                "Homepage", help="The homepage of the user"
            ),
            "gender": st.column_config.SelectboxColumn(
                "Gender", options=["male", "female", "other"]
            ),
            "age": st.column_config.NumberColumn(
                "Age",
                min_value=0,
                max_value=120,
                format="%d years",
                help="The user's age",
            ),
            "activity": st.column_config.LineChartColumn(
                "Activity (1 year)",
                help="The user's activity over the last 1 year",
                width="large",
                y_min=0,
                y_max=100,
            ),
            "daily_activity": st.column_config.BarChartColumn(
                "Activity (daily)",
                help="The user's activity in the last 25 days",
                width="medium",
                y_min=0,
                y_max=1,
            ),
            "status": st.column_config.ProgressColumn(
                "Status", min_value=0, max_value=1, format="%.2f"
            ),
            "birthdate": st.column_config.DateColumn(
                "Birthdate",
                help="The user's birthdate",
                min_value=date(1920, 1, 1),
            ),
            "email": st.column_config.TextColumn(
                "Email",
                help="The user's email address",
                validate="^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$",
            ),
        }

        st.data_editor(
            get_profile_dataset(),
            column_config=column_configuration,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
        )

if __name__ == "__main__":
    main()

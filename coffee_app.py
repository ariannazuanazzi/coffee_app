import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image, ImageDraw, ImageFont
import io

# ====== GOOGLE SHEET SETUP ======
# Replace this with your Google Sheet ID from the URL
SPREADSHEET_ID = "1s59BNzyB6QPHwE8B1bRlcyW40XBlQUnYrR37DWqJE6M"

# Google Sheets API scope
SCOPE = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

# ----------------- SECRETS -----------------
# Load credentials JSON from Streamlit Secrets
creds_json = st.secrets["GSPREAD_CREDS"]
creds_dict = json.loads(creds_json)

# Authorize
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
client = gspread.authorize(creds)

# Load spreadsheet ID from Secrets
SPREADSHEET_ID = st.secrets["SPREADSHEET_ID"]
sheet = client.open_by_key(SPREADSHEET_ID)


# ====== Load / Save Functions ======
def load_df(tab_name):
    worksheet = sheet.worksheet(tab_name)
    data = worksheet.get_all_records()
    if data:
        return pd.DataFrame(data)
    else:
        return pd.DataFrame()

def save_df(df, tab_name):
    worksheet = sheet.worksheet(tab_name)
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

# Load all tabs
df_brewing = load_df("Brewing")
df_tasting = load_df("Tasting")
df_notes = load_df("Notes")

# ====== STREAMLIT APP ======
st.set_page_config(page_title="Coffee App", layout="centered")
st.title("☕ Coffee App")


# ----------------------------
# Tabs
# ----------------------------
tabs = st.tabs(["☕ Coffee Brewing", "🌟 Coffee Tasting", "📝 Coffee Notes"])

# ----------------------------
# COFFEE BREWING
# ----------------------------
with tabs[0]:
    st.header("🧾 Coffee Brewing")

    if "brewing_data" not in st.session_state:
        st.session_state.brewing_data = {}
        st.session_state.brewing_submitted = False

    with st.form("brewing_form"):
        bean = st.text_input("Bean Name", value=st.session_state.brewing_data.get("Bean", ""))
        roaster = st.text_input("Roaster", value=st.session_state.brewing_data.get("Roaster", ""))
        method = st.selectbox(
            "Brew Method",
            ["V60","Aeropress","French Press","Espresso","Moka Pot","Other"],
            index=["V60","Aeropress","French Press","Espresso","Moka Pot","Other"].index(
                st.session_state.brewing_data.get("Method","V60")
            )
        )
        coffee_g = st.number_input("Coffee (grams)", 0.0, 100.0, value=st.session_state.brewing_data.get("Coffee (g)", 18.0))
        water_ml = st.number_input("Water (ml)", 0.0, 1000.0, value=st.session_state.brewing_data.get("Water (ml)", 250.0))
        aroma = st.slider("Aroma", 0, 10, value=st.session_state.brewing_data.get("Aroma",5))
        body = st.slider("Body", 0, 10, value=st.session_state.brewing_data.get("Body",5))
        sweetness = st.slider("Sweetness", 0, 10, value=st.session_state.brewing_data.get("Sweetness",5))
        acidity = st.slider("Acidity", 0, 10, value=st.session_state.brewing_data.get("Acidity",5))
        balance = st.slider("Balance", 0, 10, value=st.session_state.brewing_data.get("Balance",5))
        notes = st.text_area("Notes / Observations", value=st.session_state.brewing_data.get("Notes",""))

        submitted = st.form_submit_button("Save Brewing Entry")
        if submitted:
            st.session_state.brewing_data = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Bean": bean,
                "Roaster": roaster,
                "Method": method,
                "Coffee (g)": coffee_g,
                "Water (ml)": water_ml,
                "Aroma": aroma,
                "Body": body,
                "Sweetness": sweetness,
                "Acidity": acidity,
                "Balance": balance,
                "Notes": notes
            }
            df_brewing = pd.concat([df_brewing, pd.DataFrame([st.session_state.brewing_data])], ignore_index=True)
            save_df(df_brewing, "Brewing")
            st.session_state.brewing_submitted = True

    if st.session_state.brewing_submitted:
        st.markdown("---")
        st.markdown("### ☕ Your Coffee Brew Entry")
        for key, value in st.session_state.brewing_data.items():
            if key not in ['Aroma','Body','Sweetness','Acidity','Balance']:
                st.markdown(f"**{key}:** {value}")

        labels = ['Aroma','Body','Sweetness','Acidity','Balance']
        values = [st.session_state.brewing_data[l] for l in labels]
        values += values[:1]
        angles = np.linspace(0,2*np.pi,len(labels), endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(4,4), subplot_kw=dict(polar=True))
        ax.fill(angles, values, color='peru', alpha=0.25)
        ax.plot(angles, values, color='saddlebrown', linewidth=2)
        ax.set_yticks(range(0,11,2))
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)
        ax.set_title("Taste Wheel", pad=15)
        st.pyplot(fig)

        if st.button("➕ Add Another Brewing Entry"):
            st.session_state.brewing_data = {}
            st.session_state.brewing_submitted = False

# ----------------------------
# COFFEE TASTING
# ----------------------------
with tabs[1]:
    st.header("🌟 Coffee Tasting")

    if "tasting_data" not in st.session_state:
        st.session_state.tasting_data = {}
        st.session_state.tasting_submitted = False

    with st.form("tasting_form"):
        cafe = st.text_input("Cafe Name", value=st.session_state.tasting_data.get("Cafe",""))
        coffee_type = st.text_input("Coffee Type", value=st.session_state.tasting_data.get("Coffee Type",""))
        tasting_notes = st.text_area("Notes", value=st.session_state.tasting_data.get("Notes",""))
        photos = st.file_uploader("Upload Photos", accept_multiple_files=True, type=["png","jpg","jpeg"])

        submitted = st.form_submit_button("Save Tasting Entry")
        if submitted:
            photo_names = [photo.name for photo in photos] if photos else []
            st.session_state.tasting_data = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Cafe": cafe,
                "Coffee Type": coffee_type,
                "Notes": tasting_notes,
                "Photos": photo_names,
                "PhotoFiles": photos  # store actual file objects
            }
            df_tasting = pd.concat([df_tasting, pd.DataFrame([st.session_state.tasting_data])], ignore_index=True)
            save_df(df_tasting, "Tasting")
            st.session_state.tasting_submitted = True

    if st.session_state.tasting_submitted:
        st.markdown("---")
        st.markdown("### 🌟 Your Coffee Tasting Entry")
        st.markdown(f"**Cafe:** {st.session_state.tasting_data['Cafe']}")
        st.markdown(f"**Coffee Type:** {st.session_state.tasting_data['Coffee Type']}")
        st.markdown(f"**Notes:** {st.session_state.tasting_data['Notes']}")

        if "PhotoFiles" in st.session_state.tasting_data:
            st.markdown("**Photos:**")
            for photo_file in st.session_state.tasting_data["PhotoFiles"]:
                pil_img = Image.open(photo_file)
                st.image(pil_img, width=200)

        # ====== Create downloadable card ======
        card_width, card_height = 500, 600
        card_img = Image.new("RGB", (card_width, card_height), color="white")
        draw = ImageDraw.Draw(card_img)
        y_offset = 20
        line_height = 40

        draw.text((20, y_offset), f"Cafe: {st.session_state.tasting_data['Cafe']}", fill="black")
        y_offset += line_height
        draw.text((20, y_offset), f"Coffee Type: {st.session_state.tasting_data['Coffee Type']}", fill="black")
        y_offset += line_height
        draw.text((20, y_offset), f"Notes: {st.session_state.tasting_data['Notes']}", fill="black")
        y_offset += line_height + 20

        if "PhotoFiles" in st.session_state.tasting_data and st.session_state.tasting_data["PhotoFiles"]:
            pil_img = Image.open(st.session_state.tasting_data["PhotoFiles"][0])
            pil_img.thumbnail((card_width-40, 300))
            card_img.paste(pil_img, (20, y_offset))

        buf = io.BytesIO()
        card_img.save(buf, format="PNG")
        buf.seek(0)

        st.download_button(
            label="📥 Download Tasting Card",
            data=buf,
            file_name=f"{st.session_state.tasting_data['Cafe'].replace(' ','_')}_card.png",
            mime="image/png"
        )

        if st.button("➕ Add Another Tasting Entry"):
            st.session_state.tasting_data = {}
            st.session_state.tasting_submitted = False


# ----------------------------
# COFFEE NOTES
# ----------------------------
with tabs[2]:
    st.header("📝 Coffee Notes")

    if "note_data" not in st.session_state:
        st.session_state.note_data = {}
        st.session_state.note_submitted = False

    with st.form("notes_form"):
        note_title = st.text_input("Title", value=st.session_state.note_data.get("Title",""))
        note_text = st.text_area("Write your note", value=st.session_state.note_data.get("Note",""))
        submitted = st.form_submit_button("Save Note")
        if submitted:
            st.session_state.note_data = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Title": note_title,
                "Note": note_text
            }
            df_notes = pd.concat([df_notes, pd.DataFrame([st.session_state.note_data])], ignore_index=True)
            save_df(df_notes, "Notes")
            st.session_state.note_submitted = True

    if st.session_state.note_submitted:
        st.success("✅ Note saved! You can add another note below.")
        if st.button("➕ Add Another Note"):
            st.session_state.note_data = {}
            st.session_state.note_submitted = False

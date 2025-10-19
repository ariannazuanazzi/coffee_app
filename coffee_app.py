import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ====== GOOGLE SHEET SETUP ======
SCOPE = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
CREDS_FILE = "credentials.json"  # your Google service account credentials file
SHEET_NAME = "Coffee_App"        # your Google Sheet name

creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME)

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

choice = st.radio("Select what you want to do:", ["Coffee Brewing", "Coffee Tasting", "Coffee Notes"])

# ----------------------------
# COFFEE BREWING
# ----------------------------
if choice == "Coffee Brewing":
    st.header("🧾 Coffee Brewing")

    bean = st.text_input("Bean Name")
    roaster = st.text_input("Roaster")
    method = st.selectbox("Brew Method", ["V60","Aeropress","French Press","Espresso","Moka Pot","Other"])
    coffee_g = st.number_input("Coffee (grams)", 0.0, 100.0, 18.0)
    water_ml = st.number_input("Water (ml)", 0.0, 1000.0, 250.0)
    aroma = st.slider("Aroma", 0, 10, 5)
    body = st.slider("Body", 0, 10, 5)
    sweetness = st.slider("Sweetness", 0, 10, 5)
    acidity = st.slider("Acidity", 0, 10, 5)
    balance = st.slider("Balance", 0, 10, 5)
    notes = st.text_area("Notes / Observations")

    if st.button("Save Brewing Entry"):
        new_row = {
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
        df_brewing = pd.concat([df_brewing, pd.DataFrame([new_row])], ignore_index=True)
        save_df(df_brewing, "Brewing")
        st.success("✅ Brewing entry saved!")

        # ====== CARD DISPLAY ======
        with st.container():
            st.markdown("---")
            st.markdown("### ☕ Your Coffee Brew Entry")
            st.markdown(f"**Bean:** {bean}")
            st.markdown(f"**Roaster:** {roaster}")
            st.markdown(f"**Method:** {method}")
            st.markdown(f"**Coffee (g):** {coffee_g}")
            st.markdown(f"**Water (ml):** {water_ml}")
            st.markdown(f"**Notes:** {notes}")

            # Radar chart
            labels = ['Aroma', 'Body', 'Sweetness', 'Acidity', 'Balance']
            values = [aroma, body, sweetness, acidity, balance]
            values += values[:1]
            angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
            angles += angles[:1]

            fig, ax = plt.subplots(figsize=(4,4), subplot_kw=dict(polar=True))
            ax.fill(angles, values, color='peru', alpha=0.25)
            ax.plot(angles, values, color='saddlebrown', linewidth=2)
            ax.set_yticks(range(0,11,2))
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels)
            ax.set_title("Taste Wheel", pad=15)
            st.pyplot(fig)

# ----------------------------
# COFFEE TASTING
# ----------------------------
elif choice == "Coffee Tasting":
    st.header("🌟 Coffee Tasting")

    cafe = st.text_input("Cafe Name")
    coffee_type = st.text_input("Coffee Type")
    tasting_notes = st.text_area("Notes")
    photos = st.file_uploader("Upload Photos", accept_multiple_files=True, type=["png","jpg","jpeg"])

    if st.button("Save Tasting Entry"):
        photo_names = [photo.name for photo in photos] if photos else []
        new_row = {
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Cafe": cafe,
            "Coffee Type": coffee_type,
            "Notes": tasting_notes,
            "Photos": ", ".join(photo_names)
        }
        df_tasting = pd.concat([df_tasting, pd.DataFrame([new_row])], ignore_index=True)
        save_df(df_tasting, "Tasting")
        st.success("✅ Tasting entry saved!")

        # ====== CARD DISPLAY ======
        with st.container():
            st.markdown("---")
            st.markdown("### 🌟 Your Coffee Tasting Entry")
            st.markdown(f"**Cafe:** {cafe}")
            st.markdown(f"**Coffee Type:** {coffee_type}")
            st.markdown(f"**Notes:** {tasting_notes}")

            if photos:
                st.markdown("**Photos:**")
                for photo in photos:
                    st.image(photo, width=200)

# ----------------------------
# COFFEE NOTES
# ----------------------------
elif choice == "Coffee Notes":
    st.header("📝 Coffee Notes")
    note_text = st.text_area("Write your note")

    if st.button("Save Note"):
        new_row = {"Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Note": note_text}
        df_notes = pd.concat([df_notes, pd.DataFrame([new_row])], ignore_index=True)
        save_df(df_notes, "Notes")
        st.success("✅ Note saved!")

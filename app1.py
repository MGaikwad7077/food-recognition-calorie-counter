import streamlit as st
import requests
import pandas as pd
import base64

# Clarifai API key
API_KEY = "909b717649c44532b04dd6717c12b877"

# Clarifai Food Model endpoint
MODEL_URL = "https://api.clarifai.com/v2/models/food-item-recognition/outputs"

# Load custom nutrition data
nutrition_df = pd.read_csv("nutrition_data.csv")

# Page config
st.set_page_config(page_title="Food Recognition Calorie Counter", layout="centered")

# Theme toggle
dark_mode = st.toggle("🌙 Dark Mode")

# Inject CSS based on theme
if dark_mode:
    st.markdown(
        """
        <style>
        .stApp, body {
            background-color: #121212;
            color: #E0E0E0;
        }
        .stButton>button {
            background-color: #333333;
            color: #E0E0E0;
            border-radius: 8px;
        }
        .stButton>button:hover {
            background-color: #444444;
        }
        input, .stNumberInput input, .stTextInput>div>input {
            background-color: #1E1E1E !important;
            color: #E0E0E0 !important;
            border: 1px solid #333333 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        .stApp, body {
            background-color: #FFFFFF;
            color: #000000;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: #FFFFFF;
            border-radius: 8px;
        }
        .stButton>button:hover {
            background-color: #45A049;
        }
        input, .stNumberInput input, .stTextInput>div>input {
            background-color: #F0F0F0 !important;
            color: #000000 !important;
            border: 1px solid #CCCCCC !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.title("🍕 Food Recognition & Calorie Counter")

# Image upload
uploaded_file = st.file_uploader("Upload a food image", type=["jpg", "jpeg", "png"])
if not uploaded_file:
    st.info("Please upload an image to begin.")
else:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    # Encode image
    image_bytes = uploaded_file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # Call Clarifai
    headers = {"Authorization": f"Key {API_KEY}"}
    payload = {
        "inputs": [
            {"data": {"image": {"base64": image_base64}}}
        ]
    }
    resp = requests.post(MODEL_URL, json=payload, headers=headers)

    if resp.status_code != 200:
        st.error(f"❌ Clarifai API error: {resp.status_code}")
    else:
        concepts = resp.json()["outputs"][0]["data"]["concepts"]
        # Take top concept
        food_name = concepts[0]["name"]
        st.success(f"Detected: **{food_name.title()}**")

        # Lookup nutrition
        match = nutrition_df[nutrition_df["food_name"].str.lower() == food_name.lower()]
        if match.empty:
            st.warning(f"⚠️ '{food_name}' not in database.")
        else:
            # Inputs
            qty = st.number_input(f"Enter quantity of {food_name.title()} (g)", min_value=0)
            if qty > 0:
                cal = match["calories_per_100g"].iloc[0]
                prot = match["protein_per_100g"].iloc[0]
                fat = match["fat_per_100g"].iloc[0]
                carbs = match["carbs_per_100g"].iloc[0]

                st.write(f"**Nutrients for {qty}g of {food_name.title()}:**")
                st.write(f"• Calories: **{(qty/100)*cal:.2f} kcal**")
                st.write(f"• Protein: **{(qty/100)*prot:.2f} g**")
                st.write(f"• Fat: **{(qty/100)*fat:.2f} g**")
                st.write(f"• Carbs: **{(qty/100)*carbs:.2f} g**")

import streamlit as st
import requests
import pandas as pd
import base64
import random

API_KEY = "909b717649c44532b04dd6717c12b877"
MODEL_URL = "https://api.clarifai.com/v2/models/food-item-recognition/outputs"

nutrition_df = pd.read_csv("nutrition_data.csv")

# Health quotes for pop-up
health_quotes = [
    "🍎 Eating healthy is a form of self-respect.",
    "💪 A healthy outside starts from the inside.",
    "🌿 Good health is not something we can buy. However, it can be an extremely valuable savings account.",
    "🥗 Health is the greatest gift, contentment the greatest wealth, faithfulness the best relationship.",
    "🏃‍♂️ Take care of your body, it’s the only place you have to live.",
    "💧 Eat to live, don’t live to eat."
]

# Pick a random quote
quote = random.choice(health_quotes)

st.set_page_config(page_title="🍱 Food Recognition Calorie Counter", layout="centered")
st.title("🍱💪Food Recognition Calorie Couter")

# Toggle for dark mode
dark_mode = st.toggle("🌙 Dark Mode")

# Responsive and dark/light mode styling
base_style = """
    <style>
    html, body, .stApp {
        font-family: 'Segoe UI', sans-serif;
        padding: 0;
        margin: 0;
        transition: all 0.3s ease;
    }
    .stButton>button, .stFileUploader {
        border-radius: 10px;
        padding: 10px 16px;
        font-size: 16px;
    }
    .stNumberInput input, .stTextInput>div>input {
        border-radius: 8px !important;
        padding: 10px !important;
    }
    @media (max-width: 768px) {
        .stButton>button {
            font-size: 14px;
        }
        .stFileUploader {
            width: 100%;
        }
    }
    </style>
"""

dark_style = """
    <style>
    .stApp, body {
        background-color: #121313;
        color: #00C2FF;
    }
    h1, h2, h3, h4, h5, h6, label, .css-10trblm, .css-hxt7ib {
        color: #00FFAB !important;
    }
    .stButton>button {
        background-color: #333333;
        color: #E0E0E0;
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
"""

light_style = """
    <style>
    .stApp, body {
        background-color: #FFF5F7;
        color: #4B2E2E;
        font-family: 'Segoe UI', sans-serif;
    }

    h1, h2, h3, h4, h5, h6, label {
        color: #A14A4A;
    }

    .stButton>button {
        background-color: #F4978E;
        color: #ffffff;
        border-radius: 12px;
        padding: 10px 20px;
        font-weight: bold;
        border: none;
        transition: 0.3s ease;
        box-shadow: 0 4px 8px rgba(244, 151, 142, 0.3);
    }

    .stButton>button:hover {
        background-color: #F08080;
        box-shadow: 0 6px 12px rgba(244, 128, 128, 0.4);
    }

    input, .stNumberInput input, .stTextInput>div>input {
        background-color: #FFEAEA !important;
        color: #4B2E2E !important;
        border: 1px solid #F7A1A1 !important;
        border-radius: 10px !important;
        padding: 12px !important;
        font-size: 16px;
    }

    .stFileUploader {
        background-color: #FFF0F2;
        border: 2px dashed #F7A1A1;
        padding: 16px;
        border-radius: 12px;
        transition: 0.3s ease;
    }

    .stFileUploader:hover {
        background-color: #FFE5E9;
        border-color: #F4978E;
    }

    .stAlert {
        border-radius: 10px;
        padding: 10px 15px;
        font-weight: 500;
    }
    </style>
"""

st.markdown(base_style, unsafe_allow_html=True)
st.markdown(dark_style if dark_mode else light_style, unsafe_allow_html=True)

# Show health quote
st.markdown(f"**💬 {quote}**")

# Mode Selection
mode = st.radio("Choose Mode", ("Image Recognition", "Manual Input", "BMI Calculator"))

# Functions for each mode
def bmi_calculator():
    def calculate_bmi(weight, height):
        return weight / (height ** 2)

    st.title("BMI Calculator")
    
    # Get user inputs for weight and height
    weight = st.number_input("Enter your weight (kg)", min_value=1.0, step=0.1)
    height = st.number_input("Enter your height (m)", min_value=0.5, step=0.01)
    
    # Calculate BMI if inputs are provided
    if weight > 0 and height > 0:
        bmi = calculate_bmi(weight, height)
        st.write(f"Your BMI is: {bmi:.2f}")
        
        # Categorize the result
        if bmi < 18.5:
            st.write("Category: Underweight")
        elif 18.5 <= bmi < 24.9:
            st.write("Category: Normal weight")
        elif 25 <= bmi < 29.9:
            st.write("Category: Overweight")
        else:
            st.write("Category: Obese")

def manual_input_mode():
    food_name = st.text_input("Enter the food item", "").strip()

    if food_name:
        match = nutrition_df[nutrition_df["food_name"].str.lower() == food_name.lower()]

        if match.empty:
            st.warning(f"⚠️ '{food_name}' not found in the database.")
        else:
            qty = st.number_input(f"Enter quantity of {food_name.title()} (g)", min_value=0)
            if qty > 0:
                cal = match["calories_per_100g"].iloc[0]
                prot = match["protein_per_100g"].iloc[0]
                fat = match["fat_per_100g"].iloc[0]
                carbs = match["carbs_per_100g"].iloc[0]

                st.markdown(f"### Nutrients for {qty}g of {food_name.title()}:")
                st.write(f"• **Calories**: {(qty/100)*cal:.2f} kcal")
                st.write(f"• **Protein**: {(qty/100)*prot:.2f} g")
                st.write(f"• **Fat**: {(qty/100)*fat:.2f} g")
                st.write(f"• **Carbs**: {(qty/100)*carbs:.2f} g")

def image_recognition_mode():
    uploaded_file = st.file_uploader("Upload a food image", type=["jpg", "jpeg", "png"])
    
    if not uploaded_file:
        st.info("📷 Please upload an image of a single food batch to begin.")
    else:
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

        image_bytes = uploaded_file.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

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
            food_name = concepts[0]["name"]
            st.success(f"✅ Detected: **{food_name.title()}**")

            match = nutrition_df[nutrition_df["food_name"].str.lower() == food_name.lower()]
            if match.empty:
                st.warning(f"⚠️ '{food_name}' not in database.")
            else:
                qty = st.number_input(f"Enter quantity of {food_name.title()} (g)", min_value=0)
                if qty > 0:
                    cal = match["calories_per_100g"].iloc[0]
                    prot = match["protein_per_100g"].iloc[0]
                    fat = match["fat_per_100g"].iloc[0]
                    carbs = match["carbs_per_100g"].iloc[0]

                    st.markdown(f"### Nutrients for {qty}g of {food_name.title()}:")
                    st.write(f"• **Calories**: {(qty/100)*cal:.2f} kcal")
                    st.write(f"• **Protein**: {(qty/100)*prot:.2f} g")
                    st.write(f"• **Fat**: {(qty/100)*fat:.2f} g")
                    st.write(f"• **Carbs**: {(qty/100)*carbs:.2f} g")

# Call the function based on selected mode
if mode == "BMI Calculator":
    bmi_calculator()
elif mode == "Manual Input":
    manual_input_mode()
else:
    image_recognition_mode()

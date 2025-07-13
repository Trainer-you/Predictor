import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import numpy as np
import os

CSV_FILE = "data.csv"

# Load previous data if exists
if os.path.exists(CSV_FILE):
    df_all = pd.read_csv(CSV_FILE)
else:
    df_all = pd.DataFrame(columns=["A", "B", "C", "Winner"])

st.set_page_config(page_title="Pot Type Predictor", layout="centered")
st.title("🎯 Next Round Pot Type Predictor (Top 2)")
st.markdown("🔮 Predict the most likely winning **two pot types** using last 10 rounds.")

# Form to enter new round
st.subheader("➕ Enter New Round")
with st.form("round_form"):
    pot_a = st.number_input("Pot A", min_value=0, step=1)
    pot_b = st.number_input("Pot B", min_value=0, step=1)
    pot_c = st.number_input("Pot C", min_value=0, step=1)
    winner = st.selectbox("Winning Chair", ["A", "B", "C"])
    add_btn = st.form_submit_button("Add Round")

if add_btn:
    new_row = pd.DataFrame([{
        "A": pot_a, "B": pot_b, "C": pot_c, "Winner": winner
    }])
    df_all = pd.concat([df_all, new_row], ignore_index=True)
    df_all.to_csv(CSV_FILE, index=False)
    st.success("✅ Round added successfully!")

# Show full history
if not df_all.empty:
    st.subheader("📋 Full Round History")
    st.dataframe(df_all, use_container_width=True)

    # Only proceed if enough rounds
    if len(df_all) >= 10:
        df = df_all.tail(10).copy()

        def get_pot_type(row):
            pots = {"A": row["A"], "B": row["B"], "C": row["C"]}
            sorted_pots = sorted(pots.items(), key=lambda x: x[1])
            rank_map = {
                sorted_pots[0][0]: "Low",
                sorted_pots[1][0]: "Mid",
                sorted_pots[2][0]: "High"
            }
            return rank_map[row["Winner"]]

        df["WinnerPotType"] = df.apply(get_pot_type, axis=1)

        # Prepare training data
        X, y = [], []
        for i in range(len(df) - 3):
            seq = df["WinnerPotType"].iloc[i:i+3].tolist()
            target = df["WinnerPotType"].iloc[i+3]
            X.append(seq)
            y.append(target)

        if len(X) > 0:
            le = LabelEncoder()
            le.fit(["Low", "Mid", "High"])  # Ensure all pot types are known

            X_enc = [le.transform(x) for x in X]
            y_enc = le.transform(y)

            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_enc, y_enc)

            last_seq = df["WinnerPotType"].iloc[-3:].tolist()
            last_seq_enc = le.transform(last_seq).reshape(1, -1)

            proba = model.predict_proba(last_seq_enc)[0]
            top2_idx = np.argsort(proba)[-2:][::-1]

            if len(top2_idx) >= 2:
                top2_labels = le.inverse_transform(top2_idx)
                combo = f"{top2_labels[0]} & {top2_labels[1]}"
                st.subheader("🔮 Prediction")
                st.success(f"🎯 **Likely winner pot types: {combo.upper()}**")
            else:
                st.warning("⚠️ Not enough confidence to predict top 2 pot types.")
        else:
            st.warning("⚠️ Not enough sequences to train model.")
    else:
        st.info("ℹ️ Please enter at least 10 rounds to start prediction.")
else:
    st.info("👈 Enter rounds to begin.")
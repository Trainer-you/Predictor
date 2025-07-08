import streamlit as st
import pandas as pd

st.set_page_config(page_title="Teen Patti Predictor", layout="centered")
st.title("🃏 Teen Patti Chair Win Predictor")
st.markdown("Predict the next winning chair based on past 22+ rounds using smart logic.")

# Initialize round history
if "rounds" not in st.session_state:
    st.session_state.rounds = []

chairs = ["A", "B", "C"]

# Input Form
with st.form("round_form"):
    st.subheader("➕ Add Round Data")
    pot_a = st.number_input("Pot A (in thousands)", min_value=0, step=1, value=0)
    pot_b = st.number_input("Pot B (in thousands)", min_value=0, step=1, value=0)
    pot_c = st.number_input("Pot C (in thousands)", min_value=0, step=1, value=0)
    winner = st.selectbox("Winning Chair", options=chairs)
    submit = st.form_submit_button("Add Round")

if submit:
    new_round = {
        "Round": len(st.session_state.rounds) + 1,
        "A": pot_a,
        "B": pot_b,
        "C": pot_c,
        "Winner": winner,
    }
    st.session_state.rounds.append(new_round)
    st.success(f"✅ Round {new_round['Round']} added!")

# Show history
if st.session_state.rounds:
    df = pd.DataFrame(st.session_state.rounds)
    st.subheader("📊 Round History")
    st.dataframe(df, use_container_width=True)

    # Scoring logic function
    def calculate_scores(df):
        scores = {"A": 0, "B": 0, "C": 0}
        last_5 = df.tail(5)["Winner"].tolist()
        total_wins = df["Winner"].value_counts()

        for chair in scores.keys():
            scores[chair] += 5 - last_5.count(chair)  # reward underdogs
            if len(last_5) >= 1 and chair == last_5[-1]:
                scores[chair] -= 2  # punish repeat winners
            scores[chair] += max(0, 5 - total_wins.get(chair, 0))  # rare winner boost

            # Rotation bonus
            if len(last_5) >= 3:
                pattern = last_5[-3:]
                if pattern == ['A', 'B', 'C'] and chair == 'A':
                    scores[chair] += 2
                elif pattern == ['B', 'C', 'A'] and chair == 'B':
                    scores[chair] += 2
                elif pattern == ['C', 'A', 'B'] and chair == 'C':
                    scores[chair] += 2

            # Pot-based logic from last round
            last_pots = df.iloc[-1][["A", "B", "C"]]
            if df.iloc[-1][chair] == min(last_pots):
                scores[chair] += 2
            elif df.iloc[-1][chair] == sorted(last_pots)[1]:
                scores[chair] += 1

        return scores

    # Run prediction
    scores = calculate_scores(df)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_two = sorted_scores[:2]

    st.subheader("🔮 Prediction for Next Round")
    st.write("Based on current trends, the top predicted winning chairs are:")

    for idx, (chair, score) in enumerate(top_two, start=1):
        st.markdown(f"**{idx}. Chair {chair}** — Score: `{score}`")

else:
    st.info("Please add at least one round to begin predictions.")

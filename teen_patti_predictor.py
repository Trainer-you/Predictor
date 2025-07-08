# Updated Streamlit app code implementing features:
# 1. Explain prediction reasoning (Feature 7)
# 2. Allow repeated predictions (not forcing rotation)
# 3. Use only last 10 rounds for scoring

updated_app_code = """
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Teen Patti Predictor", layout="centered")
st.title("🃏 Teen Patti Chair Win Predictor (Enhanced)")
st.markdown("Smart prediction using recent 10 rounds with detailed explanation.")

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
        reasons = {chair: [] for chair in chairs}

        recent_df = df.tail(10)
        last_winners = recent_df["Winner"].tolist()
        total_wins = recent_df["Winner"].value_counts()

        for chair in chairs:
            # Reward if not winning much recently
            underdog_bonus = 5 - last_winners.count(chair)
            scores[chair] += underdog_bonus
            reasons[chair].append(f"+{underdog_bonus} for not winning much in last 10 rounds")

            # Slight penalty if won last round (repeat is allowed, but penalized slightly)
            if len(last_winners) >= 1 and chair == last_winners[-1]:
                scores[chair] -= 1
                reasons[chair].append("-1 for winning last round (repeat)")

            # Boost if total wins in recent 10 is very low
            rare_winner_bonus = max(0, 4 - total_wins.get(chair, 0))
            scores[chair] += rare_winner_bonus
            reasons[chair].append(f"+{rare_winner_bonus} for being rare winner")

            # Pattern-based rotation boost (no enforcement, just pattern matching)
            if len(last_winners) >= 3:
                pattern = last_winners[-3:]
                if pattern == ['A', 'B', 'C'] and chair == 'A':
                    scores[chair] += 2
                    reasons[chair].append("+2 for matching rotation pattern A→B→C→A")
                elif pattern == ['B', 'C', 'A'] and chair == 'B':
                    scores[chair] += 2
                    reasons[chair].append("+2 for matching rotation pattern B→C→A→B")
                elif pattern == ['C', 'A', 'B'] and chair == 'C':
                    scores[chair] += 2
                    reasons[chair].append("+2 for matching rotation pattern C→A→B→C")

            # Pot position bonus (low pot = better chance)
            last_pots = df.iloc[-1][["A", "B", "C"]]
            chair_pot = df.iloc[-1][chair]
            min_pot, max_pot = min(last_pots), max(last_pots)

            if chair_pot == min_pot:
                scores[chair] += 2
                reasons[chair].append("+2 for having lowest pot last round")
            elif chair_pot == sorted(last_pots)[1]:
                scores[chair] += 1
                reasons[chair].append("+1 for having medium pot last round")

        return scores, reasons

    # Run prediction
    scores, reasons = calculate_scores(df)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_two = sorted_scores[:2]

    st.subheader("🔮 Prediction for Next Round")
    st.write("Top predicted winning chairs (based on last 10 rounds):")
    for idx, (chair, score) in enumerate(top_two, start=1):
        st.markdown(f"**{idx}. Chair {chair}** — Score: `{score}`")
        with st.expander(f"🔎 Why Chair {chair}?"):
            for reason in reasons[chair]:
                st.write(f"- {reason}")

else:
    st.info("Please add at least one round to begin predictions.")
"""

updated_app_code

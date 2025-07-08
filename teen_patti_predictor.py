import streamlit as st

# Initialize session state
if 'rounds' not in st.session_state:
    st.session_state.rounds = []

chairs = ['A', 'B', 'C']

def next_chair(chair):
    return chairs[(chairs.index(chair) + 1) % len(chairs)]

def predict_next_winner(rounds):
    if len(rounds) < 3:
        return "Not enough data to predict"

    last_winners = [r['winner'] for r in rounds[-3:]]
    last_winner = last_winners[-1]

    if last_winners[-1] == last_winners[-2]:
        predicted = next_chair(last_winner)
    else:
        predicted = next_chair(last_winner)

    last_pots = rounds[-1]['pot']
    max_pot_chair = max(last_pots, key=last_pots.get)

    if last_pots[predicted] < 0.5 * last_pots[max_pot_chair]:
        predicted = max_pot_chair

    return predicted

st.title("Teen Patti Chair Win Predictor")

st.header("Add a New Round")

with st.form("round_form"):
    pot_A = st.number_input("Pot A (in thousands)", min_value=0, step=1)
    pot_B = st.number_input("Pot B (in thousands)", min_value=0, step=1)
    pot_C = st.number_input("Pot C (in thousands)", min_value=0, step=1)
    winner = st.selectbox("Winner Chair", chairs)
    submitted = st.form_submit_button("Add Round")

if submitted:
    round_number = len(st.session_state.rounds) + 1
    new_round = {
        'round': round_number,
        'pot': {'A': pot_A, 'B': pot_B, 'C': pot_C},
        'winner': winner
    }
    st.session_state.rounds.append(new_round)
    st.success(f"Round {round_number} added!")

if st.session_state.rounds:
    st.header("Rounds History")
    for r in st.session_state.rounds:
        st.write(f"Round {r['round']}: Pot A={r['pot']['A']}k, Pot B={r['pot']['B']}k, Pot C={r['pot']['C']}k → Winner: {r['winner']}")

    prediction = predict_next_winner(st.session_state.rounds)
    st.header("Prediction")
    st.write(f"🎯 Predicted next winning chair: **{prediction}**")

else:
    st.info("Add rounds above to start predictions.")

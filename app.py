import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.set_page_config(page_title="wen goat 🐐", page_icon=":goat:")
st.title("wen goat 🐐")

@st.cache_data
def fetch_user_id(callsign):
    url = f"https://sotl.as/api/activators/{callsign}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('userId')
    return None

def fetch_activations(user_id):
    # url = f"https://api-db.sota.org.uk/admin/activator_log_by_id?year=all&id={user_id}"
    url = f"https://api-db2.sota.org.uk/logs/activator/{user_id}/99999/0"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

def plot_progress(data, avg_points_per_week, target_points):
    df = pd.DataFrame(data)
    df['ActivationDate'] = pd.to_datetime(df['ActivationDate'])
    df.sort_values('ActivationDate', inplace=True)
    df['CumulativePoints'] = df['Total']

    plt.figure(figsize=(10, 6))
    plt.plot(df['ActivationDate'], df['CumulativePoints'], label='Current Progress', color='blue')

    # Extrapolation
    first_date = df['ActivationDate'].iloc[0]
    last_date = df['ActivationDate'].iloc[-1]
    last_total = df['CumulativePoints'].iloc[-1]

    weeks_of_activating = max((last_date - first_date).days // 7, 1)
    avg_points_per_week_calc = last_total / weeks_of_activating

    max_weeks_threshold = 5200  # ~100 years
    weeks_needed_input = max((target_points - last_total) / avg_points_per_week, 0)
    weeks_needed_input = min(weeks_needed_input, max_weeks_threshold)

    goal_date = last_date + timedelta(weeks=weeks_needed_input)
    future_dates = pd.date_range(start=datetime.now(), periods=int(weeks_needed_input) + 1, freq='W')
    future_points = [last_total + avg_points_per_week * i for i in range(len(future_dates))]
    plt.plot(future_dates, future_points, linestyle='--', color='red', label='Planned Progress')

    weeks_needed_linear = max((target_points - last_total) / avg_points_per_week_calc, 0)
    weeks_needed_linear = min(weeks_needed_linear, max_weeks_threshold)
    linear_goat_date = last_date + timedelta(weeks=weeks_needed_linear)
    future_dates_linear = pd.date_range(start=datetime.now(), periods=int(weeks_needed_linear) + 1, freq='W')
    future_points_linear = [last_total + avg_points_per_week_calc * i for i in range(len(future_dates_linear))]
    plt.plot(future_dates_linear, future_points_linear, linestyle=':', color='orange', label='Projected Progress (linear)')


    # Connect last_date of activation with nowdate
    plt.hlines(y=last_total,xmin=last_date,xmax=datetime.now(), color='blue')

    ylabels = []
    for milestone in range(1000, next_target + 1000, 1000):
        plt.axhline(milestone, color='grey', linestyle=':', alpha=0.5)
        ylabels.append(milestone)
    if last_total > 2000: # Only force milestone labels over 2000 points
        plt.yticks(ylabels)

    plt.axhline(target_points, color='green', linestyle=':', label=f'Next Milestone ({target_points} pts)')
    plt.vlines(x= datetime.now(),ymin=0,ymax=target_points, color='grey', linestyle=':', alpha=0.25) # Mark the nowdate
    plt.xlabel('Date')
    plt.ylabel('Cumulative Points')
    plt.legend()
    plt.title('SOTA Activation Progress')
    st.pyplot(plt)

    days_remaining = (goal_date - datetime.now()).days
    st.write(f"You have been activating for {weeks_of_activating} weeks with an average of {avg_points_per_week_calc:.2f} points per week.")
    st.write(f"At your current rate you'll reach {target_points} points by {linear_goat_date.strftime('%d %B %Y')}. Keep climbing! 🥾")
    st.write(f"At your selected rate you'll reach {target_points} points by {goal_date.strftime('%d %B %Y')}, or {days_remaining} days away. Keep climbing! 🥾")

# MAIN

callsign = st.text_input("Enter your callsign:").upper()

if callsign:
    user_id = fetch_user_id(callsign)
    if user_id:
        activations = fetch_activations(user_id)
        if activations:
            activations_sorted = sorted(activations, key=lambda x: x['ActivationDate'])
            total_points = activations_sorted[-1]['Total'] if activations_sorted else 0

            next_target = ((total_points // 1000) + 1) * 1000
            goat_emojis = '🐐' * (next_target // 1000)

            with st.container(border=True): # Put it in a container
                if next_target == 1000:
                    st.write(f"{callsign}, you have {total_points} points, only {next_target - total_points} to achieve Mountain Goat! 🐐")
                else:
                    st.write(f"{callsign}, you have {total_points} points, only {next_target - total_points} to go to your next Mountain Goat! {goat_emojis}")
                avg_points_per_week = st.number_input("Enter your expected average points per week:", min_value=0.0, value=5.0, format="%0.1f", step=0.1)
                plot_progress(activations, avg_points_per_week, next_target)

            with st.container(border=True): # Put it in a container
                st.subheader("Want goat now 🏔️")
                target_date = st.date_input("Select your target date to reach the next goat:", format="DD/MM/YYYY", value=None, min_value="today")
                if target_date:
                    today = datetime.now().date()
                    weeks_remaining = max((target_date - today).days / 7, 1)
                    points_needed = next_target - total_points
                    required_points_per_week = points_needed / weeks_remaining
                    st.write(f"You need to earn {required_points_per_week:.1f} points per week to reach {next_target} points by {target_date.strftime('%d %B %Y')}. Better get a move on!")
        else:
            st.error("No activation data found.")
    else:
        st.error("Invalid callsign or data not found.")

with st.expander("What is wen goat?", icon="ℹ️"):
    st.markdown('''
        A tool that analyses your SOTA (Summits on the Air) account
        and predicts the date and required time to reach Mountain Goat status.
        1000 activator points is the first milestone and rewarded with a 🐐 trophy.
        One needs to have logged at least 2 activations in the database for the tool to work.
        Tool designed by [GM5ALX](https://gm5alx.uk) and [contributors](https://github.com/alexjj/wen-goat/graphs/contributors).
    ''')

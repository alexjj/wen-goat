import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.set_page_config(page_title="wen goat 🐐")
st.title("wen goat 🐐")

@st.cache_data
def fetch_user_id(callsign):
    url = f"https://sotl.as/api/activators/{callsign}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('userId')
    return None

@st.cache_data
def fetch_activations(user_id):
    url = f"https://api-db.sota.org.uk/admin/activator_log_by_id?year=all&id={user_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

def plot_progress(data, avg_points_per_week):
    df = pd.DataFrame(data)
    df['ActivationDate'] = pd.to_datetime(df['ActivationDate'])
    df.sort_values('ActivationDate', inplace=True)
    df['CumulativePoints'] = df['Total']

    plt.figure(figsize=(10, 6))
    plt.plot(df['ActivationDate'], df['CumulativePoints'], label='Current Progress')

    # Extrapolation
    last_date = df['ActivationDate'].iloc[-1]
    last_total = df['CumulativePoints'].iloc[-1]
    weeks_needed = max((1000 - last_total) / avg_points_per_week, 0)
    goal_date = last_date + timedelta(weeks=weeks_needed)
    future_dates = pd.date_range(start=last_date, periods=int(weeks_needed) + 1, freq='W')
    future_points = [last_total + avg_points_per_week * i for i in range(len(future_dates))]
    plt.plot(future_dates, future_points, linestyle='--', color='red', label='Projected Progress')

    plt.axhline(1000, color='green', linestyle=':', label='Mountain Goat (1000 pts)')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Points')
    plt.legend()
    plt.title('SOTA Activation Progress')
    st.pyplot(plt)

    days_remaining = (goal_date - datetime.now()).days
    st.write(f"At your current rate you'll be mountain goat by {goal_date.strftime('%d %B %Y')}, or {days_remaining} days away. 🥾")

callsign = st.text_input("Enter your callsign:").upper()

if callsign:
    user_id = fetch_user_id(callsign)
    if user_id:
        activations = fetch_activations(user_id)
        if activations:
            activations_sorted = sorted(activations, key=lambda x: x['ActivationDate'])
            total_points = activations_sorted[-1]['Total'] if activations_sorted else 0
            st.write(f"{callsign}, you have {total_points} points, only {1000 - total_points} to go!")
            avg_points_per_week = st.number_input("Average points per week:", min_value=1, step=1, value=5)
            plot_progress(activations, avg_points_per_week)
        else:
            st.error("No activation data found.")
    else:
        st.error("Invalid callsign or data not found.")

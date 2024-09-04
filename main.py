import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Team Analysis App",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.streamlit.io/community',
        'Report a bug': "https://github.com/streamlit/streamlit/issues",
        'About': "# This is a football team analysis app!"
    }
)

def categorize_age(age):
    if age <= 21:
        return "U21"
    elif age <= 28:
        return "Peak (21-28)"
    elif age <= 32:
        return "Post-Peak (28-32)"
    else:
        return "Veteran"

def categorize_position(pos):
    if "Goalkeeper" in pos:
        return "GK"
    elif "Back" in pos:
        return "CB" if "Centre" in pos else "FB/WB"
    elif any(p in pos for p in ["Defensive Midfield", "Central Midfield"]):
        return "DM/CM"
    elif any(p in pos for p in ["Right Midfield", "Left Midfield"]):
        return "FB/WB"
    elif any(p in pos for p in ["Attacking Midfield", "Winger"]):
        return "AM/Winger"
    elif "Forward" in pos:
        return "FW"
    else:
        return "Other"

def get_contract_color(contract_date):
    if pd.isna(contract_date) or contract_date == '-':
        return "white"
    contract_year = int(contract_date.split('.')[-1])
    if contract_year == 2025:
        return "red"
    elif contract_year == 2026:
        return "#ffc733"
    elif contract_year >= 2027:
        return "green"
    else:
        return "white"

def position_with_most_players_over_30(team_data):
    over_30 = team_data[team_data['player_age'] > 30]
    position_counts = over_30['Position Group'].value_counts()
    return position_counts.index[0] if not position_counts.empty else "No players over 30"

def position_with_most_contracts_ending_2025(team_data):
    ending_2025 = team_data[team_data['contract_until'].str.contains('2025', na=False)]
    position_counts = ending_2025['Position Group'].value_counts()
    return position_counts.index[0] if not position_counts.empty else "No contracts ending in 2025"

def average_age_by_position(team_data):
    weighted_sum = team_data.groupby('Position Group').apply(lambda x: (x['player_age'] * x['minutes_played']).sum())
    total_minutes = team_data.groupby('Position Group')['minutes_played'].sum()
    weighted_avg = (weighted_sum / total_minutes).round(1)
    return weighted_avg

def main():
    st.title("Team Analysis App")

    # Load the CSV data
    df = pd.read_csv('players.csv')
    
    df = df.drop_duplicates()
    
    # Categorize players by age and position
    df['Age Group'] = df['player_age'].apply(categorize_age)
    df['Position Group'] = df['player_pos'].apply(categorize_position)

    # Get unique team names
    teams = sorted(df[df['league'] == 'PKO BP Ekstraklasa']['team_name'].unique())

    # Team selection dropdown
    selected_team = st.selectbox("Select a team:", teams)

    # Filter data for the selected team
    team_data = df[df['team_name'] == selected_team].drop_duplicates()
    

    

    age_groups = ["U21", "Peak (21-28)", "Post-Peak (28-32)", "Veteran"]
    position_groups = ["GK", "CB", "FB/WB", "DM/CM", "AM/Winger", "FW", "Other"]

    table_data = {pos: {age: [] for age in age_groups} for pos in position_groups}

    for _, player in team_data.iterrows():
        contract_color = get_contract_color(player['contract_until'])
        player_info = f"<span style='color: {contract_color};'>{player['player_name']} ({player['player_age']})</span>"
        table_data[player['Position Group']][player['Age Group']].append(player_info)
        
    tab1, tab2, tab3 = st.tabs(["Squad Analysis", "Simple Stats", "Possible U-21s"])

    
    
    table = []
    for pos in position_groups:
        row = [pos]
        for age in age_groups:
            players = table_data[pos][age]
            row.append("<br>".join(players) if players else "")
        table.append(row)

    # Convert to DataFrame for display
    df_table = pd.DataFrame(table, columns=['Position'] + age_groups)
    
    with tab1:      
        # Display the table
        st.header(f"{selected_team} - Player Analysis")

        # Display as table with HTML rendering for new lines
        st.write(df_table.to_html(escape=False, index=False), unsafe_allow_html=True)
            # Legend for contract colors
        st.markdown("### Contract Legend:")
        st.markdown("<span style='color: red;'>Red</span>: Contract ending in 2025", unsafe_allow_html=True)
        st.markdown("<span style='color: #ffc733;'>Yellow</span>: Contract ending in 2026", unsafe_allow_html=True)
        st.markdown("<span style='color: green;'>Green</span>: Contract ending in 2027 or later", unsafe_allow_html=True)
        
    with tab2:
        

        # Additional analysis
        st.header("Team Insights")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Position with most players over 30**")
            st.write(position_with_most_players_over_30(team_data))

            st.markdown("**Position with most contracts ending in 2025**")
            st.write(position_with_most_contracts_ending_2025(team_data))

        with col2:
            st.markdown("**Average age by position**")
            st.write(average_age_by_position(team_data))
    
    with tab3:
        position_to_filter = position_with_most_players_over_30(team_data)
        
        # Filter the DataFrame based on the position
        filtered_df = df[(df['Position Group'] == position_to_filter) & (df['player_age'] <= 21) & (df['league'] != 'PKO BP Ekstraklasa')].reset_index()
        
        # Sort the table by minutes played
        filtered_df = filtered_df.sort_values(by='minutes_played', ascending=False).reset_index()
        
        st.write(f"Players in the {position_to_filter} position with the most minutes played and under 21 years old:")
        st.write(filtered_df[['player_name', 'player_age', 'minutes_played', 'team_name', 'league']].head(10))

   

if __name__ == "__main__":
    main()
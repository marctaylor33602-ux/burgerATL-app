import streamlit as st
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
import pandas as pd
import requests
import os
import folium
from streamlit_folium import folium_static


# --- 1. CONFIGURATION ---
# This MUST be the first Streamlit command
st.set_page_config(
    page_title="Buck's Burger Scout ATL", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 1.1 CSS ---
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Luckiest+Guy&family=Fredoka:wght@400;600&display=swap');

/* 1. THE PARCHMENT: Restoration with Dot Grid */
[data-testid="stAppViewContainer"] {
    background: #fdfaf5 radial-gradient(#e5e5e5 0.5px, #fdfaf5 0.5px) !important;
    background-size: 20px 20px !important;
    background-attachment: fixed !important;
}

/* 2. THE BADGE: High-Priority Red & Mustard styling */
.must-try-badge {
    background-color: #FF4B4B !important;
    color: white !important;
    padding: 4px 12px !important;
    border-radius: 50px !important;
    font-family: 'Luckiest Guy', cursive !important;
    font-size: 0.85rem !important;
    text-transform: uppercase !important;
    border: 2px solid #FDB913 !important;
    display: inline-block !important;
    margin-left: 10px !important;
    box-shadow: 2px 2px 0px #333 !important;
    vertical-align: middle !important;
}

/* 3. MUSTARD SLIDER: Full Override */
div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {
    background: #FDB913 !important;
}
div[data-testid="stSlider"] [data-testid="stThumb"] {
    background-color: #FDB913 !important;
    border: 2px solid #333 !important;
}

/* 4. HEADERS & FONTS */
h1, h2, h3, [data-testid="stHeader"], [data-testid="stWidgetLabel"] p {
    font-family: 'Luckiest Guy', cursive !important;
    color: #FF4B4B !important;
    letter-spacing: 2px !important;
}

html, body, [data-testid="stAppViewContainer"] * {
    font-family: 'Fredoka', sans-serif !important;
}

/* 5. SIDEBAR CLEANUP: Kill the 'arrow_down' and 'keyword_double' labels */
[data-testid="stSidebar"] [data-testid="stIcon"],
[data-testid="stSidebar"] .st-emotion-cache-1ae8k90,
[data-testid="stSidebar"] span:contains("arrow_") {
    font-size: 0 !important;
    color: transparent !important;
    line-height: 0 !important;
}

[data-testid="stSidebar"] [data-testid="stIcon"]::before {
    content: '▼' !important;
    font-family: sans-serif !important;
    font-size: 14px !important;
    color: #FF4B4B !important;
    visibility: visible !important;
}
/* Lock the sidebar by hiding the collapse button */
[data-testid="collapsedControl"] {
    display: none !important;
}

/* Optional: Prevent the sidebar from being too narrow */
section[data-testid="stSidebar"] {
    min-width: 350px !important;
}

</style>
"""

# This line MUST be present to activate your styles
st.markdown(custom_css, unsafe_allow_html=True)


# --- 1.15 TITLE ---
st.title("🍔 Buck's Burger Scout")


# --- 1.2 API & PATHS ---
API_KEY = "AIzaSyDgakJhHteGv1mpS171P1-1ryJ5h73VzDA"
CSV_FILE = "burger_ratings.csv"

# Request location from the browser
location = get_geolocation()

# Use 'is not None' to avoid the truth-value error on line 95
if location is not None:
    try:
        # Extra safety check for the 'coords' key
        if 'coords' in location:
            HOME_LOCATION = [location['coords']['latitude'], location['coords']['longitude']]
        else:
            HOME_LOCATION = [33.7844, -84.4225]
    except (KeyError, TypeError):
        HOME_LOCATION = [33.7844, -84.4225]
else:
    # Default fallback to West Midtown / 30318
    HOME_LOCATION = [33.7844, -84.4225]


# --- 1.5 SCOUTED LIST LOADING ---
SCOUTED_FILE = "scouted_restaurants.csv"
scouted_df = pd.read_csv(SCOUTED_FILE) if os.path.exists(SCOUTED_FILE) else pd.DataFrame()

# --- INITIALIZE SESSION STATE ---
if "selected_spot" not in st.session_state:
    if not scouted_df.empty:
        st.session_state.selected_spot = scouted_df['Name'].iloc[0]
    else:
        st.session_state.selected_spot = None

# --- 1.8 SIDEBAR ---
with st.sidebar:
    st.image("thumbs up Buck image.png", caption="The best burgers with Buck", width=200)
    
    # ADD THIS CLICK CHECK HERE:
    if "burger_map" in st.session_state and st.session_state["burger_map"]:
        clicked_data = st.session_state["burger_map"].get("last_object_clicked_popup")
        if clicked_data:
            for name in scouted_df['Name'].unique():
                if name in clicked_data:
                    st.session_state.selected_spot = name

    st.markdown("### Your Scout Dispatch")
    # ... rest of your selectbox code follows
   
    
    if not scouted_df.empty:
        # 1. Logic to sync with Map: Get the list of names
        names_list = list(scouted_df['Name'].unique())
        
        # Find the index of the spot saved in session state (from map click or previous select)
        try:
            current_index = names_list.index(st.session_state.selected_spot)
        except (ValueError, KeyError):
            current_index = 0

        # 2. The Selectbox (using the index to allow map-sync)
        selected_spot = st.selectbox(
            "View Buck's Visit:", 
            names_list,
            index=current_index,
            key="sidebar_scout_select"
        )
        
        # Update session state so the "Brain" remembers this choice
        st.session_state.selected_spot = selected_spot
        
        # 3. Pull data for the selected spot
        venue_data = scouted_df[scouted_df['Name'] == selected_spot].iloc[0]
        
        # --- 4. Display the Burger Image ---
        if 'Image_URL' in scouted_df.columns and pd.notna(venue_data['Image_URL']):
            st.image(venue_data['Image_URL'], caption=f"The burger at {selected_spot}")
        else:
            st.image("https://via.placeholder.com/300x200?text=No+Burger+Photo", caption="No image available")
        
        # 5. Action Button
        if "show_details" not in st.session_state:
            st.session_state.show_details = False

        if st.button("⬇️ See the Venue !"):
            st.session_state.show_details = True
    
        # 6. Detail View (Video & Link)
        if st.session_state.show_details:
            target_url = venue_data['Review_URL']
            st.write(f"**Location:** {selected_spot}")
            
            clean_url = str(target_url).strip()
            if clean_url.startswith('http'):
                st.video(clean_url)
                st.link_button("Open in FOX 5 Website", clean_url, use_container_width=True)
            else:
                st.warning("No video available for this scout.")
    else:
        st.error("No restaurants found in scouted_restaurants.csv")

# --- 2. DATA PERSISTENCE ---
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["Name", "Rating", "Notes"]).to_csv(CSV_FILE, index=False)

def save_rating(name, rating, notes):
    df = pd.read_csv(CSV_FILE)
    new_entry = pd.DataFrame([[name, rating, notes]], columns=["Name", "Rating", "Notes"])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

# --- 3. GOOGLE MAPS SEARCH LOGIC ---
def search_burger_spots(query):
    # We remove the hardcoded 'burger' restriction to find specific names like 'Garden and Gun'
    # Updated radius to 80467 (approx 50 miles)
    
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&location=33.7844,-84.4225&radius=80467&key={API_KEY}"
    response = requests.get(url).json()
    return response.get('results', [])


# --- 4. APP LAYOUT ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Explore Atlanta Burgers")
    search_input = st.text_input("Find a spot (e.g., 'Best Burgers' or 'The Vortex')")
    
    # Initialize Map
    m = folium.Map(location=HOME_LOCATION, zoom_start=12)
    folium.Marker(HOME_LOCATION, popup="Home (30318)", icon=folium.Icon(color='red')).add_to(m)

    if search_input:
        results = search_burger_spots(search_input)
        for place in results:
            lat = place['geometry']['location']['lat']
            lng = place['geometry']['location']['lng']
            name = place['name']
            address = place.get('formatted_address', 'No address')
            rating = place.get('rating', 'N/A')
            
            folium.Marker(
                [lat, lng],
                popup=f"<b>{name}</b><br>Google Rating: {rating}⭐<br>{address}",
                tooltip=name,
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)

    # A. Mark Home (Red)
    folium.Marker(HOME_LOCATION, popup="Home (30318)", icon=folium.Icon(color='red', icon='home')).add_to(m)

# B. UPDATED: Plot Scouted Burgers (Red bubble with Yellow burger)
    if not scouted_df.empty:
        for _, row in scouted_df.iterrows():
            # 1. Define the logo (stays the same for all)
            logo_url = "https://images.foxtv.com/static.fox5atlanta.com/www.fox5atlanta.com/content/uploads/2020/03/932/524/BURGERS-WITH-BUCK.jpg"
            
            # 2. Get the specific burger photo from CSV
            burger_photo = row.get('Image_URL')
            
            # 3. Create the HTML for the burger photo (only if it exists)
            burger_img_html = ""
            if pd.notna(burger_photo):
                burger_img_html = f'<img src="{burger_photo}" width="150" style="border-radius: 5px; margin-top: 10px; border: 1px solid #ddd;">'
            
            html = f"""
                <div style="font-family: 'Fredoka', sans-serif; text-align: center; min-width: 160px;">
                    <img src="{logo_url}" width="120" style="border-radius: 5px;">
                    <h4 style="font-family: 'Luckiest Guy', cursive; color: #FF4B4B; margin: 10px 0;">{row['Name']}</h4>
                    {burger_img_html}
                    <br><br>
                    <a href="{row['Review_URL']}" target="_blank" 
                       style="background-color: #FDB913; color: white; padding: 8px 12px; border-radius: 15px; text-decoration: none; font-weight: bold; display: inline-block;">
                       Watch Review
                    </a>
                </div>
            """
            
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=folium.Popup(html, max_width=200),
                tooltip=f"Buck's Verdict: {row['Name']}",
                icon=folium.Icon(color='red', icon='hamburger', prefix='fa', icon_color='#FDB913')
            ).add_to(m)


    # --- 1.9 THE MAP & LISTENER ---

    # 1. Render the map
    map_data = st_folium(m, width=700, height=500, key="burger_map")

# 2. Check for clicks (Everything must be inside this 'if' block)
if map_data is not None:
    clicked_html = map_data.get("last_object_clicked_popup")
        
    # Only run the search if clicked_html actually exists
    if clicked_html:
        for name in scouted_df['Name'].unique():
            if name in clicked_html:
                if st.session_state.selected_spot != name:
                    st.session_state.selected_spot = name
                    st.rerun()



### COLUMN 2: RATINGS & IMAGES
with col2:
    # --- IMAGE PLACEMENT (Top Right) ---
    st.image("buck logo and image.png", 
             use_container_width=True) # Shrunk to fit column width

    st.subheader("Log Your Verdict")
    with st.form("rating_form"):
        res_name = st.text_input("Restaurant Name")
        my_rating = st.slider("Your Rating", 1, 5, 3)
        notes = st.text_area("Notes (e.g., Dog friendly, lively atmosphere, meat texture?)")
        
        if st.form_submit_button("Save my Verdict"):
            save_rating(res_name, my_rating, notes)
            st.success(f"Saved {res_name}!")

st.divider()

st.subheader("Your Saved Ratings")

# 1. Read the data
df = pd.read_csv(CSV_FILE)

# Clean up column names just in case there are hidden spaces
df.columns = df.columns.str.strip()

if not df.empty:
    # Check if the column exists before looping to avoid the crash
    target_col = 'Your Rating' if 'Your Rating' in df.columns else 'Rating'
    
    for index, row in df.iterrows():
        # Use the confirmed column name
        if row[target_col] == 5:
            display_name = f"{row['Name']} <span class='must-try-badge'>Must-Try!</span>"
        else:
            display_name = row['Name']
            
        st.markdown(f"### {display_name}", unsafe_allow_html=True)
        st.write(f"**Rating:** {row[target_col]}/5")
        st.write(f"**Notes:** {row['Notes']}")
        st.divider()

with col2:
    # Adding a 3rd 'spacer' column (ratio 1:1:2) keeps the images small and to the left
    sub1, sub2, spacer = st.columns([1, 1, 2])
    
    with sub1:
        st.image("burgerstock.jpg", use_container_width=True, caption="Lets eat!")
        
    with sub2:
        st.image("buck no words.png", use_container_width=True, caption="Lets choose!")
    
    
  # --- PAID ADVERTISERS MAP SECTION ---
st.markdown("---")
st.header("📍 The Advertiser's Map")

# 1. Load and Merge Data
df_map = pd.read_csv('scouted_restaurants.csv')
df_ratings = pd.read_csv('burger_ratings.csv')

# Ensure column names match for the merge
df_combined = pd.merge(df_map, df_ratings[['Name', 'Rating']], on='Name', how='left')

# 2. Map Generation
m = folium.Map(location=[33.7490, -84.3880], zoom_start=11)

from folium import CustomIcon

for _, row in df_combined.iterrows():
    # Check if rating is 5 (Must-Try)
    is_must_try = row['Rating'] == 5
    
    # Define icon size: 55x55 for Must-Try, 35x35 for others
    icon_size = (65, 75) if is_must_try else (30, 30)
    icon_url = "https://img.icons8.com/emoji/96/hamburger-emoji.png" 
    
    burger_icon = CustomIcon(icon_url, icon_size=icon_size)

    # HTML for the popup
    badge_text = "<div style='color:orange; font-weight:bold;'>⭐ MUST-TRY ⭐</div>" if is_must_try else ""
    popup_html = f"""
        <div style="text-align:center; font-family: sans-serif;">
            {badge_text}
            <b>{row['Name']}</b>
        </div>
    """

    folium.Marker(
        [row['Latitude'], row['Longitude']],
        popup=folium.Popup(popup_html, max_width=150),
        icon=burger_icon
    ).add_to(m)

# 3. THE CRITICAL MISSING LINE: This renders the map in your app
from streamlit_folium import folium_static
folium_static(m)


# --- 1.95 FINAL SYNC TRIGGER ---
if map_data and map_data.get("last_object_clicked_popup"):
    clicked_html = map_data["last_object_clicked_popup"]
    for name in scouted_df['Name'].unique():
        if name in clicked_html:
            if st.session_state.selected_spot != name:
                st.session_state.selected_spot = name
                st.rerun()

  
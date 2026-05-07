import requests
import pandas as pd
import time

API_KEY = "AIzaSyDgakJhHteGv1mpS171P1-1ryJ5h73VzDA"
# Your full list formatted for searching
INPUT_LIST = [
    "NFA Burger, Dunwoody", "The Vortex, Little 5 Points", "Bocado, Westside", 
    "H&F Burger, Ponce City Market", "Garden and Gun Club, The Battery", 
    "T’s Burger Bar, Douglasville", "Bomb Biscuit Co., Atlanta", "Mobay Spice, Toco Hills", 
    "Nest on Four, Signia Hotel", "McKendrick’s, Atlanta", "5Church Midtown", 
    "The Grove, Atlanta", "Love Your Brunches, Conyers", "Barn Belly Burgers, Dallas GA", 
    "Industry Tavern, Buckhead", "Marcus Bar and Grille, Atlanta", "Elise, Atlanta", 
    "State Farm Arena, Atlanta", "Confab Kitchen, Atlanta", "Mike & C’s, Peachtree City", 
    "Escovitchez, Atlanta", "Chico Cantina, Atlanta", "NoriFish, Atlanta", 
    "Graffiti Breakfast, Atlanta", "Miller’s Rexall, Downtown", "The General Muir, Emory Point", 
    "Fred’s Meat & Bread, Krog Street", "Majestic Diner, Poncey-Highland", 
    "The Family Dog, Morningside", "Up on the Roof, Alpharetta", "Partridge Inn, Augusta", 
    "Nick's Westside", "No Idea Burgers, Atlanta", "RaceTrac Kitchen, Atlanta", 
    "Farm Burger, East Lake", "Batsi, Buford Hwy", "Rose & Crown Tavern, Marietta", 
    "Season, Marietta", "Brasserie Margot, Four Seasons", "Saltwood, Midtown", 
    "Hubcap Grill, Houston TX", "Babalu Tapas, Atlanta", "Muss & Turner’s, Smyrna", 
    "Grindhouse Killer Burgers, Atlanta", "Village Burger, Dunwoody", "Lucky’s Burger, Roswell", 
    "Stockyard Burgers, Marietta", "Universal Joint, Decatur", "Steinbeck’s, Decatur", "Slab Brewhouse, Atlanta"
]

def geocode():
    results = []
    for item in INPUT_LIST:
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={item}&key={API_KEY}"
        data = requests.get(url).json()
        if data['results']:
            res = data['results'][0]
            results.append({
                "Name": res['name'],
                "Latitude": res['geometry']['location']['lat'],
                "Longitude": res['geometry']['location']['lng'],
                "Address": res.get('formatted_address', '')
            })
            print(f"Found: {res['name']}")
        time.sleep(0.1)
    pd.DataFrame(results).to_csv("scouted_restaurants.csv", index=False)

if __name__ == "__main__":
    geocode()

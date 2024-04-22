import requests
import pandas as pd
import os

def load_and_clean_data(file_path):
    # Load the CSV file
    df = pd.read_csv(file_path)
    
    # Check if "PAVADINIMAS" column exists
    if "PAVADIN" not in df.columns:
        raise ValueError("Column 'PAVADINIMAS' not found in the CSV file.")
    
    # Remove duplicates
    df_unique = df['PAVADIN'].drop_duplicates().reset_index(drop=True)
    
    # Convert to list if preferred, otherwise return DataFrame
    station_names_list = df_unique.tolist()
    print(df_unique.size)
    return station_names_list


def get_place_details(place_name, api_key):
    # Encode place name for URL
    place_name_encoded = requests.utils.quote(place_name)

    # Find place
    find_place_url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={place_name_encoded}&inputtype=textquery&fields=place_id&key={api_key}"
    response = requests.get(find_place_url)
    results = response.json()
    place_id = results['candidates'][0]['place_id'] if results['candidates'] else None

    if not place_id:
        return "Place not found"

    # Get place details
    place_details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=rating,user_ratings_total,reviews&key={api_key}"
    response = requests.get(place_details_url)
    place_details = response.json()

    if 'result' in place_details:
        place_info = place_details['result']
        reviews = place_info.get('reviews', [])
        return {
            "Bus Station": place_name,
            "Rating": place_info.get('rating', None),
            "Number of Ratings": place_info.get('user_ratings_total', None)
            #"Reviews": [{'author_name': review['author_name'], 'text': review['text'], 'language': review.get('language', 'Lithuanian')} for review in reviews]
        }
    else:
        return {
            "Bus Station": place_name,
            "Rating": None,
            "Number of Ratings": None
        }

def create_and_save_dataframe(data, filename='bus_station_ratings.csv'):
    
    if os.path.exists(filename):
        print(f"{filename} already exists. Loading from file...")
        return pd.read_csv(filename)
    
    df = pd.DataFrame(data)
    df = df.dropna(subset=['Rating'])
    df_sorted = df.sort_values(by='Rating', ascending=False).reset_index(drop=True)

    # Save to CSV
    df_sorted.to_csv(filename, index=False)
    return df_sorted

def load_data_from_csv(filename='bus_station_ratings.csv'):
    try:
        df = pd.read_csv(filename)
        return df
    except FileNotFoundError:
        return "File not found. Please ensure the file exists or run the data collection process first."


# Example usage
api_key = ''  # Replace with your actual API key
file_path = 'vilniaus_stoteles.csv'  # Replace with the path to your CSV file
unique_station_names = load_and_clean_data(file_path)
data = []

data = [get_place_details(name, api_key) for name in unique_station_names]
df = create_and_save_dataframe(data)
df = load_data_from_csv()
print(df.head(10))



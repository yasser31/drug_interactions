import tkinter as tk
import requests
from googletrans import Translator

# Function to find RxCUI for a given drug name
def find_rxcui(drug_name):
    """
    This function get rxcui needed for API call from a string
    """
    try:
        url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={urllib.parse.quote(drug_name)}&search=0"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        try:
            return data['idGroup']['rxnormId']
        except KeyError:
            result_label.config(text=f"{drug_name} non reconnu, vérifiez votre orthographe", fg="red")
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

# Function to translate text to French
def translate_to_french(text):
    try:
        translator = Translator()
        translation = translator.translate(text, src='en', dest='fr')
        return translation.text
    except Exception as e:
        return f"Translation Error: {e}"

# Function to find drug interactions
def find_interactions():
    """
    This function makes the call to the API
    """
    drug_names = [entry.get() for entry in drug_entries]
    rxcuis = []

    # Find RxCUI for each drug name
    for name in drug_names:
        rxcui = find_rxcui(name)
        if isinstance(rxcui, str):  # Check if it's an error message
            result_label.config(text=rxcui, fg="red")  # Display the error message in red
            return
        rxcuis.append(rxcui[0])

    # Use the RxCUIs to find drug interactions
    rxcuis_str = '+'.join(map(str, rxcuis))
    try:
        interaction_url = f"https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis={rxcuis_str}"
        response = requests.get(interaction_url)
        response.raise_for_status()
        data = response.json()
        try:
            interactions = [translate_to_french(interaction["interactionPair"][0]['description'])
                            for interaction in data['fullInteractionTypeGroup'][0]['fullInteractionType']]
        except KeyError:
            result_label.config(text='Aucune interaction entre ces molécules selon la FDA', fg="green")
        else:
            result_label.config(text='\n'.join(interactions), fg="blue")  # Display interactions in blue
    except requests.exceptions.RequestException as e:
        result_label.config(text=f"Error: {e}", fg="red")  # Display errors in red

# Create a tkinter window
window = tk.Tk()
window.title("Checker d'Interaction de Médicaments")
window.geometry("400x400")  # Set window dimensions

# Create a list to hold drug entry widgets
drug_entries = []

# Function to add a new drug entry field
def add_drug_entry():
    new_entry = tk.Entry(window)
    new_entry.pack(pady=5)  # Add padding
    drug_entries.append(new_entry)

# Button to add a new drug entry field
add_button = tk.Button(window, text="Ajouter un Médicament", command=add_drug_entry, bg="green", fg="white")  # Green button with white text
add_button.pack(pady=10)  # Add padding

# Button to find interactions
find_button = tk.Button(window, text="Trouver les Interactions", command=find_interactions, bg="blue", fg="white")  # Blue button with white text
find_button.pack(pady=10)  # Add padding

# Create a label to display the result
result_label = tk.Label(window, text="", wraplength=300, justify="left")  # Wrap text and justify left
result_label.pack(pady=20)  # Add padding

# Start the tkinter main loop
window.mainloop()

import json
from deep_translator import GoogleTranslator
import database_handler as db
import time

def translate_missing_english_names():
    # Load ingredients
    ingredients = db._load_table('ingredient')
    translator = GoogleTranslator(source='ko', target='en')
    modified = False

    # Create a backup manually
    with open('ingredient.json.bak', 'w', encoding='utf-8') as f:
        json.dump(ingredients, f, ensure_ascii=False, indent=2)
    print("Created backup of ingredient data")

    for ingredient in ingredients:
        # Check if eng name is missing or empty
        if 'name' in ingredient and ('eng' not in ingredient['name'] or not ingredient['name']['eng']):
            try:
                # Get Korean name
                korean_name = ingredient['name']['kor']
                # Translate to English
                translation = translator.translate(korean_name)
                # Update the ingredient with English name
                if 'name' not in ingredient:
                    ingredient['name'] = {}
                ingredient['name']['eng'] = translation
                modified = True
                print(f"Translated: {korean_name} -> {translation}")
                # Add a small delay to avoid hitting rate limits
                time.sleep(1)
            except Exception as e:
                print(f"Error translating {ingredient.get('name', {}).get('kor', 'unknown')}: {e}")

    # If any translations were made, save the updated data
    if modified:
        db._save_table('ingredient', ingredients)
        print("Saved updated ingredient data with translations")
    else:
        print("No missing English names found")

if __name__ == '__main__':
    translate_missing_english_names()
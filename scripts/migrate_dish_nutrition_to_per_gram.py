"""
Migration script to convert dish.json nutrition data from per-dish to per-gram format.

This script:
1. Reads existing dish.json
2. For each dish, calculates total mass from required_ingredients
3. Converts nutrition_info from amount_per_dish to amount_per_unit_mass
4. Saves the updated data back to dish.json (with backup)
"""

import json
import os
from datetime import datetime

def migrate_dish_nutrition():
    """Migrate dish nutrition from per-dish to per-gram format."""
    
    dish_file = 'dish.json'
    
    # Check if file exists
    if not os.path.exists(dish_file):
        print(f"Error: {dish_file} not found.")
        return
    
    # Create backup
    backup_file = f'dish.json.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    with open(dish_file, 'r', encoding='utf-8') as f:
        original_data = f.read()
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(original_data)
    print(f"Backup created: {backup_file}")
    
    # Load dish data
    with open(dish_file, 'r', encoding='utf-8') as f:
        dishes = json.load(f)
    
    migrated_count = 0
    skipped_count = 0
    
    for dish in dishes:
        dish_id = dish.get('id', 'unknown')
        dish_name = dish.get('name', {}).get('kor', 'N/A')
        
        # Check if already migrated (has amount_per_unit_mass)
        nutrition_info = dish.get('nutrition_info', [])
        if nutrition_info and 'amount_per_unit_mass' in nutrition_info[0]:
            print(f"Skipping {dish_id} ({dish_name}): already migrated")
            skipped_count += 1
            continue
        
        # Calculate total mass from required_ingredients
        required_ingredients = dish.get('required_ingredients', [])
        total_mass_g = sum(ing.get('amount_g', 0) for ing in required_ingredients)
        
        if total_mass_g == 0:
            print(f"Warning: {dish_id} ({dish_name}) has zero total mass. Setting nutrition to 0.")
            # Convert to per-gram format with zero values
            for nutrient in nutrition_info:
                if 'amount_per_dish' in nutrient:
                    nutrient['amount_per_unit_mass'] = 0.0
                    del nutrient['amount_per_dish']
            migrated_count += 1
            continue
        
        # Convert nutrition from per-dish to per-gram
        for nutrient in nutrition_info:
            if 'amount_per_dish' in nutrient:
                amount_per_dish = nutrient['amount_per_dish']
                amount_per_unit_mass = amount_per_dish / total_mass_g
                nutrient['amount_per_unit_mass'] = amount_per_unit_mass
                del nutrient['amount_per_dish']
        
        print(f"Migrated {dish_id} ({dish_name}): total_mass={total_mass_g}g")
        migrated_count += 1
    
    # Save updated data
    with open(dish_file, 'w', encoding='utf-8') as f:
        json.dump(dishes, f, ensure_ascii=False, indent=4)
    
    print(f"\nMigration complete!")
    print(f"Migrated: {migrated_count} dishes")
    print(f"Skipped: {skipped_count} dishes (already migrated)")
    print(f"Backup saved to: {backup_file}")

if __name__ == '__main__':
    migrate_dish_nutrition()

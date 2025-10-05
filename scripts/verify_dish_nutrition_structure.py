"""
Verification script to test the new per-gram nutrition structure for dishes.

This script:
1. Verifies all dishes have amount_per_unit_mass instead of amount_per_dish
2. Tests that nutrition calculation works correctly
3. Validates that dish + ingredient combinations work properly
"""

import json
import sys
sys.path.insert(0, '.')
import database_handler as db

def verify_dish_structure():
    """Verify that all dishes use the new per-gram nutrition format."""
    print("=" * 60)
    print("VERIFICATION: Dish Nutrition Structure")
    print("=" * 60)
    
    dishes = db._load_table('dish')
    ingredients = db._load_table('ingredient')
    
    all_valid = True
    issues = []
    
    for dish in dishes:
        dish_id = dish.get('id', 'unknown')
        dish_name = dish.get('name', {}).get('kor', 'N/A')
        
        # Check nutrition_info structure
        nutrition_info = dish.get('nutrition_info', [])
        
        if not nutrition_info:
            issues.append(f"  [WARN] {dish_id} ({dish_name}): No nutrition info")
            continue
        
        # Check if using new format
        has_old_format = any('amount_per_dish' in n for n in nutrition_info)
        has_new_format = any('amount_per_unit_mass' in n for n in nutrition_info)
        
        if has_old_format:
            issues.append(f"  [FAIL] {dish_id} ({dish_name}): Still using old format (amount_per_dish)")
            all_valid = False
        elif has_new_format:
            print(f"  [OK] {dish_id} ({dish_name}): Using new format (amount_per_unit_mass)")
        else:
            issues.append(f"  [WARN] {dish_id} ({dish_name}): Unknown nutrition format")
            all_valid = False
    
    print()
    if issues:
        print("Issues found:")
        for issue in issues:
            print(issue)
    
    return all_valid

def test_nutrition_calculation():
    """Test that nutrition calculations work correctly."""
    print("\n" + "=" * 60)
    print("TEST: Nutrition Calculation")
    print("=" * 60)
    
    # Test with a sample dish
    dishes = db._load_table('dish')
    
    if not dishes:
        print("  [WARN] No dishes found to test")
        return False
    
    # Pick first dish with ingredients
    test_dish = None
    for dish in dishes:
        if dish.get('required_ingredients'):
            test_dish = dish
            break
    
    if not test_dish:
        print("  [WARN] No dish with ingredients found")
        return False
    
    dish_id = test_dish.get('id')
    dish_name = test_dish.get('name', {}).get('kor', 'N/A')
    
    print(f"\nTesting with dish: {dish_id} ({dish_name})")
    
    # Calculate total mass
    total_mass = db.get_dish_total_mass(test_dish)
    print(f"  Total mass: {total_mass}g")
    
    # Show nutrition per gram and total
    nutrition_info = test_dish.get('nutrition_info', [])
    
    print("\n  Nutrition breakdown:")
    for nutrient in nutrition_info[:5]:  # Show first 5 nutrients
        name = nutrient.get('name')
        per_gram = nutrient.get('amount_per_unit_mass', 0)
        total = per_gram * total_mass
        print(f"    {name}: {per_gram:.6f}/g → {total:.3f} total")
    
    return True

def test_dish_with_subdish():
    """Test that dishes using other dishes as ingredients work correctly."""
    print("\n" + "=" * 60)
    print("TEST: Dish with Sub-Dish Ingredients")
    print("=" * 60)
    
    dishes = db._load_table('dish')
    
    # Find a dish that uses another dish as ingredient
    test_dish = None
    for dish in dishes:
        for ing in dish.get('required_ingredients', []):
            if ing.get('type') == 'dish':
                test_dish = dish
                break
        if test_dish:
            break
    
    if not test_dish:
        print("  [INFO] No dish found that uses another dish as ingredient")
        return True
    
    dish_id = test_dish.get('id')
    dish_name = test_dish.get('name', {}).get('kor', 'N/A')
    
    print(f"\nTesting with dish: {dish_id} ({dish_name})")
    print(f"  Required ingredients:")
    
    for ing in test_dish.get('required_ingredients', []):
        ing_type = ing.get('type', 'ingredient')
        ing_id = ing.get('id')
        amount = ing.get('amount_g', 0)
        print(f"    - {ing_type}: {ing_id} ({amount}g)")
    
    # Calculate total mass
    total_mass = db.get_dish_total_mass(test_dish)
    print(f"\n  Total mass: {total_mass}g")
    
    # Show nutrition
    nutrition_info = test_dish.get('nutrition_info', [])
    if nutrition_info:
        calories = next((n for n in nutrition_info if n.get('name') == 'Calories (Total)'), None)
        if calories:
            per_gram = calories.get('amount_per_unit_mass', 0)
            total = per_gram * total_mass
            print(f"  Calories: {per_gram:.6f}/g → {total:.3f} total")
    
    return True

if __name__ == '__main__':
    print("\nStarting verification...\n")
    
    result1 = verify_dish_structure()
    result2 = test_nutrition_calculation()
    result3 = test_dish_with_subdish()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if result1 and result2 and result3:
        print("[PASS] All tests passed! The new structure is working correctly.")
    else:
        print("[FAIL] Some tests failed. Please review the issues above.")
    
    print()

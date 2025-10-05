from app import create_app

import database_handler as db

def initialize_database():
    """Recalculate nutrition for all dishes on server startup."""
    print("Initializing and updating dish nutrition data...")
    all_dishes = db._load_table('dish')
    all_ingredients = db._load_table('ingredient')
    
    updated_dishes = []
    for dish in all_dishes:
        updated_dish = db.recalculate_dish_nutrition(dish, all_ingredients, all_dishes)
        updated_dishes.append(updated_dish)
    
    db._save_table('dish', updated_dishes)
    print("Dish nutrition data updated successfully.")

app = create_app()


if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)

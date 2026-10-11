from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

DATA_FILE = 'menu_data.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"categories": [], "foods": [], "orders": []}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"categories": [], "foods": [], "orders": []}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ----------------- ئاپی مینۆ و بەشەکان -----------------
@app.route('/api/menu', methods=['GET'])
def get_menu():
    data = load_data()
    return jsonify({
        "categories": data.get("categories", []),
        "foods": data.get("foods", [])
    })

@app.route('/api/categories', methods=['POST'])
def add_category():
    req_data = request.json
    cat_name = req_data.get('name')
    if not cat_name:
        return jsonify({"error": "ناوی بەش پڕنەکراوەتەوە"}), 400
    
    data = load_data()
    if cat_name not in data["categories"]:
        data["categories"].append(cat_name)
        save_data(data)
    return jsonify({"success": True, "categories": data["categories"]})

@app.route('/api/categories/<cat_name>', methods=['DELETE'])
def delete_category(cat_name):
    data = load_data()
    if cat_name in data["categories"]:
        data["categories"].remove(cat_name)
        # سڕینەوەی خواردنەکانی ئەم بەشەش ئەگەر پێویست بکات یان هێشتنەوەیان
        save_data(data)
    return jsonify({"success": True, "categories": data["categories"]})

# ----------------- ئاپی خواردنەکان (Foods) -----------------
@app.route('/api/foods', methods=['POST'])
def add_food():
    req_data = request.json
    data = load_data()
    
    new_id = 1
    if data["foods"]:
        new_id = max(f["id"] for f in data["foods"]) + 1

    food_item = {
        "id": new_id,
        "name": req_data.get('name'),
        "price": req_data.get('price'),
        "category": req_data.get('category'),
        "image": req_data.get('image', '')
    }
    
    data["foods"].append(food_item)
    save_data(data)
    return jsonify({"success": True, "food": food_item})

@app.route('/api/foods/<int:food_id>', methods=['DELETE'])
def delete_food(food_id):
    data = load_data()
    data["foods"] = [f for f in data["foods"] if f["id"] != food_id]
    save_data(data)
    return jsonify({"success": True})

# ----------------- ئاپی داواکارییەکان (Orders) -----------------
@app.route('/api/orders', methods=['GET'])
def get_orders():
    data = load_data()
    return jsonify(data.get("orders", []))

@app.route('/api/orders', methods=['POST'])
def create_order():
    req_data = request.json
    data = load_data()
    
    new_id = 1
    if data.get("orders"):
        new_id = max(o["id"] for o in data["orders"]) + 1

    order_item = {
        "id": new_id,
        "table": req_data.get('table'),
        "items": req_data.get('items'),
        "total": req_data.get('total')
    }
    
    if "orders" not in data:
        data["orders"] = []
        
    data["orders"].append(order_item)
    save_data(data)
    return jsonify({"success": True, "order": order_item})

@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    data = load_data()
    if "orders" in data:
        data["orders"] = [o for o in data["orders"] if o["id"] != order_id]
        save_data(data)
    return jsonify({"success": True})

# ----------------- کارپێکردنی سێرڤەر -----------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
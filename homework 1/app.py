from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Database setup
def init_sqlite_db():
    conn = sqlite3.connect('database.db')
    print("Database opened successfully")
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)')
    print("Table created successfully")
    conn.close()

init_sqlite_db()


@app.route('/add-user/', methods=['POST'])
def add_user():
    try:
        post_data = request.get_json()
        name = post_data['name']
        email = post_data['email']

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
            conn.commit()
            response = {'message': 'User added successfully!'}
    except Exception as e:
        response = {'message': str(e)}
    return jsonify(response)


@app.route('/get-users/', methods=['GET'])
def get_users():
    users = []
    try:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            for row in rows:
                users.append({'id': row[0], 'name': row[1], 'email': row[2]})
    except Exception as e:
        response = {'message': str(e)}
        return jsonify(response)
    return jsonify(users)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

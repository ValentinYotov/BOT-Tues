from flask import Flask, request, render_template, redirect, url_for, session
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Функция за свързване към базата данни
def init_db():
    return psycopg2.connect(
        host="localhost",
        port="5433",
        database="webapp_db",
        user="postgres",
        password="your_password"
    )

# Маршрут за регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        try:
            conn = init_db()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)',
                           (first_name, last_name, email, password))
            conn.commit()
            cursor.close()
            conn.close()
            # След успешна регистрация, насочваме към страницата за успех
            return redirect(url_for('registration_success'))
        except Exception as e:
            print(f"Error during registration: {e}")
            return render_template('register.html', error="Възникна грешка. Моля, опитайте отново.")
    return render_template('register.html')

# Маршрут за показване на съобщение за успешна регистрация
@app.route('/registration_success')
def registration_success():
    return render_template('registration_success.html')

# Маршрут за вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            conn = init_db()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            if user:
                session['user'] = email
                # След успешен вход, насочваме към страницата за успех
                return redirect(url_for('login_success'))
            else:
                return render_template('login.html', error="Невалидни данни за вход. Моля, опитайте отново.")
        except Exception as e:
            print(f"Error during login: {e}")
            return render_template('login.html', error="Възникна грешка. Моля, опитайте отново.")
    return render_template('login.html')

# Маршрут за показване на съобщение за успешен вход
@app.route('/login_success')
def login_success():
    if 'user' in session:
        return render_template('login_success.html', user=session['user'])
    else:
        return redirect(url_for('login'))

# Основен маршрут (начална страница)
@app.route('/')
def home():
    return render_template('home.html')

# Стартиране на приложението
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

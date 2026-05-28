import flask
import os
import psycopg2

app = flask.Flask(__name__)

@app.route('/')
def index():
    return "<p>Hello, World!</p>"

@app.route('/hello')
def hello():
    return "<p>Hello, World2!</p>"

def get_env(var_name: str) -> str:
    value = os.environ.get(var_name)
    if value is None:
        raise KeyError(f"Missing required environment variable: {var_name}")
    return value


if __name__ == '__main__':
    connection = None
    cursor = None

    try:
        DB_HOST = get_env("DB_HOST")
        DB_NAME = get_env("DB_NAME")
        DB_USER = get_env("DB_USER")
        DB_PASSWORD = get_env("DB_PASSWORD")

        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor()

        print("Starting Flask server...")
        app.run(host='0.0.0.0', port=5000, debug=True)

    except Exception as error:
        print(f"Error while running server: {error}")
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
            print("Database connection has been closed.")

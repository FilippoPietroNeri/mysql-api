from flask import Flask, render_template, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint
import mysql.connector

app = Flask(__name__)
SWAGGER_URL = '/api/docs'
API_URL = 'https://raw.githubusercontent.com/FilippoPietroNeri/FilippoPietroNeri.github.io/refs/heads/main/shagger.yaml'

# Questo serve per connetterci al nostro cloud hosting.
database = mysql.connector.connect(
    host='91.227.114.240',  # Qua mettiamo il nostro indirizzo ip del nostro cloud
    port=3306,              # La porta a cui si apre MYSQL di default è 3306
    user='root',            # Nickname di default! non e' sicuro ma a noi va bene lo stesso
    password='M0ZUp6gcsilWQaD08Ob3qkGySyy1hAHpj11',
    database='4einf'
)

# Questo metodo crea un oggetto cursore dalla connessione al database. Un cursore ti permette di interagire con il database eseguendo query SQL, recuperando dati e svolgendo operazioni sul database.
dbcursor = database.cursor()

@app.route('/testingonly')
def homepage():
    dbcursor.execute('SHOW TABLES')
    tables = dbcursor.fetchall()

    # Crea un dizionario per contenere i dati di ogni tabella
    table_data = {}
    for table in tables:
        dbcursor.execute(f'SELECT * FROM {table[0]}')
        data = dbcursor.fetchall()
        dbcursor.execute(f'SHOW COLUMNS FROM {table[0]}')
        columns = [col[0] for col in dbcursor.fetchall()]
        table_data[table[0]] = {'columns': columns, 'data': data}

    return render_template('index.html', table_data=table_data)


@app.route('/api')
def api():
    return jsonify({
        'message': 'the api is online',
        'code': 200
    }), 200


@app.route('/api/tables')
def get_tables():
    dbcursor.execute('SHOW TABLES')
    tables = dbcursor.fetchall()
    return jsonify([table[0] for table in tables]), 200


@app.route('/api/tables/<table_name>', methods=['GET'])
def get_table_data(table_name):
    column = request.args.get('column')
    colval = request.args.get('c_value')
    try:
        dbcursor.execute(f'SELECT * FROM {table_name}')
        data = dbcursor.fetchall()

        if column and colval:
            dbcursor.execute(f"WHERE {column}={colval}")
        elif column and not colval:
            dbcursor.execute(f'DESCRIBE {column}')
        else:
            dbcursor.execute(f'SHOW COLUMNS FROM {table_name}')

        columns = [col[0] for col in dbcursor.fetchall()]

        result = [dict(zip(columns, row)) for row in data]

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={ 
        'app_name': "Test application"
    },
)

app.register_blueprint(swaggerui_blueprint)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3245, debug=True)

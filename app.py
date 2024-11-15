from flask import Flask, render_template, url_for, jsonify, request
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

api_key_ = 'sasa51c64as187sadasx1sa4145as0x'
data_base_url = 'postgresql://scan_user:mVkHQPqMUsDaJICn9V15jWDNOMIRFrle@dpg-cspu3dlumphs73dn0b70-a.oregon-postgres.render.com/scan_db'

def get_connection():
    try:
        conn = psycopg2.connect(data_base_url)
        return conn
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        raise

def create_table():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_robot (
                id SERIAL PRIMARY KEY,
                sensor1 TEXT NOT NULL,
                sensor2 TEXT,
                motor1State TEXT,
                motor2State TEXT,
                speedMotor1 INTEGER,
                speedMotor2 INTEGER
            );
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al crear la tabla: {e}")
        raise

def validate_api_key(request):
    api_key = request.headers.get('API-Key')
    if api_key != api_key_:
        return jsonify({'message': 'API Key inválida'}), 403
    return None

@app.route('/',)
def documentation():
    return 'ES UNA API'

@app.route('/set-scans', methods=['POST'])
def set_scan():
    api_key_error = validate_api_key(request)
    if api_key_error:
        return api_key_error

    try:
        data = request.get_json()

        sensor1 = data.get('sensor1')
        sensor2 = data.get('sensor2')
        motor1State = data.get('motor1State')
        motor2State = data.get('motor2State')
        speedMotor1 = data.get('speedMotor1')
        speedMotor2 = data.get('speedMotor2')

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO scan_robot (sensor1, sensor2, motor1State, motor2State, speedMotor1, speedMotor2) VALUES (%s, %s, %s, %s, %s, %s)",
            (sensor1, sensor2, motor1State, motor2State, speedMotor1, speedMotor2)
        )
        conn.commit()
        conn.close()

        return jsonify({'message': 'Datos insertados correctamente'}), 200

    except Exception as e:
        return jsonify({'message': f'Error al insertar datos: {str(e)}'}), 500

@app.route('/get-scans', methods=['GET'])
def get_scans():
    api_key_error = validate_api_key(request)
    if api_key_error:
        return api_key_error

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM scan_robot")
        rows = cursor.fetchall()

        scans = []
        for row in rows:
            scans.append({
                'id': row[0],
                'sensor1': row[1],
                'sensor2': row[2],
                'motor1State': row[3],
                'motor2State': row[4],
                'speedMotor1': row[5],
                'speedMotor2': row[6]
            })

        conn.close()

        return jsonify(scans)

    except Exception as e:
        return jsonify({'message': f'Error al obtener los datos: {str(e)}'}), 500

@app.route('/get-scan-timereal', methods=['GET'])
def get_scan_timereal():
    api_key_error = validate_api_key(request)
    if api_key_error:
        return api_key_error

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM scan_robot ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()

        if row:
            scan = {
                'id': row[0],
                'sensor1': row[1],
                'sensor2': row[2],
                'motor1State': row[3],
                'motor2State': row[4],
                'speedMotor1': row[5],
                'speedMotor2': row[6]
            }
            conn.close()
            return jsonify(scan), 200
        else:
            conn.close()
            return jsonify({'message': 'No se encontraron datos'}), 404

    except Exception as e:
        return jsonify({'message': f'Error al obtener el escaneo en tiempo real: {str(e)}'}), 500


if __name__ == '__main__':
    create_table()
    app.run(host='0.0.0.0', port=8080)

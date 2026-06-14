from flask import Flask, render_template, request, jsonify
import pymysql

app = Flask(__name__)

def obtener_conexion():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Catdog.2026",
        database="vitadog",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

# Cambiamos la ruta principal para obligar al navegador a vaciar la caché
@app.route('/v2')
@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/buscar', methods=['GET'])
def buscar_perro():
    try:
        filtro_raza = request.args.get('raza', '')
        filtro_pais = request.args.get('pais', '')
        filtro_letra = request.args.get('letra', '')  
        
        limite = 20
        pagina = int(request.args.get('pagina', 1))
        offset = (pagina - 1) * limite
        
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            if filtro_letra:
                consulta = """
                    SELECT r.nombre_raza, p.nombre_pais, r.caracteristicas_fisicas, r.caracteristicas_psicologicas,
                           GROUP_CONCAT(e.nombre_enfermedad SEPARATOR ', ') AS enfermedades_comunes
                    FROM razas r
                    LEFT JOIN paises p ON r.id_pais_origen = p.id_pais
                    LEFT JOIN raza_enfermedad re ON r.id_raza = re.id_raza
                    LEFT JOIN enfermedades e ON re.id_enfermedad = e.id_enfermedad
                    WHERE r.nombre_raza LIKE %s
                    GROUP BY r.id_raza
                    LIMIT %s OFFSET %s;
                """
                buscar_r = filtro_letra + "%"
                cursor.execute(consulta, (buscar_r, limite, offset))
            else:
                consulta = """
                    SELECT r.nombre_raza, p.nombre_pais, r.caracteristicas_fisicas, r.caracteristicas_psicologicas,
                           GROUP_CONCAT(e.nombre_enfermedad SEPARATOR ', ') AS enfermedades_comunes
                    FROM razas r
                    LEFT JOIN paises p ON r.id_pais_origen = p.id_pais
                    LEFT JOIN raza_enfermedad re ON r.id_raza = re.id_raza
                    LEFT JOIN enfermedades e ON re.id_enfermedad = e.id_enfermedad
                    WHERE r.nombre_raza LIKE %s AND (p.nombre_pais LIKE %s OR p.nombre_pais IS NULL)
                    GROUP BY r.id_raza
                    LIMIT %s OFFSET %s;
                """
                buscar_r = "%" + filtro_raza + "%"
                buscar_p = "%" + filtro_pais + "%"
                cursor.execute(consulta, (buscar_r, buscar_p, limite, offset))
                
            resultados = cursor.fetchall()
            
        conexion.close()
        return jsonify(resultados)
        
    except Exception as e:
        print("\n=== ATENCIÓN: ERROR REAL DE MYSQL ===")
        print(str(e))
        print("======================================\n")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)

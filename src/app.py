from flask import Flask, render_template, request, redirect, url_for, jsonify,flash
from flask_mysqldb import MySQL
from config import config
import matplotlib.pyplot as plt


from models.modeluser import ModelUser

from models.entities.user import User

from flask_sqlalchemy import SQLAlchemy

from werkzeug.utils import secure_filename
import os

app = Flask(__name__, static_url_path='/static')



db = MySQL(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = User(0,request.form['email'],request.form['password'])
        logged_user = ModelUser.login(db,email)
        if logged_user != None :
            if logged_user.password:
                return render_template('auth/home.html')
            else:
                flash("contraseña no valida --")
        else:
            flash("usuario no encontrado")
        return render_template('auth/iniciar.html')
    else:
        return render_template('auth/iniciar.html')

@app.route('/home')
def register1():
    return render_template('auth/home.html')

@app.route('/registro', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = db.connection.cursor()
        cur.execute('INSERT INTO user (email, password) VALUES (%s, %s)', (email, password))
        db.connection.commit()
        flash("añadido")
        return redirect(url_for('register'))
    return render_template('auth/registro.html')


def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/plantas', methods=['GET', 'POST'])
def plantas():
    plants_data = []
   
    # Fetch plants data from the database
    cur = db.connection.cursor()
    cur.execute('SELECT * FROM plantas')
    plants_data = cur.fetchall()
   
    if request.method == 'POST':
        nombre_planta = request.form['nombre_planta']
        descripcion_planta = request.form['descripcion_planta']

        cur.execute('INSERT INTO plantas (nombre_planta, descripcion_planta) VALUES (%s, %s)', (nombre_planta, descripcion_planta))
        db.connection.commit()
        id = cur.lastrowid
        return redirect(url_for('plantas', id=id, nombre_planta=nombre_planta))

    return render_template('auth/plantas.html', plants_data=plants_data)

@app.route('/plantas/delete/<int:id>', methods=['POST'])
def delete_plant(id):
    cur = db.connection.cursor()

    cur.execute('SELECT id FROM plantas WHERE id = %s', (id,))
    deleted_id = cur.fetchone()

    cur.execute('DELETE FROM plantas WHERE id = %s', (id,))
    db.connection.commit()

    if deleted_id:
        cur.execute('UPDATE plantas SET id = id - 1 WHERE id > %s', (id,))
        db.connection.commit()
        cur.execute('ALTER TABLE plantas AUTO_INCREMENT = 1')
        db.connection.commit()

    flash("Planta dada de baja")
    return redirect('/plantas')


@app.route('/plantas/update/<int:id>', methods=['GET', 'POST'])
def update_plant(id):
    if request.method == 'POST':
        nombre_planta = request.form.get('nombre_planta')
        descripcion_planta = request.form.get('descripcion_planta')
        cur = db.connection.cursor()
        cur.execute('UPDATE plantas SET nombre_planta = %s, descripcion_planta = %s WHERE id = %s',
                    (nombre_planta, descripcion_planta, id))
        db.connection.commit()
        cur.close()
        return redirect('/plantas')  
    else:
        cur = db.connection.cursor()
        cur.execute('SELECT * FROM plantas WHERE id = %s', (id,))
        plant_data = cur.fetchone()
        cur.close()
        return render_template('auth/actualizar_plantas.html', plant_data=plant_data)
    

@app.route('/enfermedades', methods=['GET', 'POST'])
def enfermedades():
    if request.method == 'POST':
        nombre_enfermedad = request.form['nombre_enfermedad']
        id_planta = request.form['id']
        descripcion_enfermedad = request.form['descripcion_enfermedad']
        cur = db.connection.cursor()
        cur.execute('INSERT INTO enfermedades (nombre_enfermedad, id_planta, descripcion_enfermedad) VALUES (%s, %s, %s)', (nombre_enfermedad, id_planta, descripcion_enfermedad))
        enfer_data = cur.fetchall()

        db.connection.commit()
        flash("added")
        return redirect(url_for('enfermedades'))
    
    cur = db.connection.cursor()
    cur.execute('SELECT enfermedades.id, enfermedades.nombre_enfermedad, plantas.nombre_planta, enfermedades.descripcion_enfermedad FROM enfermedades INNER JOIN plantas ON enfermedades.id_planta = plantas.id')
    enfer_data = cur.fetchall()

    cur.execute('SELECT id, nombre_planta FROM plantas')
    plants_data = cur.fetchall()
    
    return render_template('auth/enfermedades.html', enfer_data=enfer_data, plants_data=plants_data)

@app.route('/enfermedades/delete/<int:id>', methods=['POST'])
def delete_enfermedad(id):
    cur = db.connection.cursor()

    cur.execute('SELECT id FROM enfermedades WHERE id = %s', (id,))
    deleted_id = cur.fetchone()

    cur.execute('DELETE FROM enfermedades WHERE id = %s', (id,))
    db.connection.commit()

    if deleted_id:
        cur.execute('UPDATE enfermedades SET id = id - 1 WHERE id > %s', (id,))
        db.connection.commit()
        cur.execute('ALTER TABLE enfermedades AUTO_INCREMENT = 1')
        db.connection.commit()

    flash("enfermedad dada de baja")
    return redirect('/enfermedades')

@app.route('/enfermedades/update/<int:id>', methods=['GET', 'POST'])
def update_enfermedad(id):
    if request.method == 'POST':
        nombre_enfermedad = request.form['nombre_enfermedad']
        id_planta = request.form['id']
        descripcion_enfermedad = request.form['descripcion_enfermedad']
        cur = db.connection.cursor()
        cur.execute('UPDATE enfermedades SET nombre_enfermedad = %s, id_planta = %s, descripcion_enfermedad = %s WHERE id = %s',
                    (nombre_enfermedad, id_planta, descripcion_enfermedad, id))
        db.connection.commit()
        cur.close()
        return redirect('/enfermedades')  
    else:
        cur = db.connection.cursor()
        cur.execute('SELECT * FROM enfermedades WHERE id = %s', (id,))
        enfer_data = cur.fetchone()
        cur.close()

        cur = db.connection.cursor()
        cur.execute('SELECT id, nombre_planta FROM plantas')
        plants_data = cur.fetchall()

        return render_template('auth/actualizar_enfermedades.html', enfer_data=enfer_data, plants_data=plants_data)

@app.route('/invernadero', methods=['GET', 'POST'])
def invernadero():
    if request.method == 'POST':
        nombre_invernadero = request.form['nombre_invernadero']
        id_planta = request.form['id']
        tem_max	 = float(request.form['tem_max'])
        tem_min	 = float(request.form['tem_min'])
        hum_max	 = float(request.form['hum_max'])
        hum_min	 = float(request.form['hum_min'])
        descripcion	 = request.form['descripcion']
        if hum_max > 100:
            hum_max = hum_max / 100.0
        if hum_min > 100:
            hum_min = hum_min / 100.0

        cur = db.connection.cursor()
        cur.execute('INSERT INTO invernaderos (nombre_invernadero,id_planta, tem_max, tem_min, hum_max, hum_min, descripcion) VALUES (%s, %s, %s, %s, %s, %s, %s)', (nombre_invernadero,id_planta, tem_max, tem_min, hum_max, hum_min, descripcion))
        db.connection.commit()
        flash("añadido")
        return redirect(url_for('invernadero'))
    
    cur = db.connection.cursor()
    cur.execute('SELECT invernaderos.id, invernaderos.nombre_invernadero,invernaderos.id_planta, invernaderos.tem_max, invernaderos.tem_min, invernaderos.hum_max, invernaderos.hum_min, invernaderos.descripcion FROM invernaderos INNER JOIN plantas ON invernaderos.id_planta = plantas.id')
    inver_data = cur.fetchall()

    cur.execute('SELECT id, nombre_planta FROM plantas')
    plants_data = cur.fetchall()
    
    return render_template('auth/invernadero.html', inver_data=inver_data, plants_data=plants_data)

@app.route('/invernadero/delete/<int:id>', methods=['POST'])
def delete_invernadero(id):
    cur = db.connection.cursor()

    cur.execute('SELECT id FROM invernaderos WHERE id = %s', (id,))
    deleted_id = cur.fetchone()

    cur.execute('DELETE FROM invernaderos WHERE id = %s', (id,))
    db.connection.commit()

    if deleted_id:
        cur.execute('UPDATE invernaderos SET id = id - 1 WHERE id > %s', (id,))
        db.connection.commit()
        cur.execute('ALTER TABLE invernaderos AUTO_INCREMENT = 1')
        db.connection.commit()

    flash("invernadero dada de baja")
    return redirect('/invernadero')

@app.route('/invernadero/update/<int:id>', methods=['GET', 'POST'])
def update_(id):
    if request.method == 'POST':
        nombre_invernadero = request.form['nombre_invernadero']
        id_planta = request.form['id']
        tem_max	 = float(request.form['tem_max'])
        tem_min	 = float(request.form['tem_min'])
        hum_max	 = float(request.form['hum_max'])
        hum_min	 = float(request.form['hum_min'])
        descripcion	 = request.form['descripcion']
        if hum_max > 100:
            hum_max = hum_max / 100.0
        if hum_min > 100:
            hum_min = hum_min / 100.0

        cur = db.connection.cursor()
        cur.execute('UPDATE invernaderos SET nombre_invernadero = %s, id_planta = %s, tem_max = %s, tem_min = %s, hum_max = %s, hum_min =%s, descripcion = %s WHERE id = %s',
                    (nombre_invernadero, id_planta, tem_max, tem_min, hum_max, hum_min, descripcion, id))
        db.connection.commit()
        cur.close()
        return redirect('/invernadero')  
    else:
        cur = db.connection.cursor()
        cur.execute('SELECT * FROM invernaderos WHERE id = %s', (id,))
        inver_data = cur.fetchone()
        cur.close()

        cur = db.connection.cursor()
        cur.execute('SELECT id, nombre_planta FROM plantas')
        plants_data = cur.fetchall()

        return render_template('auth/actualizar_invernadero.html', inver_data=inver_data, plants_data=plants_data)


@app.route('/temperatura-humedad')
def temperatura_humedad():
    return render_template('auth/temperatura_humedad.html')

@app.route('/reporte_enfer', methods=['GET', 'POST'])
def reporte_enfer():
    graph_file_name = None
    disease_records = [] 
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        cur = db.connection.cursor()
        cur.execute('SELECT start_date, COUNT(*) as num_records FROM enfermedades WHERE start_date BETWEEN %s AND %s GROUP BY start_date',
                    (start_date, end_date))
        disease_records = cur.fetchall()

        dates = [record['date'] for record in disease_records]
        record_counts = [record['num_records'] for record in disease_records]

        plt.figure(figsize=(10, 6))
        plt.bar(dates, record_counts, color='skyblue')
        plt.xlabel('Disease Records')
        plt.ylabel('Number of Records')
        plt.title('Disease Records over Time')
        plt.xticks(rotation=45)
        plt.tight_layout()
    
        graph_file_name = 'static/disease_records_plot.png'
        plt.savefig(graph_file_name)
        plt.close() 

    cur = db.connection.cursor()
    cur.execute('SELECT enfermedades.id, enfermedades.nombre_enfermedad, plantas.nombre_planta, enfermedades.descripcion_enfermedad FROM enfermedades INNER JOIN plantas ON enfermedades.id_planta = plantas.id')
    enfer_data = cur.fetchall()

    cur.execute('SELECT id, nombre_planta FROM plantas')
    plants_data = cur.fetchall()

    return render_template('auth/repor_enfermedades.html', plants_data=plants_data, disease_records=disease_records, graph_file_name=graph_file_name)



@app.route('/sensores')
def sensores():
    return render_template('auth/sensores.html')

@app.route('/cursos')
def cursos():
    return render_template('auth/cursos.html')

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run(debug=True, port=5001)

from flask import Flask, render_template, request, redirect, url_for, jsonify,flash
from flask_mysqldb import MySQL
from config import config

from models.modeluser import ModelUser

from models.entities.user import User

app = Flask(__name__)

db = MySQL(app)


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
        cur = db.connection.cursor()
        cur.execute('INSERT INTO plantas (nombre_planta, descripcion_planta) VALUES (%s, %s)', (nombre_planta, descripcion_planta))
        db.connection.commit()
        flash("añadido")
    return render_template('auth/plantas.html', plants_data=plants_data)



@app.route('/plantas/delete/<int:id>', methods=['POST'])
def delete_plant(id):
    cur = db.connection.cursor()
    cur.execute('DELETE FROM plantas WHERE id = %s', (id,))
    db.connection.commit()
    flash("Plant deleted")
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
    

@app.route('/enfermedades')
def enfermedades():
    if request.method == 'POST':
        nombre_enfermedad = request.form['nombre_enfermedad']
        descripcion_enfermedad	 = request.form['descripcion_enfermedad']
        cur = db.connection.cursor()
        cur.execute('INSERT INTO enfermedades (nombre_enfermedad, descripcion_enfermedad) VALUES (%s, %s)', (nombre_enfermedad, descripcion_enfermedad))
        db.connection.commit()
        flash("añadido")
        return redirect(url_for('enfermedades'))
    return render_template('auth/enfermedades.html')

@app.route('/invernadero')
def invernadero():
    if request.method == 'POST':
        nombre_invernadero = request.form['nombre_invernadero']
        tem_max	 = request.form['tem_max']
        tem_min	 = request.form['tem_min']
        hum_max	 = request.form['hum_max']
        hum_min	 = request.form['hum_min']
        descripcion	 = request.form['descripcion']
        cur = db.connection.cursor()
        cur.execute('INSERT INTO invernadero (nombre_invernadero, tem_max, tem_min, hum_max, hum_min, descripcion) VALUES (%s, %s, %s, %s, %s, %s)', (nombre_invernadero, tem_max, tem_min, hum_max, hum_min, descripcion))
        db.connection.commit()
        flash("añadido")
        return redirect(url_for('invernadero'))
    return render_template('auth/invernadero.html')

@app.route('/temperatura-humedad')
def temperatura_humedad():
    return render_template('auth/temperatura_humedad.html')

@app.route('/sensores')
def sensores():
    return render_template('auth/sensores.html')

@app.route('/cursos')
def cursos():
    return render_template('auth/cursos.html')

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run(debug=True, port=5001)

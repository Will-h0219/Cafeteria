import functools
import os
import db
import utils
import yagmail
import datetime
import io
import csv
from flask import Flask, render_template, request, flash, session, redirect, url_for, send_file, make_response, Response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

#<<<<<<Esta dirección debe ser cambiada para que se puedan guardar las imagenes>>>>>>
UPLOAD_FOLDER = 'static/images/productos'

app= Flask(__name__)
SECRET_KEY = '123'
app.secret_key = '5fffa2e766c5f3d1a85ad8979864459a4d12b25e727ae7a78d1d8f958952a828L'
#app.secret_key = os.urandom(24) #Generar clave aleatoria
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def inicio():
    return render_template('login.html')

#<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not 'user_id' in session:
            flash('Acceso denegado')
            return redirect(url_for('inicio'))
        return view()
    return wrapped_view
#<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>

@app.route('/loginAdministrador/')
def logadmin():
    return render_template('loginAdministrador.html')

@app.route('/loginCajero/')
def cajero():
    return render_template('loginCajero.html')

#Contraseña para el "admin0" = "Admin123."
@app.route('/administrador/', methods=['GET','POST'])
def admin():
    try:
        if request.method == 'POST':
            #----------Conexión a DB-----------
            conexion = db.get_db()
            #----------------------------------
            usuario = request.form['usuario'] #sacar los campos del form
            clave = request.form['clave']

            if not usuario:
                flash('Ingresa un usuario!')
                return render_template('loginAdministrador.html')
            if not clave:
                flash('Clave requerida!')
                return render_template('loginAdministrador.html')

            cur = conexion.cursor()
            cur.execute('SELECT * FROM administradores WHERE administrador = ?' , (usuario,))
            reg = cur.fetchone()

            if reg is None:
                error = 'Usuario o contraseña invalidos!'
                flash(error)
                return render_template('loginAdministrador.html')
            else:   
            #-----------Manejo de sesión--------------
                if check_password_hash(reg[2], clave):
                    session.clear()
                    session['user_id'] = reg[0] #id
                    session['user_login'] = reg[1] #usuario
                    return render_template('administrador.html')
            #-----------------------------------------
        else:
            flash('Faltan datos!')
            return render_template('loginAdministrador.html')
    except:
        flash('Error inesperado!')
        return render_template('loginAdministrador.html')

@app.route('/registroCajero/')
@login_required
def registroCajero():
    return render_template('registroCajero.html')

@app.route('/registrarCajero/', methods=['GET','POST'])
@login_required
def registrarCajero():
    try:
        if request.method == 'POST':
            usuario = request.form['usuario'] #sacar los campos del form
            clave = request.form['clave']
            email = request.form['correo']

            #------Validar que los datos ingresados cumplan los requisitos------
            if not utils.isEmailValid(email):
                flash('El correo no es valido')
                return registroCajero()
            if not utils.isUsernameValid(usuario):
                flash('Usuario invalido')
                return registroCajero()
            if not utils.isPasswordValid(clave):
                flash('La clave debe tener una minúscula, una mayúscula, un número y mínimo 8 caracteres')
                return registroCajero()
            
            #----------Conexión a DB-----------
            conexion = db.get_db()
            #----------------------------------
            cur = conexion.cursor()
            #------Validar que el correo o usuario no exista en la DB------
            cur.execute("SELECT * FROM cajeros WHERE correo=?", (email,))
            reg = cur.fetchone()
            if reg :
                flash('El correo ya existe')
                return registroCajero()
            cur.execute("SELECT * FROM cajeros WHERE usuario=?", (usuario,))
            reg = cur.fetchone()
            if reg :
                flash('El usuario ya existe')
                return registroCajero()

            #------Creación del cajero en la DB------
            hashclave = generate_password_hash(clave)
            cur.execute("INSERT INTO cajeros (usuario, clave, correo) VALUES (?,?,?)", (usuario, hashclave, email))
            conexion.commit() #Esta linea permite que se envie el query que modifica la DB
            yag = yagmail.SMTP('cafeteriabrioche.grupoa@gmail.com','Prueba_01')
            yag.send(to=email,subject='Credenciales',contents='Bienvenido, tus datos de ingreso son: Usuario: ' + usuario + ' Clave: ' + clave[0:2] + '*****')
            conexion.close()
            flash('Hemos enviado un correo con tus credenciales!')
            return registroCajero()

    except:
        flash('Error inesperado!')
        return registroCajero()

@app.route('/modificarCajero/')
@login_required
def modificarCajero():
    return render_template('modificarCajero.html')

@app.route('/selectCajero/', methods=['GET', 'POST'])
@login_required
def selectCajero():
    try:
        if request.method == 'POST':
                email = request.form['correo']

                #------Validar que los datos ingresados cumplan los requisitos------
                if not email:
                    flash('Ingresa un correo valido!')
                    return modificarCajero()
                if not utils.isEmailValid(email):
                    flash('El correo no es valido!')
                    return modificarCajero()
                
                #----------Conexión a DB-----------
                conexion = db.get_db()
                #----------------------------------
                cur = conexion.cursor()
                #------Validar que el correo exista en la DB------
                cur.execute("SELECT * FROM cajeros WHERE correo=?", (email,))
                reg = cur.fetchone()
                if not reg :
                    flash('El correo no existe')
                    return modificarCajero()

                #------Creación del cajero en la DB------
                id = reg[0]
                usuario = reg[1]
                correo = reg[3]

                conexion.close()
                return render_template('modificarcaj.html', id=id, usuario = usuario, correo = correo)

    except:
        flash('Error inesperado!')
        return modificarCajero()

@app.route('/updateCajero/', methods=['GET', 'POST'])
@login_required
def updateCajero():
    try:
        if request.method == 'POST':
            userId = request.form['userId']
            usuario = request.form['usuario']
            email = request.form['correo']

            #----------Conexión a DB-----------
            conexion = db.get_db()
            #----------------------------------
            cur = conexion.cursor()

            if request.form.get('Modificar') == 'Modificar':
                #------Modificar cajero en la DB------
                cur.execute("UPDATE cajeros SET usuario = ?, correo = ? WHERE id = ?", (usuario, email, userId))
                conexion.commit() #Esta linea permite que se envie el query que modifica la DB
                conexion.close()
                flash('Usuario modificado exitosamente!')
                return render_template('modificarcaj.html')
            elif request.form.get('Eliminar') == 'Eliminar':
                #------Eliminar cajero en la DB------
                cur.execute("DELETE FROM cajeros WHERE id = ?", (userId,))
                conexion.commit() #Esta linea permite que se envie el query que modifica la DB
                conexion.close()
                flash('Usuario eliminado exitosamente!')
                return render_template('modificarcaj.html')
    except:
        flash('Error inesperado!')
        return modificarCajero()

@app.route('/registroProducto/')
def registroProducto():
    return render_template('registroProductos.html')

@app.route('/registrarProducto/', methods=['GET','POST'])
def registrarProducto():
    try:
        if request.method == 'POST':
            idProd = request.form['id'] #sacar los campos del form
            nombre = request.form['nombre']
            precio = request.form['precio']

            if 'imagen' not in request.files:
                flash('No se ha cargado ninguna imagen')
                return render_template('registroProductos.html')
            
            imagen = request.files['imagen']

            if imagen.filename == '':
                flash('No selecciono ninguna imagen')
                return render_template('registroProductos.html')

            if imagen and utils.allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                #------------------------------------------------------------------
                #img_url = "http://localhost:5000/static/images/productos/" + filename
                img_url = "images/productos/" + filename

                #----------Conexión a DB-----------
                conexion = db.get_db()
                #----------------------------------
                cur = conexion.cursor()
                #------Validar que el id del producto no exista en la DB------
                cur.execute("SELECT * FROM productos WHERE id=?", (idProd,))
                reg = cur.fetchone()
                if reg :
                    flash('El producto ya existe')
                    return registroProducto()

                #------Creación del producto en la DB------
                cur.execute("INSERT INTO productos (id, nombre, precio, image) VALUES (?,?,?,?)", (idProd, nombre, precio, img_url))
                conexion.commit() #Esta linea permite que se envie el query que modifica la DB
                conexion.close()
                flash('Producto guardado exitosamente!')
                return registroProducto()

    except:
        flash('Error inesperado!')
        return registroProducto()

@app.route('/modificarProducto/')
def modificarProducto():
    return render_template('modificarProducto.html')

@app.route('/selectProduct/', methods=['GET', 'POST'])
def selectProduct():
    try:
        if request.method == 'POST':
                productId = request.form['productId']

                #------Validar que los datos ingresados cumplan los requisitos------
                if not productId:
                    flash('Ingresa un id valido!')
                    return modificarProducto()
                
                #----------Conexión a DB-----------
                conexion = db.get_db()
                #----------------------------------
                cur = conexion.cursor()
                #------Validar que el correo exista en la DB------
                cur.execute("SELECT * FROM productos WHERE id=?", (productId,))
                reg = cur.fetchone()
                if not reg :
                    flash('El producto no existe')
                    return modificarProducto()

                #------Creación del cajero en la DB------
                id = reg[0]
                nombre = reg[1]
                precio = reg[2]

                conexion.close()
                return render_template('modificarprod.html', id=id, nombre = nombre, precio = precio)

    except:
        flash('Error inesperado!')
        return modificarProducto()

@app.route('/updateProduct/', methods=['GET', 'POST'])
def updateProduct():
    try:
        if request.method == 'POST':
            productId = request.form['id']
            nombre = request.form['nombre']
            precio = request.form['precio']

            #----------Conexión a DB-----------
            conexion = db.get_db()
            #----------------------------------
            cur = conexion.cursor()

            if request.form.get('Modificar') == 'Modificar':
                #------Modificar cajero en la DB------
                cur.execute("UPDATE productos SET nombre = ?, precio = ? WHERE id = ?", (nombre, precio, productId))
                conexion.commit() #Esta linea permite que se envie el query que modifica la DB
                conexion.close()
                flash('Producto modificado exitosamente!')
                return render_template('modificarprod.html')
            elif request.form.get('Eliminar') == 'Eliminar':
                #------Eliminar cajero en la DB------
                cur.execute("DELETE FROM productos WHERE id = ?", (productId,))
                conexion.commit() #Esta linea permite que se envie el query que modifica la DB
                conexion.close()
                flash('Producto eliminado exitosamente!')
                return render_template('modificarprod.html')
    except:
        flash('Error inesperado!')
        return modificarProducto()

@app.route('/eliminarProducto/')
def eliminarProducto():
    return render_template('')

@app.route('/balance/')
@login_required
def balance():
    return render_template('balance.html')

@app.route('/generarBalance/', methods=['GET', 'POST'])
@login_required
def generarBalance():
    try:
        if request.method == 'POST':
            fecha = request.form['fecha']

            #----------Conexión a DB-----------
            conexion = db.get_db()
            #----------------------------------
            cur = conexion.cursor()
            #------Modificar cajero en la DB------
            cur.execute("SELECT * FROM aperturaCaja WHERE fecha = ?", (fecha,))
            regIni = cur.fetchone()
            cur.execute("SELECT * FROM cierreCaja WHERE fecha = ?", (fecha,))
            regFin = cur.fetchone()
            cur.execute("SELECT ac.fecha, v.id, v.totalVenta FROM aperturaCaja AS ac INNER JOIN cierreCaja as cc ON cc.fecha = ac.fecha INNER JOIN ventas AS v ON v.fechaVenta = ac.fecha WHERE ac.fecha = ? ORDER BY v.id", (fecha,))
            reg = cur.fetchall()
            conexion.close()

            if not regFin:
                flash('fecha no valida!')
                return balance()
            elif not regIni:
                flash('No se realizo la apertura!')
                return balance()

            output = io.StringIO()
            writer = csv.writer(output)

            line = ['Fecha, id, ventas']
            writer.writerow(line)
            line = [str(regIni[2]) + ',Dinero apertura,' + str(regIni[1])]
            writer.writerow(line)

            for row in reg:
                line = [str(row[0]) + ',' + str(row[1]) + ',' + str(row[2])]
                writer.writerow(line)

            line = [str(regFin[2]) + ', Dinero cierre,' + str(regFin[1])]
            writer.writerow(line)

            output.seek(0)

            return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=ventas_report.csv"})
    except:
        flash('Error inesperado!')
        return balance()

@app.route('/caja/', methods=['GET','POST'])
def caja():
    try:
        if request.method == 'POST':
            #----------Conexión a DB-----------
            conexion = db.get_db()
            #----------------------------------
            error = None
            usuario = request.form['usuario'] #sacar los campos del form
            clave = request.form['clave']

            if not usuario:
                error = 'Ingresa un usuario!'
                flash(error)
                return render_template('loginCajero.html')
            if not clave:
                error = 'Clave requerida!'
                flash(error)
                return render_template('loginCajero.html')

            cur = conexion.cursor()
            cur.execute('SELECT * FROM cajeros WHERE usuario = ?', (usuario,))
            reg = cur.fetchone()

            if reg is None:
                error = 'Usuario o contraseña invalidos!'
                flash(error)
                return render_template('loginCajero.html')
            else:
            #-----------Manejo de sesión--------------
                if check_password_hash(reg[2], clave):
                    session.clear()
                    session['user_id'] = reg[0] #id
                    session['user_login'] = reg[1] #usuario
                    session['user_email'] = reg[3] #correo
                    return render_template('caja.html', id=reg[0])
            #-----------------------------------------
        else:
            flask('Faltan datos!')
            return render_template('loginCajero.html')
    except:
        flash('Error inesperado!')
        return render_template('loginCajero.html')

@app.route('/recuperarContrasena/')
def recuperarContrasena():
    return render_template('recuperarContrasena.html')

@app.route('/enviarCorreo/', methods=['GET','POST'])
def enviarCorreo():
    try:
        if request.method == 'POST':
                email = request.form['correo']

                #------Validar que los datos ingresados cumplan los requisitos------
                if not email:
                    flash('Ingresa un correo valido!')
                    return recuperarContrasena()
                if not utils.isEmailValid(email):
                    flash('El correo no es valido!')
                    return recuperarContrasena()
                
                #----------Conexión a DB-----------
                conexion = db.get_db()
                #----------------------------------
                cur = conexion.cursor()
                #------Validar que el correo exista en la DB------
                cur.execute("SELECT * FROM cajeros WHERE correo=?", (email,))
                reg = cur.fetchone()
                if not reg :
                    flash('El correo no existe')
                    return recuperarContrasena()
                else:
                #------Envio de correo------
                    secret_key = utils.get_random_string(25) #Generar clave aleatoria
                    userId = reg[0]
                    correo = reg[3]
                    cur.execute("INSERT INTO recuperarPwd (id_cajero, secret_key) VALUES (?, ?)", (userId, secret_key))
                    conexion.commit() #Esta linea permite que se envie el query que modifica la DB

                    yag= yagmail.SMTP('cafeteriabrioche.grupoa@gmail.com','Prueba_01')
                    yag.send(to=correo,subject='Recuperar Contraseña',contents='<a href="http://localhost:5000/recuperarContrasena2?secret_key=' + secret_key + '">Haz clic aqui</a>')
                    conexion.close()
                    flash('Hemos enviado un correo de recuperación!')
                    return render_template('loginCajero.html')
        else:
            flash('Faltan datos!')
            return render_template('recuperarContrasena.html')
    except:
        flash('Error inesperado!')
        return recuperarContrasena()

@app.route('/recuperarContrasena2/', methods=['GET'])
def recuperacion():
    secret_key = request.args.get('secret_key')
    if secret_key:
        #----------Conexión a DB-----------
        conexion = db.get_db()
        #----------------------------------
        cur = conexion.cursor()
        cur.execute("SELECT * FROM recuperarPwd WHERE secret_key = ?", (secret_key,))
        reg = cur.fetchone()
        if reg:
            userId = reg[0]
            return render_template('recuperarContrasena2.html', userId=userId)
        else:
            flash("Error 1!")
            return render_template('recuperarContrasena2.html')
    else:
        flash("Error 2!")
        return render_template('recuperarContrasena2.html')

@app.route('/recuperarContrasena3/', methods=['POST'])
def cambioPwd():
    if request.method == 'POST':
        userId = request.form['userId']
        newPassword = request.form['newPassword']
        verPassword = request.form['verPassword']

        if newPassword != verPassword:
            flash('Error contraseñas no validas')
            return render_template('recuperarContrasena2.html')
        else:
            #----------Conexión a DB-----------
            conexion = db.get_db()
            #----------------------------------
            cur = conexion.cursor()
            hashclave = generate_password_hash(newPassword)
            cur.execute("UPDATE cajeros SET clave = ? WHERE id = ?", (hashclave, userId))
            cur.execute("DELETE FROM recuperarPwd WHERE id_cajero = ?", (userId,))
            conexion.commit() #Esta linea permite que se envie el query que modifica la DB
            conexion.close()
            flash('Contraseña actualizada!')
            return render_template('loginCajero.html')

@app.route('/apertura/')
@login_required
def apertura():
    return render_template('apertura.html')

@app.route('/registroApertura/', methods=['GET', 'POST'])
@login_required
def registroapertura():
    try:
        if request.method == 'POST':
            dineroIni = request.form['efectivo']
            fecha = request.form['fecha']

            if not fecha:
                flash('Selecciona una fecha valida!')
                return apertura()
            if not dineroIni:
                flash('Ingresa la cantidad con que inicias el día!')
                return apertura()

            #----------Conexión a DB-----------
            conexion = db.get_db()
            #----------------------------------
            cur = conexion.cursor()
            #------Validar no haya un registro en la DB------
            cur.execute("SELECT * FROM aperturaCaja WHERE fecha=?", (fecha,))
            reg = cur.fetchone()
            if reg :
                flash('Ya se realizo la apertura!')
                return apertura()
            else:
            #------Registro de fecha en la DB------
                cur.execute("INSERT INTO aperturaCaja (dineroIni, fecha) VALUES (?,?)", (dineroIni, fecha))
                conexion.commit() #Esta linea permite que se envie el query que modifica la DB
                conexion.close()
                flash('Registro completo!')
                return apertura()

    except:
        flash('Error inesperado!')
        return apertura()

@app.route('/cierre/')
@login_required
def cierre():
    return render_template('cierre.html')

@app.route('/cierreCaja/', methods=['GET', 'POST'])
@login_required
def cierreCaja():
    try:
        if request.method == 'POST':
            dineroFin = request.form['efectivo']
            fecha = request.form['fecha']

            if not fecha:
                flash('Selecciona una fecha valida!')
                return cierre()
            if not dineroFin:
                flash('Ingresa la cantidad con que finalizaste el día!')
                return cierre()

            #----------Conexión a DB-----------
            conexion = db.get_db()
            #----------------------------------
            cur = conexion.cursor()
            #------Validar no haya un registro en la DB------
            cur.execute("SELECT * FROM cierreCaja WHERE fecha=?", (fecha,))
            reg = cur.fetchone()
            if reg :
                flash('Ya se realizo el cierre!')
                return cierre()
            else:
            #------Registro de fecha en la DB------
                cur.execute("INSERT INTO cierreCaja (dineroFin, fecha) VALUES (?,?)", (dineroFin, fecha))
                conexion.commit() #Esta linea permite que se envie el query que modifica la DB
                conexion.close()
                flash('Registro completo!')
                return cierre()

    except:
        flash('Error inesperado!')
        return cierre()

@app.route('/venta/', methods=['GET', 'POST'])
@login_required
def venta():
    try:
        if request.method == 'POST':
            userId = request.form['userId']
            #----------Conexión a DB-----------
            conexion = db.get_db()
            #----------------------------------
            cur = conexion.cursor()
            cur.execute("SELECT * FROM productos")
            reg = list(cur.fetchall())
            resp = make_response(render_template('venta.html', regs = reg, id = userId))
            resp.set_cookie('same-site-cookie', 'foo', samesite='Lax');
            # Ensure you use "add" to not overwrite existing cookie headers
            resp.headers.add('Set-Cookie','cross-site-cookie=bar; SameSite=None; Secure')
            return resp
        else:
            return inicio()
    except:
        return inicio()

@app.route('/compra/', methods=['GET', 'POST'])
@login_required
def compra():
    if request.method == 'POST':
        userId = request.form['userId']
        return render_template('procesarCompra.html', id = userId)

@app.route('/registroCompra/', methods=['GET', 'POST'])
@login_required
def registroCompra():
    try:
        x = datetime.datetime.now()
        today = str(x.year) + "-" + str(x.month) + "-" + str(x.day)
        if request.method == 'POST':
            nombreCliente = request.form['destinatario']
            correoCliente = request.form['cc_to']
            totalVenta = request.form['f1t1']
            fecha = today
            idCajero = request.form['userId']
            

            if not nombreCliente:
                flash('Ingresa el nombre del cliente!')
                return render_template('procesarCompra.html')
            if not correoCliente:
                flash('Ingresa el correo del cliente!')
                return render_template('procesarCompra.html')
            if not totalVenta:
                flash('EL carrito no puede estar vacio!')
                return render_template('procesarCompra.html')

            #----------Conexión a DB-----------
            conexion = db.get_db()
            #----------------------------------
            cur = conexion.cursor()

            #------Registro de fecha en la DB------
            cur.execute("INSERT INTO ventas (fechaVenta, totalVenta, id_cajero, nombreCliente, correoCliente) VALUES (?,?,?,?,?)", (fecha, totalVenta, idCajero, nombreCliente, correoCliente))
            conexion.commit() #Esta linea permite que se envie el query que modifica la DB
            conexion.close()
            flash('Registro completo!')
            return venta()
        else:
            flash('Error inesperado!')
            return cierre()

    except:
        flash('Error inesperado!')
        return cierre()


#------Botones "Regresar" en la interfaz administrador------
@app.route('/regAdmin/')
@login_required
def regresaAdmin():
    return render_template('administrador.html')

#------Botones "Regresar" en la interfas de Cajero------
@app.route('/regCaja/')
@login_required
def regresaCaja():
    return render_template('caja.html')

@app.route('/regVenta/')
@login_required
def regresaVenta():
    return render_template('venta.html')

@app.route('/logout/')
def logout():
    session['user_id']=None
    session['user_login']=None
    session['user_email']=None
    session.clear()
    return inicio()

#end_hola

if __name__ == '__name__':
    app.run(debug = True, host = '0.0.0.0', port = 80)



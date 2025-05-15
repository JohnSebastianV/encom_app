from flask import Flask, flash, render_template, request, redirect, url_for
from forms import IncidenteForm, InsertarEventoForm, VistaForm, ProcedimientoForm
import pyodbc
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta_super_segura'  

csrf = CSRFProtect(app)
# Conexión SQL Server

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-7KL8CLB\\SQLEXPRESS;"
    "DATABASE=encom_web;"
    "Trusted_Connection=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vistas', methods=['GET', 'POST'])
def mostrar_vistas():
    form = VistaForm()
    columnas = []
    filas = []
    vista_nombre = None

    if form.validate_on_submit():
        vista_nombre = form.vista.data
        cursor.execute(f"SELECT * FROM {vista_nombre}")
        columnas = [column[0] for column in cursor.description]
        filas = cursor.fetchall()

    return render_template('vistas.html', form=form, columnas=columnas, filas=filas, vista_nombre=vista_nombre)


@app.route('/procedimientos', methods=['GET', 'POST'])
def procedimientos():
    form = ProcedimientoForm()
    resultado = None

    if form.validate_on_submit():
        procedimiento = form.procedimiento.data
        if procedimiento == 'ActualizarBDCConCasosCerrados':
            cursor.execute("EXEC dbo.ActualizarBDCConCasosCerrados")
            conn.commit()
            # Después de ejecutar el procedimiento, consultamos la tabla bdc
            cursor.execute("SELECT id_bdc, historial_resolucion_id_historial FROM bdc")
            columnas = [column[0] for column in cursor.description]
            filas = cursor.fetchall()
            resultado = {'columnas': columnas, 'filas': filas}
        elif procedimiento == 'BuscarEventosRelacionadosPorFalla':
            tipo_falla = form.tipo_falla.data
            cursor.execute("EXEC dbo.BuscarEventosRelacionadosPorFalla ?", tipo_falla)
            columnas = [column[0] for column in cursor.description]
            resultado = {'columnas': columnas, 'filas': cursor.fetchall()}

    return render_template('procedimientos.html', form=form, resultado=resultado)


@app.route('/insertar/incidente', methods=['GET', 'POST'])
def registrar_incidente():
    form = IncidenteForm()

    # Cargar opciones para cada campo desplegable
    form.id_usuario.choices = [(row.id_usuario, f"{row.id_usuario} - {row.nombre}") for row in cursor.execute("SELECT id_usuario, nombre FROM cliente")]
    form.id_area.choices = [(row.id_area, row.nombre) for row in cursor.execute("SELECT id_area, nombre FROM area")]
    form.id_tipo_falla.choices = [(row.id_tipo_falla, row.nombre) for row in cursor.execute("SELECT id_tipo_falla, nombre FROM tipo_falla")]
    
    # Agregar opción vacía (opcional) para técnico y evento_sectorial
    tecnicos = [(0, '--- Ninguno ---')] + [(row.id_tecnico, row.nombre) for row in cursor.execute("SELECT id_tecnico, nombre FROM tecnico")]
    eventos = [(0, '--- Ninguno ---')] + [(row.id_evento_sectorial, row.nombre_evento) for row in cursor.execute("SELECT id_evento_sectorial, nombre_evento FROM evento_sectorial")]

    
    form.id_tecnico.choices = tecnicos
    form.id_evento_sectorial.choices = eventos

    form.id_analista.choices = [(row.id_analista, row.nombre) for row in cursor.execute("SELECT id_analista, nombre FROM analista")]

    if form.validate_on_submit():
        # Convertir a None si es vacío o no seleccionado
        id_tecnico = form.id_tecnico.data if form.id_tecnico.data != 0 else None
        id_evento_sectorial = form.id_evento_sectorial.data if form.id_evento_sectorial.data != 0 else None


        cursor.execute("""
            INSERT INTO incidente (
                descripcion, fecha_reporte, fecha_resolucion, impacto_usuarios,
                id_usuario, id_area, id_tipo_falla, id_tecnico, id_analista, id_evento_sectorial
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            form.descripcion.data,
            form.fecha_reporte.data,
            form.fecha_resolucion.data,
            form.impacto_usuarios.data,
            form.id_usuario.data,
            form.id_area.data,
            form.id_tipo_falla.data,
            id_tecnico,
            form.id_analista.data,
            id_evento_sectorial
        ))
        conn.commit()
        flash("Incidente insertado correctamente", "success")
        return redirect(url_for('index'))

    print(form.errors)
    print("Fecha reporte:", form.fecha_reporte.data)
    return render_template('insertar_incidente.html', form=form)


@app.route('/insertar/evento', methods=['GET', 'POST'])
def insertar_evento():
    form = InsertarEventoForm()
    
    # Cargar áreas desde la base de datos
    cursor.execute("SELECT id_area, nombre FROM area")
    areas = cursor.fetchall()
    form.area_id_area.choices = [(area[0], area[1]) for area in areas]

    if form.validate_on_submit():
        data = (
            form.nombre_evento.data,
            form.descripcion.data,
            form.fecha_inicio.data,
            form.fecha_fin.data,
            form.area_id_area.data
        )
        cursor.execute("""
            INSERT INTO evento_sectorial (nombre_evento, descripcion, fecha_inicio, fecha_fin, area_id_area)
            VALUES (?, ?, ?, ?, ?)
        """, data)
        conn.commit()
        flash("Evento insertado correctamente", "success")
        return redirect(url_for('index'))

    return render_template('insertar_evento.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)

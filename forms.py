from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField, TextAreaField, DateField
from wtforms.validators import DataRequired, Optional

class IncidenteForm(FlaskForm):
    descripcion = StringField('Descripción', validators=[DataRequired()])
    fecha_reporte = DateField('Fecha de Reporte', format='%Y-%m-%d', validators=[DataRequired()])
    fecha_resolucion = DateField('Fecha de Resolución', format='%Y-%m-%d', validators=[Optional()])
    impacto_usuarios = IntegerField('Impacto a Usuarios', validators=[DataRequired()])

    id_usuario = SelectField('Usuario', coerce=int)
    id_area = SelectField('Área', coerce=int)
    id_tipo_falla = SelectField('Tipo de Falla', coerce=int)
    id_tecnico = SelectField('Técnico', coerce=int, validators=[Optional()])
    id_analista = SelectField('Analista', coerce=int)
    id_evento_sectorial = SelectField('Evento Sectorial', coerce=int, validators=[Optional()])

    submit = SubmitField('Registrar Incidente')

class InsertarEventoForm(FlaskForm):
    nombre_evento = StringField('Nombre del Evento', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[DataRequired()])
    fecha_inicio = DateField('Fecha de Inicio', format='%Y-%m-%d', validators=[DataRequired()])
    fecha_fin = DateField('Fecha de Fin', format='%Y-%m-%d', validators=[Optional()])
    area_id_area = SelectField('Área', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar')

class VistaForm(FlaskForm):
    vista = SelectField('Vista', choices=[
        ('vista_analistas_estadisticas', 'Analistas Estadísticas'),
        ('vista_casos_resueltos_bdc', 'Casos Resueltos BDC'),
        ('vista_clientes_con_contratos', 'Clientes con Contratos'),
        ('vista_lista_base_conocimiento', 'Base de Conocimiento')
    ], validators=[DataRequired()])
    submit = SubmitField('Ver Vista')

class ProcedimientoForm(FlaskForm):
    procedimiento = SelectField('Procedimiento', choices=[
        ('', 'Selecciona...'),
        ('ActualizarBDCConCasosCerrados', 'ActualizarBDCConCasosCerrados'),
        ('BuscarEventosRelacionadosPorFalla', 'BuscarEventosRelacionadosPorFalla')
    ], validators=[DataRequired()])
    tipo_falla = StringField('Tipo de falla (para BuscarEventos)', validators=[Optional()])
    submit = SubmitField('Ejecutar')
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, DecimalField,DateField, FloatField, SelectField, TextAreaField, RadioField, IntegerField
from wtforms.validators import DataRequired, Email, ValidationError, Optional, Length
from app.models import Proveedor, Producto, Cliente, Compra, Venta
from datetime import date, datetime

from app.models import Proveedor,Producto,Cliente


class CargarChequeraForm(FlaskForm):
    numero_chequera = IntegerField('Numero de chequera', validators=[DataRequired()], render_kw={'class':'input'})
    banco = StringField('Entidad Bancaria',validators=[DataRequired()],render_kw={'class':'input'})
    cantidad_cheques = IntegerField('Cantidad de cheques, 20 por defecto', validators=[Optional()],render_kw={'class':'input', 'type':'number'})
    inicio = StringField('numero inicial de los cheques', validators=[DataRequired()],render_kw={'class':'input', 'type':'number'})
    submit = SubmitField('Aceptar',render_kw={'class':'submit button is-info'})

class CargarClienteForm(FlaskForm):
    nombre = StringField('Nombre de Empresa', validators=[DataRequired()])
    contacto = StringField('Nombre de Contacto')
    direccion = StringField('Dirección')
    telefono = StringField('Teléfono')
    email = StringField('E-mail', validators=[Optional(), Email()])
    cuit = StringField('CUIT', validators=[Optional()])
    comentario = TextAreaField('Comentario')
    submit = SubmitField('Aceptar')

    def validate_nombre(self,nombre):
        print("ESTOY ACA")
        CoP = Cliente.query.filter_by(nombre=nombre.data).first()
        if CoP is not None:
            raise ValidationError('Ya existe este cliente, necesita otro nombre!.')
    def validate_cuit(self, cuit):
        print("Estoy validando el CUIT")
        mod = Cliente.query.filter_by(cuit = cuit.data).first()
        if mod is not None:
            raise ValidationError('ERROR el CUIT ya existe')

class EditarClienteForm(FlaskForm):
    nombre = StringField('Nombre de Empresa', validators=[DataRequired()])
    contacto = StringField('Nombre de Contacto')
    direccion = StringField('Dirección')
    telefono = StringField('Teléfono')
    email = StringField('E-mail', validators=[Optional(), Email()])
    cuit = StringField('CUIT', validators=[Optional()])
    comentario = TextAreaField('Comentario')
    submit = SubmitField('Aceptar')

    def __init__(self, nombre_orig, cuit_orig, email_orig, *args, **kwargs):
        super(EditarClienteForm, self).__init__(*args, **kwargs)
        self.nombre_orig = nombre_orig
        self.cuit_orig = cuit_orig
        self.email_orig = email_orig
    
    def validate_nombre(self, nombre):
        if nombre.data != self.nombre_orig:
            c = Cliente.query.filter_by(nombre=self.nombre.data).first()
            if c is not None:
                raise ValidationError('Este Cliente ya existe en la base de datos.')
    def validate_cuit(self, cuit):
        if cuit.data != self.cuit_orig:
            c = Cliente.query.filter_by(cuit=self.cuit.data).first()
            if c is not None:
                raise ValidationError('Ya existe un cliente con este CUIT')
    def validate_email(self, email):
        if email.data != self.email_orig:
            c = Cliente.query.filter_by(email=self.email.dadta).first()
            if c is not None:
                raise ValidationError('Ya existe un Cliente con este correo electrónico')

class CargarProveedorForm(FlaskForm):
    nombre = StringField('Nombre de Empresa', validators=[DataRequired()])
    contacto = StringField('Nombre de Contacto')
    direccion = StringField('Dirección')
    telefono = StringField('Teléfono')
    email = StringField('E-mail', validators=[Optional(), Email()])
    cuit = StringField('CUIT', validators=[Optional()])
    es_flete = BooleanField('Es Flete', default=False)
    comentario = TextAreaField('Comentario')
    submit = SubmitField('Aceptar')


    def validate_nombre(self,nombre):
        print("ESTOY ACA")
        CoP = Proveedor.query.filter_by(nombre=nombre.data).first()
        if CoP is not None:
            raise ValidationError('Ya existe este proveedor, necesita otro nombre!.')
    def validate_cuit(self, cuit):
        print("Estoy validando el CUIT")
        mod = Proveedor.query.filter_by(cuit = cuit.data).first()
        if mod is not None:
            raise ValidationError('ERROR el CUIT ya existe')

class EditarProveedorForm(FlaskForm):
    nombre = StringField('Nombre de Empresa', validators=[DataRequired()])
    contacto = StringField('Nombre de Contacto')
    direccion = StringField('Dirección')
    telefono = StringField('Teléfono')
    email = StringField('E-mail', validators=[Optional(), Email()])
    cuit = StringField('CUIT', validators=[Optional()])
    es_flete = BooleanField('Es Flete', default=False)
    comentario = TextAreaField('Comentario')
    submit = SubmitField('Aceptar')

    def __init__(self, nombre_orig, cuit_orig, email_orig, *args, **kwargs):
        super(EditarProveedorForm, self).__init__(*args, **kwargs)
        self.nombre_orig = nombre_orig
        self.cuit_orig = cuit_orig
        self.email_orig = email_orig
    
    def validate_nombre(self, nombre):
        if nombre.data != self.nombre_orig:
            p = Proveedor.query.filter_by(nombre=self.nombre.data).first()
            if p is not None:
                raise ValidationError('Este Nombre ya existe en la base de datos.')
    def validate_cuit(self, cuit):
        if cuit.data != self.cuit_orig:
            p = Proveedor.query.filter_by(cuit=self.cuit.data).first()
            if p is not None:
                raise ValidationError('Ya existe un proveedor con este CUIT')
    def validate_email(self, email):
        if email.data != self.email_orig:
            p = Proveedor.query.filter_by(email=self.email.dadta).first()
            if p is not None:
                raise ValidationError('Ya existe un proveedor con este correo electrónico')

class CargarProductoForm(FlaskForm):
    nombre = StringField(
        'Nombre del producto',
        validators=[DataRequired()])
    precio = FloatField('Precio unitario de venta')
    precio_compra = FloatField('Precio unitario de compra')
    cantidad_a = FloatField('Cantidad inicial A', default=0.0)
    cantidad_b = FloatField('Cantidad inicial B', default=0.0)
    ultima_modificacion = DateField(format='%d/%m/%y', default=date.today())
    submit = SubmitField('Aceptar')

    def validate_product(self, nombre):
        producto = Producto.query.filter_by(nombre=nombre.data).first()
        if producto is not None:
            raise ValidationError('El producto ya existe, necesita otro nombre!.')

class EditarProductoForm(FlaskForm):
    nombre = StringField('Nombre del producto', validators=[DataRequired()])
    precio = FloatField('Precio unitario de venta')
    precio_compra = FloatField('Precio unitario de compra')
    cantidad_a = FloatField('Cantidad inicial A', default=0.0)
    cantidad_b = FloatField('Cantidad inicial B', default=0.0)
    ultima_modificacion = DateField(format='%d/%m/%y', default=date.today())
    submit = SubmitField('Aceptar')
    
    def __init__(self, nombre_original, *args, **kwargs):
        super(EditarProductoForm, self).__init__(*args, **kwargs)
        self.nombre_original = nombre_original
    
    def validate_nombre(self, nombre):
        if nombre.data != self.nombre_original:
            p = Producto.query.filter_by(nombre=self.nombre.data).first()
            if p is not None:
                raise ValidationError('Este Producto ya existe en la base de datos.')

class CargarVentaForm(FlaskForm):
    fecha = DateField(format='%d/%m/%y - %H:%M', default=datetime.utcnow(),
    validators=[Optional()], render_kw={'class':' input',})
    clientes = SelectField('Seleccione cliente', coerce=int, render_kw={'class':'select'})
    producto = SelectField('Seleccione el producto', coerce=int)
    cantidad = FloatField('Cantidad',render_kw={'class':' input', 'type':'number'})
    precio_unitario = FloatField('Precio unitario',render_kw={'class':' input', 'type':'number'})
    sub_total = FloatField('Sub total Productos',render_kw={'class':' input', 'type':'number'})
    flete = SelectField('Servicio de flete', coerce=int)
    costo_flete = FloatField('Costo Flete', default=0,render_kw={'class':' input', 'type':'number'})
    monto_total = FloatField('Total a Pagar',render_kw={'class':' input', 'type':'number'})
    comentario=TextAreaField('Comentario',render_kw={'class':' input'})
    factura_cliente = BooleanField('Facturar cliente', default=False)
    factura_flete = BooleanField('Facturar flete', default=False)
    # pagado = BooleanField('Pagado?',default=False)
    submit = SubmitField('Aceptar')

class CargarCompraForm(FlaskForm):
    fecha = DateField(format='%d/%m/%y - %H:%M',default=datetime.utcnow() ,validators=[Optional()])
    proveedor = SelectField('Seleccione proveedor', coerce=int)
    producto = SelectField('Seleccione el producto', coerce=int)
    cantidad = FloatField('Cantidad')
    # precio_unitario = FloatField('precio unitario')
    precio_carga = FloatField('Monto de la carga')
    flete = SelectField('Servicio de Flete', coerce=int)
    precio_flete = FloatField('Costo de flete')
    monto_total = FloatField('Total a pagar')
    comentario = TextAreaField('Comentarios')
    factura_proveedor = BooleanField('Factura Proveedor', default=False)
    factura_flete = BooleanField('Factura Flete', default=False)
    # pagado = BooleanField('Pagado?')
    submit = SubmitField('Aceptar')

class CobranzaForm(FlaskForm):
    fecha = DateField('Fecha: ', format='%d/%m/%y - %H:%M',default=datetime.now,validators=[Optional()])
    cliente = SelectField('Empresa:', coerce=int)
    monto = FloatField('Monto')
    comentario = TextAreaField('Comentario')
    hay_cheque = BooleanField('Contiene Cheque')
    factura = SelectField('Factura', choices=[(0, 'A'),(1, 'B')], coerce=int)
    submit = SubmitField('Aceptar')

class CargarChequeForm(FlaskForm):
    fecha = DateField('Fecha: ', format='%d/%m/%y',default=datetime.now,validators=[Optional()])
    fecha_emision= DateField('Fecha de emisión',format='%d/%m/%y')
    fecha_cobro = DateField('Fecha de cobro',format='%d/%m/%y')
    banco = StringField('Entidad')
    numero = StringField('Nº Cheque')
    importe = FloatField('Importe')
    comentario = TextAreaField('Comentario')
    submit = SubmitField('Aceptar')

class ChequedeTercero(FlaskForm):
    cheques = SelectField('seleccione el cheque', coerce=int)
    submit = SubmitField('submit')

class ChequeChequera(FlaskForm):
    chequera = SelectField('chequera', coerce=int)
    

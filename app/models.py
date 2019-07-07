from datetime import datetime
from app import db

# Tablas relacionales
""" p_venta = db.Table('p_venta',
    db.Column('producto_id', db.Integer, db.ForeignKey('producto.id')),
    db.Column('venta_id', db.Integer, db.ForeignKey('venta.id'))
)

p_compra = db.Table('p_compra',
    db.Column('producto_id', db.Integer, db.ForeignKey('producto.id')),
    db.Column('compra_id', db.Integer, db.ForeignKey('compra.id'))
)

compra_envio = db.Table(
    'compra_envio',
    db.Column('proveedor_id', db.Integer, db.ForeignKey('proveedor.id')),
    db.Column('compra_id', db.Integer, db.ForeignKey('compra.id'))
    )

venta_envio = db.Table(
    'venta_envio',
    db.Column('porveedor_id', db.Integer, db.ForeignKey('proveedor.id')),
    db.Column('venta_id', db.Integer, db.ForeignKey('venta.id')),
)
"""


class Servicio(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'), index = True)
    compra_id = db.Column(db.Integer, db.ForeignKey('compra.id'), index=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'), index=True)


#Modelos de Compra, venta, producto, cliente, proveedor (prod y flete)
class Cliente(db.Model):
    '''
    Modelo Cliente: nombre, direccion, telefono, email, contacto, cuit, ventas, comentario, saldos
    '''
    id = db.Column(db.Integer, primary_key=True, unique=True)
    nombre = db.Column(db.String(32), index=True)
    contacto = db.Column(db.String(32))
    telefono = db.Column(db.String(32))
    direccion = db.Column(db.String(32))
    email = db.Column(db.String(32))
    cuit = db.Column(db.String(32))
    comentario = db.Column(db.String(32))
    state = db.Column(db.Boolean, default=True)

    ventas = db.relationship('Venta', backref='cliente', lazy='dynamic')
    saldo_a = db.Column(db.Float, default= 0.00)
    saldo_b = db.Column(db.Float, default=0.00)
    cobros = db.relationship('Cobro', backref='cliente', lazy='dynamic')
    cheques_emitidos = db.relationship('Cheque', backref='cliente', lazy='dynamic')


    def borrar(self):
        if (self.saldo_a > 0 | saldo_a < 0 | saldo_b < 0 | saldo_b > 0):
            flash('No puede borrarse este cliente. Posee saldos pendientes')
            return redirect(url_for('detalle_cliente', id=self.id))
        else:
            self.state = False
            db.session.commit()
            return redirect(url_for('Cliente eliminado con exito'))
    
    def restaurar(self):
        self.state = True
        flash ('Cliente restaurado, puede volver a operar con él')
        return redirect(url_for('detalle_cliente', id=self.id))
    
    def actualizar_saldo(self, monto, factura, suma):
        """monto: para que reste del saldo tiene que ser <0
        factura: True para A False para B.
        suma: True para compras entrantes(suam al saldo), False para devoluciones, pagos, ventas borradas(resta del saldo)
        """
        if factura:
            #verifica si tipo de factura
            if suma:
                #verifica si es entrada o salida
                self.saldo_a += monto
            else:
                self.saldo_a -= monto
        else:
            if suma:
                self.saldo_b += monto
            else:
                self.saldo_b -= monto
    
    def __repr__(self):
        return '<Cliente {}>'.format(self.nombre)

class Venta(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True, index=True)
    cliente_id = db.Column(db.Integer(), db.ForeignKey('cliente.id'), index=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), index=True)
    compra_id = db.Column(db.Integer, db.ForeignKey('compra.id'), index=True)

    fecha = db.Column(db.DateTime(), default=datetime.utcnow)
    pc_u = db.Column(db.Float)
    pv_u = db.Column(db.Float)
    cantidad = db.Column(db.Float)
    precio_carga = db.Column(db.Float) #pv_u*cantidad
    costo_flete = db.Column(db.Float)
    monto_total = db.Column(db.Float) #precio_carga+costo_flete
    utilidad = db.Column(db.Float) #get_utility()
    comentario = db.Column(db.String(256))
    pagado = db.Column(db.Boolean, default=False)
    state = db.Column(db.Boolean, default=True)
    factura_cliente = db.Column(db.Boolean)
    factura_flete = db.Column(db.Boolean)

    #ref a tabla de asociacion entre la Venta y el proveedor de envio
    envio = db.relationship(
        'Servicio',
        backref = 'venta',
        uselist = False
        )

    #METODOS
    def get_utility(self):
        self.utilidad =round( (self.monto_total-((self.pc_u*self.cantidad)+self.costo_flete)),2)

    def actualizar_saldo_cliente(self, suma):
        """al ejecutar la venta, se le imputa el saldo al cliente y si hay un flete elegido, precio_flete se inputa también como saldo al proveedor del flete"""

        self.cliente.actualizar_saldo(
            monto = self.monto_total,
            factura = self.factura_cliente,
            suma = suma
        )

    def actualizar_saldo_proveedor(self, suma):
        if self.envio.flete is not None:
            self.envio.flete.actualizar_saldo(
                monto = self.costo_flete,
                factura = self.factura_flete,
                suma = suma
                )

    def borrar(self):
        """ Restaura el saldo del cliente, borra la compra al proveedor del flete que consecuentemente restaura su saldo. Restaura el stock de producto y cambia [venta.state => False]
        """
        #TODO: Restaurar stock y saldo cliente
        self.producto.actualizar_stock(
            cantidad = self.cantidad,
            factura = self.factura_cliente,
            entrada = True
        )
        self.actualizar_saldo_cliente(suma=False)
        self.actualizar_saldo_proveedor(suma=False)

        self.state=False

        #TODO: Terminar restauracion del saldo de proveedor y borrado de esa compra de servicio

    def __repr__(self):
        return '<Venta nro: {id} >'.format(id=self.id)



    #Clase que guarde los pagos, con la info de cada cliente
    #Monto, fecha, nombre cliente etc

class Cobro(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True, index=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), index=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'),index=True)
    fecha = db.Column(db.DateTime(), default=datetime.utcnow)
    nombre = db.Column(db.String(64))
    monto = db.Column(db.Float)
    forma_pago = db.Column(db.String(32))
    factura = db.Column(db.Boolean)
    comentario = db.Column(db.String(240))
    cheques = db.relationship('Cheque', backref='cobro', lazy='dynamic')
    state = db.Column(db.Boolean, default=True) # para controlar si impacta o no cuando se elimina pasa a state=False
    entrada = db.Column(db.Boolean)#si es un cobro->TRUE o un pago ->FALSE
    # hay_cheque = db.Column(db.Boolean)
    hay_cheque = db.Column(db.Boolean)

    def restar_saldo(self):
        if self.entrada:
            if self.factura:
                self.cliente.saldo_a -= self.monto
            else: self.cliente.saldo_b -= self.monto
        else:
            if self.factura:
                self.proveedor.saldo_a -= self.monto
            else:
                self.proveedor.saldo_b -= self.monto
    
    def borrar(self):
        self.state = False
        for c in self.cheques:
            c.state = False
        if self.entrada:
            self.cliente.actualizar_saldo(
                monto = self.monto,
                factura = self.factura,
                suma = True
            )
        else:
            self.proveedor.actualizar_saldo(
                monto = self.monto,
                factura = self.factura,
                suma = True
            )

class Cheque(db.Model):
    id = db.Column(db.Integer, unique=True, index=True, primary_key=True)
    cobro_id = db.Column(db.Integer, db.ForeignKey('cobro.id'), index=True)
    chequera_id = db.Column(db.Integer, db.ForeignKey('chequera.id'))
    emisor = db.Column(db.String(32))
    destino = db.Column(db.String(32))
    fecha = db.Column(db.DateTime())
    fecha_emision = db.Column(db.DateTime)
    fecha_cobro = db.Column(db.DateTime)
    banco = db.Column(db.String(32))
    numero = db.Column(db.String())
    importe = db.Column(db.Float, default=0.0)
    comentario = db.Column(db.String(240))
    state = db.Column(db.Boolean, default=True)
    factura = db.Column(db.Boolean)
    es_de_tercero = db.Column(db.Boolean)
    acreditado = db.Column(db.Boolean, default=False)
    es_entrada = db.Column(db.Boolean, default=False)
    emitido = db.Column(db.Boolean, default=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'))
    # TODO: Metodo de acreditado de cheque
    def acreditar (self):
        self.acreditado = True
    
    def emitir(self):
        if not self.emitido:
            self.emitido = True
    
    def get_emisor(self):
        if self.es_de_tercero:
            emitter = Cliente.query.filter_by(id=self.cliente.id).first()
            if emitter is not None:
                self.emisor = emitter.nombre
        else:
            self.emisor = 'Propietario'
        db.session.commit()
    
    def get_destino(self):
        '''Se utilida para pagos, establece el destinatario del cheque emitido'''
        if self.emitido:
            destino = Proveedor.query.filter_by(id=self.proveedor.id).first()
            if destino is not None:
                self.destino = destino.nombre
        else:
            self.destino = 'Propietario'
    
    def get_days(self):
        """Realiza el calculo en cuenta regresiva del tiempo que resta para que se pueda acreditar el cheque
        Reorna ```type timeDelta```"""
        delta = self.fecha_cobro - datetime.today()
        return delta.days+1


class Chequera(db.Model):
    id =db.Column(db.Integer, primary_key=True, index=True)
    numero_chequera = db.Column(db.Integer, unique=True)
    cheques = db.relationship('Cheque', backref='chequera', lazy='dynamic')
    cantidad_cheques = db.Column(db.Integer, default=20)
    state = db.Column(db.Boolean, default=True)
    banco = db.Column(db.String(32))
    
    def getCeros(self, inicio):
        """ determina los ceros iniciales si es que los hay  """
        ceros = []
        res=''
        for e in inicio:
            if e != '0':
                break
            else:
                ceros.append(e)
        for e in ceros:
            res += e
        return res
    
    def generate(self, inicio, chequera):
        n = int(inicio)
        for c in range(self.cantidad_cheques):
            Cheque(
                numero = self.getCeros(inicio)+str(n),
                chequera = chequera,
                banco = self.banco,
                es_de_tercero = False,
                acreditado=False,
                emitido = False,
            )
            n += 1
    
    def disponibles(self):
        disponibles = 0;
        for cheque in self.cheques:
            if not cheque.emitido:
                disponibles += 1
        return disponibles
    
    def emitidos(self):
        emitidos=0
        for cheque in self.cheques:
            if cheque.emitido:
                emitidos += 1
        return emitidos
    def importe_total(self):
        total = 0.0
        for c in self.cheques:
            if c.emitido:
                total += c.importe
        return round(total, 2)


class Proveedor(db.Model):
    '''
    Modelo Proveedor: nombre, direccion, telefono, email, contacto, cuit, ventas, comentario, saldos
    '''
    id = db.Column(db.Integer, primary_key=True, unique=True)
    nombre = db.Column(db.String(32), index=True)
    contacto = db.Column(db.String(32))
    telefono = db.Column(db.String(32))
    direccion = db.Column(db.String(32))
    email = db.Column(db.String(32))
    cuit = db.Column(db.String(32), unique=True)
    comentario = db.Column(db.String(32))
    flete = db.Column(db.Boolean, default=False) #determina si es proveedor de flete(si es True)
    saldo_a = db.Column(db.Float, default=0.00)
    saldo_b = db.Column(db.Float, default=0.00)
    cobros = db.relationship('Cobro', backref='proveedor', lazy='dynamic')
    compras = db.relationship('Compra', backref='proveedor', lazy='dynamic')
    state = db.Column(db.Boolean, default=True)
    envios = db.relationship('Servicio', backref='flete', lazy='dynamic')
    cheques_entregados = db.relationship('Cheque',backref='proveedor', lazy='dynamic')
    
    def actualizar_saldo(self, monto, factura, suma):
        """monto: para que reste del saldo tiene que ser <0
        factura: True para A False para B.
        suma: True para compras entrantes(suam al saldo), False para devoluciones, pagos, ventas borradas(resta del saldo)
        """
        if factura:
            #verifica si tipo de factura
            if suma:
                #verifica si es entrada o salida
                self.saldo_a += monto
            else:
                self.saldo_a -= monto
        else:
            if suma:
                self.saldo_b += monto
            else:
                self.saldo_b -= monto

    #TODO: Faltan metodos de borrar proveedor....

    def __repr__(self):
        return '<Proveedor {}>'.format(self.nombre)


class Compra(db.Model):
    id = db.Column(db.Integer,primary_key=True, index=True, unique=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    # BACKREF: PROVEEDOR
    proveedor_id = db.Column(db.Integer(),db.ForeignKey('proveedor.id'), index=True)
    # BACKREF: PRODUCTO
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'))

    venta = db.relationship('Venta', backref='compra', uselist=False)

    #ref a tabla de asociacion entre la compra y el proveedor de envio
    envio = db.relationship(
        'Servicio',
        backref = 'compra',
        uselist = False
        )

    # compra_id = db.Column(db.Integer, db.ForeignKey('compra.id'))
    # compra_a_proveedor = db.Column(db.relationship)
    # cantidad de pies cuadrados en la carga
    cantidad = db.Column(db.Float)

    precio_unitario = db.Column(db.Float)
    precio_carga = db.Column(db.Float)
    precio_flete = db.Column(db.Float)
    pagado = db.Column(db.Boolean)
    monto_total = db.Column(db.Float)
    comentario = db.Column(db.String(256))
    state = db.Column(db.Boolean, default=True)
    factura_proveedor = db.Column(db.Boolean)
    factura_flete = db.Column(db.Boolean)
    es_flete = db.Column(db.Boolean, default=False)

    def get_unit_price(self):
        """Calcula el precio unitario total sumando monto de carga
        y costo de flete
        """
        self.precio_unitario = round((self.precio_carga + self.precio_flete)/self.cantidad,2)

    def actualizar_saldo_proveedor(self,suma):
        self.proveedor.actualizar_saldo(
            monto = self.precio_carga,
            factura = self.factura_proveedor,
            suma = suma
        )
    
    def actualizar_saldo_flete(self, suma):
        if self.envio:
                self.envio.flete.actualizar_saldo(
                    monto = self.precio_flete,
                    factura = self.factura_flete,
                    suma = suma
                )

    def borrar(self):
        self.producto.actualizar_stock(
            cantidad = self.cantidad,
            factura = self.factura_proveedor,
            entrada = False
        )
        actualizar_saldo_flete(suma=False)
        actualizar_saldo_proveedor(suma=False)
        self.satate = False

    def __repr__(self):
        return '<Compra nro: {id} >'.format(id=self.id)


class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, index=True)
    compras = db.relationship('Compra', backref='producto')
    ventas = db.relationship('Venta', backref='producto')
    nombre = db.Column(db.String(32), index=True, unique=True)
    precio = db.Column(db.Float)
    cantidad_a = db.Column(db.Float, default=0.00)
    cantidad_b = db.Column(db.Float, default=0.00)
    precio_compra = db.Column(db.Float)
    modificacion = db.Column(db.DateTime,default=datetime.utcnow) # => Guarda la fecha de la ultima modificacion
    offset = db.Column(db.Integer, default=0)
    last_mod=db.Column(db.Float, default=0)
    state = db.Column(db.Boolean, default=True)
    def get_offset(self):
        """establece un valor de offset que se usa para 
        discriminar los ids de [compras] inferiores al valor 
        de offset"""
        self.offset = len(self.compras)
        print('Valor actual de offset: {}'.format(self.offset))

    def calcular_precio_unitario(self):
        """Calcula el precio unitario de compra promedio 
        teniendo en cuenta un numero de compras anteriores. 
        El punto de partida esta dado por el valor de [offset] 
        hasta la ultima compra
        """
        parcial=self.last_mod
        if type(self.precio_compra) != float:
            print('Convirtiendo el tipo de dato precio')
            self.precio_compra = 0
        if self.offset !=0:
            if (self.offset+1) == len(self.compras):
                for i in range((self.offset), len(self.compras)):
                    print('PARCIAL POST EDIT {}'.format(parcial))
                    parcial += self.compras[i].precio_unitario
                    print('Offset IGUAL Precios: ${}'.format(self.compras[i].precio_unitario))
                    self.precio_compra = parcial/((len(self.compras)) - self.offset+1)
                    self.precio_compra = round(parcial/(len(self.compras) - self.offset+1),2)
            else:
                for i in range((self.offset), len(self.compras)):
                    parcial += self.compras[i].precio_unitario
                    print('Precios: ${}'.format(self.compras[i].precio_unitario))
                    print('PARCIAL {}'.format(parcial))
                    self.precio_compra = round(parcial/(len(self.compras) - self.offset+1),2)
        else:
            print('EL OFFSET ES CERO')
            for i in range(len(self.compras)):
                parcial += self.compras[i].precio_unitario
            self.precio_compra = round(parcial/(len(self.compras)+1 - self.offset),2)
        db.session.commit()
    
    def actualizar_stock(self, cantidad, factura, entrada):
        '''<cantidad> es la cantidad que sera agregada o restada del stock, si se quiere restar la cantidad el parametro debe ser < 0 lo contrario para sumar la cantidad.
        <factura -> Boolean> determina de dónde restar el stock
        '''
        if factura:
            if entrada:
                self.cantidad_a += cantidad
            else:
                self.cantidad_a -= cantidad
                if self.cantidad_a < 0:
                    self.cantidad_b += self.cantidad_a #resta a b lo que le falta para completar el pedido
                    self.cantidad_a = 0 #restaura a 0 para que no haya cant <0
        else:
            if entrada:
                self.cantidad_b += cantidad
            else:
                self.cantidad_b -= cantidad
                if self.cantidad_b < 0:
                    self.cantidad_a += self.cantidad_b #en este momento b es < 0
                    self.cantidad_b = 0 #restaura b 0 para evitar cant < 0

    def get_raw_prom(self):
        raw_prom = 0 
        for i in range(len(self.compras)):
            raw_prom += self.compras[i].precio_unitario
        raw_prom = raw_prom/len(self.compras)
        return raw_prom

    def borrar(self):
        self.state = False
    
    def restaurar(self):
        self.state = True
    def __repr__(self):
        return '<Producto {}>'.format(self.nombre)

# class Cuenta(db.Model):
#     id = db.Column(db.Integer, primary_key=True, index=True)
#     nombre = db.Column(db.String(32),default="Cuenta sin sombre")
#     monto = db.Column(db.Float, default=0)


#     pass

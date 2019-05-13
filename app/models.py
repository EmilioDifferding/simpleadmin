from datetime import datetime
from app import db

# Tablas relacionales
p_venta = db.Table('p_venta',
    db.Column('producto_id', db.Integer, db.ForeignKey('producto.id')),
    db.Column('venta_id', db.Integer, db.ForeignKey('venta.id'))
)

p_compra = db.Table('p_compra',
    db.Column('producto_id', db.Integer, db.ForeignKey('producto.id')),
    db.Column('compra_id', db.Integer, db.ForeignKey('compra.id'))
)


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
    
    def __repr__(self):
        return '<Cliente {}>'.format(self.nombre)

class Venta(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True, index=True)
    cliente_id = db.Column(db.Integer(), db.ForeignKey('cliente.id'), index=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), index=True)

    flete_proveedor = db.Column(db.String)
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

    #METODOS
    def get_utility(self):
        self.utilidad =round( (self.monto_total-((self.pc_u*self.cantidad)+self.costo_flete)),2)
    
    def actualizar_stock(self):
        """Determina de donde restar stock segun tipo factura
        si un stock queda negativo resta esa diferencia al siguiente
        stock y restable a 0 el negativo
        """
        p = self.producto
        print('Determinando factura')
        if (self.factura_cliente):
            print('Factura A')
            p.cantidad_a -= self.cantidad
            print('Resultado parcial stock A {}'.format(p.cantidad_a))
            if p.cantidad_a < 0:
                print('Stock A < 0...')
                p.cantidad_b += p.cantidad_a
                p.cantidad_a = 0
        else:
            print('Factura B')
            p.cantidad_b -= self.cantidad
            if p.cantidad_b < 0:
                p.cantidad_a += p.cantidad_b
                p.cantidad_b = 0

    def actualizar_saldo(self):
        """al ejecutar la venta, se le impyta el saldo al cliente y si hay un flete elegido, precio_flete se inputa también como saldo al proveedor del flete"""

        print('actualizando saldo de {}'.format(self.cliente.nombre))

        if self.factura_cliente:
            print('Actualizando saldo A en cliente')
            self.cliente.saldo_a += self.monto_total #self.precio_carga + self.costo_flete
        else:
            print('Actualizando saldo B en cliente')
            self.cliente.saldo_b += self.monto_total #self.precio_carga + self.costo_flete

        if self.flete_proveedor != '':
            pf = Proveedor.query.filter_by(nombre=self.flete_proveedor).first()

            c = Compra(
                proveedor = pf,
                monto_total = self.costo_flete,
                precio_flete = self.costo_flete,
                precio_carga = self.costo_flete,
                precio_unitario = self.costo_flete,
                factura_proveedor = self.factura_flete,
                flete_proveedor = pf.nombre,
                cantidad = 1,
                es_flete = True,
            )
            db.session.add(c)
            c.actualizar_saldo(self.costo_flete)


            # print('Actualizando saldo A de proveedor')
            # if self.factura_flete:
            #     pf.saldo_a += self.costo_flete
            # else:
            #     pf.saldo_b += self.costo_flete

        # if self.pagado:
        # if type(self.cliente.saldo) != float:
        #     print ('tipo Dato anterior {}'.format(type(self.cliente.saldo)))
        #     self.cliente.saldo = 0
        #     print('tipo de dato actual: {}'.format(type(self.cliente.saldo)))
        # self.cliente.saldo += self.precio_carga + self.costo_flete
        # if self.flete_proveedor != '':
        #     pf = Proveedor.query.filter_by(nombre=self.flete_proveedor).first()
        #     if type(pf.saldo) != float:
        #         pf.saldo = 0
        #     pf.saldo += self.costo_flete



    def borrar(self):
        """Desactiva la transaccion y restaura los saldos y stock"""
        if self.state:
            if self.cliente is not None:
                self.cliente.saldo -= self.precio_carga
                if self.costo_flete > 0:
                    if self.flete_proveedor != '':
                        pf = Proveedor.query.filter_by(nombre=self.flete_proveedor).first()
                        pf.saldo -= self.costo_flete
                        self.cliente.saldo -= self.costo_flete
                self.producto.cantidad += self.cantidad
            self.state = False

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

    def restar_saldo(self):
        if self.entrada:
            if self.factura:
                self.cliente.saldo_a -= self.monto
            else: self.cliente.saldo_b -= self.monto
        else:
            if self.factura:
                self.proveedor.saldo_b -= self.monto
            else:
                self.proveedor.saldo_b -= self.monto

class Cheque(db.Model):
    id = db.Column(db.Integer, unique=True, index=True, primary_key=True)
    cobro_id = db.Column(db.Integer, db.ForeignKey('cobro.id'), index=True)
    fecha = db.Column(db.DateTime())
    fecha_emision = db.Column(db.DateTime)
    fecha_cobro = db.Column(db.DateTime)
    banco = db.Column(db.String(32))
    numero = db.Column(db.String())
    importe = db.Column(db.Float)
    comentario = db.Column(db.String(240))
    state = db.Column(db.Boolean, default=True)
    factura = db.Column(db.Boolean)
    es_de_tercero = db.Column(db.Boolean)
    acreditado = db.Column(db.Boolean, default=False)
    es_entrada = db.Column(db.Boolean)


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
    

    def __repr__(self):
        return '<Proveedor {}>'.forman(self.nombre)


class Compra(db.Model):
    id = db.Column(db.Integer,primary_key=True, index=True, unique=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    # BACKREF: PROVEEDOR
    proveedor_id = db.Column(db.Integer(),db.ForeignKey('proveedor.id'), index=True)
    # BACKREF: PRODUCTO
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'))
    # cantidad de pies cuadrados en la carga
    cantidad = db.Column(db.Float)
    flete_proveedor = db.Column(db.String)

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

    def actualizar_saldo(self, monto):
        """al efectuar la compra, suma la compra a saldo del proveedor
        flah == es True cuando la compra se genera desde una venta para un proveedor
        """
        # print('actualizando saldo de {}'.format(self.proveedor.nombre))
        
        if self.factura_proveedor:
            print('Acualizanso saldo A')
            self.proveedor.saldo_a += monto
        else:
            print('Acualizanso saldo B')
            self.proveedor.saldo_b += monto
        
        # if self.flete_proveedor != '':
        #     pf = Proveedor.query.filter_by(nombre=self.flete_proveedor).first()
        #     if flag:
        #         if self.factura_flete:
        #             pf.saldo_a += self.precio_flete
        #         else:
        #             pf.saldo_b += self.precio_flete
        #     else:
        #         c = Compra(
        #         proveedor = pf,
        #         flete_proveedor = pf.nombre,
        #         monto_total = self.precio_flete,
        #         precio_carga = self.precio_flete,
        #         factura_proveedor = self.factura_flete,
        #         precio_unitario = self.precio_flete,
        #         cantidad = 1,
        #         precio_flete = 0,
        #         )
                # c.actualizar_saldo(flag=False) Genera loop infinito
                # db.session.add(c)

            

    def actualizar_stock(self):
        p = self.producto
        if (self.factura_proveedor):
            p.cantidad_a += self.cantidad
        else:
            p.cantidad_b += self.cantidad

    def borrar(self):
        if self.state:
            if self.proveedor is not None:
                self.proveedor.saldo -= self.precio_carga
                if self.precio_flete > 0:
                    if self.flete_proveedor != '':
                        pf = Proveedor.query.filter_by(nombre=self.flete_proveedor).first()
                        pf.saldo -= self.precio_flete
                self.producto.cantidad -= self.cantidad
            self.state = False
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

    def calcular_pecio_unitario(self):
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
            self.precio_compra = round(parcial/(len(self.compras) - self.offset),2)
        db.session.commit()

    def get_raw_prom(self):
        raw_prom = 0 
        for i in range(len(self.compras)):
            raw_prom += self.compras[i].precio_unitario
        raw_prom = raw_prom/len(self.compras)
        return raw_prom

    def __repr__(self):
        return '<Producto {}>'.format(self.nombre)

# class Cuenta(db.Model):
#     id = db.Column(db.Integer, primary_key=True, index=True)
#     nombre = db.Column(db.String(32),default="Cuenta sin sombre")
#     monto = db.Column(db.Float, default=0)


#     pass
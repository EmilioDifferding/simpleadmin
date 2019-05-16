from flask import render_template, url_for, redirect, flash, request
from app import app, db
from app.models import Cliente,Producto,Proveedor,Venta,Compra, Cobro, Cheque

#Formularios
from app.forms import CargarClienteForm,EditarClienteForm, CargarProveedorForm, EditarProveedorForm, EditarProductoForm, CargarCompraForm, CargarProductoForm, CargarVentaForm, CobranzaForm, CargarChequeForm

@app.route('/')
@app.route('/index')
def index():
    return render_template('base.html', title='Pagina proncipal')

@app.route('/cargar-producto', methods=['GET','POST'])
def cargar_producto():
    '''Ruta del form de carga de producto, lee, valida y guarda en db'''
    form = CargarProductoForm()
    if form.validate_on_submit():
        n = form.nombre.data
        p = round(form.precio.data,2)
        p_compra = round(form.precio_compra.data,2)
        producto = Producto(
            nombre=n,
            precio=p,
            precio_compra=p_compra,
            cantidad_a= form.cantidad_a.data,
            cantidad_b = form.cantidad_b.data,
            last_mod=p_compra
            )
        db.session.add(producto)
        db.session.commit()
        flash('Producto cargado!')
        return redirect(url_for('listar_productos'))
    return render_template('formulario-de-carga.html', form=form, title='Cargar nuevo producto', atras=url_for('listar_productos'))

@app.route('/productos')
def listar_productos():
    header_list = [
        'Producto','Cantidad', 'Precio de Compra','Precio de venta','Modificación']
    productos = Producto.query.all()
    return render_template('productos.html', header_list=header_list, productos=productos)

@app.route('/producto/<id>/editar', methods=['GET','POST'])
def editar_producto(id):
    p = Producto.query.filter_by(id=id).first()
    form = EditarProductoForm(nombre_original=p.nombre)
    if form.validate_on_submit():
        p.nombre = form.nombre.data
        p.precio = round(form.precio.data,2)
        p.cantidad_a = form.cantidad_a.data
        p.cantidad_b = form.cantidad_b.data
        if form.precio_compra.data != p.precio_compra:
            p.precio_compra = round(form.precio_compra.data,2)
            p.last_mod = form.precio_compra.data
            p.get_offset()
            flash('El precio de compra promedio fue restaurado, comenzará un nuevo calculo desde ahora')
        flash('Prducto Editado con exito')
        db.session.commit()
        return redirect(url_for('detalle_producto', id=p.id))
    elif request.method == 'GET':
        form.nombre.data = p.nombre
        form.precio.data = p.precio
        form.precio_compra.data = p.precio_compra
        form.cantidad_a.data = p.cantidad_a
        form.cantidad_b.data = p.cantidad_b
    return render_template('formulario-de-carga.html', form=form, title='Editar Producto: {}'.format(p.nombre),atras=url_for('detalle_producto',id=p.id))

@app.route('/producto/<id>')
def detalle_producto(id):
    p = Producto.query.filter_by(id=id).first_or_404()
    c_compras = len(p.compras)-p.offset
    return render_template('detalle-producto.html', p=p,c_compras=c_compras, title='Detalle de producto: {}'.format(p.nombre))

@app.route('/producto/<id>/borrar')
def borrar_producto(id):
    producto = Producto.query.filter_by(id=id).first_or_404()
    borrar(id, Producto)
    flash('producto: {nombre} borrado con exito.'.format(nombre=producto.nombre))
    return redirect(url_for('listar_productos'))

################################
###ADMINISTRACION DE CLIENTES###
################################

@app.route('/cargar-cliente', methods=['GET','POST'])
def cargar_cliente():
    form = CargarClienteForm()
    # form.validate_data(model=Cliente, nombre=form.nombre.data)
    if form.validate_on_submit():
        n = form.nombre.data
        c = form.contacto.data
        d = form.direccion.data
        t = form.telefono.data
        email = form.email.data
        cuit = form.cuit.data
        comentario = form.comentario.data
        cliente = Cliente(nombre=n, contacto=c, direccion=d, telefono=t, email=email, comentario=comentario, cuit=cuit)
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente cargado')
        return redirect(url_for('listar_clientes'))
    return render_template('formulario-de-carga.html', form=form, title='Cargar nuevo cliente', atras=url_for('listar_clientes'))

@app.route('/clientes')
def listar_clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', title='Lista de clientes', clientes=clientes)

@app.route('/cliente/<id>')
def detalle_cliente(id):
    cliente = Cliente.query.filter_by(id=id).first_or_404()
    return render_template('detalle-cliente.html', title='detalle de {}'.format(cliente.nombre), cliente=cliente)


@app.route('/cliente/<id>/editar', methods=['GET','POST'])
def editar_cliente(id):
    cliente = Cliente.query.filter_by(id = id).first()
    form = EditarClienteForm(
        nombre_orig = cliente.nombre,
        cuit_orig = cliente.cuit,
        email_orig=cliente.email
        )

    if form.validate_on_submit():
        cliente.nombre = form.nombre.data
        cliente.contacto = form.contacto.data
        cliente.direccion = form.direccion.data
        cliente.telefono = form.telefono.data
        cliente.email = form.email.data
        cliente.comentario = form.comentario.data
        cliente.cuit = form.cuit.data
        db.session.commit()
        flash('Editado correctamente.')
        print("COMMITED")
        return redirect(url_for('detalle_cliente', id=id))
    elif request.method == 'GET':
        form.nombre.data = cliente.nombre
        form.contacto.data = cliente.contacto
        form.cuit.data = cliente.cuit
        form.telefono.data = cliente.telefono
        form.direccion.data = cliente.direccion
        form.comentario.data = cliente.comentario
        form.email.data = cliente.email
    return render_template('formulario-de-carga.html', title='Editar: {}'.format(cliente.nombre), form=form, atras=url_for('listar_clientes'))


@app.route('/cliente/<id>/borrar')
def borrar_cliente(id):
    borrar(id, Cliente)
    flash('Cliente Borrado')
    return redirect(url_for('listar_clientes'))

#################################
##FIN DMINISTRACION DE CLIENTES##
################################# 

#####~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~####

#################################
#######INICIO PROVEEDORES########
#################################
@app.route('/cargar-proveedor', methods=['GET','POST'])
def cargar_proveedor():
    form = CargarProveedorForm()
    if form.validate_on_submit():
        n = form.nombre.data
        c = form.contacto.data
        d = form.direccion.data
        t = form.telefono.data
        email = form.email.data
        cuit = form.cuit.data
        comentario = form.comentario.data
        es_flete = form.es_flete.data
        proveedor = Proveedor(nombre=n, contacto=c, direccion=d, telefono=t, email=email, comentario=comentario, cuit=cuit, flete=es_flete)
        db.session.add(proveedor)
        db.session.commit()
        flash('Proveedor cargado')
        return redirect(url_for('listar_proveedores'))
    return render_template('formulario-de-carga.html', form=form, title='Cargar nuevo proveedor', atras=url_for('listar_proveedores'))

@app.route('/proveedores')
def listar_proveedores():
    proveedores = Proveedor.query.order_by('nombre').all()
    return render_template('proveedores.html', proveedores=proveedores, title='Lista de proveedores')

@app.route('/proveedor/<id>/editar', methods=['GET','POST'])
def editar_proveedor(id):
    proveedor = Proveedor.query.filter_by(id=id).first_or_404()
    form = EditarProveedorForm(nombre_orig=proveedor.nombre, cuit_orig=proveedor.cuit, email_orig=proveedor.email)

    if form.validate_on_submit():
        proveedor.nombre = form.nombre.data
        proveedor.contacto = form.contacto.data
        proveedor.direccion = form.direccion.data
        proveedor.telefono = form.telefono.data
        proveedor.email = form.email.data
        proveedor.comentario = form.comentario.data
        proveedor.cuit = form.cuit.data
        proveedor.flete = form.es_flete.data
        db.session.commit()
        flash('Editado correctamente.')
        print("COMMITED")
        return redirect(url_for('detalle_proveedor', id=id))
    elif request.method == 'GET':
        form.nombre.data = proveedor.nombre
        form.contacto.data = proveedor.contacto
        form.cuit.data = proveedor.cuit
        form.telefono.data = proveedor.telefono
        form.direccion.data = proveedor.direccion
        form.comentario.data = proveedor.comentario
        form.email.data = proveedor.email
        form.es_flete = proveedor.flete
    return render_template('formulario-de-carga.html', title='Editar: {}'.format(proveedor.nombre), form=form, atras=url_for('listar_proveedores'))

@app.route('/proveedor/<id>')
def detalle_proveedor(id):
    p = Proveedor.query.filter_by(id=id).first_or_404()
    return render_template('detalle-proveedor.html', p=p, title='Detalle de {}'.format(p.nombre))


@app.route('/borrar/<id>/proveedor')
def borrar_proveedor(id):
    borrar(id, Proveedor)
    flash('Proveedor borrado')
    return redirect(url_for('listar_proveedores'))

#################################
#########FIN PROVEEDORES#########
#################################

#####~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~####

#################################
##########INICIO VENTAS##########
################################# 

@app.route('/cargar-venta', methods=['GET','POST'])
def cargar_venta():
    '''Cuando se da al boton de VENTA despliega el form correspondiente, las choices son opciones de la base de datos de cada model. al confirmar se crea una transaccion y se cargan a db los datos, se inputa una deuda al cliente y aparece en sus saldos, a menos que marque en casilla de "pagado" 
    '''
    form = CargarVentaForm()
    form.clientes.choices=[
        (c.id, c.nombre)
        for c in Cliente.query.order_by('nombre').all()]
    form.producto.choices=[
        (p.id, p.nombre+' '+
        str(p.cantidad_a + p.cantidad_b))for p in Producto.query.order_by('nombre').all()]
    form.flete.choices = [(0,"---")]+[
        (f.id, f.nombre)for f in Proveedor.query.filter_by(flete=True).all()]

    if form.validate_on_submit():
        prod = Producto.query.filter_by(id=form.producto.data).first()
        cli = Cliente.query.filter_by(id=form.clientes.data).first()
        cant = form.cantidad.data
        if ((prod.cantidad_a + prod.cantidad_b) < form.cantidad.data):
            flash('No hay suficiente stock')
            return redirect(url_for('cargar_venta'))
        else:
            # TODO: // agregar codigo para hacer la venta efectiva
            if form.flete.data != 0:
                flete = Proveedor.query.filter_by(id=form.flete.data).first()
                flete = flete.nombre
            else: flete = ''
            venta = Venta(
                fecha = form.fecha.data,
                cliente = cli,
                producto = prod,
                cantidad = cant,
                pv_u = form.precio_unitario.data,
                pc_u = prod.precio_compra,
                precio_carga = form.sub_total.data,
                flete_proveedor = flete,
                costo_flete = form.costo_flete.data,
                monto_total =form.monto_total.data,
                comentario = form.comentario.data,
                pagado = form.pagado.data,
                factura_cliente = form.factura_cliente.data,
                factura_flete = form.factura_flete.data
            )
            db.session.add(venta)
            venta.get_utility()
            venta.producto.actualizar_stock(cantidad=cant, factura=factura_cliente)
            venta.actualizar_saldo_cliente()
            venta.actualizar_saldo_proveedor()
            db.session.commit()
            flash('Venta realizada con exito!')
            return redirect(url_for('listar_ventas'))
    
    return render_template('formulario-de-carga.html',form=form, title='Cargar venta nueva')

####LISTA LAS VENTAS EN ORDEN CRONOLOGICO###
@app.route('/ventas/')
def listar_ventas():
    ventas = Venta.query.filter_by(state=True).order_by(Venta.fecha.desc()).all()
    return render_template('ventas.html', ventas=ventas, title="registro de ventas(TODAS)")
# def listar_ventas():
#     ventas = Venta.query.order_by(Venta.fecha.desc()).all()
#     print(ventas)
#     return render_template('ventas.html',ventas=ventas,title='Registro de ventas', )


@app.route('/ventas/<string:factura>')
def listar_ventas_a(factura):
    if factura == 'a':
        ventas = Venta.query.filter_by(factura_cliente=True).order_by(Venta.fecha.desc())
        return render_template('ventas.html', ventas=ventas, title='Registros de ventas A')
    elif factura=='b':
        ventas = Venta.query.filter_by(factura_cliente=False).order_by(Venta.fecha.desc())
        return render_template('ventas.html', ventas=ventas, title='Registros de ventas A')
    else: return listar_ventas()

    
###DETALLE DE VENTA###
@app.route('/venta/<id>')
def detalle_venta(id):
    venta = Venta.query.filter_by(id=id).first()
    return render_template('venta.html', title='Detalle de Venta Nº {}'.format(id), venta=venta)

@app.route('/borrar/<id>/venta')
def borrar_venta(id):
    '''Borra la venta, devuelve el stock al producto y resta el saldo correspondiente'''
    venta = Venta.query.filter_by(id=id).first()
    if venta.state:
        venta.borrar()
        db.session.commit()
        flash('Venta Borrada')
    else: flash('Esta compra ya se ha dado de baja')
    return redirect(url_for('listar_ventas'))
#################################
##########FIN VENTAS#############
#################################

###~~~~~~~~~~~~~~~~~~~~~~~~~~~###

#################################
##########INICIO COMPRAS#########
#################################
@app.route('/cargar-compra', methods=['GET','POST'])
def cargar_compra():
    form = CargarCompraForm()
    form.proveedor.choices=[(p.id, p.nombre)for p in Proveedor.query.order_by('nombre').all()]
    form.producto.choices = [(p.id, p.nombre)for p in Producto.query.order_by('nombre').all()]
    form.flete.choices=[(0,"---")]+[(f.id, f.nombre) for f in Proveedor.query.filter_by(flete=True).all()]

    if form.validate_on_submit():
        producto = Producto.query.filter_by(id=form.producto.data).first()
        proveedor = Proveedor.query.filter_by(id=form.proveedor.data).first()
        cant = form.cantidad.data
        precio_carga = form.precio_carga.data
        flete = round(form.precio_flete.data,2)
        flete_p = form.flete.data
        monto_total = form.monto_total.data
        comentario = form.comentario.data
        pagado = form.pagado.data
        fecha = form.fecha.data
        compra = Compra(
            proveedor = proveedor,
            producto = producto,
            fecha = fecha,
            cantidad = cant,
            precio_flete = flete,
            precio_carga = round(precio_carga,2),
            pagado = pagado,
            monto_total = round(monto_total,2),
            factura_proveedor = form.factura_proveedor.data,
            factura_flete = form.factura_flete.data,
        )
        if flete_p != 0:
            flete_proveedor = Proveedor.query.filter_by(id=flete_p).first()
            compra.flete_proveedor = flete_proveedor.nombre
            compra_flete = Compra(
                proveedor = flete_proveedor,
                monto_total = flete,
                precio_flete = flete,
                precio_carga = flete,
                precio_unitario = flete,
                factura_proveedor = form.factura_flete.data,
                flete_proveedor = flete_proveedor.nombre,
                cantidad = 1,
                es_flete= True,
            )
            db.session.add(compra_flete)
            compra_flete.actualizar_saldo(flete)
        else: compra.flete_proveedor =''

        db.session.add(compra)
        compra.get_unit_price()
        compra.actualizar_saldo(round(precio_carga,2))
        compra.actualizar_stock()
        compra.producto.calcular_pecio_unitario()
        
        db.session.commit()
        flash('Compra cargada con Exito!')
        return redirect(url_for('listar_compras'))
        
    return render_template('formulario-de-carga.html', form=form, title='Cargar nueva compra', atras=url_for('listar_compras'))

@app.route('/compras')
def listar_compras():
    compras = Compra.query.filter_by(state=True).order_by(Compra.fecha.desc()).all()
    return render_template('compras.html',compras=compras,title='Registro de Compras')

@app.route('/compras/historial/bajas')
# TODO: Hacer una plantilla para visualizar y restituir las compras y ventas inactivas
def listar_compras_inactivas():
    c = Compra.query.filter_by(state=False).order_by(Compra.fecha.desc()).all()
    return render_template('compras.html', compras=c, title="COMPRAS INACTIVAS")

@app.route('/compra/<id>')
def detalle_compra(id):
    compra = Compra.query.filter_by(id=id).first_or_404()
    return render_template('detalle_compra.html', compra=compra, title='Detalle de compra Nº: {}'.format(compra.id))

@app.route('/compra/borrar/<id>')
def borrar_compra(id):
    compra = Compra.query.filter_by(id=id).first()
    if compra.state:
        compra.borrar()
        db.session.commit()
        flash('Compra borrada con éxito')
    else: flash('Esta compra ya esta desactivada')
    return redirect(url_for('listar_compras'))

#################################
###########FIN COMPRAS###########
#################################
#TODO: Redefinir las peticiones teniendo en cuenta las facturas
@app.route('/caja')
def caja():
    totalProdAcum = 0.0 #activos en productos
    prodAcum_a= 0.0 #activos productos factura A
    prodAcum_b= 0.0 #activos productos factura V
    saldoProveedores = 0.0 #$ que se va a ir
    spa=0.0
    spb=0.0
    sca=0.0
    scb=0.0
    saldoClientes = 0.0 #$ que va a entrar
    cobros = 0.0 #$ que ingreso
    pagos = 0.0 # $ que salio
    cheques_in =0.0 # cheques que se registraron como cobro
    cheques_out = 0.0 #cheuqes registrados como pagos

    prod = Producto.query.filter((Producto.cantidad_a > 0) | (Producto.cantidad_b > 0)).all()
    
    clientes = Cliente.query.filter((Cliente.saldo_a > 0) | (Cliente.saldo_b > 0)|(Cliente.saldo_a < 0 )| (Cliente.saldo_b < 0)).all()
    
    proveedores = Proveedor.query.filter((Proveedor.saldo_a > 0) | (Proveedor.saldo_b > 0)|(Proveedor.saldo_a < 0) | (Proveedor.saldo_b < 0)).all()

    entradas = Cobro.query.filter_by(entrada=True).all()
    salidas = Cobro.query.filter_by(entrada=False).all()
    
    def filtrar_True(l):
        return (l.factura)
    
    def filtrar_False(l):
        return ((l.factura) == False)

    entradas_a = 0.0
    for e in filter(filtrar_True, entradas):
        entradas_a += e.monto
    
    entradas_b = 0.0
    for e in filter(filtrar_False, entradas):
        entradas_b += e.monto

    salidas_a = 0.0
    for s in filter(filtrar_True, salidas):
        salidas_a += s.monto
    
    salidas_b = 0.0
    for s in filter(filtrar_False, salidas):
        salidas_b += s.monto
    
    # Valor acumulado de productos en stock
    for p in prod:
        prodAcum_a += (p.precio_compra * p.cantidad_a)
        prodAcum_b += (p.precio_compra * p.cantidad_b)
        totalProdAcum += (p.precio_compra*(p.cantidad_a + p.cantidad_b))
    print(totalProdAcum)
    print('CANTIDAD DE PROD CONTADOS {}'.format(len(prod)))

    # Total de saldos de clientes
    for c in clientes:
        sca += c.saldo_a
        scb += c.saldo_b
        saldoClientes += (c.saldo_a + c.saldo_b)
    saldoClientes = round(saldoClientes,2)
    
    # Total de saldos a proveedores
    for p in proveedores:
        spa += p.saldo_a
        spb += p.saldo_b 
        saldoProveedores += (p.saldo_a + p.saldo_b)
    saldoProveedores = round(saldoProveedores,2)

    # Entradas de dinero
    for e in entradas:
        cobros += round(e.monto,2)

    # Salidas de dinero
    for s in salidas:
        pagos +=round( s.monto,2)


    print('SALDO CLIENTES: {}'.format(saldoClientes))
    print('CLIENTES CONTADOS: {}'.format(len(clientes)))
    
    totin = (saldoClientes+cobros+totalProdAcum)
    totout = saldoProveedores+pagos
    balance = round(totin-totout,2)
    return render_template(
        'caja.html',
        title='Caja',
        pagos=pagos,
        cobros=cobros,
        saldoP=saldoProveedores,
        saldoC=saldoClientes,
        totalP_A=totalProdAcum,
        balance=balance,
        prodAcum_a=prodAcum_a,
        prodAcum_b=prodAcum_b,
        spa=spa,
        spb=spb,
        sca=sca,
        scb=scb,
        sa=salidas_a,
        sb=salidas_b,
        ea=entradas_a,
        eb=entradas_b
        )

@app.route('/clientes/saldos')
def saldo_clientes():
    saldoTotal = 0.0
    saldo_a = 0.0
    saldo_b = 0.0
    clientes = Cliente.query.filter((Cliente.saldo_a < 0)|(Cliente.saldo_a > 0)|(Cliente.saldo_b <0 )|(Cliente.saldo_b > 0)).order_by(Cliente.nombre).all()
    for cliente in clientes:
        saldoTotal += (cliente.saldo_a + cliente.saldo_b)
        saldo_a += cliente.saldo_a
        saldo_b += cliente.saldo_b
    return render_template(
        'saldo-cli.html',
        saldo=saldoTotal,
        clientes=clientes,
        saldo_a = saldo_a,
        saldo_b = saldo_b,
        title='Saldo de clientes')

@app.route('/proveedores/saldos')
def saldo_proveedores():
    saldoTotal=0.0
    saldo_a = 0.0
    saldo_b = 0.0
    # proveedores = Proveedor.query.all()
    proveedores = Proveedor.query.filter((Proveedor.saldo_a > 0)|(Proveedor.saldo_a<0)|(Proveedor.saldo_b < 0)| (Proveedor.saldo_b > 0)).order_by(Proveedor.nombre).all()
    for p in proveedores:
        saldoTotal += (p.saldo_a + p.saldo_b)
        saldo_a += p.saldo_a
        saldo_b += p.saldo_b
    return render_template(
        'saldo-prov.html',
        saldo=saldoTotal,
        proveedores=proveedores,
        saldo_b=saldo_b,
        saldo_a=saldo_a,
        title='Saldo a proveedores')


@app.route('/cobrar', methods=['GET','POST'])
def cobrar():
    form = CobranzaForm()
    form.cliente.choices = [(c.id, c.nombre)for c in Cliente.query.filter_by(state=True).order_by('nombre').all()]
    
    if form.validate_on_submit():
        cliente = Cliente.query.filter_by(id=form.cliente.data).first()
        if form.factura.data < 1:
            factura = True
        else:
            factura = False
        cobro = Cobro(
            proveedor = None,
            cliente = cliente,
            nombre = cliente.nombre,
            factura = factura,
            monto = round(form.monto.data,2),
            fecha = form.fecha.data,
            comentario = form.comentario.data,
            hay_cheque = form.hay_cheque.data,
            entrada = True,
            state = True,
        )
        db.session.add(cobro)
        cobro.restar_saldo()
        db.session.commit()

        if form.hay_cheque.data:
            flash('Ahora cargue los datos del cheque.')
            return redirect(url_for('cargar_cheque', id=cobro.id))
        else:
            flash('Cobro en efectivo cargado con exito!.')
            return redirect(url_for('listar-Cobros'))
    return render_template('formulario-de-carga.html', title='Cargar cobro de un cliente', form=form)

@app.route('/pagar', methods=['GET','POST'])
def pagar():
    form = CobranzaForm()
    form.cliente.choices = [(c.id, c.nombre)for c in Proveedor.query.filter_by(state=True).order_by('nombre').all()]

    if form.validate_on_submit():
        proveedor = Proveedor.query.filter_by(id=form.cliente.data).first()

        if form.factura.data < 1:
            factura = True
        else:
            factura = False
        cobro = Cobro(
            proveedor = proveedor,
            cliente = None,
            nombre = proveedor.nombre,
            factura= factura,
            monto = round(form.monto.data,2),
            fecha = form.fecha.data,
            comentario = form.comentario.data,
            hay_cheque = form.hay_cheque.data,
            entrada=False,
            state = True
        )
        db.session.add(cobro)
        cobro.restar_saldo()
        db.session.commit()
        
        if form.hay_cheque.data:
            flash('Ahora cargue los datos del cheque')
            return redirect(url_for('cargar_cheque', id=cobro.id))
        else:
            flash('Pago cargado con exito!.')
            return redirect(url_for('listar_pagos'))
    return render_template('formulario-de-carga.html', title='Cargar un pago de cliente', form=form)

@app.route('/cargar-cheque/<id>', methods=['GET','POST'])
def cargar_cheque(id):
    form = CargarChequeForm()
    cobro = Cobro.query.filter_by(id=id).first_or_404()
    if form.validate_on_submit():
        if cobro.entrada:
            es_de_tercero = True
        else:
            es_de_tercero = False
        cheque = Cheque(
            fecha= form.fecha.data,
            fecha_emision = form.fecha_emision.data,
            fecha_cobro = form.fecha_cobro.data,
            numero = form.numero.data,
            banco = form.banco.data,
            importe = form.importe.data,
            comentario = form.comentario.data,
            cobro=cobro,
            es_de_tercero = es_de_tercero
            )
        db.session.add(cheque)
        db.session.commit()
        flash('Cheque cargado')
        return redirect(url_for('caja'))
    elif request.method =='GET':
        form.importe.data = cobro.monto
    return render_template('formulario-de-carga.html', title='Cargar Cheque', form=form)


@app.route('/registro-de-cobros')
def listar_cobros():
    cobros = Cobro.query.filter_by(entrada=True).order_by(Cobro.fecha.desc()).all()
    return render_template('cobros.html', title='Registro de cobros', cobros=cobros)

@app.route('/registro-de-pagos')
def listar_pagos():
    pagos = Cobro.query.filter_by(entrada=False).order_by(Cobro.fecha.desc()).all()
    return render_template('pagos.html', title='Registro de pagos', pagos=pagos)

@app.route('/registro-de-cheques')
def listar_cheques():
    cheques = Cheque.query.filter_by(state=True)

    cheques_in = filter(lambda cheque: cheque.es_entrada & state, cheques)
    cheques_out = filter(lambda cheque: not(cheque.es_entrada) & state, cheques)

    return render_template(
        'lista-cheques.html',
        cheques=cheques,
        cheques_in=cheques_in,
        cheques_out=cheques_out,
        title = 'lista de cheques')

@app.route('/detalle-cheque/<id>')
def detalle_cheque(id):
    c = Cheque.query.filter_by(id=id).first_or_404()
    emisor = c.cobro.nombre
    return render_template('detalle_cheque.html',c=c, title='Detalle de cheque Nº: {}'.format(c.numero), emisor=emisor)

@app.route('/borrar-cobro/<id>')
def borrar_cobro(id):
    cobro = Cobro.query.filter_by(id=id).first_or_404()
    if cobro.forma_pago == 'Cheque':
        cheque = cobro.cheques[0].id
        borrar(cheque, Cheque)
    sumar_saldo(Cliente, cobro.cliente_id, cobro.monto)
    borrar(cobro.id, Cobro)
    db.session.commit()
    flash('Este cobro fue eliminado, se recupero el saldo del cliente')
    print('Cobro: {}, cliente: {}'.format(cobro, cobro.cliente_id) )
    return redirect(url_for('listar_cobros'))


def sumar_saldo(modelo, id, monto):
    print('Ejecuta la suma del saldo')
    modelo = modelo.query.filter_by(id=id).first()
    modelo.saldo += monto

def restar_saldo(modelo, id, monto):
    print('Ejecuta restar saldo() id:{}'.format(id))
    modelo = modelo.query.filter_by(id=id).first()
    modelo.saldo -= monto

def borrar(id, modelo):
    modelo = modelo.query.filter_by(id = id).first()
    db.session.delete(modelo)
    db.session.commit()


@app.route('/tet')
def pagosycobros():
    cobro = Cobro.query.all()
    return render_template('tet.html', cobro = cobro)
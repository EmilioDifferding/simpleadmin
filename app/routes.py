from flask import render_template, url_for, redirect,jsonify, flash, request
from app import app, db
from app.models import Cliente,Producto,Proveedor,Venta,Compra, Cobro, Cheque, Servicio, Chequera
from datetime import date, datetime, timedelta

#Formularios
from app.forms import CargarClienteForm,EditarClienteForm, CargarProveedorForm, EditarProveedorForm, EditarProductoForm, CargarCompraForm, CargarProductoForm, CargarVentaForm, CobranzaForm, CargarChequeForm,ChequedeTercero, CargarChequeraForm

@app.route('/')
@app.route('/index')
def index():
    return render_template('base.html', title='Pagina principal')

@app.route('/precio/<id>')
def precio(id):
    p = Producto.query.filter_by(id=id).first()
    return str(p.precio)


@app.route('/chequera',methods=['GET','POST'])
def c ():
    form = CargarChequeForm()
    chequeras = Chequera.query.filter_by(state = True).all()
    p = Proveedor.query.filter_by(state=True).all()
    lista = list(filter(lambda chequera: chequera.state, chequeras))
    listaChequera = [{'id': c.id, 'numero':c.numero_chequera, 'banco':c.banco} for c in lista]
    c = chequeras
    return render_template('cargar-pago.html',proveedores=p, chequeras = c, form=form)

@app.route('/_obtener_cheques/<id>', methods=['GET'])
def obtener_cheqeus(id):
    chequera = Chequera.query.filter_by(id = id).first()
    cheques = Cheque.query.filter_by(chequera = chequera)
    print(list(cheques))
    listaCheques=list(filter(lambda cheque: (cheque.acreditado==False)&(cheque.emitido ==False), cheques))
    numeroCheque = [{'id':c.id , 'numero':c.numero} for c in listaCheques]
    print (jsonify(numeroCheque))
    print(id)
    return jsonify( numeroCheque)
    # return str([chequera.cheques.count(), chequera.banco, numeroCheque])

@app.route('/_obtener_cheques/tercero/')
def chequeTercero():
    cheques = Cheque.query.filter_by(state=True).filter_by(acreditado=False).filter_by(es_de_tercero = True).filter_by(emitido=False).all()
    print('chequesTercerosFiltrados',cheques)
    lista = [{'id':c.id, 'numero':c.numero, 'monto':c.importe, 'banco':c.banco, 'postdatado':datetime.strftime(c.fecha_cobro, '%d/%m/%y'),'factura':c.factura} for c in cheques]
    print(jsonify(lista))
    return jsonify(lista)

@app.route('/_obtener_cheques/tercero/<id>')
def getValue (id):
    cheque = Cheque.query.filter_by(id=id).first()
    return str(cheque.importe)

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
    envios = Servicio.query.filter_by(proveedor_id=p.id).all()
    return render_template('detalle-proveedor.html', p=p,envios=envios, title='Detalle de {}'.format(p.nombre))


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
        for c in Cliente.query.filter_by(state=True).order_by('nombre').all()]
    form.producto.choices=[
        (p.id, p.nombre+' '+
        str(p.cantidad_a + p.cantidad_b))for p in Producto.query.filter_by(state=True).order_by('nombre').all()]
    form.flete.choices = [(0,"---")]+[
        (f.id, f.nombre)for f in Proveedor.query.filter_by(flete=True).filter_by(state=True).order_by('nombre').all()]
    
    if form.validate_on_submit():
        producto = Producto.query.filter_by(id = form.producto.data).first()
        if (producto.cantidad_a + producto.cantidad_b) < form.cantidad.data:
            flash('No hay suficiente stock para realizar esta venta')
            return redirect(url_for('cargar_venta'))
        else:
            cliente = Cliente.query.filter_by(id = form.clientes.data).first()
            if form.flete.data != 0:
                flete = Proveedor.query.filter_by(id=form.flete.data).first()
            else: flete = None
        
        venta = Venta(
            fecha = form.fecha.data,
            cliente = cliente,
            producto = producto,
            cantidad = form.cantidad.data,
            pv_u = form.precio_unitario.data,
            pc_u = producto.precio_compra,
            precio_carga = form.sub_total.data,
            costo_flete = form.costo_flete.data,
            monto_total =form.monto_total.data,
            comentario = form.comentario.data,
            
            factura_cliente = form.factura_cliente.data,
            factura_flete = form.factura_flete.data
            )
        if flete is not None:
            service = Servicio(flete=flete, venta=venta)
            db.session.add(service)
            venta.actualizar_saldo_proveedor(suma=True)
        else:
            db.session.add(venta)
        venta.get_utility()
        venta.producto.actualizar_stock(
            cantidad = form.cantidad.data,
            factura = form.factura_cliente.data,
            entrada = False # porque es salida de producto, se resta del stock
        )
        venta.actualizar_saldo_cliente(suma=True)
        db.session.commit()
        flash ('Venta Realizada con éxito.')
        return redirect(url_for('listar_ventas'))
    elif request.method == 'GET':
        form.cantidad.data = 0
        form.sub_total.data = 0
        form.costo_flete.data = 0
        form.monto_total.data = 0
    return render_template(
        'formulario-de-carga.html',
        form = form,
        title = 'Cargar nueva venta'
        )

####LISTA LAS VENTAS EN ORDEN CRONOLOGICO###
@app.route('/ventas/')
def listar_ventas():
    ventas = Venta.query.filter_by(state=True).order_by(Venta.fecha.desc()).all()
    funcion='filtrarVentas()'
    return render_template('ventas.html', ventas=ventas, title="registro de ventas (TODAS)", funcion=funcion)

@app.route('/filtrar-ventas', methods=['POST'])
def filtrar_ventas():
    formato = "%Y-%m-%d"
    if request.method == 'POST':
        r = request.get_json()
        inicio = datetime.strptime(r['inicio']['inicio'],formato)
        fin = datetime.strptime(r['fin']['fin'],formato)
        if(fin<inicio):
            return 'corroborar fecha'

        ventas = Venta.query.filter_by(state=True).order_by(Venta.id.desc()).all()
        ventasFiltradas = [v for v in ventas if v.fecha > inicio and v.fecha < fin+timedelta(days=1)]
        lista = []

        keys = [
            'id', 'fecha',
            'cliente','cliente_id',
            'producto', 'producto_id',
            'cantidad', 'precioCompra',
            'precioVenta', 'precioCarga',
            'precioFlete', 'flete', 'flete_id',
            'total', 'utilidad','factura_cliente',
            ]
        for venta in ventasFiltradas:
            d = dict.fromkeys(keys,0)
            d['id'] = venta.id
            d['fecha'] = datetime.strftime(venta.fecha, format='%d/%m/%y - %H:%M')
            d['cliente'] = venta.cliente.nombre
            d['cliente_id'] = venta.cliente.id
            d['producto'] = venta.producto.nombre
            d['producto_id'] = venta.producto.id
            d['cantidad'] = venta.cantidad
            d['precioCompra'] = venta.pc_u
            d['precioVenta'] = venta.pv_u
            d['precioCarga'] = venta.precio_carga
            d['precioFlete'] = venta.costo_flete
            d['total'] = venta.monto_total
            d['factura_cliente'] = venta.factura_cliente
            d['utilidad'] = venta.utilidad
            if venta.envio is not None:
                d['flete'] = venta.envio.flete.nombre
                d['flete_id'] = venta.envio.flete.id
            else:
                d['flete'] = 'Sin Envio'
                # d['flete_id'] = 'null'
            lista.append(d)

        print ('LA LISTA',lista)

        return jsonify(lista)

@app.route('/ventas/<string:factura>')
def listar_ventas_a(factura):
    if factura == 'a':
        ventas = Venta.query.filter_by(factura_cliente=True).order_by(Venta.fecha.desc())
        return render_template('ventas.html', ventas=ventas, title='Registros de ventas A')
    elif factura=='b':
        ventas = Venta.query.filter_by(factura_cliente=False).order_by(Venta.fecha.desc())
        return render_template('ventas.html', ventas=ventas, title='Registros de ventas B')
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
    form.proveedor.choices=[(p.id, p.nombre)for p in Proveedor.query.filter_by(state=True).order_by('nombre').all()]
    form.producto.choices = [(p.id, p.nombre)for p in Producto.query.filter_by(state=True).order_by('nombre').all()]
    form.flete.choices=[(0,"---")]+[(f.id, f.nombre) for f in Proveedor.query.filter_by(state=True).filter_by(flete=True).order_by('nombre').all()]

    if form.validate_on_submit():
        producto = Producto.query.filter_by(id=form.producto.data).first()
        proveedor = Proveedor.query.filter_by(id=form.proveedor.data).first()
        precio_flete = round(form.precio_flete.data,2)
        precio_carga = round(form.precio_carga.data,2)
        monto_total = round(form.monto_total.data,2)
        comentario = form.comentario.data
        # pagado = form.pagado.data
        compra = Compra(
            proveedor = Proveedor.query.filter_by(id=form.proveedor.data).first(),
            producto = Producto.query.filter_by(id=form.producto.data).first(),
            fecha = form.fecha.data,
            cantidad = form.cantidad.data,
            precio_flete = precio_flete,
            precio_carga = precio_carga,
            
            monto_total = monto_total,
            factura_proveedor = form.factura_proveedor.data,
            factura_flete = form.factura_flete.data,
        )
        compra.get_unit_price()
        db.session.add(compra)

        # def hay_servicio():
        if form.flete.data != 0:
            flete = Proveedor.query.filter_by(id=form.flete.data).first()
            servicio = Servicio(flete=flete, compra=compra)
            compra.actualizar_saldo_flete(suma=True)
            db.session.add(servicio)


        compra.actualizar_saldo_proveedor(suma=True)
        
        compra.producto.actualizar_stock(
            cantidad = form.cantidad.data,
            factura = form.factura_proveedor.data,
            entrada = True
        )
        
        # compra.actualizar_saldo_flete(suma=True)
        # if hay_servicio():
        #     db.session.add(hay_servicio()[1])
        db.session.commit()
        compra.producto.calcular_precio_unitario()
        flash('Compra cargada con Exito!')
        return redirect(url_for('listar_compras'))
        
    return render_template('formulario-de-carga.html', form=form, title='Cargar nueva compra', atras=url_for('listar_compras'))

@app.route('/compras')
def listar_compras():
    compras = Compra.query.filter_by(state=True).order_by(Compra.id.desc()).all()
    funcion='filtrarCompras()'
    return render_template('compras.html',compras=compras,title='Registro de Compras', funcion=funcion)

@app.route('/filtrar-compras', methods=['GET','POST'])
def filtrar_compras():
    formato = "%Y-%m-%d"
    if request.method == 'POST':
        r = request.get_json()
        inicio = datetime.strptime(r['inicio']['inicio'],formato)
        fin = datetime.strptime(r['fin']['fin'],formato)
        if(fin<inicio):
            return 'corroborar fecha'

        compras = Compra.query.filter_by(state=True).order_by(Compra.fecha.desc()).all()
        comprasFiltradas = [c for c in compras if c.fecha > inicio and c.fecha< fin+timedelta(days=1)]
        lista = []

        keys = [
            'id',
            'proveedor', 'fecha',
            'producto', 'valor_unitario',
            'p_carga', 'p_flete',
            'factura_prov', 'flete',
            'cantidad', 'total',
            'proveedor_id', 'flete_id',
            'producto_id'
            ]
        for compra in comprasFiltradas:
            d = dict.fromkeys(keys,0)
            d['id'] = compra.id
            d['fecha'] = compra.fecha
            d['proveedor'] = compra.proveedor.nombre
            d['producto'] = compra.producto.nombre
            d['cantidad'] = compra.cantidad
            d['valor_unitario'] = compra.precio_unitario
            d['p_carga'] = compra.precio_carga
            d['p_flete'] = compra.precio_flete
            d['total'] = compra.monto_total
            d['factura_prov'] = compra.factura_proveedor
            d['proveedor_id'] = compra.proveedor.id
            d['producto_id'] = compra.producto.id
            if compra.envio is not None:
                d['flete'] = compra.envio.flete.nombre
                d['flete_id'] = compra.envio.flete.id
            else:
                d['flete'] = 'Sin Envio'
                # d['flete_id'] = 'null'
            lista.append(d)

        print ('LA LISTA',lista)

        return jsonify(lista)

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
@app.route('/administracion')
def administracion():
    #Productos [ACTIVOS] con cantidad > de 0
    productos = Producto.query.filter(
        Producto.state & ((Producto.cantidad_a>0)|(Producto.cantidad_b>0)|
        (Producto.cantidad_a<0)|(Producto.cantidad_b<0))
    ).all()

    #Clientes [ACTIVOS] con saldos != de 0
    clientes = Cliente.query.filter(
        (Cliente.state) & ((Cliente.saldo_a > 0) | (Cliente.saldo_b > 0)|(Cliente.saldo_a < 0 )| (Cliente.saldo_b < 0))
        ).all()

    #Proveedores [ACTIVOS] con saldos != de 0
    proveedores = Proveedor.query.filter(
        Proveedor.state & ((Proveedor.saldo_a>0)|(Proveedor.saldo_b>0)|
        (Proveedor.saldo_a<0)|(Proveedor.saldo_b<0))
    ).all()

    #Lista de entradas y salidas que no se hayan borrado
    inOut = Cobro.query.filter_by(state=True).all() 

    entradas = list(filter(lambda e: e.entrada, inOut))
    entradas_a = list(filter(lambda entrada: entrada.factura, entradas))
    entradas_b = list(filter(lambda entrada: not(entrada.factura),entradas))

    salidas = list(filter(lambda e: not(e.entrada),inOut))
    salidas_a = list(filter(lambda salida: salida.factura, salidas))
    salidas_b = list(filter(lambda salida: not(salida.factura), salidas))

    def getMonto(lista):
        """ Obtiene de Cobro los de cada monto y los suma"""
        monto = 0.0
        for element in lista:
            monto += element.monto
        return round(monto,2)

    cobranzas_a = getMonto(entradas_a)
    cobranzas_b = getMonto(entradas_b)
    pagos_a = getMonto(salidas_a)
    pagos_b = getMonto(salidas_b)

    chequesInAcr = Cheque.query.filter_by(state=True).filter_by(acreditado=True).filter_by(es_entrada=True).all()
    cobrosEfectivo = Cobro.query.filter_by(state=True).filter_by(entrada=True).filter_by(forma_pago='efectivo').all()
    chequesOutAcred = Cheque.query.filter_by(state=True).filter_by(acreditado=True).filter_by(es_entrada=False).all()
    pagosEfectivo = Cobro.query.filter_by(state=True).filter_by(entrada=False).filter_by(forma_pago='efectivo').all()
    cOutAcred = 0.0
    cInAcred = 0.0
    inEfectivo = 0.0
    outEfectivo = 0.0
    for cheques in chequesInAcr:
        cInAcred += cheques.importe
    for cobro in cobrosEfectivo:
        inEfectivo += cobro.monto
    for cheques in chequesOutAcred:
        cOutAcred += cheques.importe
    for pago in pagosEfectivo:
        outEfectivo += pago.monto

    caja = cobranzas_a + cobranzas_b - pagos_a - pagos_b
    caja2 = inEfectivo + cInAcred - cOutAcred -outEfectivo
    def getAcumuladoProductos(lista):
        acum_a = 0.0
        acum_b = 0.0
        for element in lista:
            acum_a += (element.cantidad_a*element.precio_compra)
            acum_b += (element.cantidad_b*element.precio_compra)
        return [round(acum_a,2), round(acum_b,2), round((acum_a+acum_b),2)]
    acumuladoProductos = getAcumuladoProductos(productos)

    def getSaldos(lista):
        """ Devuelve una lista con los saldos_a y saldos_b y ambos sumados"""
        saldo_a= 0.0
        saldo_b = 0.0
        saldoTotal = 0.0
        for element in lista:
            saldo_a += element.saldo_a
            saldo_b += element.saldo_b
            saldoTotal = saldo_a + saldo_b
        return [round(saldo_a,2) , round(saldo_b,2), round(saldoTotal,2)] 

    saldoClientes = getSaldos(clientes)
    saldoProveedores = getSaldos(proveedores)

    chequesDeTerceros = Cheque.query.filter(Cheque.state & Cheque.es_de_tercero & (not Cheque.acreditado)).all()

    chequesPropios = Cheque.query.filter(Cheque.state & (not Cheque.es_de_tercero) &(not Cheque.acreditado)).all()
    totalCheques = 0.0
    for c in chequesPropios:
        totalCheques += c.importe
    
    balance = saldoClientes[2]+acumuladoProductos[2]+caja-saldoProveedores[2]-totalCheques
    return render_template(
        'administracion.html',
        title='Caja',
        saldoClientes = saldoClientes,
        saldoProveedores = saldoProveedores,
        pagos_a = pagos_a,
        pagos_b = pagos_b,
        cobranzas_a = cobranzas_a,
        cobranzas_b = cobranzas_b,
        acum = acumuladoProductos,
        balance=balance,
        caja=caja,
        caja2 = caja2
    )


""" def caja():
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

    prod = Producto.query.filter(((Producto.cantidad_a > 0) | (Producto.cantidad_b > 0))&(Producto.state)).all()
    
    clientes = Cliente.query.filter(((Cliente.saldo_a > 0) | (Cliente.saldo_b > 0)|(Cliente.saldo_a < 0 )| (Cliente.saldo_b < 0))&(Cliente.state)).all()
    
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
    #TODO: FORMULA BALANCE
    #saldo proveedores, cheques emitidos. caja.
    # +Stock - (salida)Saldoproveedores +SaldoClientes +Caja Efectivo y cheque -Cheques emitidos. 
    #Implementar chequera 
    
    balance = round(totin-totout,2)
    return render_template(
        'caja.html',
        title='Caja',
        caja = caja,
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
        ) """

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
    clientes = Cliente.query.filter_by(state=True).all()
    if request.method == 'POST':
        req = request.get_json()
        cliente = Cliente.query.filter_by(id=req['cliente']['id']).first()
        
        if int(req['cliente']['factura']) < 1:
            factura = True
        else:
            factura = False
        
        if req['cliente']['forma_pago'] == 'cheque':
            hay_cheque = True
            forma_pago = 'cheque'
        else:
            hay_cheque = False
            forma_pago = 'efectivo'
        cobro = Cobro(
            proveedor = None,
            cliente = cliente,
            nombre = cliente.nombre,
            factura = factura,
            monto = round(req['cliente']['monto'],2),
            fecha = datetime.utcnow(),
            comentario = req['cliente']['comentario'],
            hay_cheque = hay_cheque,
            entrada = True,
            state = True,
            forma_pago=forma_pago
        )
        db.session.add(cobro)
        cobro.restar_saldo()

        if hay_cheque:
            cheque = Cheque(
                fecha_emision = datetime.strptime(req['cheque']['fechaEmision'], "%Y-%m-%d"),
                fecha_cobro = datetime.strptime(req['cheque']['fechaCobro'],"%Y-%m-%d"),
                banco = req['cheque']['entidad'],
                importe=req['cheque']['monto'],
                numero = req['cheque']['numero'],
                comentario = cobro.comentario,
                fecha = datetime.utcnow(),
                emisor = cliente.nombre,
                es_entrada= True,
                es_de_tercero=True,
                cliente = cliente,
                factura =factura,
                proveedor=None,
                cobro = cobro,
            )
            cheque.get_destino()
            db.session.add(cheque)
            db.session.commit()
            return 'cobro con cheque OK'
        else:
            db.session.commit()
            return 'Cobro efectivo OK'
    return render_template('cargar-cobranza.html', title='Cargar cobro de un cliente', clientes=clientes)


@app.route('/decodificar',methods=['GET','POST'])
def decodificar():
    print(request.is_json)
    c = request.get_json()
    if int(c['proveedor']['factura']) < 1:
        factura = True
    else:
        factura = False
    cobro = Cobro(
        # forma_pago = c['forma_pago'],
        monto =int(c['proveedor']['monto']),
        comentario=c['proveedor']['comentario'],
        proveedor = Proveedor.query.filter_by(id=c['proveedor']['id']).first(),
        entrada = False,
        factura = factura,
        fecha = datetime.strptime(c['proveedor']['fecha'],"%Y-%m-%d"),
    )
    db.session.add(cobro)
    db.session.commit()
    print (cobro)
    print(cobro.proveedor.nombre)
    print(c['proveedor']['forma_pago'])
    print(c)
    return str(c)

@app.route('/pagar', methods=['GET', 'POST'])
def pagar():
    chequeras = Chequera.query.filter_by(state=True).all()
    p = Proveedor.query.filter_by(state=True).all()
    chequesTerceros = Cheque.query.filter_by(state=True).filter_by(es_de_tercero =True).filter_by(acreditado= False).filter_by(emitido= False).all()
    print('chequesTercerosFiltrados',chequesTerceros)
    
    if request.method == 'POST':
        req = request.get_json()
        proveedor = Proveedor.query.filter_by(id=req['proveedor']['id']).first()
        # proveedor = Proveedor.query.filter_by(id=c['proveedor']['id']).first()
        if int(req['proveedor']['factura']) < 1:
            factura = True
        else:
            factura = False
        if req['proveedor']['forma_pago'] == 'chequera':
            hay_cheque = True
            forma_pago = 'cheque'
        elif req['proveedor']['forma_pago']=='cheque3ro':
            for id in req['cheq']['cids']:
                print(id)
            hay_cheque = True
            forma_pago = 'cheque'
        else:
            hay_cheque = False
            forma_pago = 'efectivo'

        
        pago = Cobro(
            monto = round(float(req['proveedor']['monto']),2),
            comentario = req['proveedor']['comentario'],
            proveedor = proveedor,
            nombre = proveedor.nombre,
            entrada = False,
            factura = factura,
            fecha = datetime.utcnow(),
            state = True,
            hay_cheque = hay_cheque,
            forma_pago = forma_pago,
            )
        db.session.add(pago)
        pago.restar_saldo()
        #db.session.commit()
        if hay_cheque:
            if req['proveedor']['forma_pago'] == 'chequera':
                cheque = Cheque.query.filter_by(id=req['cheq']['id']).first()
                cheque.fecha = datetime.utcnow()
                cheque.fecha_emision = datetime.strptime(req['cheq']['fecha_emision'], "%Y-%m-%d")
                cheque.fecha_cobro = datetime.strptime(req['cheq']['fecha_cobro'], "%Y-%m-%d")
                cheque.cobro = pago
                cheque.importe = round(float(req['proveedor']['monto']),2)
                cheque.comentario = req['proveedor']['comentario']
                cheque.es_entrada = False
                cheque.es_de_tercero = False
                cheque.acreditado = False
                cheque.proveedor = proveedor
                cheque.emitir()
                cheque.get_destino()
                cheque.get_emisor()
                db.session.commit()
                return 'El Pago se realizo con éxito'
            elif req['proveedor']['forma_pago']=='cheque3ro':
                chequesTerceros = []
                for id in req['cheq']['cids']:
                    c = Cheque.query.filter_by(id=id).first()
                    c.es_entrada =False
                    c.emitir()
                    pago.cheques.append(c)
                    c.proveedor = proveedor
                    c.get_destino()
                    print('emitidoooo')
                db.session.commit()
                return 'Cheques cargados'
        else:
            db.session.commit()
            return 'Pago Cargado'
    
    else:
        return render_template('cargar-pago.html', proveedores=p, chequeras=chequeras, title='Cargar pago a proveedor')




# BACKUP FORMA ANTIGUA
"""      strptime(c['proveedor']['fecha'],"%Y-%m-%d")
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
            return redirect(url_for('listar_pagos')) """

@app.route('/cargar-cheque/<id>', methods=['GET','POST'])
def cargar_cheque(id):
    control = True
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
            es_de_tercero = es_de_tercero,
            es_entrada = cobro.entrada,
            factura = cobro.factura,
            cliente = cobro.cliente
            )
        db.session.add(cheque)
        db.session.commit()
        flash('Cheque cargado')
        return redirect(url_for('administracion'))
    elif request.method =='GET':
        form.importe.data = cobro.monto
    return render_template('formulario-de-carga.html', title='Cargar Cheque', form=form, control=control, id=cobro.id)

@app.route('/cargar-chequera', methods=['GET','POST'])
def cargar_chequera():
    form = CargarChequeraForm()
    ultima_chequera = Chequera.query.all()
    if form.validate_on_submit():
        chequera = Chequera(
            numero_chequera = form.numero_chequera.data,
            cantidad_cheques = form.cantidad_cheques.data,
            banco = form.banco.data,
        )
        db.session.add(chequera)
        db.session.commit()
        chequera.generate(inicio=form.inicio.data, chequera=chequera)
        db.session.commit()
        flash('Chequera cargada!')
    elif request.method == 'GET':
        form.numero_chequera.data = len(ultima_chequera)+ 1
    return render_template('formulario-de-carga.html', form=form, title='Cargar Chequera')
    


@app.route('/cheque-tercero/<id>',methods=['GET','POST'])
def cheque_tercero(id):
    form = ChequedeTercero()
    form.cheques.choices = [(c.id, c.importe)for c in Cheque.query.filter_by(state=True).filter_by(es_de_tercero=True).order_by('importe').all()]
    return render_template('formulario-de-carga.html',form=form)

@app.route('/filtrar-cobros', methods=['POST'])
#TODO: COMPLETAR Y REALIZAR EL ENVIO QUE FALTA A FILTRO-FECHAS.js
def filtrar_cobros():
    formato = "%Y-%m-%d"
    if request.method == 'POST':
        r = request.get_json()
        inicio = datetime.strptime(r['inicio']['inicio'],formato)
        fin = datetime.strptime(r['fin']['fin'],formato)
        if(fin<inicio):
            return 'la fecha de inicio debe ser menor a la de fin.'

        cobros = Cobro.query.filter_by(state=True).order_by(Venta.id.desc()).filter_by(entrada=True).all()
        cobrosFiltrados = [c for c in cobros if c.fecha > inicio and c.fecha < fin+timedelta(days=1)]
        lista = []

        keys = [
            'id', 'fecha',
            'cliente','cliente_id',
            'comentario', 'monto',
            'forma_pago', 'factura',
            'cheques'
            ]
            
        for venta in ventasFiltradas:
            d = dict.fromkeys(keys,0)
            d['id'] = venta.id
            d['fecha'] = datetime.strftime(venta.fecha, format='%d/%m/%y - %H:%M')
            d['cliente'] = venta.cliente.nombre
            d['cliente_id'] = venta.cliente.id
            d['producto'] = venta.producto.nombre
            d['producto_id'] = venta.producto.id
            d['cantidad'] = venta.cantidad
            d['precioCompra'] = venta.pc_u
            d['precioVenta'] = venta.pv_u
            d['precioCarga'] = venta.precio_carga
            d['precioFlete'] = venta.costo_flete
            d['total'] = venta.monto_total
            d['factura_cliente'] = venta.factura_cliente
            d['utilidad'] = venta.utilidad
            if venta.envio is not None:
                d['flete'] = venta.envio.flete.nombre
                d['flete_id'] = venta.envio.flete.id
            else:
                d['flete'] = 'Sin Envio'
                # d['flete_id'] = 'null'
            lista.append(d)

        print ('LA LISTA',lista)

        return jsonify(lista)
    pass
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
    cheques = Cheque.query.filter_by(state=True).all()
    cheques_all = Cheque.query.filter_by(state=True).filter_by(emitido=True).all()
    cheques_in = filter(lambda cheque: cheque.es_entrada and(cheque.cliente!=None), cheques)
    cheques_out = filter(lambda cheque: not(cheque.es_entrada) and (cheque.proveedor !=None), cheques)
    cheques_redireccionados = filter(lambda cheque: (cheque.es_de_tercero is True) and (cheque.emitido is True), cheques)
    return render_template(
        'lista-cheques.html',
        cheques=cheques_all,
        cheques_in=cheques_in,
        cheques_out=cheques_out,
        chredirect = cheques_redireccionados,
        title = 'lista de cheques')

@app.route('/acreditar-cheque/<id>')
def acreditar_cheque(id):
    cheque = Cheque.query.filter_by(id=id).first()
    cheque.acreditado = True
    cheque.state= False
    db.session.commit()
    return redirect(url_for('listar_cheques'))

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
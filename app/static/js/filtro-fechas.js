let fechaInicio = document.getElementById('fechaInicio');
let fechaFin = document.getElementById('fechaFin');
let data;
function filtrarCompras(){
    alert('funciona '+ fechaInicio.value+' '+fechaFin.value)
    let url = "/filtrar-compras";
    inicio = {
        inicio: fechaInicio.value
    }
    fin = {
        fin : fechaFin.value
    }
    let http = new XMLHttpRequest();
    http.open("POST", url,true);
    http.setRequestHeader('Content-Type','application/json');
    http.onreadystatechange = ()=>{
        if (http.readyState == 4 && http.status == 200){
            //ACA entra la respuesta
            data = JSON.parse(http.response);

            alert(data.length);
            generarTablaCompras(data);
        }
    }
    http.send(JSON.stringify({inicio, fin}))
}

function generarTablaCompras(data){
    let tabla = document.getElementById('cuerpoTabla')
    tabla.innerHTML= '';
    let i;
    let factura;
    let linkFlete;
    for (i=0;i<data.length;i++){
        if(data[i].factura_prov){
            factura = 'A'
        }
        else factura = 'B';
        if (data[i].flete_id != 0){
            linkFlete = `<a href="proveedor/${data[i].flete_id}">${data[i].flete}</a>`
        }
        else{
            linkFlete = `${data[i].flete}`
        }
        let tr =  document.createElement('tr');
        tr.innerHTML = `
        <td><a href="compra/${data[i].id}">${data[i].fecha}</a></td>
        <td><a href="proveedor/${data[i].proveedor_id}">${data[i].proveedor}</a></td>
        <td><a href="producto/${data[i].producto_id}">${data[i].producto}</a></td>
        <td>${parseFloat(data[i].cantidad).toFixed(2)}</td>
        <td>${parseFloat(data[i].valor_unitario).toFixed(2)}</td>
        <td>${parseFloat(data[i].p_carga).toFixed(2)}</td>
        <td>${linkFlete}</td>
        <td>${data[i].p_flete.toFixed(2)}</td>
        <td>${data[i].total.toFixed(2)}</td>
        <td>${factura}</td>
        `
        tabla.appendChild(tr)
    }

}

function filtrarVentas(){
    alert('funciona '+ fechaInicio.value+' '+fechaFin.value)
    let url = "/filtrar-ventas";
    inicio = {
        inicio: fechaInicio.value
    }
    fin = {
        fin : fechaFin.value
    }
    let http = new XMLHttpRequest();
    http.open("POST", url,true);
    http.setRequestHeader('Content-Type','application/json');
    http.onreadystatechange = ()=>{
        if (http.readyState == 4 && http.status == 200){
            //ACA entra la respuesta
            data = JSON.parse(http.response);

            alert(data.length);
            alert(data)
            generarTablaVentas(data);
        }
    }
    http.send(JSON.stringify({inicio, fin}))
}
function generarTablaVentas(data) {
    let tabla = document.getElementById('cuerpoTabla')
    tabla.innerHTML= '';
    let i;
    let factura;
    let linkFlete;
    for (i=0;i<data.length;i++){
        if(data[i].factura_cliente){
            factura = 'A'
        }
        else factura = 'B';
        if (data[i].flete_id != 0){
            linkFlete = `<a href="proveedor/${data[i].flete_id}">${data[i].flete}</a>`
        }
        else{
            linkFlete = `${data[i].flete}`
        }
        let tr =  document.createElement('tr');
        tr.innerHTML = `
        <td><a href="/venta/${data[i].id}">${data[i].fecha}</a></td>
        <td><a href="/cliente/${data[i].cliente_id}">${data[i].cliente}</a></td>
        <td><a href="/producto/${data[i].producto_id}">${data[i].producto}</a></td>
        <td> ${parseFloat(data[i].cantidad).toFixed(2)}</td>
        <td>$ ${parseFloat(data[i].precioCompra).toFixed(2)}</td>
        <td>$ ${parseFloat(data[i].precioVenta).toFixed(2)}</td>
        <td>$ ${parseFloat(data[i].precioCarga).toFixed(2)}</td>
        <td>${linkFlete}</td>
        <td>$ ${data[i].precioFlete.toFixed(2)}</td>
        <td>$ ${data[i].total.toFixed(2)}</td>
        <td>$ ${data[i].utilidad.toFixed(2)}</td>
        <td>${factura}</td>
        `
        tabla.appendChild(tr)
    }
}

function filtrarCobros(){
    let url = '/filtrar-cobros';
    inicio = {inicio:fechaInicio.value};
    fin = {fin: fechaFin.value};
    let http = new XMLHttpRequest();
    http.open('POST', url,True);
    http.setRequestHeader('Content-Type','application/json');
    http.onreadystatechange = ()=>{
        if(http.readyState == 4 && http.status ==200){
            data = JSON.parse(http.response);
            generarTablaCobros(data);
        }
    }
    http.send(JSON.stringify({inicio, fin}))
}
function generarTablaCobros(data){
    // TODO: COMPLETAR ARMADO DE TABLA Y LA RUTA EN ROUTES.PY
    let tabla = document.getElementById('cuerpoTabla')
    tabla.innerHTML= '';
    let i;
    let factura;
    for (i=0;i<data.length;i++){
        if(data[i].factura){
            factura = 'A'
        }
        else factura = 'B';
        
        let tr =  document.createElement('tr');
        tr.innerHTML = `
        <td><a href="/venta/${data[i].id}">${data[i].fecha}</a></td>
        <td><a href="/cliente/${data[i].cliente_id}">${data[i].cliente}</a></td>
        <td><a href="/producto/${data[i].producto_id}">${data[i].producto}</a></td>
        <td> ${parseFloat(data[i].cantidad).toFixed(2)}</td>
        <td>$ ${parseFloat(data[i].precioCompra).toFixed(2)}</td>
        <td>$ ${parseFloat(data[i].precioVenta).toFixed(2)}</td>
        <td>$ ${parseFloat(data[i].precioCarga).toFixed(2)}</td>
        <td>${linkFlete}</td>
        <td>$ ${data[i].precioFlete.toFixed(2)}</td>
        <td>$ ${data[i].total.toFixed(2)}</td>
        <td>$ ${data[i].utilidad.toFixed(2)}</td>
        <td>${factura}</td>
        `
        tabla.appendChild(tr)
    }
}
let producto = document.getElementById('producto');
let precioUnitario = document.getElementById('precio_unitario');
let cantidad = document.getElementById('cantidad');
let subTotal = document.getElementById('sub_total')
let costoFlete = document.getElementById('costo_flete')
let total = document.getElementById('monto_total')

producto.addEventListener('blur',getUnitPrice)
cantidad.addEventListener('change',getSubTotal)
costoFlete.addEventListener('blur', getTotal)
precioUnitario.addEventListener('change', getSubTotal)
function getUnitPrice(){
    const url = '/precio/'+producto.value;
    const http = new XMLHttpRequest();
    http.open('GET',url, true);
    http.onload = ()=>{
        if(http.status === 200){
            precioUnitario.value = http.response;
            getSubTotal();
        }
    }
    http.send()
}

function getSubTotal(){
    subTotal.value =( precioUnitario.value * cantidad.value).toFixed(2);
    getTotal();
}

function getTotal(){
    total.value = (parseFloat(subTotal.value) + parseFloat(costoFlete.value)).toFixed(2)
}

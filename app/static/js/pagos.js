let chequePropio = document.getElementById('cheque-propio');
let chequeTercero = document.getElementById('cheque3roContainer');
let formaDePago = document.getElementsByClassName('radio-input');
let fp;
for (let i = 0; i<formaDePago.length;i++){
    formaDePago[i].addEventListener('change', getFormaDePago)
}
let campo = document.getElementById('chequera');
let lista = document.getElementById('cheques');
campo.addEventListener('change',getlista);
lista.selectedIndex = 0;

function getFormaDePago(e){
    let index;
    for (index=0; index<formaDePago.length; index++){
        if (formaDePago[index].checked){
            switch (formaDePago[index].value){
                case 'efectivo':
                    chequePropio.style.display = 'none';
                    chequeTercero.style.display = 'none';
                    console.log(formaDePago[index].value);
                    fp = formaDePago[index].value;
                    break;
                case 'chequera':
                chequePropio.style.display = 'block';
                chequeTercero.style.display = 'none';
                console.log(formaDePago[index].value);
                fp = formaDePago[index].value;
                break;

                case 'cheque3ro':
                chequePropio.style.display = 'none';
                chequeTercero.style.display = 'block';
                console.log(formaDePago[index].value);
                fp = formaDePago[index].value;
                break;
            }
        }
    }
}getFormaDePago();

function getlista(e){
    lista.length=0;
    // e.evenTarget = lista;
    const url = '/_obtener_cheques/'+campo.value;
    const request = new XMLHttpRequest();
    request.open('GET', url, true);
    request.onload = () =>{
        if (request.status === 200){
            const data = JSON.parse(request.responseText);
            let option;
            let i;
            for (i=0; i< data.length; i++){
                option = document.createElement('option');
                option.text = data[i].numero;
                option.value = data[i].id;
                lista.add(option)
            }
        }
    }
    request.send()
} getlista()

numeroCheque=document.getElementById('numero');
lista.addEventListener('change', updateNumber);
function updateNumber(e){
    numeroCheque.value = lista.selectedOptions[0].text
}

let idArr= [];
let btnAceptar = document.getElementById('generar');
btnAceptar.addEventListener('click', gjson);
function gjson(e){
    let p = document.getElementById('proveedor').value;
    let m = document.getElementById('monto').value;
    let c = document.getElementById('comentario').value;
    let cheq;
    let proveedor = {
        id:p,//document.getElementById('proveedor').value,
        monto:parseFloat(m),
        comentario:c,
        factura:factura.value,
        forma_pago:fp,
    }
    if (fp == 'chequera'){
        cheq ={
            id : cheques.value,
            fecha_cobro:fecha_cobro.value,
            fecha_emision:fecha_emision.value,
            chequera:chequera.value,
            factura:factura.value,
            cheque:cheques.value
        }
    }
    else if (fp == 'cheque3ro'){
        
        
        cheq ={
            cids :idArr
        }
    }
    console.log(JSON.stringify({proveedor,cheq }))
    let http = new XMLHttpRequest();
    let url = "/pagar";
    http.open("POST", url,true);
    http.setRequestHeader("Content-Type", "application/json");
    http.onreadystatechange = function(){
        if(http.readyState == 4 && http.status == 200) { 
            //aqui obtienes la respuesta de tu peticion
            console.log(http.responseText);
            alert(http.responseText);
        }
    }
    http.send(JSON.stringify({proveedor,cheq }))
}
let addSelect = document.getElementById('addSelect');
addSelect.addEventListener('click', addField);
let delSelect = document.getElementById('delSelect');
delSelect.addEventListener('click', delField)

let id = 0;
function addField(){
    let nodo = document.getElementById('cheque3ro');
    id = nodo.childElementCount+1;
    console.log(id)
    let field = document.createElement('div');
    field.classList.add('field');
    let control = document.createElement('div');
    control.classList.add('control');
    let selectDiv = document.createElement('div');
    selectDiv.classList.add('select');
    let select = document.createElement('select');
    select.classList.add('select');
    select.classList.add('select3');
    select.setAttribute('id', 'sid-'+id)
    selectDiv.appendChild(select)
    control.appendChild(selectDiv)
    field.appendChild(control);
    nodo.appendChild(field);
    getCheuqesTercero(select);
    
}

btnCalculo = document.getElementById('calcular');
btnCalculo.addEventListener('click',sumar)

function getIds(){
    idArr= [];
    for (let index = 1; index <= id; index++) {
        const element = document.getElementById('sid-'+index);
        idArr.push(element.value)
    }
    console.log('array de values: '+idArr)
}
function sumar(){
    getIds();;
    let suma =[];
    let selected;
    let i;
    if(id > 0){
        for (i=1; i <= id; i++){
            selected = document.getElementById('sid-'+i);
            const url = '/_obtener_cheques/tercero/'+selected.value;
                const request = new XMLHttpRequest();
                request.open('GET', url, true);
                request.onload = () =>{
                    if (request.status === 200){
                        const data = JSON.parse(request.response);
                        console.log(data)
                        suma.push(data);
                        console.log('Res Suma: '+suma)
                    }
                    getTotal(suma);
                }
                request.send()
        }
    }else{
        alert('no hay cheques para calcular')
    }
    
}
function getTotal(arr){
    let i;
    let total = 0;
    for (i=0; i< arr.length; i++){
        total += arr[i];
    }
    document.getElementById('monto').value = total
}
function delField() {
    let field = document.getElementById('cheque3ro');
    field.removeChild(field.lastChild)
    id--;
    console.log(id)
}
function getCheuqesTercero(lista){
        const url = '/_obtener_cheques/tercero/';
        const request = new XMLHttpRequest();
        request.open('GET', url, true);
        request.onload = () =>{
            if (request.status === 200){
                const data = JSON.parse(request.responseText);
                console.log(data)
                let option;
                let i;
                for (i=0; i< data.length; i++){
                    let factura;
                    if(data[i].factura){
                        factura = 'A';
                    }else {factura ='B' }
                    option = document.createElement('option');
                    option.text = `Bco: ${data[i].banco} Nº:${data[i].numero} $ ${data[i].monto} Fecha:${data[i].postdatado} - ${factura}`;
                    option.value = data[i].id;
                    lista.add(option)
                }
            }
        }
        request.send()
}
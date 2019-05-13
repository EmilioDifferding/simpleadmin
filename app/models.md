# SimpleAdmin Models
Es una app para que utilice una pequeña o mediana empresa, y le permita administrar y visualizar datos relacionados con clientes, proveedores de MP y Transporte , productos, compras, ventas, cheques y caja efectivo.
La aplicación debe permitir crear y almacenar de forma persistente clientes, proveedores y productos con sus datos, poder editar/actualizar y borrar su información.
Tener diferentes interfaces donde se pueda ver información de distinto tipo.

## Interfaces / Secciones
### Clientes
Esta sección es donde el usuario puede crear, editar/actualiza, borrar y ver información de todos los clientes en el sistema.
+ Debe contar con una __interface de carga__ que contega un __Formulario__ donde poder ir introduciendo los datos de:
    - Nombre de empresa / cliente /Razon social
    - Nombre contacto
    - Télefono
    - E-mail
    - Dirección
    - CUIT
    - un comentario (opcional)

+ __Inteface de Lista de Clientes__:
    - Es una vista en forma de tabla donde se muestran algunos datos útiles de cada cliente de forma rápda, como nombre de razón social, contacto, número telefónico, etc
    - En la parte superior tiene un botón para __cargar nuevo cliente__.
    - Al lado de cada cliente hay 2 botones __Editar__ y __Eliminar__ cliente

+ __Interface de 'Detalle de cliente'__
    - Muestra todos los datos que se cargaron al cliente más la información de __compras__, __saldos__ y __cobranzas__ de el cliente que se esté visualizando.
    - Debe Contar con __3 botones:__ _Editar, Borrar, y efectuar pago_.
    - La misma interface debe contar con dos(2) Pestañas en las que se visualicen como tabla las __Compras__ y __Cobranzas__ que haya efectuado el cliente.

+ __Datos que el sistema gestiona de forma automática:__
    - Una vez que se carga un cliente al sistema, se crean en la base de datos unos campos extras:
        - __saldos_a:__ donde se acumula la cta corriente facturada según la venta que se le impute
        - __saldo_b__: donde se acumula la cta corriente __no__ facturada según la venta que se le impute
        - __Ventas__: donde se le asocian todas las ventas que el cliente realice.
        - __Cobros__: donde se le asocian todos los cobros que se realicen al cliente en particular, también tiene la informacion de los __cheques__ que el cliente entrego.
        - Además un campo que determina si el cliente se encuentra activo en el sistema _(El cliente deja de estar activo en el sistema si se le da al boton borrar de la interface de clientes, si no está activo, los saldos, cobranzas no tienen efecto en ctas corrientes y caja)_.
        





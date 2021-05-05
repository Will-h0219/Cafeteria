const compra = new Carrito();
const listaCompra = document.querySelector('#lista-compra tbody');
const carritoCompra = document.getElementById('carrito');

cargarEventosCompra();

function cargarEventosCompra(){
    document.addEventListener('DOMContentLoaded', compra.leerLocalStorageCompra());

    carritoCompra.addEventListener('click', (e)=>{compra.eliminarProducto(e)});

    compra.calcularTotal();
}
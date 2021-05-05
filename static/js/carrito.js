class Carrito {

    //Añadir producto
    comprarProducto(e){
        e.preventDefault();
        if(e.target.classList.contains('agregar-carrito')){
            const producto = e.target.parentElement.parentElement;
            this.leerDatosProducto(producto);
        }
    }

    leerDatosProducto(producto){
        const infoProducto = {
            imagen : producto.querySelector('img').src,
            nombre : producto.querySelector('h4').textContent,
            precio : producto.querySelector('.precio span').textContent,
            id : producto.querySelector('a').getAttribute('data-id'),
            cantidad : 1
        }
        this.insertarCarrito(infoProducto);
    }

    insertarCarrito(producto){
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <img src="${producto.imagen}" width=50>
            </td>
            <td>${producto.nombre}</td>
            <td>${producto.precio}</td>
            <td>
                <a href="#" class="borrar-producto far fa-trash-alt" data-id="${producto.id}"></a>
            </td>
        `;
        listaProductos.appendChild(row);
        this.guardarProductosLocalStorage(producto);
    }

    eliminarProducto(e){
        e.preventDefault();
        let producto, productoId;
        if(e.target.classList.contains('borrar-producto')){
            e.target.parentElement.parentElement.remove();
            producto = e.target.parentElement.parentElement;
            //Para alamacenar el valor el localstorage
            productoId = producto.querySelector('a').getAttribute('data-id');
        }
        this.eliminarProductoLocalStorage(productoId);
        this.calcularTotal();
    }

    vaciarCarrito(e){
        e.preventDefault();
        while(listaProductos.firstChild){
            listaProductos.removeChild(listaProductos.firstChild);
        }
        this.vaciarLocalStorage();
        return false;
    }

    guardarProductosLocalStorage(producto){
        let productos;
        productos = this.obtenerProductosLocalStorage();
        productos.push(producto);
        localStorage.setItem('productos', JSON.stringify(productos));
    }

    obtenerProductosLocalStorage(){
        let productoLS;

        if(localStorage.getItem('productos') === null){
            productoLS = [];
        }else{
            productoLS = JSON.parse(localStorage.getItem('productos'));
        }
        return productoLS;
    }

    eliminarProductoLocalStorage(productoId){
        let productosLS;
        productosLS = this.obtenerProductosLocalStorage();
        productosLS.forEach(function(productoLS, index){
            if(productoLS.id === productoId){
                productosLS.splice(index, 1);
            }
        });

        localStorage.setItem('productos', JSON.stringify(productosLS));
    }

    leerLocalStorage(){
        let productosLS;
        productosLS = this.obtenerProductosLocalStorage();
        productosLS.forEach(function(producto){
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <img src="${producto.imagen}" width=50>
                </td>
                <td>${producto.nombre}</td>
                <td>${producto.precio}</td>
                <td>
                    <a href="#" class="borrar-producto far fa-trash-alt" data-id="${producto.id}"></a>
                </td>
            `;
            listaProductos.appendChild(row);
        });
    }

    vaciarLocalStorage(){
        localStorage.clear();
    }

    leerLocalStorageCompra(){
        let productosLS;
        productosLS = this.obtenerProductosLocalStorage();
        productosLS.forEach(function(producto){
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <img src="${producto.imagen}" width=50>
                </td>
                <td>${producto.nombre}</td>
                <td>${producto.precio}</td>
                <td>
                    <input type="number" class="cantidad" min="1" value=${producto.cantidad}>
                </td>
                <td>${producto.precio * producto.cantidad}</td>
                <td>
                    <a href="#" class="borrar-producto far fa-trash-alt" data-id="${producto.id}"></a>
                </td>
            `;
            listaCompra.appendChild(row);
        });
    }

    calcularTotal(){
        let productoLS;
        let total = 0, subtotal = 0, iva = 0;
        productoLS = this.obtenerProductosLocalStorage();
        for(let i = 0; i < productoLS.length; i++){
            let element = Number(productoLS[i].precio * productoLS[i].cantidad);
            subtotal = subtotal + element;
        }
        iva = parseFloat(subtotal * 0.19).toFixed(2);
        total = parseFloat(subtotal + parseFloat(iva)).toFixed(2);

        document.getElementById('subtotal').innerHTML = "$ " + subtotal.toFixed(2);
        document.getElementById('iva').innerHTML = "$ " + iva;
        document.getElementById('total').innerHTML = "$ " + total;
        document.getElementById('f1t1').value = total;
    }

}
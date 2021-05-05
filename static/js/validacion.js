function validar_formulario()
{
    var usuario = document.getElementById("usuario").value;
    var correo = document.getElementById("correo").value;
    var clave = document.getElementById("clave").value;

    
    if(correo=="")
    {
        alert("Debe ingresar un correo");
        document.getElementById("correo").focus();//pone el cursor
        return false;
    }
    if (usuario=="" || usuario.length <8)
    {
        alert("El usuario debe tener mínimo 8 caracteres");
        document.getElementById("usuario").focus();//pone el cursor
        return false;
    }
    if (clave =="" || clave.length <8)
    {
        alert("La clave debe tener mínimo 8 caracteres");
        document.getElementById("clave").focus();//pone el cursor
        return false;
    }

   return true;
}

function validar_pwd()
{
    var newPassword = document.getElementById("newPassword").value;
    var verPassword = document.getElementById("verPassword").value;

    if (newPassword =="" || newPassword.length <8)
    {
        alert("La clave debe tener mínimo 8 caracteres");
        document.getElementById("newPassword").focus();//pone el cursor
        return false;
    }
    if (verPassword =="" || verPassword.length <8)
    {
        alert("La clave debe tener mínimo 8 caracteres");
        document.getElementById("verPassword").focus();//pone el cursor
        return false;
    }

   return true;
}

/* mostrar paswword*/
function mostrarPassword()
{
    document.getElementById("clave").type="text";
}

/* Ocultar paswword*/
function ocultarPassword()
{
    document.getElementById("clave").type="password";
}

function vaciarLS(){
    localStorage.clear();
}

function busqueda() {
    var input, filter, tabla, tr, td, i, txtValue;
    input = document.getElementById("buscar");
    filter = input.value.toUpperCase();
    tabla = document.getElementById("lista-productos");
    tr = tabla.getElementsByTagName("div");
    for (i=0; tr.length; i++){
        td = tr[i].getElementsByTagName("h4")[0];
        if (td) {
            txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            }else{
                tr[i].style.display = "none";
            }
        }
    }
}
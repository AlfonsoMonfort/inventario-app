from flask import Flask, render_template_string, request, redirect, url_for, send_file
from openpyxl import Workbook
from datetime import datetime
import os

app = Flask(__name__)

inventario = {
    "fecha": "",
    "almacen": "",
    "vendedor": "",
    "articulos": {}
}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Inventario</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/quagga/0.12.1/quagga.min.js"></script>
</head>

<body style="font-family: Arial; padding: 20px;">

<h2>Inicio Inventario</h2>
<form method="POST" action="/inicio">
    Almacén:<br>
    <input type="text" name="almacen" required><br><br>

    Vendedor:<br>
    <input type="text" name="vendedor" required><br><br>

    <button type="submit">Empezar</button>
</form>

<hr>

<h2>Escanear Código</h2>

<p><b>Toca la imagen para activar el escaneo</b></p>

Cantidad:<br>
<input type="number" id="cantidad" value="1" min="1"><br><br>

<div id="scanner" style="width:100%; max-width:400px; border:2px solid black;"></div>

<form method="POST" action="/agregar" id="scanForm">
    <input type="hidden" name="codigo" id="codigoInput">
    <input type="hidden" name="cantidad" id="cantidadInput">
</form>

<hr>

<h3>Artículos Escaneados</h3>
<ul>
{% for codigo, cant in inventario["articulos"].items() %}
    <li>{{codigo}} - {{cant}}</li>
{% endfor %}
</ul>

<br>
<a href="/excel">
    <button style="padding:15px; font-size:16px;">
        Finalizar y Generar Excel
    </button>
</a>

<script>

let scannerActivo = false;

function iniciarScanner() {

    if (scannerActivo) return;

    scannerActivo = true;

    Quagga.init({
        inputStream : {
            name : "Live",
            type : "LiveStream",
            target: document.querySelector('#scanner'),
            constraints: {
                facingMode: "environment"
            }
        },
        decoder : {
            readers : ["ean_reader"]
        }
    }, function(err) {
        if (!err) {
            Quagga.start();
        }
    });

    Quagga.onDetected(function(result) {

        let code = result.codeResult.code;

        if (!/^\d{13}$/.test(code)) return;

        // Parar completamente el scanner
        Quagga.stop();
        scannerActivo = false;

        document.getElementById("codigoInput").value = code;
        document.getElementById("cantidadInput").value =
            document.getElementById("cantidad").value;

        document.getElementById("scanForm").submit();
    });
}

// Solo escanea cuando tocas la imagen
document.getElementById("scanner").addEventListener("click", function() {
    iniciarScanner();
});

</script>

</body>
</html>
"""




@app.route("/")
def home():
    return render_template_string(HTML, inventario=inventario)

@app.route("/inicio", methods=["POST"])
def inicio():
    inventario["fecha"] = datetime.now().strftime("%Y-%m-%d")
    inventario["almacen"] = request.form["almacen"]
    inventario["vendedor"] = request.form["vendedor"]
    inventario["articulos"] = {}
    return redirect(url_for("home"))

@app.route("/agregar", methods=["POST"])
def agregar():
    codigo = request.form["codigo"]
    cantidad = int(request.form["cantidad"])

    if codigo in inventario["articulos"]:
        inventario["articulos"][codigo] += cantidad
    else:
        inventario["articulos"][codigo] = cantidad

    return redirect(url_for("home"))

@app.route("/excel")
def excel():
    from openpyxl import Workbook
    from flask import send_file
    from datetime import datetime

    filename = f"inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "Inventario"

    headers = ["fecha", "almacen", "referencia", "cantidad", "numero vendedor"]
    ws.append(headers)

    for codigo, cantidad in inventario["articulos"].items():
        ws.append([
            inventario["fecha"],
            inventario["almacen"],
            codigo,
            cantidad,
            inventario["vendedor"]
        ])

    wb.save(filename)

    # 🔥 RESET INVENTARIO DESPUÉS DE GENERAR EXCEL
    inventario["fecha"] = ""
    inventario["almacen"] = ""
    inventario["vendedor"] = ""
    inventario["articulos"] = {}

    return send_file(filename, as_attachment=True)






if __name__ == "__main__":
    app.run()

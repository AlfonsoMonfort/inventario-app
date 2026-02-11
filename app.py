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

Cantidad:<br>
<input type="number" id="cantidad" value="1" min="1"><br><br>

<div id="scanner" style="width:100%; max-width:400px;"></div>

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
        readers : ["ean_reader","ean_8_reader","code_128_reader"]
    }
}, function(err) {
    if (!err) {
        Quagga.start();
    }
});

Quagga.onDetected(function(result) {
    let code = result.codeResult.code;
    document.getElementById("codigoInput").value = code;
    document.getElementById("cantidadInput").value =
        document.getElementById("cantidad").value;

    document.getElementById("scanForm").submit();
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
    filename = "inventario.xlsx"

    wb = Workbook()
    ws = wb.active

    ws.append(["Fecha", inventario["fecha"]])
    ws.append(["Almacén", inventario["almacen"]])
    ws.append(["Vendedor", inventario["vendedor"]])
    ws.append([])
    ws.append(["Código", "Cantidad"])

    for codigo, cant in inventario["articulos"].items():
        ws.append([codigo, cant])

    wb.save(filename)

    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run()

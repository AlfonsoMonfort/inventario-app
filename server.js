import express from "express";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import fs from "fs";

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET;

// ===== USUARIOS (HASH REAL MÁS ABAJO) =====
const usuarios = [
  {
    usuario: "admin",
    password: "$2b$10$Ud2R1DIpgqna7eWBG2NdFOxZq.QwiCld3Wcx9XODTsb5sD8Lbt00i"
  }
];

// ===== LOGIN =====
app.post("/login", async (req, res) => {
  const { usuario, password } = req.body;

  const user = usuarios.find(u => u.usuario === usuario);
  if (!user) return res.status(401).json({ error: "No autorizado" });

  const ok = await bcrypt.compare(password, user.password);
  if (!ok) return res.status(401).json({ error: "No autorizado" });

  const token = jwt.sign(
    { usuario },
    JWT_SECRET,
    { expiresIn: "7d" }
  );

  res.json({ token });
});

// ===== MIDDLEWARE TOKEN =====
function verificarToken(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth) return res.sendStatus(401);

  const token = auth.split(" ")[1];

  try {
    jwt.verify(token, JWT_SECRET);
    next();
  } catch {
    res.sendStatus(401);
  }
}

// ===== EQUIVALENCIAS PROTEGIDAS =====
app.get("/equivalencias", verificarToken, (req, res) => {
  const data = fs.readFileSync("./equivalencias.json");
  res.json(JSON.parse(data));
});

// ===== RUTA RAÍZ =====
app.get("/", (req, res) => {
  res.send("Backend funcionando correctamente");
});

// ===== SERVIR FRONTEND =====
app.use(express.static("public"));

app.listen(PORT, () => {
  console.log("Servidor iniciado");
});
// --- CONFIGURACIÓN DE VARIABLES ---
const galeria = document.getElementById("galeria");
const tituloElemento = document.getElementById("titulo-escrito");
const frase = "Cuidamos tu salud visual con la mejor tecnología";
let index = 0;
let borrando = false;
let datosInventario = [];

// 1. CARGA DE DATOS (Con truco Anti-Cache)
async function cargarDatos() {
  try {
    const respuesta = await fetch(`inventario.json?v=${Date.now()}`); // Más rápido que new Date().getTime()
    datosInventario = await respuesta.json();
    cargarObras("todos");
  } catch (error) {
    console.error("Error en el motor de datos:", error);
  }
}

// 2. FILTRADO DE CATEGORÍAS
function filtrar(categoria, btn) {
  const botones = document.querySelectorAll(".filter-btn");
  botones.forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  cargarObras(categoria);
}

// 3. RENDERIZADO DE CARTAS (Optimizado con DocumentFragment)
function cargarObras(filtro = "todos") {
  if (!galeria) return;
  galeria.innerHTML = "";
  const fragmento = document.createDocumentFragment();

  const items =
    filtro.toLowerCase() === "todos"
      ? datosInventario
      : datosInventario.filter(
          (i) => i.cat.toLowerCase() === filtro.toLowerCase(),
        );

  items.forEach((item) => {
    const card = document.createElement("div");
    card.className = "card animar-subida";

    const esMulti = Array.isArray(item.nombre);
    const imgFrente = esMulti ? item.nombre[0] : item.nombre;
    const imgLado = esMulti && item.nombre[1] ? item.nombre[1] : null;
    const textoParaGrid =
      item.desc && item.desc.trim() !== "" ? item.desc : "Opticentro A&E";

    card.innerHTML = `
      <div class="img-container ${imgLado ? "has-hover" : ""}">
        <img data-src="img/${imgFrente}.jpeg" class="img-main loader-target" alt="${imgFrente}">
        ${imgLado ? `<img data-src="img/${imgLado}.jpeg" class="img-hover loader-target" alt="${imgLado}">` : ""}
      </div>
      <span class="descripcion-viva">${textoParaGrid}</span>
    `;

    // TRUCO DE FLUIDEZ: Disparar la carga y detectar el final
    const imagenes = card.querySelectorAll(".loader-target");
    imagenes.forEach((img) => {
      // Pasamos el data-src al src real
      img.src = img.getAttribute("data-src");

      // Cuando la imagen cargue...
      img.onload = () => {
        img.classList.add("loaded"); // Activa la opacidad en CSS
      };

      // Si ya estaba en caché, forzamos el evento
      if (img.complete) img.onload();
    });

    card.onclick = () => abrirModal(imgFrente, item.desc);
    fragmento.appendChild(card);
  });

  galeria.appendChild(fragmento);
}

// 4. FUNCIONES DEL MODAL (Separadas para mayor limpieza)
function abrirModal(imagen, descripcion) {
  const modal = document.getElementById("modal-visor");
  const imgFull = document.getElementById("img-full");
  const descTxt = document.getElementById("desc-texto");

  imgFull.src = `img/${imagen}.jpeg`;
  descTxt.textContent = descripcion || "Calidad y estilo para tu visión.";
  modal.style.display = "flex";
  document.body.classList.add("modal-open"); // Usamos la clase CSS que creamos antes
}

function cerrarModal() {
  document.getElementById("modal-visor").style.display = "none";
  document.body.classList.remove("modal-open");
}

// 5. EFECTO ESCRITURA (Título Principal)
function loopEscritura() {
  if (!tituloElemento) return;
  tituloElemento.textContent = frase.substring(0, index);

  let vel = borrando ? 50 : 120;

  if (!borrando && index === frase.length) {
    vel = 3000;
    borrando = true;
  } else if (borrando && index === 0) {
    borrando = false;
    vel = 1000;
  }

  index += borrando ? -1 : 1;
  setTimeout(loopEscritura, vel);
}

// 6. DARK MODE TOGGLE (Más robusto)
const themeBtn = document.getElementById("theme-toggle");
if (themeBtn) {
  themeBtn.onclick = () => {
    const root = document.documentElement;
    const isDark = root.getAttribute("data-theme") === "dark";
    const newTheme = isDark ? "light" : "dark";

    root.setAttribute("data-theme", newTheme);
    themeBtn.innerHTML = isDark
      ? '<i class="fas fa-sun"></i>'
      : '<i class="fas fa-moon"></i>';
    // Opcional: Guardar preferencia del usuario
    localStorage.setItem("theme", newTheme);
  };
}

// 7. INICIALIZACIÓN Y EVENTOS
window.addEventListener("DOMContentLoaded", () => {
  // Carga inicial de datos y efectos
  cargarDatos();
  loopEscritura();

  // Listener para cerrar modal (Esc y botón)
  const btnCerrar = document.querySelector(".cerrar-modal");
  if (btnCerrar) btnCerrar.onclick = cerrarModal;

  window.onclick = (e) => {
    if (e.target.id === "modal-visor") cerrarModal();
  };
});

// Quitar preloader al cargar todo
window.addEventListener("load", () => {
  const preloader = document.getElementById("preloader-art");
  if (preloader) {
    preloader.style.opacity = "0";
    setTimeout(() => preloader.remove(), 800); // .remove() es más limpio que .display = 'none'
  }
});

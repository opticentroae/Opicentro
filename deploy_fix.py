import os
import re
import subprocess
import shutil
import stat
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

# --- CONFIGURACIÓN DE PROYECTOS ---
PROYECTOS = {
    "Centro Visual Cristiano": {
        "url": "https://github.com/opticentroae/Centro_Visual_Cristiano.git",
        "url_web": "https://opticentroae.github.io/Centro_Visual_Cristiano/",
        "prefix": "CVC"
    },
    "Opticentro A&E": {
        "url": "https://github.com/opticentroae/Opicentro.git",
        "url_web": "https://opicentroae.com/",
        "prefix": "OPT"
    }
}

IMG_DIR = 'img'
EXTENSIONS = ('.html', '.css', '.js')

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

class AppMultiAuditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ArticDash Multi-Deployer 🚀")
        self.root.geometry("400x250")
        self.root.eval('tk::PlaceWindow . center')
        
        self.proyecto_seleccionado = None
        
        # Interfaz de Selección
        tk.Label(self.root, text="¿En qué proyecto trabajamos hoy?", font=("Arial", 12, "bold")).pack(pady=20)
        
        for nombre in PROYECTOS.keys():
            tk.Button(self.root, text=nombre, width=30, height=2, 
                      command=lambda n=nombre: self.seleccionar(n)).pack(pady=5)

    def seleccionar(self, nombre):
        self.proyecto_seleccionado = PROYECTOS[nombre]
        self.nombre_proyecto = nombre
        self.root.destroy() # Cerramos el selector y seguimos con la lógica

    def solicitar_mensaje(self):
        prefix = self.proyecto_seleccionado["prefix"]
        msg = simpledialog.askstring("Git Push", f"Mensaje para {self.nombre_proyecto}:", 
                                     initialvalue=f"🚀 {prefix}: Update Optimized")
        return msg if msg else f"🚀 {prefix}: System Update"

    def auditoria_reparacion(self):
        print(f"🛠️  Auditoría para {self.nombre_proyecto}...")
        log = []
        real_files = os.listdir(IMG_DIR) if os.path.exists(IMG_DIR) else []
        real_files_lower = {f.lower(): f for f in real_files}
        
        for root, dirs, files in os.walk('.'):
            if '.git' in dirs: dirs.remove('.git')
            for file in files:
                if file.endswith(EXTENSIONS):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Fix Slashes y Case Sensitivity (Tu lógica original)
                        new_content = re.sub(r'((?:src|href)=["\'])/(?!http|https|//)', r'\1', content)

                        def fix_img_logic(match):
                            img_name = match.group(1)
                            if img_name.lower() in real_files_lower:
                                correct_name = real_files_lower[img_name.lower()]
                                if img_name != correct_name:
                                    log.append(f"🔧 Renombrado: {img_name} -> {correct_name} en {file}")
                                return f'img/{correct_name}'
                            return match.group(0)

                        new_content = re.sub(r'img/([a-zA-Z0-9\._\-\s]+\.(?:jpg|jpeg|png|gif|svg|webp))', 
                                             fix_img_logic, new_content, flags=re.IGNORECASE)

                        if content != new_content:
                            with open(path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                    except Exception as e:
                        print(f"⚠️ Error: {e}")
        
        return "\n".join(log) if log else "✅ Todo limpio, rutas perfectas."

    def ejecutar_flujo(self):
        self.root.mainloop() # Abre el selector
        
        if not self.proyecto_seleccionado: return # Por si cierran la ventana

        # 1. Preguntar Acción
        opcion = messagebox.askyesnocancel("Auditor ArticDash", 
                                          f"Proyecto: {self.nombre_proyecto}\n\n"
                                          "Yes: Reparar y Subir a GitHub\n"
                                          "No: Solo Reparar localmente\n"
                                          "Cancel: Salir")
        
        if opcion is None: return 

        # 2. Reparación
        resultado = self.auditoria_reparacion()
        messagebox.showinfo("Resultado Auditoría", resultado)

        # 3. Despliegue al Repo seleccionado
        if opcion is True:
            commit_msg = self.solicitar_mensaje()
            repo_url = self.proyecto_seleccionado["url"]
            web_url = self.proyecto_seleccionado["url_web"]
            
            try:
                if os.path.exists('.git'):
                    shutil.rmtree('.git', onerror=remove_readonly)
                
                subprocess.run(["git", "init"], check=True)
                subprocess.run(["git", "add", "."], check=True)
                subprocess.run(["git", "commit", "-m", commit_msg], check=True)
                subprocess.run(["git", "branch", "-M", "main"], check=True)
                subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
                
                print(f"📤 Subiendo a {self.nombre_proyecto}...")
                subprocess.run(["git", "push", "-u", "origin", "main", "--force"], check=True)
                
                messagebox.showinfo("¡Éxito!", f"✨ Proyecto actualizado:\n{web_url}")
            except Exception as e:
                messagebox.showerror("Error Git", f"No se pudo subir:\n{e}")

if __name__ == "__main__":
    app = AppMultiAuditor()
    app.ejecutar_flujo()
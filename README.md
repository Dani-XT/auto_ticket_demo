# Carga Automática de Ticket — Versión Demo

Aplicación de escritorio desarrollada en **Python + Tkinter** para automatizar la creación y cierre de tickets en **ProactivaNet** a partir de una planilla Excel.

---

## Requisitos

Para ejecutar el proyecto en modo desarrollador se necesita lo siguiente:

- **Visual Studio Code**
- **Python 3.14.3**
- navegador compatible instalado en el equipo para la automatización

---

## Ejecución en modo desarrollador

### 1. Instalar Visual Studio Code

Descarga e instala **Visual Studio Code** en el equipo.

### 2. Instalar Python

Instala **Python 3.14.3** y verifica que quede disponible desde terminal:

```bash
python --version
```

### 3. Abrir el proyecto

Abre la carpeta del proyecto en **Visual Studio Code**.

### 4. Instalar virtualenv

Desde la terminal del proyecto, instala `virtualenv` usando este formato:

```bash
python -m pip install virtualenv
```

### 5. Crear el entorno virtual

```bash
python -m virtualenv venv
```

### 6. Activar el entorno virtual

#### En Windows PowerShell

Si PowerShell bloquea la ejecución del script de activación, ejecuta primero:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Luego activa el entorno virtual con:

```powershell
.\venv\Scripts\Activate.ps1
```

#### En Windows CMD

```cmd
venv\Scripts\activate.bat
```

#### En Linux o macOS

```bash
source venv/bin/activate
```

### 7. Instalar dependencias

Si el proyecto ya cuenta con archivo `requirements.txt`, ejecuta:

```bash
python -m pip install -r requirements.txt
```

Si no existe `requirements.txt`, instala manualmente las dependencias necesarias:

```bash
python -m pip install pillow polars openpyxl playwright python-dotenv
```

### 8. Ejecutar la aplicación

```bash
python main.py
```

---

## Flujo recomendado de ejecución

El flujo recomendado para trabajar en desarrollo es el siguiente:

1. Abrir el proyecto en Visual Studio Code.  
2. Abrir una terminal dentro del proyecto.  
3. Crear el entorno virtual si aún no existe.  
4. Activar el entorno virtual.  
5. Instalar dependencias si aún no están instaladas.  
6. Ejecutar la aplicación con:

```bash
python main.py
```

---

## Inicio rápido

### Windows PowerShell

```powershell
python -m pip install virtualenv
python -m virtualenv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

### Windows CMD

```cmd
python -m pip install virtualenv
python -m virtualenv venv
venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python main.py
```

### Linux o macOS

```bash
python -m pip install virtualenv
python -m virtualenv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

---

## Consideraciones

- La aplicación utiliza archivos de apoyo ubicados en `assets/templates`.
- Si faltan archivos base, el sistema intentará prepararlos al iniciar.
- Para utilizar otra cuenta en la automatización, puede ser necesario eliminar la sesión guardada desde la pantalla de configuración.
- Si trabajas en **PowerShell** y no puedes activar el entorno virtual, revisa la política de ejecución antes de intentar nuevamente.

---

## Estructura general del proyecto

```text
auto_ticket_demo/
│
├─ main.py
├─ assets/
│  ├─ icons/
│  ├─ images/
│  └─ templates/
│
├─ storages/
│  ├─ auth/
│  ├─ logs/
│  ├─ settings/
│  └─ templates/
│
├─ src/
│  ├─ app/
│  ├─ automation/
│  ├─ controllers/
│  ├─ core/
│  ├─ excel/
│  ├─ manager/
│  ├─ models/
│  ├─ repositories/
│  ├─ services/
│  ├─ ui/
│  └─ utils/
```

---

## Nota

Esta documentación corresponde a la **versión demo** del proyecto.
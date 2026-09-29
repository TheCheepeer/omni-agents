# omni-agents (Español)

> Traducciones: [English](../../README.md) | [Português](README.pt-BR.md) | Español

Un centro de control unificado y agnóstico de herramientas para versionar, gestionar y distribuir subagentes especializados, reglas de desarrollo y bibliotecas de skills modulares a través de múltiples asistentes de código con IA.

---

## Herramientas Compatibles

`omni-agents` unifica la gestión de contexto y compila directamente en el formato nativo esperado por cada asistente:

| Herramienta            | ID de Destino | Alcance            | Archivos Generados y Destinos                                         |
| :--------------------- | :------------ | :----------------- | :-------------------------------------------------------------------- |
| **Google Antigravity** | `antigravity` | Global + Workspace | `.agents/` (`skills.json`, `rules/`, `agents/`) y `~/.gemini/config/` |
| **Claude Code**        | `claude`      | Global + Workspace | `CLAUDE.md` en la raíz del proyecto y `~/.claude/CLAUDE.md`           |
| **Cursor IDE**         | `cursor`      | Workspace          | `.cursor/rules/*.mdc` (con metadatos `globs` y `alwaysApply`)         |
| **GitHub Copilot**     | `copilot`     | Workspace          | `.github/copilot-instructions.md` consolidado                         |
| **Universal**          | `universal`   | Workspace          | `AGENTS.md` estandarizado en la raíz del proyecto                     |
| **Kiro**               | `kiro`        | Workspace          | `AGENTS.md` en la raíz y directorio `.kiro/`                          |
| **OpenCode**           | `opencode`    | Workspace          | `AGENTS.md` en la raíz y directorio `.opencode/`                      |
| **Codex (OpenAI)**     | `codex`       | Workspace          | `AGENTS.md` en la raíz adaptado para el ecosistema Codex              |

---

## Estructura del Repositorio

```text
omni-agents/
├── agents/                          # Personas y subagentes especializados
│   ├── accessibility-reviewer.md
│   ├── code-reviewer.md
│   └── security-auditor.md
├── rules/                           # Perfiles modulares de reglas (un AGENTS.md por carpeta)
│   ├── general/                     # Directrices generales de ingeniería (Inglés)
│   │   └── AGENTS.md
│   └── pt-br-dev/                   # Directrices para desarrollo en Portugués Brasileño
│       └── AGENTS.md
├── src/                                 # Paquete de código fuente (Src Layout)
│   └── omni_agents/                     # Paquete principal de la CLI
│       ├── cli.py                       # Punto de entrada de la CLI, parser y dispatch
│       ├── core/                        # Reglas de negocio (scanner, linker, config)
│       ├── tui/                         # Menús interactivos en terminal
│       ├── commands/                    # Handlers de comandos headless
│       ├── i18n.py                      # Motor de internacionalización desacoplado
│       ├── languages/                   # Catálogos de traducción (en.json, pt.json, es.json...)
│       └── targets/                     # Módulos adaptadores por herramienta
│           ├── __init__.py              # Registro central de destinos
│           ├── base.py                  # Contratos base y utilidades de sistema de archivos
│           ├── antigravity.py           # Adaptador para Google Antigravity
│           ├── claude.py                # Adaptador para Claude Code (CLAUDE.md)
│           ├── cursor.py                # Adaptador para Cursor IDE (.cursor/rules/*.mdc)
│           ├── copilot.py               # Adaptador para GitHub Copilot
│           └── universal.py             # Adaptador para Universal, Kiro, OpenCode y Codex
├── tests/                               # Suite de pruebas unitarias automatizadas
├── skills/
│   ├── global/                      # GLOBAL CORE (~800 tokens) - Esenciales para todos los proyectos
│   │   ├── coding-standards/        # Excelencia técnica, Clean Code y patrones de ingeniería
│   │   ├── comunicacao-clara/       # Comunicación clara, explicaciones paso a paso y síntesis
│   │   ├── grug-brained-dev/        # Mentalidad anti-sobreingeniería y simplicidad radical
│   │   ├── reducing-entropy/        # Combate a la deuda técnica y eliminación de código muerto
│   │   └── researching-codebases/   # Investigación y navegación de código con múltiples agentes
│   ├── planning/                    # BIBLIOTECA: Planificación, auditoría y roadmaps
│   ├── docs/                        # BIBLIOTECA: Redacción técnica y documentación
│   ├── frontend/                    # BIBLIOTECA: Diseño de UI, directrices visuales y Tailwind CSS
│   ├── meta/                        # BIBLIOTECA: Ingeniería de prompts y creación de skills
│   └── stacks/                      # BIBLIOTECA: Frameworks, lenguajes e infraestructura
├── docs/
│   └── translations/                # Versiones traducidas de la documentación
│       ├── README.pt-BR.md
│       └── README.es.md
└── README.md                        # Documentación principal en inglés
```

---

## Contenido

### 1. Subagentes (`agents/`)

- `accessibility-reviewer.md`: Especialista en accesibilidad digital (a11y), directrices WCAG 2.1/2.2 (A, AA, AAA) y patrones WAI-ARIA.
- `code-reviewer.md`: Análisis estático de código, Clean Code, legibilidad y solidez arquitectónica.
- `security-auditor.md`: Auditoría de seguridad ofensiva/defensiva en aplicaciones, OWASP Top 10 y prácticas de código seguro.

### 2. Perfiles de Reglas (`rules/`)

Organizados en carpetas modulares por perfil, conteniendo cada una su archivo de contrato `AGENTS.md`:

- `pt-br-dev/AGENTS.md`: Directrices de desarrollo, seguridad, comunicación en portugués brasileño, respeto riguroso a la acentuación y puntuación, prohibición estricta de emojis y estándar obligatorio de Tailwind CSS.
- `general/AGENTS.md`: Directrices universales en inglés para proyectos y equipos internacionales, Clean Code, seguridad y arquitectura sólida.

### 3. Biblioteca Modular de Skills (`skills/`)

Para optimizar el consumo de tokens y evitar dudas en los modelos al seleccionar herramientas:

1. **Global Core (`skills/global/`):** 5 skills esenciales que establecen el comportamiento fundamental de pair programming en cualquier proyecto (~800 tokens en total).
2. **Biblioteca Bajo Demanda (`skills/{planning,docs,frontend,meta,stacks}/`):** Skills especializadas que se vinculan selectivamente solo en repositorios donde sean pertinentes.

---

## Instalación

Recomendamos ampliamente instalar `omni-agents` a través de **gestores de herramientas CLI aislados** (`pipx` o `uv`). Esto garantiza que el entorno Python global de su sistema permanezca intacto y limpio, manteniendo los comandos `omni-agents` y `omni` accesibles globalmente en su terminal.

---

### Método 1: Recomendado — Instalación Aislada vía `pipx`

`pipx` instala aplicaciones de terminal en entornos virtuales dedicados y expone sus ejecutables directamente en su `PATH`.

#### Paso 1: Instale `pipx` en su Sistema Operativo

- **Windows (PowerShell):**
  La forma oficial y recomendada de instalar `pipx` en Windows es directamente mediante `pip`:
  ```powershell
  python -m pip install --user pipx
  python -m pipx ensurepath
  ```
  *(Reinicie su ventana de terminal o PowerShell tras ejecutar `ensurepath`).*

- **Linux (Ubuntu / Debian):**
  ```bash
  sudo apt update && sudo apt install -y pipx
  pipx ensurepath
  ```
  *(Fedora: `sudo dnf install pipx` | Arch Linux: `sudo pacman -S python-pipx` | O vía pip: `python3 -m pip install --user pipx`)*

- **macOS:**
  ```bash
  brew install pipx
  pipx ensurepath
  ```
  *(O vía pip: `python3 -m pip install --user pipx`)*

#### Paso 2: Instale `omni-agents`

```bash
pipx install omni-agents-cli
```

Para actualizar a la versión más reciente en el futuro:
```bash
pipx upgrade omni-agents-cli
```

---

### Método 2: Alternativa de Alto Rendimiento — Instalación Aislada vía `uv`

`uv` es un gestor moderno y ultrarrápido para paquetes y herramientas Python, desarrollado en Rust.

#### Paso 1: Instale `uv` en su Sistema Operativo

- **Windows (PowerShell):**
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
  *(O mediante winget: `winget install astral-sh.uv`)*

- **Linux y macOS:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
  *(O en macOS con Homebrew: `brew install uv`)*

#### Paso 2: Instale `omni-agents`

```bash
uv tool install omni-agents-cli
```

Para actualizar a la versión más reciente en el futuro:
```bash
uv tool upgrade omni-agents-cli
```

---

### Método 3: Instalación Directa vía `pip`

Si prefiere instalar directamente en el entorno Python global o actual:

```bash
pip install omni-agents-cli
```

Para actualizar:
```bash
pip install --upgrade omni-agents-cli
```

---

### Método 4: Instaladores de Comando Único

- **Windows (PowerShell):**
  ```powershell
  irm https://raw.githubusercontent.com/TheCheepeer/omni-agents/main/install.ps1 | iex
  ```
- **Linux / macOS:**
  ```bash
  curl -fsSL https://raw.githubusercontent.com/TheCheepeer/omni-agents/main/install.sh | bash
  ```

---

## Configuración y Automatización Multiplataforma

La herramienta puede ejecutarse globalmente mediante el comando **`omni-agents`** (o el alias `omni`).

Para desarrollo local dentro del repositorio clonado, instale en modo editable:

```bash
pip install -e .
```

### 1. Modo Interactivo (TUI / GUI)

```bash
# Iniciar el menú interactivo globalmente:
omni-agents
# o mediante el alias:
omni

# O especificando la ruta del proyecto destino directamente:
omni-agents /ruta/al/proyecto
omni-agents .
```

#### Estructura del Menú Interactivo:

```text
=================================================================
  CONFIGURADOR MULTI-TOOL DE AGENTES, REGLAS Y SKILLS (v1.0.0)
=================================================================
  Modo:               Modo de Desarrollo Local (Repositorio)
  Workspace Destino:  [/ruta/al/proyecto]
  Herramientas Activas: antigravity, cursor, claude
-----------------------------------------------------------------
  [t] Seleccionar Herramientas Destino (Antigravity, Cursor, Claude...)
  [1] Configuración Global del Sistema (Antigravity y Claude)
  [2] Subagentes para el Workspace
  [3] Reglas para el Workspace
  [4] Skills Modulares para el Workspace
  [e] Extensiones Remotas (Catálogo GitHub / ext/)
  [o] Abrir Carpeta Personal (Documentos/omni-agents)
  [s] Sincronizar Todo (Sync herramientas activas en lote)
  [c] Limpiar / Desinstalar por Herramienta
  [l] Idioma / Language: [ES | EN | PT-BR]
  [5] Salir
-----------------------------------------------------------------
  [w] Definir / Cambiar Workspace Destino
=================================================================
```

---

### 2. Interfaz de Línea de Comandos (CLI / Automatización)

Ejecute comandos directamente en terminales o pipelines de CI/CD:

```bash
# Diagnóstico e información de rutas del sistema:
omni-agents --info

# Comprobar y actualizar omni-agents:
omni-agents --update

# Listar todas las herramientas compatibles:
omni-agents --list-tools

# Sincronizar el workspace en todas las herramientas activas:
omni-agents /ruta/al/proyecto --sync

# Configurar para una herramienta específica:
omni-agents /ruta/al/proyecto --tool cursor --sync
omni-agents /ruta/al/proyecto --tool claude --sync
omni-agents /ruta/al/proyecto --tool copilot --sync

# Configurar para todas las herramientas simultáneamente (Multi-Tool):
omni-agents /ruta/al/proyecto --tool all --sync

# Remover configuración de una sola herramienta sin afectar a las demás:
omni-agents /ruta/al/proyecto --tool cursor --clean
omni-agents /ruta/al/proyecto --clean  # Remueve todas

# Aplicar configuración global del sistema:
omni-agents --global
omni-agents --tool claude --global

# Forzar idioma de la interfaz:
omni-agents --lang es
omni-agents --lang en
omni-agents --lang pt
```

---

### 3. Escenarios Estratégicos

#### Flujo de Trabajo en Equipo Multi-Tool

En equipos donde diferentes desarrolladores utilizan distintos entornos (por ejemplo, el desarrollador A usa Cursor, el desarrollador B usa VS Code con Copilot y el desarrollador C usa Antigravity), use `--tool all`. El script exporta los archivos de configuración nativos para cada asistente desde una única fuente de verdad, garantizando coherencia en todo el proyecto.

#### Sincronización Rápida (Sync)

Al actualizar reglas o skills en este repositorio, ejecute `--sync` en cualquier proyecto destino para regenerar instantáneamente los archivos consolidados (`CLAUDE.md`, `copilot-instructions.md`, `.cursor/rules/`, etc.).

#### Persistencia de Estado

Las preferencias del workspace se guardan en `.agents/workspace_state.json` (agregado automáticamente a `.gitignore`), lo que permite inspeccionar y modificar los destinos activos en cualquier momento.

---

## Documentación Técnica

Para guías detalladas y referencias de ingeniería (en inglés), consulte:

- [Arquitectura y Diseño](../architecture.md): Resolución de componentes en capas, vinculación en sistemas de archivos y patrones de adaptadores.
- [Referencia de Línea de Comandos (CLI)](../cli.md): Sintaxis completa, parámetros, navegación interactiva (TUI) y automatización CI/CD sin interfaz.
- [Configuración y Extensiones](../configuration.md): Esquema de `config.json`, personalizaciones en `custom/`, catálogo remoto y actualizaciones.
- [Guía de Contribución y Estándares](../contributing.md): Configuración del entorno local, directrices de código, nuevos adaptadores e internacionalización.

---

## Créditos y Agradecimientos

Diversas skills incluidas en este repositorio fueron adaptadas a partir de:

- [agent-skills](https://github.com/joshuadavidthomas/agent-skills) por Josh Thomas (Licencia MIT).
- [The Grug Brained Developer](https://grugbrain.dev/) por Colin McDonnell.
- [Framework Diátaxis](https://diataxis.fr/) por Daniele Procida.

Consulte el archivo [NOTICE](../../NOTICE) para las declaraciones formales de licencias y derechos de autor de terceros.

---

## Licencia

Distribuido bajo la Licencia Apache 2.0. Consulte el archivo [LICENSE](../../LICENSE) para más detalles.

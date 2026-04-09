# Guía rápida para publicar este proyecto en GitHub

## 1. No subas el respaldo completo
Tu carpeta actual es un **backup de trabajo**, no un portafolio. Para una propuesta laboral, arma un repositorio limpio.

## 2. Qué sí debes subir
- `src/mecanum_robot/`
- `src/my_localizer_launcher/` (si es tuyo)
- `README.md`
- `.gitignore`
- `docs/` con imágenes, diagramas y explicación técnica
- `maps/` solo si quieres mostrar un mapa de ejemplo pequeño

## 3. Qué NO debes subir
- `build/`
- `devel/`
- `__pycache__/`
- paquetes de terceros sin cambios propios (`rplidar_ros`, `turtlebot3`, etc.)
- credenciales, IPs fijas, usuarios, contraseñas
- archivos pesados innecesarios

## 4. Estructura recomendada
```text
mecanum-robot-ros/
├── README.md
├── .gitignore
├── LICENSE
├── docs/
│   └── media/
├── src/
│   ├── mecanum_robot/
│   └── my_localizer_launcher/
└── maps/
```

## 5. Flujo recomendado
```bash
mkdir mecanum-robot-ros
cd mecanum-robot-ros
mkdir -p src docs/media maps
```

Luego copia manualmente tus paquetes propios dentro de `src/`.

## 6. Inicializar Git
```bash
git init
git add .
git commit -m "Initial commit: mecanum robot ROS project"
git branch -M main
```

## 7. Crear repositorio en GitHub
En GitHub:
- New repository
- Nombre recomendado: `mecanum-robot-ros`
- Descripción recomendada: `ROS-based mecanum mobile robot with teleoperation, obstacle avoidance, odometry and 2D mapping`
- Público, salvo que tengas restricciones

Luego conecta el remoto:

```bash
git remote add origin https://github.com/TU_USUARIO/mecanum-robot-ros.git
git push -u origin main
```

## 8. Activos que elevan mucho el valor del repo
- foto del robot
- GIF corto moviéndose
- screenshot de RViz
- mapa generado
- diagrama de nodos y tópicos ROS

## 9. Ajuste fino para que se vea profesional
- README en inglés
- commits con mensajes claros
- sin archivos basura
- sin rutas locales ni configuraciones privadas
- una sección de “Future Work”
- una sección de “System Architecture”

## 10. Regla clave
Tu GitHub debe parecer un **producto de ingeniería**, no una carpeta exportada del disco.

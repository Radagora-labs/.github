# Radagora Labs

Repositorio especial de la organización:

- `profile/README.md`: la portada que se ve en https://github.com/Radagora-labs, con sus recursos en `profile/assets/`.
- `SECURITY.md`: política de seguridad por defecto para todos los repositorios de la organización.
- `marca/`: avatar de la organización (`avatar.png`, 500×500) e imagen para compartir en redes (`social.png`, 1280×640).
- `herramientas/generar.py`: regenera los SVG del perfil. Los textos se convierten en trazos con Space Grotesk (licencia OFL, en `herramientas/fuentes/`), porque GitHub no carga fuentes dentro de un SVG.

```bash
pip install fonttools
python herramientas/generar.py herramientas/fuentes profile/assets
```

Las animaciones son CSS dentro de cada SVG (GitHub no ejecuta JavaScript) y se desactivan cuando el sistema pide reducir el movimiento.

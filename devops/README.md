# DevOps

## Configuración

Asegurese de navegar primero al directorio `devops` antes de ejecutar cualquier comando listado en este documento.

```shell
cd devops
```

### Configuración del entorno

Empiece creando un archivo `.env` en el directorio `devops`. Puede copiar el archivo `.env_dist` como punto de partida:

```shell
cp .env_dist .env
```

Edite el archivo `.env` para adecuarlo a su entorno. Por ejemplo:

```
ANSIBLE_REMOTE_PORT=22
```

## Crear contenedor docker

```
make server-setup
```

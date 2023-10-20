# Plugin de AGESIC para CKAN

<!-- Table of Contents -->
# Tabla de contenido
- [Sobre el repositorio](#sobre-el-repositorio)
  * [Tecnologías](#tecnologías)
  * [Características](#características)
  * [Referencia de colores](#referencia-de-colores)
- [Como empezar](#como-empezar)
  * [Prerrequisitos](#prerrequisitos)
  * [Instalación](#instalación)
- [Licencia](#licencia)
- [Contacto](#contacto)

## Sobre el repositorio
Este es un plugin personalizado para CKAN que agrega funcionalidades específicas y personalizaciones a la plataforma CKAN. El objetivo principal de este plugin es mejorar la experiencia del usuario y extender las capacidades de CKAN.

### Tecnologías

  <ul>
    <li><a href="https://ckan.org/">CKAN</a></li>
    <li><a href="https://www.python.org/">Python 3</a></li>
    <li><a href="https://www.postgresql.org/">PostgreSQL</a></li>
    <li><a href="https://solr.apache.org/">Apache Solr</a></li>
  </ul>


### Características
- Personalizaciones de Vistas: Este plugin proporciona vistas personalizadas que permiten una presentación de datos más atractiva y significativa para los usuarios de CKAN, basado en las necesidades del Catálogo de Datos de Uruguay. Las vistas personalizadas se han diseñado para resaltar la información clave y mejorar la navegación. Además de cumplir los requisitos técnicos definidos en el Decreto 406/022 que corresponden a las pautas de accesibilidad WCAG 2.1 de la W3C.

- Instalación: se incluyen scripts para la instalación del plugin, como la instalación de dependencias, configuraciones específicas y ejecución del proceso para poner en funcionamiento el plugin.

- Compatibilidad: este plugin es compatible con las últimas versiones de CKAN (2.9.X), lo que garantiza que los usuarios puedan aprovechar las características más recientes de la plataforma.

- Dockerizado: Esta solución se ha dockerizado para simplificar el proceso de despliegue.

### Referencia de colores

|     Color             | Hex |
| -------------------   | ----  |
|      Ref1             |![#003da5](https://via.placeholder.com/10/003da5?text=+) #003da5|
|      Ref2             |![#042f62](https://via.placeholder.com/10/042f62?text=+) #042f62|
|      Ref3             |![#f9f9f9](https://via.placeholder.com/10/f9f9f9?text=+) #f9f9f9|


## Como empezar

### Prerrequisitos

Este proyecto utiliza Python 3.9 como lenguaje base y otros contenedores docker.

### Instalación

Clonar el proyecto y configurar las variables de entorno. Compilar e iniciar los contenedores.

```bash
 cd contrib
 docker-compose build
 docker-compose up
```
## Licencia
Distribuido bajo GNU GPL.

## Contacto
Por cualquier duda o consulta, puede comunicarse a datosabiertos@agesic.gub.uy


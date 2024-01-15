# Máster Ciencia de Datos de la UOC 
## Visualización de Datos (Práctica parte II) - Sergio Sánchez Romero

### Introducción

En esta segunda parte de la práctica, el alumno tendrá que desarrollar una visualización de datos que demuestre su conocimiento del campo, así como el uso de diferentes herramientas y técnicas, basadas en el conjunto de datos seleccionado y validado en la primera parte de la práctica.

Esta práctica está orientada a los siguientes objetivos:

- Utilización de diversas herramientas avanzadas para la creación de visualizaciones.
- Creación de un proyecto de visualización de datos con una estructura, diseño y contenido profesional.
- Practicar  varios tipos de enfoques sobre las preguntas clave a responder.
- Comprender los elementos de interactividad que proporcionan valor a una visualización.


### Selección del dataset a estudiar

El conjunto de datos escogido contiene una relación de personas que han sufrido algún tipo de lesión (heridos leves, heridos graves o fallecidos) en un accidente gestionado por la Policía en la ciudad de Barcelona.
Este dataset se puede encontrar en la página de Open Data BCN y concretamente en la siguiente dirección:

https://opendata-ajuntament.barcelona.cat/data/es/dataset/accidentspersones-gu-bcn

donde se pueden escoger varios ficheros de tipo csv desde los años 2010 al 2022.
Estos datos tendrían el tercer nivel en el modelo de cinco estrellas de Open Data ya que corresponden a un formato estructurado abierto y es el mínimo recomendado para poder realizar una buena visualización.

![image](https://github.com/ssanchezromer/PRAVD/assets/122234525/b22e8a90-3e1e-4c46-904b-f15d3cb17873)

He escogido este tipo de dataset porque puede ser fundamental para mejorar la seguridad vial, diseñar políticas efectivas y, en última instancia, salvar vidas al reducir la incidencia y gravedad de los accidentes de tráfico. He encontrado
interesante tener más conocimientos en este ámbito de la ciudad que vivo actualmente.

Decir que el conjunto de datos cuenta con licencia tipo Creative Commons Attribution 4.0 (Open Data).

### Datos combinados

Se han combinado varios ficheros csv de diferentes años (2018-2022) para poder realizar un estudio temporal. 
Se han tenido que ajustar nombres de las columnas y adaptar los datos porque no tenían el mismo número de columnas.
El conjunto de datos final está en la carpeta `data` y se llama `datos_combinados.csv`.

### Solución propuesta

Se ha realizado una app en Streamlit donde podemos visualizar varios gráficos que nos permiten entender nuestros datos.

### Instalación/Ejecución del programa

Para poder ejecutar el programa podemos hacerlo desde la versión online subida al servidor de streamlit:

https://ssanchezromer-pravd.streamlit.app/

Si queremos ejecutarla en local debemos realizar los siguientes pasos:

1) Descargar el código del programa que está en la carpeta `code`.

2) Ir a nuestra terminal y crear el environment.

3) Instalar las librerías dentro de nuestro environment desde el fichero `requirements.txt`

```python
pip install -r requirements.txt
```
   
4) Ejecutar la aplicación mediante el comando:
   
```python
   streamlit run main.py
```

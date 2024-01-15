import streamlit as st
import pandas as pd
import plotly.express as px
import time
import threading
import queue

# Configuración de la página
st.set_page_config(
    page_title="PRA: Visualización de Datos (parte II)",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

scale_color = px.colors.qualitative.Pastel


# Cargar datos desde el archivo CSV
# @st.cache_data
def load_data():
    data = pd.read_csv("../data/datos_combinados.csv", encoding='utf8', delimiter=';')
    return data


def page_home():
    st.title("Práctica Visualización de Datos (parte II)")
    st.markdown("""
        <h3 style="color:gray">Personas involucradas en accidentes gestionados por la Guardia Urbana en la ciudad de Barcelona</h3>
        <p>Personas involucradas en un accidente gestionado por la Guardia Urbana en la ciudad de Barcelona y que han sufrido algún tipo de lesión (herido leve, herido grave o muerte).
        Incluye descripción de la persona (conductor, pasajero o peatón), sexo, edad, vehículo asociado a la persona y si la causa ha sido del peatón.<br />
        Hemos recopilado un total de 5 años en nuestro conjuntos de datos, del <b>2018 al 2022</b>.<br /><br />
        ¡Esperamos que encuentres la información interesante!</p>
        <a href="https://opendata-ajuntament.barcelona.cat/data/es/dataset/accidents-persones-gu-bcn" target="_blank" style="font-size: 10px">Fuente de datos</a>
        <p>&nbsp;</p>
    """, unsafe_allow_html=True)

    # saber el número de expedientes, personas implicadas, años diferentes,
    # número de distritos, número de barrios, número de calles
    data = load_data()
    # get the total expedientes
    total_expedientes = data["Numero_expedient"].nunique()
    # get the total personas implicadas
    total_personas_implicadas = data["Numero_expedient"].count()
    # get the total years
    total_years = data["NK_Any"].nunique()
    # get the total distritos
    total_distritos = data["Nom_districte"].nunique()
    # get the total barrios
    total_barrios = data["Nom_barri"].nunique()
    # get the total calles
    total_calles = data["Nom_carrer"].nunique()
    # dividir en 6 columnas y mostrar los datos
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric(label="Años", value=total_years)
    col2.metric(label="Expedientes", value=total_expedientes)
    col3.metric(label="Personas Implicadas", value=total_personas_implicadas)
    col4.metric(label="Distritos", value=total_distritos)
    col5.metric(label="Barrios", value=total_barrios)
    col6.metric(label="Calles", value=total_calles)

    # obtener numero de muertos, heridos graves, heridos leves, sanos, desconocidos
    victimizacion_mapping = {
        "Ferit lleu: Amb assistència sanitària en lloc d'accident": "Herido leve",
        "Ferit lleu: Hospitalització fins a 24h": "Herido leve",
        "Ferit lleu: Rebutja assistència sanitària": "Herido leve",
        "Ferit greu: hospitalització superior a 24h": "Herido grave",
        "Mort (dins 24h posteriors accident)": "Muerto",
        "Mort (després de 24h posteriors accident)": "Muerto",
        "Mort natural": "Muerto",
        "Il.lès": "Sano",
        "Desconegut": "Desconocido",
        "Es desconeix": "Desconocido",
    }

    data["Descripcio_victimitzacio"] = data["Descripcio_victimitzacio"].map(victimizacion_mapping)
    # contar cuantos muertos, heridos graves, heridos leves, sanos, desconocidos hay
    cuantos_muertos = data[data["Descripcio_victimitzacio"] == "Muerto"].count()
    cuantos_heridos_graves = data[data["Descripcio_victimitzacio"] == "Herido grave"].count()
    cuantos_heridos_leves = data[data["Descripcio_victimitzacio"] == "Herido leve"].count()
    cuantos_sanos = data[data["Descripcio_victimitzacio"] == "Sano"].count()
    cuantos_desconocidos = data[data["Descripcio_victimitzacio"] == "Desconocido"].count()
    # dividir en 6 columnas y mostrar los datos
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric(label="Personas Implicadas", value=total_personas_implicadas)
    col2.metric(label="Muertos", value=cuantos_muertos["Descripcio_victimitzacio"])
    col3.metric(label="Heridos Graves", value=cuantos_heridos_graves["Descripcio_victimitzacio"])
    col4.metric(label="Heridos Leves", value=cuantos_heridos_leves["Descripcio_victimitzacio"])
    col5.metric(label="Sanos", value=cuantos_sanos["Descripcio_victimitzacio"])
    col6.metric(label="Desconocidos", value=cuantos_desconocidos["Descripcio_victimitzacio"])

    # show head of the data
    # st.subheader("Primeras filas de los datos")
    st.dataframe(data.head(10))


def create_bar_chart(data, años):
    fig = px.bar(
        data,
        x="accident_count_yearly",
        y="Desc_Tipus_vehicle_implicat",
        title=f"Evolución Temporal de Tipos de Vehículos Implicados en Accidentes ({años})",
        labels={"Desc_Tipus_vehicle_implicat": "Tipo de Vehículo",
                "accident_count_yearly": "Número de Accidentes",
                "NK_Any": "Año"},
        height=500,
        color="NK_Any",
        text="accident_count_yearly",
        color_discrete_sequence=scale_color

    )
    totals = data.groupby("Desc_Tipus_vehicle_implicat")["accident_count_yearly"].sum()
    for i, category in enumerate(data["Desc_Tipus_vehicle_implicat"].unique()):
        fig.add_annotation(
            x=totals[category],
            y=category,
            text=f'<span style="font-weight:bold; font-size: 16px;">{totals[category]}</span>',
            showarrow=True,
            arrowhead=0,
            ax=30,
            ay=0
        )

    # fig.layout.showlegend = False
    return fig


def create_pie_chart(data, años):
    fig = px.pie(
        data,
        names="Desc_Tipus_vehicle_implicat",
        title=f"Tipos de Vehículos Implicados en Accidentes ({años})",
        labels={"Desc_Tipus_vehicle_implicat": "Tipo de Vehículo"},
        height=500,
        color_discrete_sequence=scale_color,
    )
    fig.update_traces(insidetextfont=dict(color='white', size=16),
                      outsidetextfont=dict(color='gray', size=16))

    return fig


def page_grafico_vehiculos():
    st.title("Tipos de Vehículos Implicados en Accidentes")


    # Cargar datos
    data = load_data()

    # Slider de mínimo de accidentes
    selected_minAccidente = st.sidebar.slider("Seleccionar número mínimo de accidentes", min_value=1,
                                              max_value=data.groupby("Desc_Tipus_vehicle_implicat")[
                                                  "Desc_Tipus_vehicle_implicat"].transform("count").max(), value=500)
    show_all_years = st.sidebar.checkbox("Mostrar todos los años", value=True)
    color = "NK_Any"
    category_orders = {"NK_Any": sorted(data["NK_Any"].unique())}

    años = f"{data['NK_Any'].min()}-{data['NK_Any'].max()}"

    if not show_all_years:
        selected_years = st.sidebar.select_slider("Seleccionar Rango de Años",
                                                  options=list(range(data["NK_Any"].min(), data["NK_Any"].max() + 1)),
                                                  value=(data["NK_Any"].min(), data["NK_Any"].max()))
        data = data[data["NK_Any"].between(selected_years[0], selected_years[1])]
        if selected_years[0] == selected_years[1]:
            años = f"{selected_years[0]}"
        else:
            años = f"{selected_years[0]}-{selected_years[1]}"

    # Agregar columna con el número de accidentes por categoría
    data["accident_count"] = data.groupby("Desc_Tipus_vehicle_implicat")["Desc_Tipus_vehicle_implicat"].transform(
        "count")

    # Filtrar datos originales por el número mínimo de accidentes
    filtered_data = data[data["accident_count"] >= selected_minAccidente]

    # Ordenar datos por el número de accidentes
    filtered_data = filtered_data.sort_values(by=["NK_Any", "accident_count"], ascending=[True, True])

    # Agregar columna con el número de accidentes por categoría y año
    filtered_data["accident_count_yearly"] = filtered_data.groupby(["Desc_Tipus_vehicle_implicat", "NK_Any"])[
        "Desc_Tipus_vehicle_implicat"].transform("count")


    # Capturar los 3 vehículos más implicados en accidentes
    top_vehicles = filtered_data.groupby("Desc_Tipus_vehicle_implicat")["accident_count_yearly"].sum().sort_values(
        ascending=False).head(5).index.tolist()
    # obtener el texto de los 3 vehículos más implicados en accidentes
    top_vehicles = ", ".join(top_vehicles)

    st.markdown(f"""
    Los tipos de vehículos más implicados en accidentes entre **:gray[{años}]** son: **:red[{str(top_vehicles)}]**.\n
    (Núm. mínimo de vehículos implicados: **:gray[{selected_minAccidente}]**)\n\n
    Realizamos un gráfico de barras y de tarta para ver la distribución de los 
    tipos de vehículos implicados en accidentes.\n  
    """)


    # Seleccionar columnas únicas
    selected_columns = ["Desc_Tipus_vehicle_implicat", "NK_Any", "accident_count_yearly"]
    unique_data = filtered_data[selected_columns].drop_duplicates()
    unique_data["NK_Any"] = unique_data["NK_Any"].astype(str)
    unique_data["Desc_Tipus_vehicle_implicat"] = unique_data["Desc_Tipus_vehicle_implicat"].astype(str)

    # Crear y mostrar el gráfico de barras
    st.plotly_chart(create_bar_chart(unique_data, años), use_container_width=True)

    # Crear y mostrar el gráfico de piechart
    st.plotly_chart(create_pie_chart(filtered_data, años), use_container_width=True)


def create_sex_pie_chart(filtered_data, selected_years, show_percentage):

    # contar cuantos hombres, mujeres y desconocidos hay
    cuantos_hombres = filtered_data[filtered_data["Descripcio_sexe"] == "Hombre"].count()
    cuantos_mujeres = filtered_data[filtered_data["Descripcio_sexe"] == "Mujer"].count()
    cuantos_desconocidos = filtered_data[filtered_data["Descripcio_sexe"] == "Desconocido"].count()
    # hacer una array de las etiquetas y valores
    labels = ["Hombre", "Mujer", "Desconocido"]
    values = [cuantos_hombres["Descripcio_sexe"], cuantos_mujeres["Descripcio_sexe"], cuantos_desconocidos["Descripcio_sexe"]]
    # construir un array de labels y values para poder ordernar por values
    labels_values = []
    for i in range(len(labels)):
        labels_values.append([labels[i], values[i]])
    # ordenar el array por values
    labels_values.sort(key=lambda x: x[1], reverse=True)
    category_order_pie_chart = []
    # imprimir array labels_Values
    for i in range(len(labels_values)):
        category_order_pie_chart.append(labels_values[i][0])


    # Crear gráfico de pie para mostrar la distribución porcentual de accidentes por sexo
    fig = px.pie(
        filtered_data,
        names="Descripcio_sexe",
        title=f"Distribución de Accidentes por Sexo ({'-'.join(map(str, selected_years))})",
        labels={"Descripcio_sexe": "Sexo"},
        height=500,
        width=700,
        hole=0.3,  # Agujero en el centro para hacerlo parecer un donut
        color_discrete_sequence=scale_color
    )

    fig.update_traces(insidetextfont=dict(color='white', size=16),
                      outsidetextfont=dict(color='gray', size=16))

    # Añadir etiquetas con porcentajes
    if show_percentage:
        fig.update_traces(textinfo='percent+label', pull=[0.1, 0.1, 0.1])
    else:
        fig.update_traces(textinfo='value+label', pull=[0.1, 0.1, 0.1])

    pie_chart_colors = scale_color[:3]
    # category_order_pie_chart = ["Hombre", "Mujer", "Desconocido"]

    return fig, pie_chart_colors, category_order_pie_chart


def create_age_pie_chart(filtered_data, selected_years, show_percentage):


    # Crear gráfico de pie para mostrar la distribución porcentual de accidentes por sexo
    fig = px.pie(
        filtered_data,
        names="Franja_Edad",
        title=f"Distribución de Accidentes por Edad ({'-'.join(map(str, selected_years))})",
        labels={"Franja_Edad": "Edad"},
        height=500,
        width=700,
        hole=0.3,  # Agujero en el centro para hacerlo parecer un donut
        color_discrete_sequence=scale_color
    )
    # determine order to print the pie chart
    order = filtered_data["Franja_Edad"].value_counts().index

    fig.update_traces(insidetextfont=dict(color='white', size=16),
                      outsidetextfont=dict(color='gray', size=16))

    # Añadir etiquetas con porcentajes
    if show_percentage:
        fig.update_traces(textinfo='percent+label',
                          pull=[0.1, 0.1, 0.1, 0.1])
    else:
        fig.update_traces(textinfo='value+label', pull=[0.1, 0.1, 0.1, 0.1])

    # fig.layout.showlegend = False
    fig.layout.legend.title = "Grupo de Edad"

    pie_chart_colors = scale_color[:4]

    return fig, pie_chart_colors, order


def create_personas_pie_chart(data, selected_years, show_percentage):
    # Filtrar los datos por los años seleccionados
    filtered_data = data[data["NK_Any"].isin(selected_years)]

    # Calcular el número total de accidentes
    total_accidents = len(filtered_data)

    personas_mapping = {"Conductor": "Conductor", "Vianant": "Peatón", "Passatger": "Pasajero", "Desconegut": "Desconocido"}
    filtered_data["Descripcio_tipus_persona"] = filtered_data["Descripcio_tipus_persona"].map(personas_mapping)

    # saber cuantos registros hay de tipo conductor, pasajero, peaton, desconocido
    cuantos_conductores = filtered_data[filtered_data["Descripcio_tipus_persona"] == "Conductor"].count()
    cuantos_pasajeros = filtered_data[filtered_data["Descripcio_tipus_persona"] == "Pasajero"].count()
    cuantos_peatones = filtered_data[filtered_data["Descripcio_tipus_persona"] == "Peatón"].count()
    cuantos_desconocidos = filtered_data[filtered_data["Descripcio_tipus_persona"] == "Desconocido"].count()
    # hacer una array de las etiquetas y valores
    labels = ["Conductor", "Pasajero", "Peatón", "Desconocido"]
    values = [cuantos_conductores["Descripcio_tipus_persona"], cuantos_pasajeros["Descripcio_tipus_persona"],
                                cuantos_peatones["Descripcio_tipus_persona"], cuantos_desconocidos["Descripcio_tipus_persona"]]
    # construir un array de labels y values para poder ordernar por values
    labels_values = []
    for i in range(len(labels)):
        labels_values.append([labels[i], values[i]])
    # ordenar el array por values
    labels_values.sort(key=lambda x: x[1], reverse=True)
    category_order_pie_chart = []
    # imprimir array labels_Values
    for i in range(len(labels_values)):
        category_order_pie_chart.append(labels_values[i][0])

    # Crear gráfico de pie para mostrar la distribución porcentual de accidentes por sexo
    fig = px.pie(
        filtered_data,
        names="Descripcio_tipus_persona",
        title=f"Distribución de Accidentes por tipo de persona ({'-'.join(map(str, selected_years))})",
        labels={"Descripcio_tipus_persona": "Tipo de Persona"},
        height=500,
        width=700,
        hole=0.3,  # Agujero en el centro para hacerlo parecer un donut
        color_discrete_sequence=scale_color
    )

    fig.update_traces(insidetextfont=dict(color='white', size=16),
                      outsidetextfont=dict(color='gray', size=16))

    # Añadir etiquetas con porcentajes
    if show_percentage:
        fig.update_traces(textinfo='percent+label', pull=[0.1, 0.1, 0.1])
    else:
        fig.update_traces(textinfo='value+label', pull=[0.1, 0.1, 0.1])

    pie_chart_colors = scale_color[:4]

    return fig, pie_chart_colors, category_order_pie_chart


def create_victimizacion_pie_chart(data, selected_years, show_percentage):
    # Filtrar los datos por los años seleccionados
    filtered_data = data[data["NK_Any"].isin(selected_years)]

    # Calcular el número total de accidentes
    total_accidents = len(filtered_data)

    victimizacion_mapping = {"Ferit lleu: Amb assistència sanitària en lloc d'accident": "Herido leve",
                             "Ferit lleu: Hospitalització fins a 24h": "Herido leve",
                             "Ferit lleu: Rebutja assistència sanitària": "Herido leve",
                             "Ferit greu: hospitalització superior a 24h": "Herido grave",
                             "Mort (dins 24h posteriors accident)": "Muerto",
                             "Mort (després de 24h posteriors accident)": "Muerto",
                             "Mort natural": "Muerto",
                             "Il.lès": "Sano",
                             "Desconegut": "Desconocido",
                             "Es desconeix": "Desconocido",
                             }

    filtered_data["Descripcio_victimitzacio"] = filtered_data["Descripcio_victimitzacio"].map(victimizacion_mapping)

    # saber cuantos registros hay de tipo muerto, herido grave, herido leve, sano, desconocido
    cuantos_muertos = filtered_data[filtered_data["Descripcio_victimitzacio"] == "Muerto"].count()
    cuantos_heridos_graves = filtered_data[filtered_data["Descripcio_victimitzacio"] == "Herido grave"].count()
    cuantos_heridos_leves = filtered_data[filtered_data["Descripcio_victimitzacio"] == "Herido leve"].count()
    cuantos_sanos = filtered_data[filtered_data["Descripcio_victimitzacio"] == "Sano"].count()
    cuantos_desconocidos = filtered_data[filtered_data["Descripcio_victimitzacio"] == "Desconocido"].count()

    # hacer una array de las etiquetas y valores
    labels = ["Muerto", "Herido grave", "Herido leve", "Sano", "Desconocido"]
    values = [cuantos_muertos["Descripcio_victimitzacio"], cuantos_heridos_graves["Descripcio_victimitzacio"],
                                cuantos_heridos_leves["Descripcio_victimitzacio"], cuantos_sanos["Descripcio_victimitzacio"],
                                cuantos_desconocidos["Descripcio_victimitzacio"]]
    # construir un array de labels y values para poder ordernar por values
    labels_values = []
    for i in range(len(labels)):
        labels_values.append([labels[i], values[i]])
    # ordenar el array por values
    labels_values.sort(key=lambda x: x[1], reverse=True)

    category_order_pie_chart = []
    # imprimir array labels_Values
    for i in range(len(labels_values)):
        category_order_pie_chart.append(labels_values[i][0])

    # Crear gráfico de pie para mostrar la distribución porcentual de accidentes por sexo
    fig = px.pie(
        filtered_data,
        names="Descripcio_victimitzacio",
        title=f"Distribución de Accidentes por victimización ({'-'.join(map(str, selected_years))})",
        labels={"Descripcio_victimitzacio": "Victimización"},
        height=500,
        width=700,
        hole=0.3,  # Agujero en el centro para hacerlo parecer un donut
        color_discrete_sequence=scale_color
    )

    fig.update_traces(insidetextfont=dict(color='white', size=16),
                      outsidetextfont=dict(color='gray', size=16))

    # Añadir etiquetas con porcentajes
    if show_percentage:
        fig.update_traces(textinfo='percent+label', pull=[0.1, 0.1, 0.1])
    else:
        fig.update_traces(textinfo='value+label', pull=[0.1, 0.1, 0.1])

    pie_chart_colors = scale_color[:5]


    return fig, pie_chart_colors, category_order_pie_chart



def create_sex_line_chart(filtered_data, selected_years, pie_chart_colors, category_order_pie_chart, show_percentage):


    # # Filtrar los datos por los años seleccionados
    # filtered_data = data[data["NK_Any"].isin(selected_years)]
    #
    # filtered_data["NK_Any"] = filtered_data["NK_Any"].astype(str)
    #
    # sex_mapping = {"Home": "Hombre", "Dona": "Mujer", "Desconegut": "Desconocido"}
    # filtered_data["Descripcio_sexe"] = filtered_data["Descripcio_sexe"].map(sex_mapping)

    # Agrupar por año y sexo para obtener el número total de implicados en accidentes
    total_involved = filtered_data.groupby(["NK_Any", "Descripcio_sexe"]).size().reset_index(name="Total Implicados")

    # Calcular los totales para porcentaje si es necesario
    if show_percentage:
        total_accidents_by_year = filtered_data.groupby("NK_Any").size().reset_index(name="Total Accidentes")
        total_involved = pd.merge(total_involved, total_accidents_by_year, on="NK_Any")
        total_involved["Total Implicados"] = (total_involved["Total Implicados"] / total_involved[
            "Total Accidentes"]) * 100

    # Formatear el porcentaje a dos decimales
    total_involved["Total Implicados"] = total_involved["Total Implicados"].round(2)

    # Crear gráfico de líneas para mostrar el número total de implicados en accidentes por sexo
    fig_line = px.line(
        total_involved,
        x="NK_Any",
        y="Total Implicados",
        color="Descripcio_sexe",
        labels={
            "Total Implicados": "Porcentaje de Implicados (%)" if show_percentage else "Nº total Implicados Accidentes",
            "NK_Any": "Año", "Descripcio_sexe": "Sexo"},

        title=f"Número Total de Implicados en Accidentes por Sexo ({'-'.join(map(str, selected_years))})",
        height=500,
        width=700,
        color_discrete_sequence=pie_chart_colors,
        category_orders={"Descripcio_sexe": category_order_pie_chart},  # Aplicar el orden de las categorías
        text='Total Implicados'
    )

    # desplazamiento de las etiquetas
    fig_line.update_traces(textposition='top center')

    return fig_line


def create_age_line_chart(filtered_data, selected_years, pie_chart_colors, category_order_pie_chart, show_percentage):
    # # Filtrar los datos por los años seleccionados
    # filtered_data = data[data["NK_Any"].isin(selected_years)]
    #
    # filtered_data["NK_Any"] = filtered_data["NK_Any"].astype(str)
    #
    # filtered_data["Edat"] = pd.to_numeric(filtered_data["Edat"],
    #                                       errors="coerce")  # Intenta convertir a numérico, maneja errores como NaN

    # Definir las categorías
    # bins = [-1, 24, 50, 75, 140]
    # labels = ["< 25", "25-50", "51-75", "> 75"]
    #
    # # Crear una columna categórica
    # filtered_data["Franja_Edad"] = pd.cut(filtered_data["Edat"], bins=bins, labels=labels)

    # Agrupar por año y sexo para obtener el número total de implicados en accidentes
    total_involved = filtered_data.groupby(["NK_Any", "Franja_Edad"]).size().reset_index(name="Total Implicados")

    # Calcular los totales para porcentaje si es necesario
    if show_percentage:
        total_accidents_by_year = filtered_data.groupby("NK_Any").size().reset_index(name="Total Accidentes")
        total_involved = pd.merge(total_involved, total_accidents_by_year, on="NK_Any")
        total_involved["Total Implicados"] = (total_involved["Total Implicados"] / total_involved[
            "Total Accidentes"]) * 100

    # Formatear el porcentaje a dos decimales
    total_involved["Total Implicados"] = total_involved["Total Implicados"].round(2)

    # Crear gráfico de líneas para mostrar el número total de implicados en accidentes por sexo
    fig_line = px.line(
        total_involved,
        x="NK_Any",
        y="Total Implicados",
        color="Franja_Edad",
        labels={
            "Total Implicados": "Porcentaje de Implicados (%)" if show_percentage else "Nº total Implicados Accidentes",
            "NK_Any": "Año", "Franja_Edad": "Edad"},

        title=f"Número Total de Implicados en Accidentes por Franja de Edad ({'-'.join(map(str, selected_years))})",
        height=500,
        width=700,
        color_discrete_sequence=pie_chart_colors,
        category_orders={"Franja_Edad": category_order_pie_chart, "NK_Any": selected_years},
        # Aplicar el orden de las categorías
        text='Total Implicados'
    )

    # desplazamiento de las etiquetas
    fig_line.update_traces(textposition='top center')
    fig_line.layout.legend.title = "Grupo de Edad"

    return fig_line


def create_personas_line_chart(data, selected_years, pie_chart_colors, category_order_pie_chart, show_percentage):
    # Filtrar los datos por los años seleccionados
    filtered_data = data[data["NK_Any"].isin(selected_years)]

    filtered_data["NK_Any"] = filtered_data["NK_Any"].astype(str)

    personas_mapping = {"Conductor": "Conductor", "Vianant": "Peatón", "Passatger": "Pasajero", "Desconegut": "Desconocido"}
    filtered_data["Descripcio_tipus_persona"] = filtered_data["Descripcio_tipus_persona"].map(personas_mapping)

    # Agrupar por año y sexo para obtener el número total de implicados en accidentes
    total_involved = filtered_data.groupby(["NK_Any", "Descripcio_tipus_persona"]).size().reset_index(name="Total Implicados")

    # Calcular los totales para porcentaje si es necesario
    if show_percentage:
        total_accidents_by_year = filtered_data.groupby("NK_Any").size().reset_index(name="Total Accidentes")
        total_involved = pd.merge(total_involved, total_accidents_by_year, on="NK_Any")
        total_involved["Total Implicados"] = (total_involved["Total Implicados"] / total_involved[
            "Total Accidentes"]) * 100

    # Formatear el porcentaje a dos decimales
    total_involved["Total Implicados"] = total_involved["Total Implicados"].round(2)

    # Crear gráfico de líneas para mostrar el número total de implicados en accidentes por sexo
    fig_line = px.line(
        total_involved,
        x="NK_Any",
        y="Total Implicados",
        color="Descripcio_tipus_persona",
        labels={
            "Total Implicados": "Porcentaje de Implicados (%)" if show_percentage else "Nº total Implicados Accidentes",
            "NK_Any": "Año", "Descripcio_tipus_persona": "Sexo"},

        title=f"Número Total de Implicados en Accidentes por tipo de persona ({'-'.join(map(str, selected_years))})",
        height=500,
        width=700,
        color_discrete_sequence=pie_chart_colors,
        category_orders={"Descripcio_tipus_persona": category_order_pie_chart},  # Aplicar el orden de las categorías
        text='Total Implicados'
    )

    # desplazamiento de las etiquetas
    fig_line.update_traces(textposition='top center')

    return fig_line



def create_victimizacion_line_chart(data, selected_years, pie_chart_colors, category_order_pie_chart, show_percentage):
    # Filtrar los datos por los años seleccionados
    filtered_data = data[data["NK_Any"].isin(selected_years)]

    filtered_data["NK_Any"] = filtered_data["NK_Any"].astype(str)

    victimizacion_mapping = {"Ferit lleu: Amb assistència sanitària en lloc d'accident": "Herido leve",
                             "Ferit lleu: Hospitalització fins a 24h": "Herido leve",
                             "Ferit lleu: Rebutja assistència sanitària": "Herido leve",
                             "Ferit greu: hospitalització superior a 24h": "Herido grave",
                             "Mort (dins 24h posteriors accident)": "Muerto",
                             "Mort (després de 24h posteriors accident)": "Muerto",
                             "Mort natural": "Muerto",
                             "Il.lès": "Sano",
                             "Desconegut": "Desconocido",
                             "Es desconeix": "Desconocido",
                             }

    filtered_data["Descripcio_victimitzacio"] = filtered_data["Descripcio_victimitzacio"].map(victimizacion_mapping)

    # Agrupar por año y sexo para obtener el número total de implicados en accidentes
    total_involved = filtered_data.groupby(["NK_Any", "Descripcio_victimitzacio"]).size().reset_index(name="Total Implicados")

    # Calcular los totales para porcentaje si es necesario
    if show_percentage:
        total_accidents_by_year = filtered_data.groupby("NK_Any").size().reset_index(name="Total Accidentes")
        total_involved = pd.merge(total_involved, total_accidents_by_year, on="NK_Any")
        total_involved["Total Implicados"] = (total_involved["Total Implicados"] / total_involved[
            "Total Accidentes"]) * 100

    # Formatear el porcentaje a dos decimales
    total_involved["Total Implicados"] = total_involved["Total Implicados"].round(2)

    # Crear gráfico de líneas para mostrar el número total de implicados en accidentes por sexo
    fig_line = px.line(
        total_involved,
        x="NK_Any",
        y="Total Implicados",
        color="Descripcio_victimitzacio",
        labels={
            "Total Implicados": "Porcentaje de Implicados (%)" if show_percentage else "Nº total Implicados Accidentes",
            "NK_Any": "Año", "Descripcio_victimitzacio": "Victimización"},

        title=f"Número Total de Implicados en Accidentes victimización ({'-'.join(map(str, selected_years))})",
        height=500,
        width=700,
        color_discrete_sequence=pie_chart_colors,
        category_orders={"Descripcio_victimitzacio": category_order_pie_chart},  # Aplicar el orden de las categorías
        text='Total Implicados'
    )

    # desplazamiento de las etiquetas
    fig_line.update_traces(textposition='top center')

    return fig_line

def page_sexo():
    st.title("Distribución de Accidentes por Sexo")
    # Cargar datos
    data = load_data()

    # Obtener la lista única de años en los datos
    available_years = sorted(data["NK_Any"].unique())

    # Checkbox para seleccionar los años
    selected_years = sorted(st.sidebar.multiselect("Seleccionar Años", available_years, default=available_years))

    # Radio para seleccionar entre porcentaje y valor real
    show_percentage = st.sidebar.radio("Mostrar en:", ["Porcentaje", "Valor Real"]) == "Porcentaje"

    # Filtrar los datos por los años seleccionados
    filtered_data = data[data["NK_Any"].isin(selected_years)]

    filtered_data["NK_Any"] = filtered_data["NK_Any"].astype(str)

    sex_mapping = {"Home": "Hombre", "Dona": "Mujer", "Desconegut": "Desconocido"}
    filtered_data["Descripcio_sexe"] = filtered_data["Descripcio_sexe"].map(sex_mapping)

    # Obtener sexo predominante (sex mapping)
    sex_predominant = filtered_data["Descripcio_sexe"].value_counts().index[0]

    if selected_years[0] == selected_years[1]:
        años = f"{selected_years[0]}"
    else:
        años = f"{selected_years[0]}-{selected_years[-1]}"

    st.markdown(f"""
        El sexo predominante en accidentes entre **:gray[{años}]** es: **:red[{str(sex_predominant)}]**.\n
        Realizamos un gráfico de barras y de tarta para ver la distribución del genéro implicado en accidentes.\n  
        """)


    # Crear pie chart
    fig_pie, pie_chart_colors, category_order_pie_chart = create_sex_pie_chart(filtered_data, sorted(selected_years),
                                                                               show_percentage)

    if len(selected_years) > 1:
        # Crear gráfica de líneas
        fig_line = create_sex_line_chart(filtered_data, sorted(selected_years), pie_chart_colors, category_order_pie_chart,
                                         show_percentage)
        # Colocar las dos gráficas una al lado de la otra
        col1, col2 = st.columns(2)

        col1.plotly_chart(fig_pie, use_container_width=True)
        col2.plotly_chart(fig_line, use_container_width=True)
    else:
        if len(selected_years) == 1:
            st.plotly_chart(fig_pie, use_container_width=True)


def page_personas():
    st.title("Distribución de Accidentes por tipos de persona")
    # Cargar datos
    data = load_data()

    # Obtener la lista única de años en los datos
    available_years = sorted(data["NK_Any"].unique())

    # Checkbox para seleccionar los años
    selected_years = sorted(st.sidebar.multiselect("Seleccionar Años", available_years, default=available_years))

    # Radio para seleccionar entre porcentaje y valor real
    show_percentage = st.sidebar.radio("Mostrar en:", ["Porcentaje", "Valor Real"]) == "Porcentaje"




    # Crear pie chart
    fig_pie, pie_chart_colors, category_order_pie_chart = create_personas_pie_chart(data, sorted(selected_years),
                                                                               show_percentage)

    if len(selected_years) > 1:
        # Crear gráfica de líneas
        fig_line = create_personas_line_chart(data, sorted(selected_years), pie_chart_colors, category_order_pie_chart,
                                         show_percentage)
        # Colocar las dos gráficas una al lado de la otra
        col1, col2 = st.columns(2)

        col1.plotly_chart(fig_pie, use_container_width=True)
        col2.plotly_chart(fig_line, use_container_width=True)
    else:
        if len(selected_years) == 1:
            st.plotly_chart(fig_pie, use_container_width=True)

def page_edad():
    st.title("Distribución de Accidentes por franjas de edad")
    # Cargar datos
    data = load_data()

    # Obtener la lista única de años en los datos
    available_years = sorted(data["NK_Any"].unique())

    # Checkbox para seleccionar los años
    selected_years = sorted(st.sidebar.multiselect("Seleccionar Años", available_years, default=available_years))

    # Radio para seleccionar entre porcentaje y valor real
    show_percentage = st.sidebar.radio("Mostrar en:", ["Porcentaje", "Valor Real"]) == "Porcentaje"

    # Filtrar los datos por los años seleccionados
    filtered_data = data[data["NK_Any"].isin(selected_years)]

    # quitamos los nulos y valores vacios
    filtered_data = filtered_data[filtered_data["Edat"] != "Desconegut"]
    filtered_data = filtered_data[filtered_data["Edat"] != "-1"]
    # drop na
    filtered_data = filtered_data.dropna(subset=["Edat"])
    # quitar categoria null de mis datos
    filtered_data = filtered_data[filtered_data["Edat"].notnull()]

    filtered_data["Edat"] = pd.to_numeric(filtered_data["Edat"],
                                          errors="coerce")  # Intenta convertir a numérico, maneja errores como NaN

    # Definir las categorías
    bins = [-1, 24, 50, 75, 140]
    labels = ["< 25", "25-50", "51-75", "> 75"]

    # Crear una columna categórica
    filtered_data["Franja_Edad"] = pd.cut(filtered_data["Edat"], bins=bins, labels=labels)


    # Obtener la franja más común
    age_group = filtered_data["Franja_Edad"].value_counts().index[0]

    st.markdown(f"""La franja de edad que acumula más accidente entre
     **:gray[{selected_years[0]}-{selected_years[-1]}]** es la de **:red[{str(age_group)}] años**.\n""")

    # Crear pie chart
    fig_pie, pie_chart_colors, category_order_pie_chart = create_age_pie_chart(filtered_data, sorted(selected_years),
                                                                               show_percentage)
    if len(selected_years) > 1:
        # Crear gráfica de líneas
        fig_line = create_age_line_chart(filtered_data, sorted(selected_years), pie_chart_colors, category_order_pie_chart,
                                         show_percentage)
        # Colocar las dos gráficas una al lado de la otra
        col1, col2 = st.columns(2)

        col1.plotly_chart(fig_pie, use_container_width=True)
        col2.plotly_chart(fig_line, use_container_width=True)
    else:
        if len(selected_years) == 1:
            st.plotly_chart(fig_pie, use_container_width=True)


def page_histograma_edad():

    st.title("Distribución de Accidentes por edad y nº vehículos implicados")

    # Cargar datos
    data = load_data()

    # Obtener la lista única de años en los datos
    available_years = sorted(data["NK_Any"].unique())

    # Checkbox para seleccionar los años
    selected_years = st.sidebar.multiselect("Seleccionar Años", available_years, default=available_years)

    st.sidebar.button("Recargar datos")

    filtered_data = data[data["NK_Any"].isin(selected_years)]

    # Calcular el número máximo de vehículos implicados
    max_vehicles = filtered_data.groupby("Numero_expedient")["Numero_expedient"].transform("count").max()

    # Filtrar los valores "Desconegut"
    unknown_mask = filtered_data["Edat"] == "Desconegut"
    unknown_values = filtered_data.loc[unknown_mask, "Edat"]

    # Eliminar temporalmente los valores "Desconegut"
    filtered_data.loc[unknown_mask, "Edat"] = None

    # Crear un histograma interactivo con plotly
    fig = px.histogram(
        filtered_data,
        x="Edat",
        nbins=20,
        title="Distribución de Edades",
        labels={"Edat": "Edad", "count": "Frecuencia"},
        color_discrete_sequence=scale_color,
    )

    def test_run():
        for x in range(1, max_vehicles + 1):
            time.sleep(1)
            q.put(x)

    q = queue.Queue()
    is_exit_target_if_main_exits = True
    threading.Thread(
        target=test_run,
        daemon=is_exit_target_if_main_exits).start()

    # Exit loop if we will not receive data within timeoutsec.
    timeoutsec = 30

    # creating a single-element container.
    placeholder = st.empty()

    # Simulate data from test_run() in placeholder.
    while True:
        try:
            val = q.get(block=True, timeout=timeoutsec)
        except queue.Empty:
            break  # exit loop
        else:
            with placeholder.container():
                # # Filtrar los datos por el número de vehículos implicados
                filtered_vehicles_data = filtered_data[
                    filtered_data.groupby("Numero_expedient")["Numero_expedient"].
                    transform("count").between(val, max_vehicles)]
                unknown_mask2 = filtered_vehicles_data["Edat"] == "Desconegut"
                unknown_values2 = filtered_vehicles_data.loc[unknown_mask2, "Edat"]

                # Eliminar temporalmente los valores "Desconegut"
                filtered_vehicles_data.loc[unknown_mask2, "Edat"] = None

                fig2 = px.histogram(
                    filtered_vehicles_data,
                    x="Edat",
                    nbins=20,
                    title=f"Distribución de Edades en Accidentes con {val}-{max_vehicles} Vehículos Implicados",
                    labels={"Edat": "Edad", "count": "Frecuencia"},
                    color_discrete_sequence=["coral"],
                )

                col1, col2 = st.columns(2)
                col1.plotly_chart(fig, use_container_width=True)
                col2.plotly_chart(fig2, use_container_width=True)
                col2.metric(label="Nº min vehículos implicados", value=val)
                q.task_done()
                if val == max_vehicles - 1:
                    break


def page_mapa():
    st.title("Mapa Accidentes en Barcelona")
    # Cargar datos
    data = load_data()

    # Multiselect para años
    selected_years = st.sidebar.multiselect("Seleccionar Años", sorted(data["NK_Any"].unique()),
                                            default=sorted(data["NK_Any"].unique()))

    # Checkbox para tipos de vehículo
    all_vehicle_types = sorted(data["Desc_Tipus_vehicle_implicat"].unique())
    selected_vehicle_types = st.sidebar.multiselect("Seleccionar Tipos de Vehículo", all_vehicle_types,
                                                    default=all_vehicle_types)

    filtered_data = data[data["NK_Any"].isin(selected_years) &
                         data["Desc_Tipus_vehicle_implicat"].isin(selected_vehicle_types)]

    location_data = filtered_data.groupby(["Latitud", "Longitud"]).size().reset_index(name="Vehículos Implicados")

    # Crear una nueva columna que represente la intensidad
    location_data["Intensidad"] = location_data["Vehículos Implicados"] / location_data["Vehículos Implicados"].max()

    # Definir una escala de colores personalizada
    color_scale = [
        [0, "green"],
        [0.5, "orange"],
        [1, "red"]
    ]

    # Crear el mapa
    fig = px.scatter_mapbox(
        location_data,
        lat="Latitud",
        lon="Longitud",
        hover_data=["Vehículos Implicados"],
        # Información adicional que se mostrará al pasar el ratón sobre los puntos
        title="Número de Vehículos Implicados en Accidentes de Tráfico en Barcelona",
        labels={"Desc_Tipus_vehicle_implicat": "Tipo de Vehículo", "Vehículos Implicados": "Num. Vehículos"},
        mapbox_style="carto-positron",  # Estilo del mapa (puedes elegir otros estilos)
        height=600,
        size="Vehículos Implicados",
        size_max=8,
        opacity=0.7,
        color="Vehículos Implicados",  # Columna que se utilizará para la escala de colores
        color_continuous_scale=color_scale
    )

    # Personalizar el diseño del mapa
    fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},  # Márgenes del mapa
        mapbox={"zoom": 11, "center": {"lat": 41.3851, "lon": 2.1734}},  # Nivel de zoom inicial
    )
    fig.update_traces(
        hovertemplate='Num. Vehículos: <b>%{customdata[0]}</b><extra></extra>'
    )

    # Mostrar el mapa
    st.plotly_chart(fig, use_container_width=True)


def page_distritos_barrios():
    st.title("Distribución accidente por distritos y barrios")
    # Cargar datos
    data = load_data()

    # Obtener la lista única de años en los datos
    available_years = sorted(data["NK_Any"].unique())

    # Checkbox para seleccionar los años
    selected_years = st.sidebar.multiselect("Seleccionar Años", available_years, default=available_years)

    filtered_data = data[data["NK_Any"].isin(selected_years)]

    # agrupar por expediente
    filtered_data = filtered_data.groupby(["Numero_expedient"]).first().reset_index()

    # get total accidents by Year and District
    total_accidents = filtered_data.groupby(["Nom_districte", "Nom_barri"]).size().reset_index(name="Accidentes")

    fig = px.treemap(
        total_accidents,
        path=['Nom_districte', 'Nom_barri'],
        title="",
        labels={'Nom_districte': 'Distrito', 'Nom_barri': 'Barrio'},
        color='Accidentes',  # Puedes usar otra columna numérica para colorear los treemaps
        color_continuous_scale='Viridis',  # Puedes ajustar la escala de color según tus preferencias
    )

    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

    # print metric values for the 3 barrios with more accidents
    # get top 3 barrios with more accidents
    top3_barrios = total_accidents.groupby(["Nom_districte", "Nom_barri"])["Accidentes"].sum().nlargest(3)
    # get the top 3 barrios
    top3_barrios = top3_barrios.reset_index()
    # get the top 3 barrios names
    top3_barrios_names = top3_barrios["Nom_barri"].tolist()
    # get the top 3 barrios accidents
    top3_barrios_accidents = top3_barrios["Accidentes"].tolist()
    # get the top 3 barrios districts
    top3_barrios_districts = top3_barrios["Nom_districte"].tolist()

    # create a dataframe with the top 3 barrios
    top3_barrios_df = pd.DataFrame(
        {'Distrito': top3_barrios_districts, 'Barrio': top3_barrios_names, 'Accidentes': top3_barrios_accidents})
    # get the total accidents
    total_accidents_year = filtered_data.groupby(["NK_Any"]).size().reset_index(name="Accidentes")
    # get the total accidents by year
    total_accidents_by_year = total_accidents_year.groupby(["NK_Any"])["Accidentes"].sum()
    # get the total accidents by year
    total_accidents_by_year = total_accidents_by_year.reset_index()
    # get the total accidents by year
    total_accidents_by_year = total_accidents_by_year["Accidentes"].tolist()
    # get the total accidents by year
    total_accidents_by_year = sum(total_accidents_by_year)
    if len(selected_years) > 0:
        total_accidents_by_year = total_accidents_by_year / len(selected_years)
    else:
        total_accidents_by_year = 0
    # get the total accidents by year
    total_accidents_by_year = round(total_accidents_by_year, 2)

    # get total 3 districts with more accidents
    top3_districts = total_accidents.groupby(["Nom_districte"])["Accidentes"].sum().nlargest(3)
    # get the top 3 districts
    top3_districts = top3_districts.reset_index()
    # get the top 3 districts names
    top3_districts_names = top3_districts["Nom_districte"].tolist()
    # get the top 3 districts accidents
    top3_districts_accidents = top3_districts["Accidentes"].tolist()

    col1, col2, col3 = st.columns(3)

    # show the average accidents by year, aligned to center
    col1.metric(label="Media accidentes por año", value=total_accidents_by_year)
    # get the "Nom_carrer" with most accidents
    top_calle = filtered_data.groupby(["Nom_carrer"])["Numero_expedient"].nunique().nlargest(1)
    # get the "Nom_carrer" with most accidents
    top_calle = top_calle.reset_index()
    # get the "Nom_carrer" with most accidents
    calle = top_calle["Nom_carrer"].tolist()[0]
    numero_acc = top_calle["Numero_expedient"].tolist()[0]
    # show the "Nom_carrer" with most accidents
    col1.metric(label="Calle con más accidentes (" + str(numero_acc) + ")", value=calle)
    # sacar metrica de año con mas accidentes
    top_year = filtered_data.groupby(["NK_Any"])["Numero_expedient"].nunique().nlargest(1)
    # sacar metrica de año con mas accidentes
    top_year = top_year.reset_index()
    # sacar metrica de año con mas accidentes
    year = top_year["NK_Any"].tolist()[0]
    numero_acc = top_year["Numero_expedient"].tolist()[0]
    # sacar metrica de año con mas accidentes
    col1.metric(label="Año con más accidentes (" + str(numero_acc) + ")", value=year)
    # sacar metrica de año con menos accidentes
    bottom_year = filtered_data.groupby(["NK_Any"])["Numero_expedient"].nunique().nsmallest(1)
    # sacar metrica de año con menos accidentes
    bottom_year = bottom_year.reset_index()
    # sacar metrica de año con menos accidentes
    year = bottom_year["NK_Any"].tolist()[0]
    numero_acc = bottom_year["Numero_expedient"].tolist()[0]
    # sacar metrica de año con menos accidentes
    col1.metric(label="Año con menos accidentes (" + str(numero_acc) + ")", value=year)

    # show the dataframe
    col2.markdown("""
        {}""".format(top3_districts.to_html(index=False)), unsafe_allow_html=True)
    col2.markdown("""
        <small> Top 3 distritos ({})</small>
        """.format('-'.join(map(str, sorted(selected_years)))), unsafe_allow_html=True)

    # show the dataframe without index column
    col3.markdown("""
    {}""".format(top3_barrios_df.to_html(index=False)), unsafe_allow_html=True)
    col3.markdown("""
    <small>Top 3 barrios ({})</small>
    """.format('-'.join(map(str, sorted(selected_years)))), unsafe_allow_html=True)

    total_accidents_by_distrito = data.groupby("Nom_districte")["Numero_expedient"].nunique().reset_index(
        name="Total_Accidents")

    district_coordinates = filtered_data.groupby("Nom_districte").agg(
        {"Latitud": "mean", "Longitud": "mean"}).reset_index()

    # quitamos valores negativos o nulos en Latitud y Longitud
    district_coordinates = district_coordinates[district_coordinates["Latitud"] > 0]
    district_coordinates = district_coordinates[district_coordinates["Longitud"] > 0]

    map_data = pd.merge(total_accidents_by_distrito, district_coordinates, on="Nom_districte", how="left")

    # quitamos "Desconegut" de los datos
    map_data = map_data[map_data["Nom_districte"] != "Desconegut"]

    color_scale = [
        [0, "green"],
        [0.5, "orange"],
        [1, "red"]
    ]

    fig = px.scatter_mapbox(
        map_data,
        lat="Latitud",
        lon="Longitud",
        color="Total_Accidents",  # Puedes ajustar el color según la cantidad de accidentes
        size="Total_Accidents",  # Puedes ajustar el tamaño de los puntos según la cantidad de accidentes
        opacity=0.7,
        # hover_name="Nom_barri",  # Información adicional al pasar el ratón sobre los puntos
        hover_data=["Nom_districte", "Total_Accidents"],  # Más información al pasar el ratón
        mapbox_style="carto-positron",
        title="Mapa de Barcelona con Números de Accidentes por Distritos",
        labels={"Total_Accidents": "Número de Accidentes"},
        color_continuous_scale=color_scale,
    )

    # Personalizar el diseño del mapa
    fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},  # Márgenes del mapa
        mapbox={"zoom": 11, "center": {"lat": 41.3851, "lon": 2.1734}},  # Nivel de zoom inicial
    )
    fig.update_traces(marker=dict(sizemode='diameter', sizeref=100))

    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

    # hacer un mapa ahora por barrios
    total_accidents_by_barrio = data.groupby("Nom_barri")["Numero_expedient"].nunique().reset_index(
        name="Total_Accidents")

    barrio_coordinates = filtered_data.groupby("Nom_barri").agg(
        {"Latitud": "mean", "Longitud": "mean"}).reset_index()
    map_data = pd.merge(total_accidents_by_barrio, barrio_coordinates, on="Nom_barri", how="left")
    # quitamos "Desconegut" de los datos
    map_data = map_data[map_data["Nom_barri"] != "Desconegut"]

    fig = px.scatter_mapbox(
        map_data,
        lat="Latitud",
        lon="Longitud",
        color="Total_Accidents",  # Puedes ajustar el color según la cantidad de accidentes
        size="Total_Accidents",  # Puedes ajustar el tamaño de los puntos según la cantidad de accidentes
        opacity=0.7,
        # hover_name="Nom_barri",  # Información adicional al pasar el ratón sobre los puntos
        hover_data=["Nom_barri", "Total_Accidents"],  # Más información al pasar el ratón
        mapbox_style="carto-positron",
        title="Mapa de Barcelona con Números de Accidentes por Barrios",
        labels={"Total_Accidents": "Número de Accidentes"},
        color_continuous_scale=color_scale,
    )
    # Personalizar el diseño del mapa
    fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},  # Márgenes del mapa
        mapbox={"zoom": 10, "center": {"lat": 41.3851, "lon": 2.1734}},  # Nivel de zoom inicial
    )
    fig.update_traces(marker=dict(sizemode='diameter', sizeref=100))

    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)


def page_momento_accidente():
    st.title("Distribución accidente por momento del día (I)")
    # Cargar datos
    data = load_data()

    # filtrar por numero expediente
    data2 = data.groupby(["Numero_expedient"]).first().reset_index()

    # Obtener la lista única de años en los datos
    available_years = sorted(data2["NK_Any"].unique())

    available_months = sorted(data2["Mes_any"].unique())

    # Checkbox para seleccionar los años
    selected_years = st.sidebar.multiselect("Seleccionar Años", available_years, default=available_years)

    # Checkbox para seleccionar los años
    selected_months = st.sidebar.slider("Seleccionar Meses", min_value=1, max_value=12, value=(1, 12))

    primer_mes = selected_months[0]
    ultimo_mes = selected_months[1]
    lista_meses_seleccionados = list(range(primer_mes, ultimo_mes + 1))

    data2 = data2[data2["NK_Any"].isin(selected_years)]

    data2 = data2[data2["Mes_any"].isin(lista_meses_seleccionados)]

    # Filtrar los datos según sea necesario
    filtered_data = data2[(data2["Descripcio_dia_setmana"].notnull()) & (data2["Hora_dia"].notnull())]

    # Crear un histograma de horas del día
    fig_horas_dia = px.histogram(
        filtered_data,
        x="Hora_dia",
        nbins=24,  # Puedes ajustar el número de bins según tus necesidades
        title="Distribución de Accidentes por Horas del Día",
        labels={"Hora_dia": "Hora del Día", "count": "Frecuencia"},
        category_orders={"Hora_dia": sorted(filtered_data["Hora_dia"].unique())},  # Ordenar las horas del día
    )

    # Actualizar el diseño del gráfico
    fig_horas_dia.update_layout(
        xaxis_title="Hora del Día",
        yaxis_title="Número de Accidentes",
    )

    # Filtrar los datos según sea necesario
    filtered_data = data2[data2["Descripcio_torn"].notnull()]

    # Crear un gráfico de barras para el día de la semana
    fig_torn = px.bar(
        filtered_data,
        x="Descripcio_torn",
        title="Frecuencia de Accidentes por Turno",
        labels={"Descripcio_torn": "Turno", "count": "Frecuencia"},
        category_orders={"Descripcio_torn": ["Matí", "Tarda", "Nit"]},  # Ordenar los turnos
    )

    # Actualizar el diseño del gráfico
    fig_torn.update_layout(
        xaxis_title="Turno",
        yaxis_title="Número de Accidentes",
    )

    # Filtrar los datos según sea necesario
    # -------------------------------------
    filtered_data = data2[(data2["Dia_mes"].notnull()) & (data2["Dia_mes"].notnull())]

    # Crear un histograma de horas del día
    fig_dia_mes = px.histogram(
        filtered_data,
        x="Dia_mes",
        nbins=31,  # Puedes ajustar el número de bins según tus necesidades
        title="Distribución de Accidentes por Día del mes",
        labels={"Dia_mes": "Día del mes", "count": "Frecuencia"},
        category_orders={"Dia_mes": sorted(filtered_data["Dia_mes"].unique())},  # Ordenar las horas del día
    )

    # Actualizar el diseño del gráfico
    fig_dia_mes.update_layout(
        xaxis_title="Día del mes",
        yaxis_title="Número de Accidentes",
    )

    # Filtrar los datos según sea necesario
    # -------------------------------------
    filtered_data = data2[data2["Descripcio_dia_setmana"].notnull()]

    # Crear un gráfico de barras para el día de la semana
    fig_dia_semana = px.bar(
        filtered_data,
        x="Descripcio_dia_setmana",
        title="Frecuencia de Accidentes por Día de la Semana",
        labels={"Descripcio_dia_setmana": "Día de la Semana", "count": "Frecuencia"},
        category_orders={"Descripcio_dia_setmana": ["Dilluns", "Dimarts", "Dimecres", "Dijous", "Divendres", "Dissabte",
                                                    "Diumenge"]},  # Ordenar los días de la semana
    )

    # Actualizar el diseño del gráfico
    fig_dia_semana.update_layout(
        xaxis_title="Día de la Semana",
        yaxis_title="Número de Accidentes",
    )
    # Mostrar graficos
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig_horas_dia, use_container_width=True)
    col2.plotly_chart(fig_torn, use_container_width=True)

    col3, col4 = st.columns(2)
    col3.plotly_chart(fig_dia_mes, use_container_width=True)
    col4.plotly_chart(fig_dia_semana, use_container_width=True)

def page_momento_accidente2():
    st.title("Distribución accidente por momento del día (II)")
    # Cargar datos
    data = load_data()

    # filtrar por numero expediente
    data2 = data.groupby(["Numero_expedient"]).first().reset_index()

    # Obtener la lista única de años en los datos
    available_years = sorted(data2["NK_Any"].unique())

    available_months = sorted(data2["Mes_any"].unique())

    # Checkbox para seleccionar los años
    selected_years = st.sidebar.multiselect("Seleccionar Años", available_years, default=available_years)

    # Checkbox para seleccionar los años
    selected_months = st.sidebar.slider("Seleccionar Meses", min_value=1, max_value=12, value=(1, 12))

    primer_mes = selected_months[0]
    ultimo_mes = selected_months[1]
    lista_meses_seleccionados = list(range(primer_mes, ultimo_mes + 1))

    data2 = data2[data2["NK_Any"].isin(selected_years)]

    data2 = data2[data2["Mes_any"].isin(lista_meses_seleccionados)]

    # Filtrar los datos según sea necesario
    filtered_data = data2[data2["Descripcio_dia_setmana"].notnull()]

    # Crear un mapa de calor para Día-Hora
    fig_heatmap = px.scatter(
        filtered_data.groupby(["Hora_dia", "Descripcio_dia_setmana"]).size().reset_index(name="count"),
        x="Hora_dia",
        y="Descripcio_dia_setmana",
        size="count",
        labels={"Hora_dia": "Hora del Día", "Descripcio_dia_setmana": "Día de la Semana", "count": "Frecuencia"},
        title="Mapa de Calor Día-Hora de Accidentes",
        category_orders={"Descripcio_dia_setmana": ["Dilluns", "Dimarts", "Dimecres", "Dijous", "Divendres", "Dissabte",
                                                    "Diumenge"]},  # Ordenar los días de la semana
        color="count",  # Usa el tamaño para representar la frecuencia
        color_continuous_scale="Viridis",  # Puedes ajustar la escala de colores según tus preferencias
    )

    # Actualizar el diseño del gráfico
    fig_heatmap.update_layout(
        xaxis_title="Hora del Día",
        yaxis_title="Día de la Semana",
    )

    # Mostrar el mapa de calor
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # Filtrar los datos según sea necesario
    filtered_data = data2[data2["Descripcio_dia_setmana"].notnull()]

    # Crear un mapa de calor para Día-Mes
    fig_heatmap_month = px.scatter(
        filtered_data.groupby(["Nom_mes", "Descripcio_dia_setmana"]).size().reset_index(name="count"),
        x="Nom_mes",
        y="Descripcio_dia_setmana",
        size="count",
        labels={"Nom_mes": "Mes", "Descripcio_dia_setmana": "Día de la Semana", "count": "Frecuencia"},
        title="Mapa de Calor Día-Mes de Accidentes",
        category_orders={"Descripcio_dia_setmana": ["Dilluns", "Dimarts", "Dimecres", "Dijous", "Divendres", "Dissabte",
                                                    "Diumenge"],
                         "Nom_mes": ["Gener", "Febrer", "Març", "Abril", "Maig", "Juny", "Juliol", "Agost", "Setembre",
                                     "Octubre", "Novembre", "Desembre"]},
        color="count",  # Usa el tamaño para representar la frecuencia
        color_continuous_scale="Viridis",  # Puedes ajustar la escala de colores según tus preferencias
    )

    # Actualizar el diseño del gráfico
    fig_heatmap_month.update_layout(
        xaxis_title="Mes",
        yaxis_title="Día de la Semana",
    )

    # Mostrar el mapa de calor
    st.plotly_chart(fig_heatmap_month, use_container_width=True)

    # Mapa de calor del mes en función del año
    # Filtrar los datos según sea necesario
    filtered_data = data2[data2["Nom_mes"].notnull()]
    filtered_data = filtered_data.groupby(["NK_Any", "Nom_mes"]).size().reset_index(name="count")
    filtered_data["NK_Any"] = filtered_data["NK_Any"].astype(str)

    # Crear un mapa de calor para Día-Mes
    fig_heatmap_year = px.scatter(
        filtered_data,
        x="Nom_mes",
        y="NK_Any",
        size="count",
        labels={"Nom_mes": "Mes", "NK_Any": "Año", "count": "Frecuencia"},
        title="Mapa de Calor Mes-Año de Accidentes",
        category_orders={"Nom_mes": ["Gener", "Febrer", "Març", "Abril", "Maig", "Juny", "Juliol", "Agost", "Setembre",
                                     "Octubre", "Novembre", "Desembre"]},  # Ordenar los días de la semana
        color="count",  # Usa el tamaño para representar la frecuencia
        color_continuous_scale="Viridis",  # Puedes ajustar la escala de colores según tus preferencias
    )

    # Actualizar el diseño del gráfico
    fig_heatmap_year.update_layout(
        xaxis_title="Mes",
        yaxis_title="Año",
    )

    # Mostrar el mapa de calor
    st.plotly_chart(fig_heatmap_year, use_container_width=True)


def page_victimizacion():
    # titulo
    st.title("Victimización de los accidentes")
    # Cargar datos
    data = load_data()

    # Obtener la lista única de años en los datos
    available_years = sorted(data["NK_Any"].unique())

    # Checkbox para seleccionar los años
    selected_years = st.sidebar.multiselect("Seleccionar Años", available_years, default=available_years)

    # Radio para seleccionar entre porcentaje y valor real
    show_percentage = st.sidebar.radio("Mostrar en:", ["Porcentaje", "Valor Real"]) == "Porcentaje"

    # Crear pie chart
    fig_pie, pie_chart_colors, category_order_pie_chart = create_victimizacion_pie_chart(data, sorted(selected_years),
                                                                                    show_percentage)

    if len(selected_years) > 1:
        # Crear gráfica de líneas
        fig_line = create_victimizacion_line_chart(data, sorted(selected_years), pie_chart_colors, category_order_pie_chart,
                                              show_percentage)
        # Colocar las dos gráficas una al lado de la otra
        col1, col2 = st.columns(2)

        col1.plotly_chart(fig_pie, use_container_width=True)
        col2.plotly_chart(fig_line, use_container_width=True)
    else:
        if len(selected_years) == 1:
            st.plotly_chart(fig_pie, use_container_width=True)


def main():
    st.sidebar.title("Opciones de Visualización")

    pages = {
        "Inicio": page_home,
        "Vehículos Implicados en Accidentes": page_grafico_vehiculos,
        "Accidentes por Sexo": page_sexo,
        "Accidentes por grupos de Edad": page_edad,
        "Accidentes por edad y nº vehículos": page_histograma_edad,
        "Accidentes por tipos de persona": page_personas,
        "Mapa accidentes": page_mapa,
        "Distritos y barrios": page_distritos_barrios,
        "Momento del accidente (I)": page_momento_accidente,
        "Momento del accidente (II)": page_momento_accidente2,
        "Victimización": page_victimizacion,
    }

    selection = st.sidebar.selectbox("Seleccionar página", list(pages.keys()))
    page = pages[selection]

    for i in range(0, 5):
        st.empty()
    # Mostrar la página seleccionada
    page()


# Ejecutar la aplicación
if __name__ == "__main__":
    main()

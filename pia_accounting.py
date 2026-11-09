import pandas as pd
from tabulate import tabulate



productos_projecciones = {
    "Producto": [],
    "Unidades a vender primer semestre": [],
    "Precio de venta primer semestre": [],
    "Unidades a vender segundo semestre": [],
    "Precio de venta segundo semestre": [],
}

productos_inventario = {
    "Producto": [],
    "Unidades a vender primer semestre": [],
    "Unidades a vender segundo semestre": [],
    "Inventario inicial": [],
    "Inventario inicial segundo semestre": [],
    "Inventario final segundo semestre": [],
}

productos_req = {
    "Producto": [],
    "Unidades a producir primer semestre": [],
    "Unidades a producir segundo semestre": [],
    "Total de unidades a producir": [],
}

mano_obra = {
    "Producto": [],
    "Horas req por unidad": [],
    "Unidades a producir primer semestre": [],
    "Unidades a producir segundo semestre": [],
    "Total de unidades a producir": [],
    "Costo de mano obra 1hra primer semestre": [],
    "Costo de mano de obra 1hra segundo semestre": [],
}

materiales = {
    "Material": [],
    "Inventario inicial": [],
    "Costo del material primer semestre": [],
    "Inventario inicial segundo semestre": [],
    "Inventario final segundo semestre": [],
    "Costo del material segundo semestre": [],
    "Total requerido primer semestre": [],
    "Total requerido segundo semestre": [],
    "Total requerido": [],
}

clientes_flujo = {
    "Saldo de clientes previo": [],
    "Ventas": [],
    "Por cobranza periodo previo": [],
    "Por cobranza periodo actual": [],
}

prov_flujo = {
    "Saldo de proveedores previo": [],
    "Compras": [],
    "Por pagar periodo previo": [],
    "Por pagar periodo actual": [],
}

gif = {
    "Presupuesto de gastos indirectos de fabricacion": [],
    "Primer semestre": [],
    "Segundo semestre": [],
    "Annual": [],
}

gav = {
    "Presupuesto de gastos de operacion": [],
    "Primer semestre": [],
    "Segundo semestre": [],
    "Annual": [],
}

# Ahora estas cuentas son dinamicas el usuario escribe los nombres y saldos.
# Se conserva un diccionario separado para cada clasificacion contable.
activos_circulante = {}
activos_no_circulantes = {}
pasivos_cp = {}
pasivos_lp = {}
capital_contable = {}
periodos = []
srt = {
    "Producto": [],
    "Unidades a producir primer semestre": [],
    "Unidades a producir segundo semestre": [],
    "Total a producir": [],
}

# Guarda la cuenta de Clientes y Proveedores que el usuario seleccione.
cuentas_especiales = {
    "clientes": None,
    "proveedores": None,
    "efectivo": None,
    "inventario_materiales": None,
    "inventario_productos": None,
    "activo_fijo": None,
    "depreciacion_acumulada": None,
    "isr": None,
    "ptu": None,
}
cuentas_resta_activo = set()
gastos_no_efectivo = {"gif": [], "gav": []}

# DataFrames de calculo que comparten las funciones
df_ventas_calculado = pd.DataFrame()
df_produccion_calculado = pd.DataFrame()
df_req_materiales_calculado = pd.DataFrame()
df_compra_materiales_calculado = pd.DataFrame()
df_mano_obra_calculado = pd.DataFrame()
df_costos_unitarios = pd.DataFrame()
df_val_inventarios = pd.DataFrame()
df_estado_costo = pd.DataFrame()
df_estado_resultados = pd.DataFrame()
df_estado_flujo = pd.DataFrame()
df_balance_final = pd.DataFrame()
costos_unitarios_producto = {}
total_inv_final_materiales = 0.0
total_inv_final_productos = 0.0
costo_ventas_calculado = 0.0
impuesto_isr_calculado = 0.0
impuesto_ptu_calculado = 0.0
utilidad_neta_calculada = 0.0
efectivo_final_calculado = 0.0
compra_activo_calculada = 0.0
nombre_activo_adquirido = None
pago_isr_previo_calculado = 0.0
pago_isr_actual_calculado = 0.0
pago_ptu_previo_calculado = 0.0
pago_ptu_actual_calculado = 0.0

tot_hr_ov = 0
gif_hr = 0
ANIO_PRESUPUESTO = 2026


 
# Funciones auxiliares de captura y tablas
 

def pedir_texto(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("El dato no puede quedar vacio.")


def pedir_numero(mensaje, minimo=0):
    while True:
        entrada = input(mensaje).strip().replace(",", "").replace("$", "")
        try:
            valor = float(entrada)
        except ValueError:
            print("Ingresa un numero valido.")
            continue
        if minimo is not None and valor < minimo:
            print(f"El valor debe ser igual o mayor que {minimo}.")
            continue
        return valor


def pedir_entero(mensaje, minimo=0):
    while True:
        entrada = input(mensaje).strip()
        try:
            valor = int(entrada)
        except ValueError:
            print("Ingresa un numero entero valido.")
            continue
        if valor < minimo:
            print(f"El valor debe ser igual o mayor que {minimo}.")
            continue
        return valor


def pedir_porcentaje(mensaje):
    """Solicita porcentaje de 0 a 100 y devuelve su equivalente decimal."""
    while True:
        valor = pedir_numero(mensaje, minimo=0)
        if valor <= 100:
            return valor / 100
        print("El porcentaje debe estar entre 0 y 100.")


def pedir_si_no(mensaje):
    while True:
        respuesta = input(mensaje).strip().lower()
        if respuesta in ("s", "si", "sí"):
            return True
        if respuesta in ("n", "no"):
            return False
        print("Responde S o N.")


def mostrar_seccion(titulo):
    print("\n" + "=" * 70)
    print(f"Section: {titulo}")
    print("=" * 70)


def mostrar_tabla(titulo, tabla):
    print("\n" + "=" * 100)
    print(titulo.upper())
    print("=" * 100)
    if tabla is None or tabla.empty:
        print("No hay datos para mostrar.")
    else:
        print(tabulate(
            tabla.fillna(""),
            headers="keys",
            tablefmt="grid",
            showindex=False,
            floatfmt=",.2f",
            intfmt=",",
            numalign="right",
            stralign="left",
        ))


def crear_fila(concepto, primero="", segundo="", anual="", columna="Concepto"):
    return {
        columna: concepto,
        "1er. semestre": primero,
        "2ndo. semestre": segundo,
        str(ANIO_PRESUPUESTO): anual,
    }


def capturar_cuentas(titulo, diccionario, permite_resta=False):
    """Captura cuentas del balance; permite marcar cuentas complementarias de activo."""
    mostrar_seccion(titulo)
    cantidad = pedir_entero("Cuantas cuentas deseas registrar en esta clasificacion? ", minimo=0)

    for i in range(cantidad):
        print(f"Cuenta {i + 1}")
        nombre = pedir_texto("Nombre de la cuenta: ")
        while nombre in diccionario:
            print("Ya existe una cuenta con ese nombre. Usa otro nombre.")
            nombre = pedir_texto("Nombre de la cuenta: ")
        saldo = pedir_numero(f"Saldo de {nombre}: $", minimo=None)
        diccionario[nombre] = [saldo]
        if permite_resta and pedir_si_no(
            f"La cuenta {nombre} disminuye el valor del activo (ej. depreciacion acumulada)? (S/N): "
        ):
            cuentas_resta_activo.add(nombre)


def seleccionar_cuenta(diccionario, mensaje, permitir_ninguna=True):
    """Permite seleccionar una cuenta capturada sin fijar nombres contables."""
    nombres = list(diccionario.keys())
    if not nombres:
        print(f"No se registraron cuentas para: {mensaje}. Se utilizara 0.")
        return None

    print(f"\nSelecciona cual cuenta corresponde a {mensaje}:")
    if permitir_ninguna:
        print("0. Ninguna / No aplica")
    for i, nombre in enumerate(nombres, start=1):
        print(f"{i}. {nombre}")

    minimo = 0 if permitir_ninguna else 1
    while True:
        opcion = pedir_entero("Numero de cuenta: ", minimo=minimo)
        if permitir_ninguna and opcion == 0:
            return None
        if 1 <= opcion <= len(nombres):
            return nombres[opcion - 1]
        print("Selecciona una opcion de la lista.")


def saldo_seleccionado(diccionario, nombre):
    if nombre is None:
        return 0.0
    return float(diccionario[nombre][0])


 
# Balance general previo
 

def bal_previo():
    mostrar_seccion("Balance general previo")
    print("\nPara comenzar se requiere el balance general previo.")
    print("Puedes registrar las cuentas que tenga tu empresa; no hay nombres fijos.")

    capturar_cuentas("Activo circulante", activos_circulante)
    capturar_cuentas("Activo no circulante", activos_no_circulantes, permite_resta=True)
    capturar_cuentas("Pasivo a corto plazo", pasivos_cp)
    capturar_cuentas("Pasivo a largo plazo", pasivos_lp)
    capturar_cuentas("Capital contable", capital_contable)

    # Se identifican cuentas que alimentan formulas de los reportes posteriores.
    # Los nombres pueden ser distintos en cada empresa.
    cuentas_especiales["efectivo"] = seleccionar_cuenta(
        activos_circulante, "Efectivo / bancos"
    )
    cuentas_especiales["clientes"] = seleccionar_cuenta(
        activos_circulante, "Clientes / cuentas por cobrar"
    )
    cuentas_especiales["inventario_materiales"] = seleccionar_cuenta(
        activos_circulante, "Inventario de materiales"
    )
    cuentas_especiales["inventario_productos"] = seleccionar_cuenta(
        activos_circulante, "Inventario de productos terminados"
    )
    cuentas_especiales["activo_fijo"] = seleccionar_cuenta(
        activos_no_circulantes, "Maquinaria / equipo / activo fijo"
    )
    cuentas_especiales["depreciacion_acumulada"] = seleccionar_cuenta(
        {k: v for k, v in activos_no_circulantes.items() if k in cuentas_resta_activo},
        "Depreciacion acumulada / cuenta complementaria de activo"
    )
    if cuentas_especiales["depreciacion_acumulada"]:
        cuentas_resta_activo.add(cuentas_especiales["depreciacion_acumulada"])
    clientes = saldo_seleccionado(activos_circulante, cuentas_especiales["clientes"])

    if cuentas_especiales["clientes"] is not None:
        clientes_pag = pedir_porcentaje(
            "Que porcentaje del saldo anterior de Clientes se cobrara durante el ejercicio? (0 a 100): "
        )
    else:
        clientes_pag = 0

    clientes_flujo["Saldo de clientes previo"].append(clientes)
    clientes_flujo["Por cobranza periodo previo"].append(clientes * clientes_pag)

    cuentas_especiales["proveedores"] = seleccionar_cuenta(
        pasivos_cp, "Proveedores / cuentas por pagar"
    )
    cuentas_especiales["isr"] = seleccionar_cuenta(
        pasivos_cp, "ISR / impuesto sobre la renta por pagar"
    )
    cuentas_especiales["ptu"] = seleccionar_cuenta(
        pasivos_cp, "PTU / participacion de trabajadores por pagar"
    )
    prov = saldo_seleccionado(pasivos_cp, cuentas_especiales["proveedores"])

    if cuentas_especiales["proveedores"] is not None:
        prov_p = pedir_porcentaje(
            "Que porcentaje del saldo anterior de Proveedores se pagara durante el ejercicio? (0 a 100): "
        )
    else:
        prov_p = 0

    prov_flujo["Saldo de proveedores previo"].append(prov)
    prov_flujo["Por pagar periodo previo"].append(prov * prov_p)

    # Tabla dinamica con todas las cuentas que introdujo el usuario.
    filas = []
    grupos = [
        ("ACTIVO CIRCULANTE", activos_circulante),
        ("ACTIVO NO CIRCULANTE", activos_no_circulantes),
        ("PASIVO A CORTO PLAZO", pasivos_cp),
        ("PASIVO A LARGO PLAZO", pasivos_lp),
        ("CAPITAL CONTABLE", capital_contable),
    ]
    for titulo, diccionario in grupos:
        filas.append({"Clasificacion": titulo, "Cuenta": "", "Saldo": ""})
        for nombre, saldo in diccionario.items():
            importe = -abs(saldo[0]) if nombre in cuentas_resta_activo else saldo[0]
            filas.append({"Clasificacion": "", "Cuenta": nombre, "Saldo": importe})
    df_balance_previo = pd.DataFrame(filas)
    return df_balance_previo


 
# Presupuesto de ventas
 

def pres_ventas(num_productos):
    mostrar_seccion("Presupuesto de ventas")
    for _ in range(num_productos):
        nom_prod = pedir_texto("Ingresa el nombre o clave del producto: ")
        if nom_prod in productos_projecciones["Producto"]:
            print("Ese producto ya fue capturado. Ingresa otro nombre.")
            while nom_prod in productos_projecciones["Producto"]:
                nom_prod = pedir_texto("Nombre o clave diferente: ")

        productos_projecciones["Producto"].append(nom_prod)
        productos_inventario["Producto"].append(nom_prod)
        mano_obra["Producto"].append(nom_prod)

        ud_v_ps = pedir_numero("Ingresa las unidades a vender el primer semestre: ")
        precio_ps = pedir_numero("Ingresa el precio de venta del producto durante el primer semestre: $")
        ud_v_ss = pedir_numero("Ingresa las unidades a vender el segundo semestre: ")
        precio_ss = pedir_numero("Ingresa el precio de venta del producto durante el segundo semestre: $")

        productos_projecciones["Unidades a vender primer semestre"].append(ud_v_ps)
        productos_projecciones["Precio de venta primer semestre"].append(precio_ps)
        productos_projecciones["Unidades a vender segundo semestre"].append(ud_v_ss)
        productos_projecciones["Precio de venta segundo semestre"].append(precio_ss)
        productos_inventario["Unidades a vender primer semestre"].append(ud_v_ps)
        productos_inventario["Unidades a vender segundo semestre"].append(ud_v_ss)

    clientes_cob = pedir_porcentaje(
        "Que porcentaje de las ventas del ejercicio sera cobrado durante el ejercicio? (0 a 100): "
    )

    global df_ventas_calculado
    df_calc = pd.DataFrame(productos_projecciones)
    df_calc["Importe de venta primer semestre"] = (
        df_calc["Unidades a vender primer semestre"] * df_calc["Precio de venta primer semestre"]
    )
    df_calc["Importe de venta segundo semestre"] = (
        df_calc["Unidades a vender segundo semestre"] * df_calc["Precio de venta segundo semestre"]
    )
    df_calc["Importe total anual"] = (
        df_calc["Importe de venta primer semestre"] + df_calc["Importe de venta segundo semestre"]
    )
    df_calc["Unidades a vender"] = (
        df_calc["Unidades a vender primer semestre"] + df_calc["Unidades a vender segundo semestre"]
    )
    df_ventas_calculado = df_calc.copy()

    tot_ps = df_calc["Importe de venta primer semestre"].sum()
    tot_ss = df_calc["Importe de venta segundo semestre"].sum()
    tot = df_calc["Importe total anual"].sum()
    clientes_flujo["Ventas"].append(tot)
    clientes_flujo["Por cobranza periodo actual"].append(clientes_cob * tot)

    filas = []
    for _, row in df_calc.iterrows():
        filas.append(crear_fila(row["Producto"], columna="Presupuesto de ventas"))
        filas.append(crear_fila(
            "Unidades a vender",
            row["Unidades a vender primer semestre"],
            row["Unidades a vender segundo semestre"],
            row["Unidades a vender"],
            columna="Presupuesto de ventas",
        ))
        filas.append(crear_fila(
            "Precio de venta",
            row["Precio de venta primer semestre"],
            row["Precio de venta segundo semestre"],
            "",
            columna="Presupuesto de ventas",
        ))
        filas.append(crear_fila(
            "Importe de venta",
            row["Importe de venta primer semestre"],
            row["Importe de venta segundo semestre"],
            row["Importe total anual"],
            columna="Presupuesto de ventas",
        ))
        filas.append(crear_fila("", columna="Presupuesto de ventas"))

    filas.append(crear_fila(
        "Total de ventas por semestre", tot_ps, tot_ss, tot,
        columna="Presupuesto de ventas",
    ))
    return pd.DataFrame(filas)


 
# Determinacion del saldo de clientes y flujo de entradas
 

def det_clientes_entradas():
    mostrar_seccion("Determinacion de saldo de clientes y flujo de entradas")
    df_calc = pd.DataFrame(clientes_flujo)
    df_calc["Total de clientes"] = (
        df_calc["Ventas"] + df_calc["Saldo de clientes previo"]
    )
    df_calc["Total a cobrar"] = (
        df_calc["Por cobranza periodo previo"] + df_calc["Por cobranza periodo actual"]
    )
    df_calc["Saldo de clientes total"] = (
        df_calc["Total de clientes"] - df_calc["Total a cobrar"]
    )

    dato = df_calc.iloc[0]
    fila = [
        {"Determinacion de saldo de clientes y flujo de entradas": "Descripcion", "Importe": "", "Total": ""},
        {"Determinacion de saldo de clientes y flujo de entradas": "Saldo de clientes previo", "Importe": "", "Total": dato["Saldo de clientes previo"]},
        {"Determinacion de saldo de clientes y flujo de entradas": "Ventas", "Importe": "", "Total": dato["Ventas"]},
        {"Determinacion de saldo de clientes y flujo de entradas": "Total clientes", "Importe": "", "Total": dato["Total de clientes"]},
        {"Determinacion de saldo de clientes y flujo de entradas": "", "Importe": "", "Total": ""},
        {"Determinacion de saldo de clientes y flujo de entradas": "Entradas de efectivo:", "Importe": "", "Total": ""},
        {"Determinacion de saldo de clientes y flujo de entradas": "Por cobranza previo", "Importe": dato["Por cobranza periodo previo"], "Total": ""},
        {"Determinacion de saldo de clientes y flujo de entradas": "Por cobranza actual", "Importe": dato["Por cobranza periodo actual"], "Total": ""},
        {"Determinacion de saldo de clientes y flujo de entradas": "Total a cobrar", "Importe": "", "Total": dato["Total a cobrar"]},
        {"Determinacion de saldo de clientes y flujo de entradas": "", "Importe": "", "Total": ""},
        {"Determinacion de saldo de clientes y flujo de entradas": "TOTAL DE SALDO DE CLIENTES", "Importe": "", "Total": dato["Saldo de clientes total"]},
    ]
    return pd.DataFrame(fila)


 
# Presupuesto de produccion
 

def pres_produccion():
    mostrar_seccion("Presupuesto de produccion")
    prod_len = len(productos_inventario["Producto"])
    for i in range(prod_len):
        nombre = productos_inventario["Producto"][i]
        inv_in = pedir_numero(f"Inventario inicial del primer semestre para {nombre}: ")
        inv_in_ss = pedir_numero(
            f"Inventario inicial del segundo semestre (inventario final del primero) para {nombre}: "
        )
        inv_f_ss = pedir_numero(f"Inventario final del segundo semestre para {nombre}: ")

        productos_inventario["Inventario inicial"].append(inv_in)
        productos_inventario["Inventario inicial segundo semestre"].append(inv_in_ss)
        productos_inventario["Inventario final segundo semestre"].append(inv_f_ss)

    global df_produccion_calculado
    df_calc = pd.DataFrame(productos_inventario)
    df_calc["Total de unidades a vender"] = (
        df_calc["Unidades a vender primer semestre"] + df_calc["Unidades a vender segundo semestre"]
    )
    df_calc["Total de unidades primer semestre"] = (
        df_calc["Unidades a vender primer semestre"] + df_calc["Inventario inicial segundo semestre"]
    )
    df_calc["Total de unidades segundo semestre"] = (
        df_calc["Unidades a vender segundo semestre"] + df_calc["Inventario final segundo semestre"]
    )
    df_calc["Total de unidades"] = (
        df_calc["Total de unidades a vender"] + df_calc["Inventario final segundo semestre"]
    )
    df_calc["Unidades a producir primer semestre"] = (
        df_calc["Total de unidades primer semestre"] - df_calc["Inventario inicial"]
    )
    df_calc["Unidades a producir segundo semestre"] = (
        df_calc["Total de unidades segundo semestre"] - df_calc["Inventario inicial segundo semestre"]
    )
    df_calc["Total de unidades a producir"] = (
        df_calc["Unidades a producir primer semestre"] + df_calc["Unidades a producir segundo semestre"]
    )
    df_produccion_calculado = df_calc.copy()

    fila = []
    for _, row in df_calc.iterrows():
        fila.append(crear_fila(row["Producto"], columna="Presupuesto de produccion"))
        fila.append(crear_fila(
            "Unidades a vender", row["Unidades a vender primer semestre"],
            row["Unidades a vender segundo semestre"], row["Total de unidades a vender"],
            columna="Presupuesto de produccion",
        ))
        fila.append(crear_fila(
            "Inventario final", row["Inventario inicial segundo semestre"],
            row["Inventario final segundo semestre"], row["Inventario final segundo semestre"],
            columna="Presupuesto de produccion",
        ))
        fila.append(crear_fila(
            "Total de unidades", row["Total de unidades primer semestre"],
            row["Total de unidades segundo semestre"], row["Total de unidades"],
            columna="Presupuesto de produccion",
        ))
        fila.append(crear_fila(
            "Inventario inicial", row["Inventario inicial"],
            row["Inventario inicial segundo semestre"], row["Inventario inicial"],
            columna="Presupuesto de produccion",
        ))
        fila.append(crear_fila(
            "Unidades a producir", row["Unidades a producir primer semestre"],
            row["Unidades a producir segundo semestre"], row["Total de unidades a producir"],
            columna="Presupuesto de produccion",
        ))
        fila.append(crear_fila("", columna="Presupuesto de produccion"))

        mano_obra["Unidades a producir primer semestre"].append(row["Unidades a producir primer semestre"])
        mano_obra["Unidades a producir segundo semestre"].append(row["Unidades a producir segundo semestre"])
        mano_obra["Total de unidades a producir"].append(row["Total de unidades a producir"])

    return pd.DataFrame(fila)


 
# Presupuesto de requerimiento de materiales
 

def pres_req_materiales(df_pres_produccion):
    mostrar_seccion("Presupuesto de requerimiento de materiales")
    num_mat = pedir_entero("Cuantos materiales se utilizan? ", minimo=1)

    # Se reinicia la parte variable para poder usar cualquier numero de materiales.
    materiales["Material"].clear()
    materiales["Total requerido primer semestre"].clear()
    materiales["Total requerido segundo semestre"].clear()
    materiales["Total requerido"].clear()
    for llave in list(productos_req.keys()):
        if llave not in (
            "Producto", "Unidades a producir primer semestre",
            "Unidades a producir segundo semestre", "Total de unidades a producir",
        ):
            del productos_req[llave]

    for _ in range(num_mat):
        nombre_mat = pedir_texto("Ingresa el nombre del material: ")
        if nombre_mat in materiales["Material"]:
            print("Ese material ya fue capturado. Ingresa otro nombre.")
            while nombre_mat in materiales["Material"]:
                nombre_mat = pedir_texto("Nombre de material diferente: ")
        materiales["Material"].append(nombre_mat)
        productos_req[f"{nombre_mat} req. para 1 pza"] = []

    prod_len = len(productos_projecciones["Producto"])
    mat_len = len(materiales["Material"])

    # Los datos de produccion se toman de su DataFrame de calculo
    for p in range(prod_len):
        fila_prod = df_produccion_calculado.iloc[p]
        productos_req["Producto"].append(fila_prod["Producto"])
        productos_req["Unidades a producir primer semestre"].append(
            fila_prod["Unidades a producir primer semestre"]
        )
        productos_req["Unidades a producir segundo semestre"].append(
            fila_prod["Unidades a producir segundo semestre"]
        )
        productos_req["Total de unidades a producir"].append(
            fila_prod["Total de unidades a producir"]
        )

        for m in range(mat_len):
            nombre_mat = materiales["Material"][m]
            req = pedir_numero(
                f"Cuanto {nombre_mat} se requiere para elaborar una pieza de {productos_projecciones['Producto'][p]}? "
            )
            productos_req[f"{nombre_mat} req. para 1 pza"].append(req)

    df_calc = pd.DataFrame(productos_req)
    for i in range(mat_len):
        nom_mat = materiales["Material"][i]
        columna_req = f"{nom_mat} req. para 1 pza"
        df_calc[f"{columna_req} requerido primer semestre"] = (
            df_calc["Unidades a producir primer semestre"] * df_calc[columna_req]
        )
        df_calc[f"{columna_req} requerido segundo semestre"] = (
            df_calc["Unidades a producir segundo semestre"] * df_calc[columna_req]
        )
        df_calc[f"{columna_req} requerido total"] = (
            df_calc[f"{columna_req} requerido primer semestre"]
            + df_calc[f"{columna_req} requerido segundo semestre"]
        )

    global df_req_materiales_calculado
    df_req_materiales_calculado = df_calc.copy()

    fila = []
    for _, row in df_calc.iterrows():
        fila.append(crear_fila(row["Producto"], columna="Presupuesto de requerimiento de materiales"))
        fila.append(crear_fila(
            "Unidades a producir", row["Unidades a producir primer semestre"],
            row["Unidades a producir segundo semestre"], row["Total de unidades a producir"],
            columna="Presupuesto de requerimiento de materiales",
        ))
        fila.append(crear_fila("", columna="Presupuesto de requerimiento de materiales"))

        for z in range(mat_len):
            nom_mat = materiales["Material"][z]
            columna_req = f"{nom_mat} req. para 1 pza"
            fila.append(crear_fila(nom_mat, columna="Presupuesto de requerimiento de materiales"))
            fila.append(crear_fila(
                "Requerimiento de material", row[columna_req], row[columna_req], row[columna_req],
                columna="Presupuesto de requerimiento de materiales",
            ))
            fila.append(crear_fila(
                "Total requerido",
                row[f"{columna_req} requerido primer semestre"],
                row[f"{columna_req} requerido segundo semestre"],
                row[f"{columna_req} requerido total"],
                columna="Presupuesto de requerimiento de materiales",
            ))
        fila.append(crear_fila("", columna="Presupuesto de requerimiento de materiales"))

    fila.append(crear_fila("Total de requerimientos", columna="Presupuesto de requerimiento de materiales"))
    for b in range(mat_len):
        mat_name = materiales["Material"][b]
        columna_req = f"{mat_name} req. para 1 pza"
        tot_ps = df_calc[f"{columna_req} requerido primer semestre"].sum()
        tot_ss = df_calc[f"{columna_req} requerido segundo semestre"].sum()
        tot_ov = df_calc[f"{columna_req} requerido total"].sum()
        materiales["Total requerido primer semestre"].append(tot_ps)
        materiales["Total requerido segundo semestre"].append(tot_ss)
        materiales["Total requerido"].append(tot_ov)
        fila.append(crear_fila(
            mat_name, tot_ps, tot_ss, tot_ov,
            columna="Presupuesto de requerimiento de materiales",
        ))

    return pd.DataFrame(fila)


 
# Presupuesto de compra de materiales
 

def pres_compra_mat():
    mostrar_seccion("Presupuesto de compra de materiales")
    mat_len = len(materiales["Material"])

    for i in range(mat_len):
        nombre = materiales["Material"][i]
        inv_ps = pedir_numero(f"Inventario inicial del primer semestre de {nombre}: ")
        pc_ps = pedir_numero(f"Precio de compra de {nombre} durante el primer semestre: $")
        inv_is = pedir_numero(
            f"Inventario inicial del segundo semestre (inventario final del primero) de {nombre}: "
        )
        inv_fs = pedir_numero(f"Inventario final del segundo semestre de {nombre}: ")
        pc_ss = pedir_numero(f"Precio de compra de {nombre} durante el segundo semestre: $")

        materiales["Inventario inicial"].append(inv_ps)
        materiales["Costo del material primer semestre"].append(pc_ps)
        materiales["Inventario inicial segundo semestre"].append(inv_is)
        materiales["Inventario final segundo semestre"].append(inv_fs)
        materiales["Costo del material segundo semestre"].append(pc_ss)

    df_calc = pd.DataFrame(materiales)
    df_calc["Total de materiales primer semestre"] = (
        df_calc["Total requerido primer semestre"] + df_calc["Inventario inicial segundo semestre"]
    )
    df_calc["Total de materiales segundo semestre"] = (
        df_calc["Total requerido segundo semestre"] + df_calc["Inventario final segundo semestre"]
    )
    df_calc["Total de materiales requeridos"] = (
        df_calc["Total requerido"] + df_calc["Inventario final segundo semestre"]
    )
    df_calc["Material a comprar primer semestre"] = (
        df_calc["Total de materiales primer semestre"] - df_calc["Inventario inicial"]
    )
    df_calc["Material a comprar segundo semestre"] = (
        df_calc["Total de materiales segundo semestre"] - df_calc["Inventario inicial segundo semestre"]
    )
    df_calc["Total de material a comprar"] = (
        df_calc["Material a comprar primer semestre"] + df_calc["Material a comprar segundo semestre"]
    )
    df_calc["Total material en $ primer semestre"] = (
        df_calc["Costo del material primer semestre"] * df_calc["Material a comprar primer semestre"]
    )
    df_calc["Total material en $ segundo semestre"] = (
        df_calc["Costo del material segundo semestre"] * df_calc["Material a comprar segundo semestre"]
    )
    df_calc["Total material en $ anual"] = (
        df_calc["Total material en $ primer semestre"] + df_calc["Total material en $ segundo semestre"]
    )

    tot = df_calc["Total material en $ primer semestre"].sum()
    tot_ss = df_calc["Total material en $ segundo semestre"].sum()
    tot_ovr = df_calc["Total material en $ anual"].sum()

    # El flujo de proveedores utiliza el total de compras
    prov_flujo["Compras"].append(tot_ovr)
    pago_actual = pedir_porcentaje(
        "Que porcentaje de las compras del ejercicio se pagara durante el ejercicio? (0 a 100): "
    )
    prov_flujo["Por pagar periodo actual"].append(tot_ovr * pago_actual)

    global df_compra_materiales_calculado
    df_compra_materiales_calculado = df_calc.copy()

    fila = []
    for _, row in df_calc.iterrows():
        fila.append(crear_fila(row["Material"], columna="Presupuesto de compra de materiales"))
        fila.append(crear_fila(
            "Requerimientos de materiales", row["Total requerido primer semestre"],
            row["Total requerido segundo semestre"], row["Total requerido"],
            columna="Presupuesto de compra de materiales",
        ))
        fila.append(crear_fila(
            "Inventario final", row["Inventario inicial segundo semestre"],
            row["Inventario final segundo semestre"], row["Inventario final segundo semestre"],
            columna="Presupuesto de compra de materiales",
        ))
        fila.append(crear_fila(
            "Total de materiales", row["Total de materiales primer semestre"],
            row["Total de materiales segundo semestre"], row["Total de materiales requeridos"],
            columna="Presupuesto de compra de materiales",
        ))
        fila.append(crear_fila(
            "Inventario inicial", row["Inventario inicial"],
            row["Inventario inicial segundo semestre"], row["Inventario inicial"],
            columna="Presupuesto de compra de materiales",
        ))
        fila.append(crear_fila(
            "Material a comprar", row["Material a comprar primer semestre"],
            row["Material a comprar segundo semestre"], row["Total de material a comprar"],
            columna="Presupuesto de compra de materiales",
        ))
        fila.append(crear_fila(
            "Precio de compra", row["Costo del material primer semestre"],
            row["Costo del material segundo semestre"], "",
            columna="Presupuesto de compra de materiales",
        ))
        fila.append(crear_fila(
            "Total en $", row["Total material en $ primer semestre"],
            row["Total material en $ segundo semestre"], row["Total material en $ anual"],
            columna="Presupuesto de compra de materiales",
        ))
        fila.append(crear_fila("", columna="Presupuesto de compra de materiales"))

    fila.append(crear_fila(
        "Compras totales", tot, tot_ss, tot_ovr,
        columna="Presupuesto de compra de materiales",
    ))
    return pd.DataFrame(fila)


 
# Determinacion del saldo de proveedores y flujo de salidas
 

def prov_salidas():
    mostrar_seccion("Determinacion de saldo de proveedores y flujo de salidas")
    df_calc = pd.DataFrame(prov_flujo)
    df_calc["Total de proveedores"] = (
        df_calc["Compras"] + df_calc["Saldo de proveedores previo"]
    )
    df_calc["Total a pagar"] = (
        df_calc["Por pagar periodo previo"] + df_calc["Por pagar periodo actual"]
    )
    df_calc["Saldo de proveedores total"] = (
        df_calc["Total de proveedores"] - df_calc["Total a pagar"]
    )

    dato = df_calc.iloc[0]
    fila = [
        {"Determinacion de saldo de proveedores y flujo de salidas": "Descripcion", "Importe": "", "Total": ""},
        {"Determinacion de saldo de proveedores y flujo de salidas": "Saldo de proveedores previo", "Importe": "", "Total": dato["Saldo de proveedores previo"]},
        {"Determinacion de saldo de proveedores y flujo de salidas": "Compras", "Importe": "", "Total": dato["Compras"]},
        {"Determinacion de saldo de proveedores y flujo de salidas": "Total de proveedores", "Importe": "", "Total": dato["Total de proveedores"]},
        {"Determinacion de saldo de proveedores y flujo de salidas": "", "Importe": "", "Total": ""},
        {"Determinacion de saldo de proveedores y flujo de salidas": "Salidas de efectivo:", "Importe": "", "Total": ""},
        {"Determinacion de saldo de proveedores y flujo de salidas": "Por pagar previo", "Importe": dato["Por pagar periodo previo"], "Total": ""},
        {"Determinacion de saldo de proveedores y flujo de salidas": "Por pagar actual", "Importe": dato["Por pagar periodo actual"], "Total": ""},
        {"Determinacion de saldo de proveedores y flujo de salidas": "Total a pagar", "Importe": "", "Total": dato["Total a pagar"]},
        {"Determinacion de saldo de proveedores y flujo de salidas": "", "Importe": "", "Total": ""},
        {"Determinacion de saldo de proveedores y flujo de salidas": "TOTAL DE SALDO DE PROVEEDORES", "Importe": "", "Total": dato["Saldo de proveedores total"]},
    ]
    return pd.DataFrame(fila)


 
# Presupuesto de mano de obra directa
 

def pres_mano_obra():
    mostrar_seccion("Presupuesto de mano de obra directa")
    prod_len = len(productos_projecciones["Producto"])
    mod_ps = pedir_numero("Costo de mano de obra por hora del primer semestre: $")
    mod_ss = pedir_numero("Costo de mano de obra por hora del segundo semestre: $")

    for i in range(prod_len):
        producto = productos_projecciones["Producto"][i]
        mod_ud = pedir_numero(
            f"Horas requeridas para elaborar una pieza del producto {producto}: "
        )
        mano_obra["Horas req por unidad"].append(mod_ud)
        mano_obra["Costo de mano obra 1hra primer semestre"].append(mod_ps)
        mano_obra["Costo de mano de obra 1hra segundo semestre"].append(mod_ss)

    global df_mano_obra_calculado, tot_hr_ov
    df_calc = pd.DataFrame(mano_obra)
    df_calc["Total horas requeridas primer semestre"] = (
        df_calc["Unidades a producir primer semestre"] * df_calc["Horas req por unidad"]
    )
    df_calc["Total horas requeridas segundo semestre"] = (
        df_calc["Unidades a producir segundo semestre"] * df_calc["Horas req por unidad"]
    )
    df_calc["Total horas requeridas"] = (
        df_calc["Total de unidades a producir"] * df_calc["Horas req por unidad"]
    )
    df_calc["Importe mano obra primer semestre"] = (
        df_calc["Total horas requeridas primer semestre"] * df_calc["Costo de mano obra 1hra primer semestre"]
    )
    df_calc["Importe mano obra segundo semestre"] = (
        df_calc["Total horas requeridas segundo semestre"] * df_calc["Costo de mano de obra 1hra segundo semestre"]
    )
    df_calc["Importe total mano obra"] = (
        df_calc["Importe mano obra primer semestre"] + df_calc["Importe mano obra segundo semestre"]
    )
    df_mano_obra_calculado = df_calc.copy()

    imp_ps_total = df_calc["Importe mano obra primer semestre"].sum()
    imp_ss_total = df_calc["Importe mano obra segundo semestre"].sum()
    imp_tt = df_calc["Importe total mano obra"].sum()
    tot_hr_ps = df_calc["Total horas requeridas primer semestre"].sum()
    tot_hr_ss = df_calc["Total horas requeridas segundo semestre"].sum()
    tot_hr_ov = df_calc["Total horas requeridas"].sum()

    fila = []
    for _, row in df_calc.iterrows():
        fila.append(crear_fila(row["Producto"], columna="Presupuesto de mano de obra directa"))
        fila.append(crear_fila(
            "Unidades a producir", row["Unidades a producir primer semestre"],
            row["Unidades a producir segundo semestre"], row["Total de unidades a producir"],
            columna="Presupuesto de mano de obra directa",
        ))
        fila.append(crear_fila(
            "Horas requeridas por unidad", row["Horas req por unidad"],
            row["Horas req por unidad"], row["Horas req por unidad"],
            columna="Presupuesto de mano de obra directa",
        ))
        fila.append(crear_fila(
            "Total horas requeridas", row["Total horas requeridas primer semestre"],
            row["Total horas requeridas segundo semestre"], row["Total horas requeridas"],
            columna="Presupuesto de mano de obra directa",
        ))
        fila.append(crear_fila(
            "Cuota por hora", row["Costo de mano obra 1hra primer semestre"],
            row["Costo de mano de obra 1hra segundo semestre"], "",
            columna="Presupuesto de mano de obra directa",
        ))
        fila.append(crear_fila(
            "Importe mano de obra directa", row["Importe mano obra primer semestre"],
            row["Importe mano obra segundo semestre"], row["Importe total mano obra"],
            columna="Presupuesto de mano de obra directa",
        ))
        fila.append(crear_fila("", columna="Presupuesto de mano de obra directa"))

    fila.append(crear_fila(
        "Total de horas requeridas por semestre", tot_hr_ps, tot_hr_ss, tot_hr_ov,
        columna="Presupuesto de mano de obra directa",
    ))
    fila.append(crear_fila(
        "Total de M.O.D. por semestre", imp_ps_total, imp_ss_total, imp_tt,
        columna="Presupuesto de mano de obra directa",
    ))
    return pd.DataFrame(fila)


 
# Captura y presupuesto de gastos (GIF y gastos de operacion)
 

def capturar_gastos(diccionario, columna_nombre, titulo, grupo="gif"):
    while True:
        nombre = pedir_texto(f"Ingresa el nombre del gasto de {titulo}: ")
        monto = pedir_numero("Ingresa el monto del gasto: $")
        periodo = pedir_entero(
            "Ingresa el periodo: 1 primer semestre, 2 segundo semestre, 3 anual: ",
            minimo=1,
        )
        while periodo not in (1, 2, 3):
            periodo = pedir_entero("Selecciona 1, 2 o 3: ", minimo=1)

        if periodo == 1:
            monto_1, monto_2 = monto, 0
        elif periodo == 2:
            monto_1, monto_2 = 0, monto
        else:
            porcentaje_1 = pedir_porcentaje(
                "Que porcentaje del gasto anual corresponde al primer semestre? (0 a 100): "
            )
            monto_1 = monto * porcentaje_1
            monto_2 = monto - monto_1

        diccionario[columna_nombre].append(nombre)
        diccionario["Primer semestre"].append(monto_1)
        diccionario["Segundo semestre"].append(monto_2)
        diccionario["Annual"].append(monto_1 + monto_2)
        gastos_no_efectivo[grupo].append(
            pedir_si_no("Es un gasto sin salida de efectivo (ej. depreciacion)? (S/N): ")
        )

        if not pedir_si_no(f"Deseas ingresar otro gasto de {titulo}? (S/N): "):
            break


def gastos_fab_ind():
    mostrar_seccion("Gastos indirectos de fabricacion")
    capturar_gastos(
        gif,
        "Presupuesto de gastos indirectos de fabricacion",
        "fabricacion",
        grupo="gif",
    )

    df_pres_gif = pd.DataFrame(gif)
    gif_1er = df_pres_gif["Primer semestre"].sum()
    gif_2ndo = df_pres_gif["Segundo semestre"].sum()
    gif_tot = df_pres_gif["Annual"].sum()

    global gif_hr
    if tot_hr_ov == 0:
        gif_hr = 0
    else:
        gif_hr = gif_tot / tot_hr_ov

    df_pres_gif.loc[len(df_pres_gif)] = ["Total G.I.F. por semestre", gif_1er, gif_2ndo, gif_tot]
    df_pres_gif.loc[len(df_pres_gif)] = ["Determinacion del costo por hora", "", "", ""]
    df_pres_gif.loc[len(df_pres_gif)] = ["Total G.I.F.", "", "", gif_tot]
    df_pres_gif.loc[len(df_pres_gif)] = ["Total horas M.O.D. anual", "", "", tot_hr_ov]
    df_pres_gif.loc[len(df_pres_gif)] = ["Costo por hora de G.I.F.", "", "", gif_hr]
    return df_pres_gif


def Pres_gast_op():
    """Captura gastos administrativos/de venta; permite comisiones sobre ventas."""
    mostrar_seccion("Gastos administrativos y ventas")
    ventas_ps = float(df_ventas_calculado["Importe de venta primer semestre"].sum())
    ventas_ss = float(df_ventas_calculado["Importe de venta segundo semestre"].sum())

    while True:
        print("\nTipo de gasto de administracion / ventas:")
        print("1. Gasto por importe fijo")
        print("2. Comision como porcentaje de las ventas")
        tipo = pedir_entero("Selecciona el tipo de gasto: ", minimo=1)
        while tipo not in (1, 2):
            tipo = pedir_entero("Selecciona 1 o 2: ", minimo=1)

        if tipo == 2:
            nombre = pedir_texto("Nombre del gasto (ej. Comisiones): ")
            porcentaje = pedir_porcentaje("Porcentaje de comision sobre ventas (0 a 100): ")
            monto_1 = ventas_ps * porcentaje
            monto_2 = ventas_ss * porcentaje
            es_no_efectivo = False
            print(
                f"Comision calculada: primer semestre ${monto_1:,.2f}; "
                f"segundo semestre ${monto_2:,.2f}."
            )
        else:
            nombre = pedir_texto("Ingresa el nombre del gasto de administracion/ventas: ")
            monto = pedir_numero("Ingresa el monto del gasto: $")
            periodo = pedir_entero(
                "Ingresa el periodo: 1 primer semestre, 2 segundo semestre, 3 anual: ",
                minimo=1,
            )
            while periodo not in (1, 2, 3):
                periodo = pedir_entero("Selecciona 1, 2 o 3: ", minimo=1)

            if periodo == 1:
                monto_1, monto_2 = monto, 0
            elif periodo == 2:
                monto_1, monto_2 = 0, monto
            else:
                porcentaje_1 = pedir_porcentaje(
                    "Que porcentaje del gasto anual corresponde al primer semestre? (0 a 100): "
                )
                monto_1 = monto * porcentaje_1
                monto_2 = monto - monto_1

            es_no_efectivo = pedir_si_no(
                "Es un gasto sin salida de efectivo (ej. depreciacion)? (S/N): "
            )

        gav["Presupuesto de gastos de operacion"].append(nombre)
        gav["Primer semestre"].append(monto_1)
        gav["Segundo semestre"].append(monto_2)
        gav["Annual"].append(monto_1 + monto_2)
        gastos_no_efectivo["gav"].append(es_no_efectivo)

        if not pedir_si_no("Deseas ingresar otro gasto de administracion/ventas? (S/N): "):
            break

    df_pres_gav = pd.DataFrame(gav)
    gav_1er = df_pres_gav["Primer semestre"].sum()
    gav_2ndo = df_pres_gav["Segundo semestre"].sum()
    gav_tot = df_pres_gav["Annual"].sum()
    df_pres_gav.loc[len(df_pres_gav)] = [
        "Total de gastos de operacion", gav_1er, gav_2ndo, gav_tot
    ]
    return df_pres_gav


 
# 10. Determinacion del costo unitario de productos terminados
 

def det_costo_unitario():
    """Calcula costo unitario usando costo de materiales y cuotas del 2do semestre."""
    mostrar_seccion("Determinacion del costo unitario de productos terminados")
    global df_costos_unitarios, costos_unitarios_producto
    costos_unitarios_producto = {}
    filas = []

    for _, producto in df_req_materiales_calculado.iterrows():
        nombre_producto = producto["Producto"]
        filas.append({"Producto": nombre_producto, "Concepto": "", "Costo": "", "Cantidad": "", "Costo unitario": ""})
        total_unitario = 0.0

        for nombre_material in materiales["Material"]:
            col_req = f"{nombre_material} req. para 1 pza"
            indice = materiales["Material"].index(nombre_material)
            costo_material = float(materiales["Costo del material segundo semestre"][indice])
            cantidad = float(producto[col_req])
            importe_unitario = costo_material * cantidad
            total_unitario += importe_unitario
            filas.append({
                "Producto": "", "Concepto": nombre_material,
                "Costo": costo_material, "Cantidad": cantidad,
                "Costo unitario": importe_unitario,
            })

        mod_row = df_mano_obra_calculado.loc[
            df_mano_obra_calculado["Producto"] == nombre_producto
        ].iloc[0]
        cuota_mod = float(mod_row["Costo de mano de obra 1hra segundo semestre"])
        horas_unidad = float(mod_row["Horas req por unidad"])
        importe_mod = cuota_mod * horas_unidad
        total_unitario += importe_mod
        filas.append({
            "Producto": "", "Concepto": "Mano de obra directa",
            "Costo": cuota_mod, "Cantidad": horas_unidad,
            "Costo unitario": importe_mod,
        })

        importe_gif = float(gif_hr) * horas_unidad
        total_unitario += importe_gif
        filas.append({
            "Producto": "", "Concepto": "Gastos indirectos de fabricacion",
            "Costo": float(gif_hr), "Cantidad": horas_unidad,
            "Costo unitario": importe_gif,
        })
        filas.append({
            "Producto": "", "Concepto": "COSTO UNITARIO DEL PRODUCTO",
            "Costo": "", "Cantidad": "", "Costo unitario": total_unitario,
        })
        filas.append({"Producto": "", "Concepto": "", "Costo": "", "Cantidad": "", "Costo unitario": ""})
        costos_unitarios_producto[nombre_producto] = total_unitario

    df_costos_unitarios = pd.DataFrame(filas)
    return df_costos_unitarios


 
# 11. Valuacion de inventarios finales
 

def valuacion_inventarios_finales():
    mostrar_seccion("Valuacion de inventarios finales")
    global df_val_inventarios, total_inv_final_materiales, total_inv_final_productos
    filas = []
    filas.append({"Tipo": "INVENTARIO FINAL DE MATERIALES", "Descripcion": "", "Unidades": "", "Costo unitario": "", "Costo total": ""})
    total_inv_final_materiales = 0.0
    for i, nombre in enumerate(materiales["Material"]):
        unidades = float(materiales["Inventario final segundo semestre"][i])
        costo = float(materiales["Costo del material segundo semestre"][i])
        total = unidades * costo
        total_inv_final_materiales += total
        filas.append({"Tipo": "Material", "Descripcion": nombre, "Unidades": unidades, "Costo unitario": costo, "Costo total": total})
    filas.append({"Tipo": "", "Descripcion": "TOTAL INVENTARIO FINAL DE MATERIALES", "Unidades": "", "Costo unitario": "", "Costo total": total_inv_final_materiales})
    filas.append({"Tipo": "", "Descripcion": "", "Unidades": "", "Costo unitario": "", "Costo total": ""})
    filas.append({"Tipo": "INVENTARIO FINAL DE PRODUCTOS TERMINADOS", "Descripcion": "", "Unidades": "", "Costo unitario": "", "Costo total": ""})

    total_inv_final_productos = 0.0
    for i, nombre in enumerate(productos_inventario["Producto"]):
        unidades = float(productos_inventario["Inventario final segundo semestre"][i])
        costo = float(costos_unitarios_producto[nombre])
        total = unidades * costo
        total_inv_final_productos += total
        filas.append({"Tipo": "Producto terminado", "Descripcion": nombre, "Unidades": unidades, "Costo unitario": costo, "Costo total": total})
    filas.append({"Tipo": "", "Descripcion": "TOTAL INVENTARIO FINAL DE PRODUCTOS TERMINADOS", "Unidades": "", "Costo unitario": "", "Costo total": total_inv_final_productos})

    df_val_inventarios = pd.DataFrame(filas)
    return df_val_inventarios


 
# 12. Estado de costo de produccion y ventas
 

def estado_costo_produccion_ventas():
    mostrar_seccion("Estado de costo de produccion y ventas")
    saldo_inicial_mat = saldo_seleccionado(
        activos_circulante, cuentas_especiales["inventario_materiales"]
    )
    saldo_inicial_pt = saldo_seleccionado(
        activos_circulante, cuentas_especiales["inventario_productos"]
    )
    compras = float(df_compra_materiales_calculado["Total material en $ anual"].sum())
    mod_total = float(df_mano_obra_calculado["Importe total mano obra"].sum())
    gif_total = float(pd.DataFrame(gif)["Annual"].sum())
    material_disponible = saldo_inicial_mat + compras
    materiales_utilizados = material_disponible - total_inv_final_materiales
    costo_produccion = materiales_utilizados + mod_total + gif_total
    produccion_disponible = costo_produccion + saldo_inicial_pt
    costo_ventas = produccion_disponible - total_inv_final_productos

    filas = [
        {"Estado de costo de produccion y ventas": "Saldo inicial de materiales", "Importe": saldo_inicial_mat},
        {"Estado de costo de produccion y ventas": "(+) Compras de materiales", "Importe": compras},
        {"Estado de costo de produccion y ventas": "(=) Material disponible", "Importe": material_disponible},
        {"Estado de costo de produccion y ventas": "(-) Inventario final de materiales", "Importe": total_inv_final_materiales},
        {"Estado de costo de produccion y ventas": "(=) Materiales utilizados", "Importe": materiales_utilizados},
        {"Estado de costo de produccion y ventas": "(+) Mano de obra directa", "Importe": mod_total},
        {"Estado de costo de produccion y ventas": "(+) Gastos indirectos de fabricacion", "Importe": gif_total},
        {"Estado de costo de produccion y ventas": "(=) Costo de produccion", "Importe": costo_produccion},
        {"Estado de costo de produccion y ventas": "(+) Inventario inicial de productos terminados", "Importe": saldo_inicial_pt},
        {"Estado de costo de produccion y ventas": "(=) Total de produccion disponible", "Importe": produccion_disponible},
        {"Estado de costo de produccion y ventas": "(-) Inventario final de productos terminados", "Importe": total_inv_final_productos},
        {"Estado de costo de produccion y ventas": "(=) COSTO DE VENTAS", "Importe": costo_ventas},
    ]
    global df_estado_costo, costo_ventas_calculado
    costo_ventas_calculado = costo_ventas
    df_estado_costo = pd.DataFrame(filas)
    return df_estado_costo


 
# 13. Estado de resultados
 

def estado_resultados():
    mostrar_seccion("Estado de resultados")
    ventas = float(df_ventas_calculado["Importe total anual"].sum())
    utilidad_bruta = ventas - float(costo_ventas_calculado)
    gastos_operacion = float(pd.DataFrame(gav)["Annual"].sum())
    utilidad_operacion = utilidad_bruta - gastos_operacion

    tasa_isr = pedir_porcentaje("Ingresa la tasa de ISR (porcentaje, 0 a 100): ")
    tasa_ptu = pedir_porcentaje("Ingresa la tasa de PTU (porcentaje, 0 a 100): ")
    isr = max(0.0, utilidad_operacion) * tasa_isr
    ptu = max(0.0, utilidad_operacion) * tasa_ptu
    utilidad_neta = utilidad_operacion - isr - ptu

    global df_estado_resultados, impuesto_isr_calculado, impuesto_ptu_calculado, utilidad_neta_calculada
    impuesto_isr_calculado = isr
    impuesto_ptu_calculado = ptu
    utilidad_neta_calculada = utilidad_neta
    df_estado_resultados = pd.DataFrame([
        {"Estado de resultados": "Ventas", "Importe": ventas},
        {"Estado de resultados": "(-) Costo de ventas", "Importe": costo_ventas_calculado},
        {"Estado de resultados": "(=) Utilidad bruta", "Importe": utilidad_bruta},
        {"Estado de resultados": "(-) Gastos de operacion", "Importe": gastos_operacion},
        {"Estado de resultados": "(=) Utilidad de operacion", "Importe": utilidad_operacion},
        {"Estado de resultados": "(-) ISR", "Importe": isr},
        {"Estado de resultados": "(-) PTU", "Importe": ptu},
        {"Estado de resultados": "(=) UTILIDAD NETA", "Importe": utilidad_neta},
    ])
    return df_estado_resultados


 
# 14. Estado de flujo de efectivo
 

def estado_flujo_efectivo():
    mostrar_seccion("Estado de flujo de efectivo")
    efectivo_inicial = saldo_seleccionado(
        activos_circulante, cuentas_especiales["efectivo"]
    )
    cobro_anterior = float(clientes_flujo["Por cobranza periodo previo"][0])
    cobro_actual = float(clientes_flujo["Por cobranza periodo actual"][0])
    total_entradas = cobro_anterior + cobro_actual
    efectivo_disponible = efectivo_inicial + total_entradas

    pago_prov_anterior = float(prov_flujo["Por pagar periodo previo"][0])
    pago_prov_actual = float(prov_flujo["Por pagar periodo actual"][0])
    pago_mod = float(df_mano_obra_calculado["Importe total mano obra"].sum())
    gif_anual = float(pd.DataFrame(gif)["Annual"].sum())
    gif_no_efectivo = sum(
        monto for monto, es_no_efectivo in zip(gif["Annual"], gastos_no_efectivo["gif"])
        if es_no_efectivo
    )
    pago_gif = gif_anual - gif_no_efectivo
    gav_anual = float(pd.DataFrame(gav)["Annual"].sum())
    gav_no_efectivo = sum(
        monto for monto, es_no_efectivo in zip(gav["Annual"], gastos_no_efectivo["gav"])
        if es_no_efectivo
    )
    pago_gav = gav_anual - gav_no_efectivo

    compra_activo = pedir_numero(
        "Importe de compras de activo fijo/equipo durante el ejercicio (si no hubo, 0): $"
    )
    nombre_activo_nuevo = None
    if compra_activo > 0:
        nombre_activo_nuevo = pedir_texto(
            "Nombre de la cuenta de activo fijo a incrementar (ej. Maquinaria y equipo): "
        )

    saldo_isr_previo = saldo_seleccionado(pasivos_cp, cuentas_especiales["isr"])
    if saldo_isr_previo > 0:
        porcentaje_isr_previo = pedir_porcentaje(
            "Que porcentaje del ISR del ejercicio anterior se pagara durante este ejercicio? (0 a 100): "
        )
    else:
        porcentaje_isr_previo = 0
    pago_isr_previo = saldo_isr_previo * porcentaje_isr_previo

    porcentaje_isr_actual = pedir_porcentaje(
        "Que porcentaje del ISR generado este ejercicio se pagara dentro del mismo ejercicio? (0 a 100): "
    )
    pago_isr_actual = impuesto_isr_calculado * porcentaje_isr_actual
    saldo_ptu_previo = saldo_seleccionado(pasivos_cp, cuentas_especiales["ptu"])
    if saldo_ptu_previo > 0:
        porcentaje_ptu_previo = pedir_porcentaje(
            "Que porcentaje del PTU anterior se pagara durante este ejercicio? (0 a 100): "
        )
    else:
        porcentaje_ptu_previo = 0
    pago_ptu_previo = saldo_ptu_previo * porcentaje_ptu_previo
    porcentaje_ptu_actual = pedir_porcentaje(
        "Que porcentaje del PTU generado este ejercicio se pagara dentro del mismo ejercicio? (0 a 100): "
    )
    pago_ptu_actual = impuesto_ptu_calculado * porcentaje_ptu_actual

    salidas = [
        ("Proveedores del ejercicio anterior", pago_prov_anterior),
        ("Proveedores del ejercicio actual", pago_prov_actual),
        ("Pago de mano de obra directa", pago_mod),
        ("Pago de gastos indirectos de fabricacion", pago_gif),
        ("Pago de gastos de operacion", pago_gav),
        ("Compra de activo fijo", compra_activo),
        ("Pago de ISR anterior", pago_isr_previo),
        ("Pago de ISR actual", pago_isr_actual),
        ("Pago de PTU anterior", pago_ptu_previo),
        ("Pago de PTU actual", pago_ptu_actual),
    ]
    total_salidas = sum(valor for _, valor in salidas)
    flujo_final = efectivo_disponible - total_salidas

    global df_estado_flujo, efectivo_final_calculado, compra_activo_calculada
    global nombre_activo_adquirido, pago_isr_previo_calculado, pago_isr_actual_calculado
    global pago_ptu_previo_calculado, pago_ptu_actual_calculado
    efectivo_final_calculado = flujo_final
    compra_activo_calculada = compra_activo
    nombre_activo_adquirido = nombre_activo_nuevo
    pago_isr_previo_calculado = pago_isr_previo
    pago_isr_actual_calculado = pago_isr_actual
    pago_ptu_previo_calculado = pago_ptu_previo
    pago_ptu_actual_calculado = pago_ptu_actual

    filas = [
        {"Estado de flujo de efectivo": "Saldo inicial de efectivo", "Importe": efectivo_inicial},
        {"Estado de flujo de efectivo": "ENTRADAS", "Importe": ""},
        {"Estado de flujo de efectivo": "Cobranza del ejercicio anterior", "Importe": cobro_anterior},
        {"Estado de flujo de efectivo": "Cobranza del ejercicio actual", "Importe": cobro_actual},
        {"Estado de flujo de efectivo": "Total de entradas", "Importe": total_entradas},
        {"Estado de flujo de efectivo": "Efectivo disponible", "Importe": efectivo_disponible},
        {"Estado de flujo de efectivo": "SALIDAS", "Importe": ""},
    ]
    filas.extend({"Estado de flujo de efectivo": concepto, "Importe": valor} for concepto, valor in salidas)
    filas.extend([
        {"Estado de flujo de efectivo": "Total de salidas", "Importe": total_salidas},
        {"Estado de flujo de efectivo": "FLUJO DE EFECTIVO FINAL", "Importe": flujo_final},
    ])
    df_estado_flujo = pd.DataFrame(filas)
    return df_estado_flujo


 
# 15. Balance general presupuestado
 

def _actualizar_cuenta(diccionario, nombre, valor, nombre_predeterminado):
    if nombre is None:
        nombre = nombre_predeterminado
    diccionario[nombre] = [float(valor)]
    return nombre


def balance_general_final():
    mostrar_seccion("Balance general presupuestado")
    # Se trabaja con copias el balance anterior permanece disponible y sin cambios
    ac = {k: [v[0]] for k, v in activos_circulante.items()}
    anc = {k: [v[0]] for k, v in activos_no_circulantes.items()}
    pcp = {k: [v[0]] for k, v in pasivos_cp.items()}
    plp = {k: [v[0]] for k, v in pasivos_lp.items()}
    cap = {k: [v[0]] for k, v in capital_contable.items()}

    nombre_efectivo = _actualizar_cuenta(
        ac, cuentas_especiales["efectivo"], efectivo_final_calculado, "Efectivo"
    )
    nombre_clientes = _actualizar_cuenta(
        ac, cuentas_especiales["clientes"],
        float(clientes_flujo["Saldo de clientes previo"][0]
              + clientes_flujo["Ventas"][0]
              - clientes_flujo["Por cobranza periodo previo"][0]
              - clientes_flujo["Por cobranza periodo actual"][0]),
        "Clientes",
    )
    _actualizar_cuenta(
        ac, cuentas_especiales["inventario_materiales"],
        total_inv_final_materiales, "Inventario de materiales"
    )
    _actualizar_cuenta(
        ac, cuentas_especiales["inventario_productos"],
        total_inv_final_productos, "Inventario de productos terminados"
    )

    if compra_activo_calculada > 0:
        nombre_fijo = cuentas_especiales["activo_fijo"]
        if nombre_fijo is None:
            nombre_fijo = nombre_activo_adquirido or "Activo fijo adquirido"
            anc[nombre_fijo] = [compra_activo_calculada]
        else:
            anc[nombre_fijo] = [float(anc[nombre_fijo][0]) + compra_activo_calculada]

   #dep accounts do not represent a cash exit, however they do affect the accounts. need to keep track of it
    depreciacion_total = sum(
        monto for monto, es_no_efectivo in zip(gif["Annual"], gastos_no_efectivo["gif"])
        if es_no_efectivo
    ) + sum(
        monto for monto, es_no_efectivo in zip(gav["Annual"], gastos_no_efectivo["gav"])
        if es_no_efectivo
    )
    nombre_depreciacion = cuentas_especiales["depreciacion_acumulada"]
    if nombre_depreciacion is None and depreciacion_total > 0:
        nombre_depreciacion = "Depreciacion acumulada"
        anc[nombre_depreciacion] = [depreciacion_total]
        cuentas_resta_activo.add(nombre_depreciacion)
    elif nombre_depreciacion is not None:
        anc[nombre_depreciacion] = [float(anc[nombre_depreciacion][0]) + depreciacion_total]

    # Saldos finales de pasivos operativos e impuestos.
    proveedores_final = float(prov_flujo["Saldo de proveedores previo"][0]
                              + prov_flujo["Compras"][0]
                              - prov_flujo["Por pagar periodo previo"][0]
                              - prov_flujo["Por pagar periodo actual"][0])
    _actualizar_cuenta(pcp, cuentas_especiales["proveedores"], proveedores_final, "Proveedores")

    isr_final = max(0.0, saldo_seleccionado(pasivos_cp, cuentas_especiales["isr"])
                    - pago_isr_previo_calculado
                    + impuesto_isr_calculado - pago_isr_actual_calculado)
    if cuentas_especiales["isr"] is not None or isr_final > 0:
        _actualizar_cuenta(pcp, cuentas_especiales["isr"], isr_final, "ISR por pagar")

    ptu_final = max(0.0, saldo_seleccionado(pasivos_cp, cuentas_especiales["ptu"])
                    - pago_ptu_previo_calculado
                    + impuesto_ptu_calculado - pago_ptu_actual_calculado)
    if cuentas_especiales["ptu"] is not None or ptu_final > 0:
        _actualizar_cuenta(pcp, cuentas_especiales["ptu"], ptu_final, "PTU por pagar")

    # La utilidad del ejercicio se presenta como una partida separada del capital.
    cap["Utilidad del ejercicio"] = [float(utilidad_neta_calculada)]

    filas = []
    def agregar_grupo(titulo, diccionario, contra=False):
        filas.append({"Clasificacion": titulo, "Cuenta": "", "Importe": ""})
        subtotal = 0.0
        for nombre, valor_lista in diccionario.items():
            valor = float(valor_lista[0])
            if contra and nombre in cuentas_resta_activo:
                valor = -abs(valor)
            filas.append({"Clasificacion": "", "Cuenta": nombre, "Importe": valor})
            subtotal += valor
        filas.append({"Clasificacion": "", "Cuenta": f"Total {titulo}", "Importe": subtotal})
        filas.append({"Clasificacion": "", "Cuenta": "", "Importe": ""})
        return subtotal

    total_ac = agregar_grupo("ACTIVO CIRCULANTE", ac)
    total_anc = agregar_grupo("ACTIVO NO CIRCULANTE", anc, contra=True)
    activo_total = total_ac + total_anc
    filas.append({"Clasificacion": "", "Cuenta": "ACTIVO TOTAL", "Importe": activo_total})
    filas.append({"Clasificacion": "", "Cuenta": "", "Importe": ""})
    total_pcp = agregar_grupo("PASIVO A CORTO PLAZO", pcp)
    total_plp = agregar_grupo("PASIVO A LARGO PLAZO", plp)
    pasivo_total = total_pcp + total_plp
    total_cap = agregar_grupo("CAPITAL CONTABLE", cap)
    suma_pasivo_capital = pasivo_total + total_cap
    diferencia = activo_total - suma_pasivo_capital
    filas.append({"Clasificacion": "", "Cuenta": "PASIVO TOTAL", "Importe": pasivo_total})
    filas.append({"Clasificacion": "", "Cuenta": "SUMA DE PASIVO Y CAPITAL", "Importe": suma_pasivo_capital})
    filas.append({"Clasificacion": "", "Cuenta": "DIFERENCIA (ACTIVO - PASIVO Y CAPITAL)", "Importe": diferencia})

    global df_balance_final
    df_balance_final = pd.DataFrame(filas)
    return df_balance_final


 
# Programa principal
 

def main():
    global ANIO_PRESUPUESTO

    print("\nGENERADOR DE PRESUPUESTOS")
    print("El programa solicita los datos de cada empresa y muestra los reportes en tablas.")
    mostrar_seccion("Datos generales del presupuesto")
    ANIO_PRESUPUESTO = pedir_entero("Ingresa el año del presupuesto: ", minimo=1)

    df_balance_previo = bal_previo()

    num_productos = pedir_entero("Cuantos productos fabrica o vende la empresa? ", minimo=1)
    df_presupuesto_ventas = pres_ventas(num_productos)
    df_saldo_clientes = det_clientes_entradas()
    df_pres_produccion = pres_produccion()
    df_pres_req_materiales = pres_req_materiales(df_pres_produccion)
    df_pres_compra_mat = pres_compra_mat()
    df_saldo_proveedores = prov_salidas()
    df_pres_mod = pres_mano_obra()
    df_pres_gif = gastos_fab_ind()
    df_pres_gav = Pres_gast_op()

    # Estados financieros presupuestados que se calculan con los nueve reportes previos
    df_costo_unitario = det_costo_unitario()
    df_val_inventarios = valuacion_inventarios_finales()
    df_estado_costo = estado_costo_produccion_ventas()
    df_estado_resultados = estado_resultados()
    df_estado_flujo = estado_flujo_efectivo()
    df_balance_final = balance_general_final()

    # Los reportes se muestran en el mismo orden de las funciones
    mostrar_tabla("Balance general previo capturado", df_balance_previo)
    mostrar_tabla("1. Presupuesto de ventas", df_presupuesto_ventas)
    mostrar_tabla("2. Determinacion de saldo de clientes y flujo de entradas", df_saldo_clientes)
    mostrar_tabla("3. Presupuesto de produccion", df_pres_produccion)
    mostrar_tabla("4. Presupuesto de requerimiento de materiales", df_pres_req_materiales)
    mostrar_tabla("5. Presupuesto de compra de materiales", df_pres_compra_mat)
    mostrar_tabla("6. Determinacion de saldo de proveedores y flujo de salidas", df_saldo_proveedores)
    mostrar_tabla("7. Presupuesto de mano de obra directa", df_pres_mod)
    mostrar_tabla("8. Presupuesto de gastos indirectos de fabricacion", df_pres_gif)
    mostrar_tabla("9. Presupuesto de gastos de operacion", df_pres_gav)
    mostrar_tabla("10. Determinacion del costo unitario de productos terminados", df_costo_unitario)
    mostrar_tabla("11. Valuacion de inventarios finales", df_val_inventarios)
    mostrar_tabla("12. Estado de costo de produccion y ventas", df_estado_costo)
    mostrar_tabla("13. Estado de resultados", df_estado_resultados)
    mostrar_tabla("14. Estado de flujo de efectivo", df_estado_flujo)
    mostrar_tabla("15. Balance general presupuestado", df_balance_final)


if __name__ == "__main__":
    pd.set_option("display.width", 180)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", 250)
    main()

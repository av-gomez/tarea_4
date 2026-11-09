# Referencia técnica de la ENAHO 2024

## Archivos

| Módulo | Archivo dentro del zip | Unidad | Filas | Llaves | Factor |
|---|---|---|---|---|---|
| 34 Sumaria | `966-Modulo34/sumaria-2024.dta` | hogar | 33,691 | `conglome`, `vivienda`, `hogar` | `factor07` (hogares) |
| 02 Miembros | `966-Modulo02/enaho01-2024-200.dta` | persona | 117,721 | las tres + `codperso` | `facpob07` (personas) |

El zip del módulo 34 incluye también `sumaria-2024-12g.dta` (gasto en 12 grupos); el script usa
`sumaria-2024.dta`.

## Variables usadas

| Variable | Módulo | Significado | Codificación |
|---|---|---|---|
| `ubigeo` | 34, 02 | Ubicación geográfica (departamento, provincia, distrito) | Texto de 6 dígitos; `ubigeo[:2]` = departamento |
| `dominio` | 34 | Dominio geográfico | 1 Costa Norte, 2 Costa Centro, 3 Costa Sur, 4 Sierra Norte, 5 Sierra Centro, 6 Sierra Sur, 7 Selva, 8 Lima Metropolitana |
| `estrato` | 34 | Estrato geográfico por tamaño de centro poblado | 1-5 urbano, 6-8 rural |
| `pobreza` | 34 | Condición de pobreza monetaria | 1 pobre extremo, 2 pobre no extremo, 3 no pobre |
| `mieperho` | 34 | Miembros del hogar (excluye trabajadores del hogar y pensionistas) | Entero |
| `factor07` | 34 | Factor de expansión del hogar | Real |
| `linea`, `linpe` | 34 | Línea de pobreza total y extrema (S/ por persona al mes) | Real |
| `gashog2d` | 34 | Gasto total bruto anual del hogar (deflactado) | S/ al año |
| `inghog1d` | 34 | Ingreso bruto anual del hogar (deflactado) | S/ al año |
| `p203` | 02 | Parentesco con el jefe del hogar | 1 jefe(a), 2 cónyuge, 3 hijo(a), ... |
| `p204` | 02 | ¿Es miembro del hogar? | 1 sí, 2 no |
| `p205` | 02 | ¿Estuvo ausente más de 30 días? | 1 sí, 2 no |
| `p206` | 02 | ¿Estuvo presente más de 30 días? (no miembros) | 1 sí, 2 no |
| `p207` | 02 | Sexo | 1 hombre, 2 mujer |
| `p208a` | 02 | Edad en años cumplidos | Entero |
| `facpob07` | 02 | Factor de expansión poblacional | Real |

## Reglas de cálculo

1. **Pobreza monetaria (INEI):** una persona es pobre si el gasto per cápita de su hogar es menor que la línea
   de pobreza; la variable `pobreza` ya incorpora esa comparación.
2. **Estimación oficial:** proporción de personas pobres = `sum(pondera * pobre) / sum(pondera)`, con
   `pondera = factor07 * mieperho` sobre la sumaria. Reproduce 27.6 % nacional y los 25 departamentos
   publicados.
3. **Estimación individual:** para sexo y edad se usa el módulo 02 (residentes habituales) con `facpob07`; da
   27.53 % nacional (diferencia de 0.05 p.p. con la oficial por la calibración del factor poblacional).
4. **Error de muestreo:** linealización de Taylor; UPM = `conglome`; estratos = departamento × `estrato`. Se
   reporta EE, IC 95 % y CV. El INEI considera referenciales las cifras con CV mayor a 15 %.
5. **Territorio:** Lima (15) incluye Lima Metropolitana y Lima provincias; Callao (07) va separado. Para Lima
   Metropolitana use `dominio == 8` (28.2 %).

## Valores de validación 2024

| Cifra | Valor |
|---|---|
| Pobreza monetaria nacional | 27.6 % |
| Pobreza extrema | 5.5 % |
| Urbana / rural | 24.8 % / 39.3 % |
| Residentes habituales | 108,664 |
| Hogares | 33,691 |
| Departamentos | 25 (ver `referencias/pobreza_departamento_2024.csv`) |

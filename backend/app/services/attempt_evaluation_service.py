from __future__ import annotations

from collections import Counter

from app.db.connection import get_connection


def _build_pattern(cod_objetivo: str, cod_intento: str) -> list[str]:
    """
    V = acierto exacto (verde)
    N = presente en otra posicion (naranja)
    G = ausente (gris)
    """
    target = list(cod_objetivo)
    guess = list(cod_intento)

    result = ["G"] * len(guess)
    remaining_target = []

    for idx, (g_char, t_char) in enumerate(zip(guess, target)):
        if g_char == t_char:
            result[idx] = "V"
        else:
            remaining_target.append(t_char)

    counter = Counter(remaining_target)

    for idx, g_char in enumerate(guess):
        if result[idx] == "V":
            continue

        if counter.get(g_char, 0) > 0:
            result[idx] = "N"
            counter[g_char] -= 1

    return result


def evaluate_attempt(cod_termino: str) -> dict:
    cod_intento = (cod_termino or "").strip().lower()

    query = """
    SET NOCOUNT ON;

    SELECT TOP (1)
        C.PK_DEMO_B,
        C.TD_DEMO_A,
        M.COD_DEMO_B AS COD_OBJETIVO,
        M.VAL_DEMO_A,
        MAX_INTENTOS = TRY_CAST((
            SELECT TOP (1) P.DES_DEMO_B
            FROM dbo.T_DEMO_A_03 P
            WHERE P.COD_DEMO_D = 'MAX_INTENTOS'
              AND P.FLG_DEMO_B = 1
        ) AS INT)
    FROM dbo.T_DEMO_A_02 C
    INNER JOIN dbo.T_DEMO_A_01 M
        ON M.PK_DEMO_A = C.FK_DEMO_A
    WHERE C.TD_DEMO_A = CAST(GETDATE() AS DATE)
      AND C.FLG_DEMO_B = 1
    ORDER BY C.PK_DEMO_B DESC;
    """

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
    finally:
        conn.close()

    if row is None:
        return {
            "status": "no_data",
            "data": {
                "message": "No existe asignacion diaria activa."
            }
        }

    cod_objetivo = str(row.COD_OBJETIVO)
    val_longitud = int(row.VAL_DEMO_A)
    val_max_intentos = int(row.MAX_INTENTOS) if row.MAX_INTENTOS is not None else 6

    if len(cod_intento) != val_longitud:
        return {
            "status": "ok",
            "data": {
                "flg_valido": False,
                "flg_acierto": False,
                "cod_termino": cod_intento,
                "val_longitud_esperada": val_longitud,
                "message": "Longitud incorrecta."
            }
        }

    pattern = _build_pattern(cod_objetivo=cod_objetivo, cod_intento=cod_intento)
    flg_acierto = all(item == "V" for item in pattern)

    return {
        "status": "ok",
        "data": {
            "pk_cuaderno": int(row.PK_DEMO_B),
            "td_referencia": str(row.TD_DEMO_A),
            "cod_termino": cod_intento,
            "val_longitud": val_longitud,
            "val_max_intentos": val_max_intentos,
            "flg_valido": True,
            "flg_acierto": flg_acierto,
            "txt_patron": "".join(pattern),
            "detalle": pattern
        }
    }


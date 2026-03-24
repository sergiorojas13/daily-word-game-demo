from __future__ import annotations

from collections import Counter

from app.db.connection import get_connection


def _build_pattern(cod_objetivo: str, cod_intento: str) -> list[str]:
    result = ["G"] * len(cod_intento)
    remaining_target = []

    for idx, (g_char, t_char) in enumerate(zip(cod_intento, cod_objetivo)):
        if g_char == t_char:
            result[idx] = "V"
        else:
            remaining_target.append(t_char)

    counter = Counter(remaining_target)

    for idx, g_char in enumerate(cod_intento):
        if result[idx] == "V":
            continue

        if counter.get(g_char, 0) > 0:
            result[idx] = "N"
            counter[g_char] -= 1

    return result


def submit_attempt(cod_usuario: str, des_usuario: str | None, cod_termino: str) -> dict:
    cod_usuario_norm = (cod_usuario or "").strip().lower()
    des_usuario_norm = (des_usuario or "").strip() or None
    cod_intento = (cod_termino or "").strip().lower()

    if not cod_usuario_norm:
        return {
            "status": "error",
            "data": {
                "message": "cod_usuario es obligatorio."
            }
        }

    conn = get_connection()
    conn.autocommit = False

    try:
        cursor = conn.cursor()

        cursor.execute("""
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
            ) AS INT),
            PUNTOS_BASE = TRY_CAST((
                SELECT TOP (1) P.DES_DEMO_B
                FROM dbo.T_DEMO_A_03 P
                WHERE P.COD_DEMO_D = 'PUNTOS_BASE'
                  AND P.FLG_DEMO_B = 1
            ) AS INT),
            PENALIZACION = TRY_CAST((
                SELECT TOP (1) P.DES_DEMO_B
                FROM dbo.T_DEMO_A_03 P
                WHERE P.COD_DEMO_D = 'PENALIZACION_INTENTO_EXTRA'
                  AND P.FLG_DEMO_B = 1
            ) AS INT)
        FROM dbo.T_DEMO_A_02 C
        INNER JOIN dbo.T_DEMO_A_01 M
            ON M.PK_DEMO_A = C.FK_DEMO_A
        WHERE C.TD_DEMO_A = CAST(GETDATE() AS DATE)
          AND C.FLG_DEMO_B = 1
        ORDER BY C.PK_DEMO_B DESC;
        """)

        row_day = cursor.fetchone()

        if row_day is None:
            conn.rollback()
            return {
                "status": "error",
                "data": {
                    "message": "No existe asignacion diaria activa."
                }
            }

        pk_cuaderno = int(row_day.PK_DEMO_B)
        td_referencia = str(row_day.TD_DEMO_A)
        cod_objetivo = str(row_day.COD_OBJETIVO)
        val_longitud = int(row_day.VAL_DEMO_A)
        val_max_intentos = int(row_day.MAX_INTENTOS) if row_day.MAX_INTENTOS is not None else 6
        puntos_base = int(row_day.PUNTOS_BASE) if row_day.PUNTOS_BASE is not None else 100
        penalizacion = int(row_day.PENALIZACION) if row_day.PENALIZACION is not None else 10

        if len(cod_intento) != val_longitud:
            conn.rollback()
            return {
                "status": "ok",
                "data": {
                    "pk_cuaderno": pk_cuaderno,
                    "td_referencia": td_referencia,
                    "cod_usuario": cod_usuario_norm,
                    "cod_termino": cod_intento,
                    "flg_registrado": False,
                    "flg_valido": False,
                    "message": "Longitud incorrecta.",
                    "val_longitud_esperada": val_longitud
                }
            }

        cursor.execute("""
        SELECT TOP (1)
            M.PK_DEMO_A
        FROM dbo.T_DEMO_A_01 M
        WHERE M.COD_DEMO_B = ?
          AND M.FLG_DEMO_B = 1
          AND M.VAL_DEMO_A = ?;
        """, cod_intento, val_longitud)

        row_term = cursor.fetchone()

        if row_term is None:
            conn.rollback()
            return {
                "status": "ok",
                "data": {
                    "pk_cuaderno": pk_cuaderno,
                    "td_referencia": td_referencia,
                    "cod_usuario": cod_usuario_norm,
                    "cod_termino": cod_intento,
                    "flg_registrado": False,
                    "flg_valido": False,
                    "message": "El termino no pertenece al catalogo activo."
                }
            }

        cursor.execute("""
        SELECT TOP (1)
            B.PK_DEMO_C,
            B.FLG_DEMO_C,
            B.FLG_DEMO_D,
            B.VAL_DEMO_B,
            B.VAL_DEMO_C,
            B.VAL_DEMO_D
        FROM dbo.T_DEMO_F_01 B
        WHERE B.TD_DEMO_A = CAST(GETDATE() AS DATE)
          AND B.COD_DEMO_C = ?;
        """, cod_usuario_norm)

        row_bitacora = cursor.fetchone()

        if row_bitacora is None:
            cursor.execute("""
            INSERT INTO dbo.T_DEMO_F_01
            (
                TD_DEMO_A,
                COD_DEMO_C,
                DES_DEMO_A,
                FLG_DEMO_C,
                FLG_DEMO_D,
                VAL_DEMO_C,
                VAL_DEMO_D
            )
            VALUES
            (
                CAST(GETDATE() AS DATE),
                ?,
                ?,
                0,
                0,
                0,
                0
            );

            SELECT CAST(SCOPE_IDENTITY() AS BIGINT) AS PK_DEMO_C;
            """, cod_usuario_norm, des_usuario_norm)

            pk_bitacora = int(cursor.fetchone().PK_DEMO_C)
            flg_resuelto_actual = False
            flg_cerrado_actual = False
            val_intento_total_actual = 0
        else:
            pk_bitacora = int(row_bitacora.PK_DEMO_C)
            flg_resuelto_actual = bool(row_bitacora.FLG_DEMO_C)
            flg_cerrado_actual = bool(row_bitacora.FLG_DEMO_D)
            val_intento_total_actual = int(row_bitacora.VAL_DEMO_C)

        if flg_cerrado_actual:
            conn.rollback()
            return {
                "status": "ok",
                "data": {
                    "pk_cuaderno": pk_cuaderno,
                    "pk_bitacora": pk_bitacora,
                    "td_referencia": td_referencia,
                    "cod_usuario": cod_usuario_norm,
                    "cod_termino": cod_intento,
                    "flg_registrado": False,
                    "flg_valido": True,
                    "message": "La ronda del dia ya esta cerrada."
                }
            }

        val_orden = val_intento_total_actual + 1

        if val_orden > val_max_intentos:
            conn.rollback()
            return {
                "status": "ok",
                "data": {
                    "pk_cuaderno": pk_cuaderno,
                    "pk_bitacora": pk_bitacora,
                    "td_referencia": td_referencia,
                    "cod_usuario": cod_usuario_norm,
                    "cod_termino": cod_intento,
                    "flg_registrado": False,
                    "flg_valido": True,
                    "message": "No quedan intentos disponibles."
                }
            }

        pattern = _build_pattern(cod_objetivo=cod_objetivo, cod_intento=cod_intento)
        txt_patron = "".join(pattern)
        flg_acierto = all(item == "V" for item in pattern)

        cursor.execute("""
        INSERT INTO dbo.T_DEMO_F_02
        (
            FK_DEMO_B,
            VAL_DEMO_E,
            COD_DEMO_A,
            COD_DEMO_B,
            TXT_DEMO_A,
            FLG_DEMO_E,
            FLG_DEMO_F
        )
        VALUES
        (
            ?,
            ?,
            ?,
            ?,
            ?,
            1,
            ?
        );
        """, pk_bitacora, val_orden, cod_intento, cod_intento, txt_patron, 1 if flg_acierto else 0)

        flg_resuelto_nuevo = flg_acierto
        flg_cerrado_nuevo = flg_acierto or (val_orden >= val_max_intentos)
        val_intento_ok = val_orden if flg_acierto else None
        val_puntos = max(0, puntos_base - ((val_orden - 1) * penalizacion)) if flg_acierto else 0

        cursor.execute("""
        UPDATE dbo.T_DEMO_F_01
        SET
            DES_DEMO_A       = COALESCE(?, DES_DEMO_A),
            FLG_DEMO_C      = ?,
            FLG_DEMO_D       = ?,
            VAL_DEMO_B    = ?,
            VAL_DEMO_C = ?,
            VAL_DEMO_D        = ?,
            TS_DEMO_B        = CASE WHEN ? = 1 THEN SYSUTCDATETIME() ELSE TS_DEMO_B END,
            TS_DEMO_F        = SYSUTCDATETIME()
        WHERE PK_DEMO_C = ?;
        """,
            des_usuario_norm,
            1 if flg_resuelto_nuevo else 0,
            1 if flg_cerrado_nuevo else 0,
            val_intento_ok,
            val_orden,
            val_puntos,
            1 if flg_cerrado_nuevo else 0,
            pk_bitacora
        )

        conn.commit()

        return {
            "status": "ok",
            "data": {
                "pk_cuaderno": pk_cuaderno,
                "pk_bitacora": pk_bitacora,
                "td_referencia": td_referencia,
                "cod_usuario": cod_usuario_norm,
                "des_usuario": des_usuario_norm,
                "cod_termino": cod_intento,
                "val_orden": val_orden,
                "val_longitud": val_longitud,
                "val_max_intentos": val_max_intentos,
                "flg_registrado": True,
                "flg_valido": True,
                "flg_acierto": flg_acierto,
                "flg_cerrado": flg_cerrado_nuevo,
                "txt_patron": txt_patron,
                "detalle": pattern,
                "val_puntos": val_puntos
            }
        }

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


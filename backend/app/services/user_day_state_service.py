from __future__ import annotations

from app.db.connection import get_connection


def _ensure_today_assignment(cursor) -> None:
    cursor.execute("""
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @TD_HOY date = CAST(GETDATE() AS DATE);

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.T_DEMO_A_02
        WHERE TD_DEMO_A = @TD_HOY
          AND FLG_DEMO_B = 1
    )
    BEGIN
        ;WITH E AS (
            SELECT
                M.PK_DEMO_A,
                ROW_NUMBER() OVER (ORDER BY M.PK_DEMO_A) AS RN,
                COUNT(*) OVER () AS CNT
            FROM dbo.T_DEMO_A_01 M
            WHERE M.FLG_DEMO_B = 1
              AND M.FLG_DEMO_A = 1
              AND M.VAL_DEMO_A = 5
        ),
        PICK AS (
            SELECT TOP (1) E.PK_DEMO_A
            FROM E
            WHERE E.RN = ((ABS(CHECKSUM(CONVERT(varchar(10), @TD_HOY, 23))) % E.CNT) + 1)
        )
        INSERT INTO dbo.T_DEMO_A_02 (
            TD_DEMO_A,
            FK_DEMO_A,
            FLG_DEMO_B,
            TS_DEMO_D,
            TS_DEMO_E,
            TS_DEMO_F
        )
        SELECT
            @TD_HOY,
            P.PK_DEMO_A,
            1,
            SYSUTCDATETIME(),
            SYSUTCDATETIME(),
            SYSUTCDATETIME()
        FROM PICK P;
    END

    UPDATE dbo.T_DEMO_A_02
       SET FLG_DEMO_B = 1,
           TS_DEMO_F = SYSUTCDATETIME(),
           TS_DEMO_D = COALESCE(TS_DEMO_D, SYSUTCDATETIME())
    WHERE TD_DEMO_A = @TD_HOY;
    """)


def get_user_day_state(cod_usuario: str) -> dict:
    cod_usuario_norm = (cod_usuario or "").strip().lower()

    if not cod_usuario_norm:
        return {
            "status": "error",
            "data": {
                "message": "cod_usuario es obligatorio."
            }
        }

    conn = get_connection()
    try:
        cursor = conn.cursor()

        _ensure_today_assignment(cursor)

        cursor.execute("""
        SET NOCOUNT ON;

        SELECT TOP (1)
            C.PK_DEMO_B,
            C.TD_DEMO_A,
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
        """)

        row_day = cursor.fetchone()

        if row_day is None:
            return {
                "status": "no_data",
                "data": {
                    "message": "No existe asignacion diaria activa."
                }
            }

        pk_cuaderno = int(row_day.PK_DEMO_B)
        td_referencia = str(row_day.TD_DEMO_A)
        val_longitud = int(row_day.VAL_DEMO_A)
        val_max_intentos = int(row_day.MAX_INTENTOS) if row_day.MAX_INTENTOS is not None else 6

        cursor.execute("""
        SET NOCOUNT ON;

        SELECT TOP (1)
            B.PK_DEMO_C,
            B.COD_DEMO_C,
            B.DES_DEMO_A,
            B.FLG_DEMO_C,
            B.FLG_DEMO_D,
            B.VAL_DEMO_B,
            B.VAL_DEMO_C,
            B.VAL_DEMO_D,
            B.TS_DEMO_A,
            B.TS_DEMO_B
        FROM dbo.T_DEMO_F_01 B
        WHERE B.TD_DEMO_A = CAST(GETDATE() AS DATE)
          AND B.COD_DEMO_C = ?;
        """, cod_usuario_norm)

        row_bitacora = cursor.fetchone()

        if row_bitacora is None:
            return {
                "status": "ok",
                "data": {
                    "pk_cuaderno": pk_cuaderno,
                    "td_referencia": td_referencia,
                    "cod_usuario": cod_usuario_norm,
                    "flg_existe_bitacora": False,
                    "flg_resuelto": False,
                    "flg_cerrado": False,
                    "val_longitud": val_longitud,
                    "val_max_intentos": val_max_intentos,
                    "val_intento_total": 0,
                    "val_puntos": 0,
                    "trazas": []
                }
            }

        pk_bitacora = int(row_bitacora.PK_DEMO_C)

        cursor.execute("""
        SET NOCOUNT ON;

        SELECT
            T.PK_DEMO_D,
            T.VAL_DEMO_E,
            T.COD_DEMO_B,
            T.TXT_DEMO_A,
            T.FLG_DEMO_E,
            T.FLG_DEMO_F,
            T.TS_DEMO_C
        FROM dbo.T_DEMO_F_02 T
        WHERE T.FK_DEMO_B = ?
        ORDER BY T.VAL_DEMO_E ASC, T.PK_DEMO_D ASC;
        """, pk_bitacora)

        rows_traza = cursor.fetchall()

        trazas = []
        for row in rows_traza:
            trazas.append({
                "pk_traza": int(row.PK_DEMO_D),
                "val_orden": int(row.VAL_DEMO_E),
                "cod_termino": str(row.COD_DEMO_B),
                "txt_patron": str(row.TXT_DEMO_A),
                "detalle": list(str(row.TXT_DEMO_A)),
                "flg_valido": bool(row.FLG_DEMO_E),
                "flg_acierto": bool(row.FLG_DEMO_F),
                "ts_intento_utc": str(row.TS_DEMO_C)
            })

        return {
            "status": "ok",
            "data": {
                "pk_cuaderno": pk_cuaderno,
                "pk_bitacora": pk_bitacora,
                "td_referencia": td_referencia,
                "cod_usuario": str(row_bitacora.COD_DEMO_C),
                "des_usuario": row_bitacora.DES_DEMO_A,
                "flg_existe_bitacora": True,
                "flg_resuelto": bool(row_bitacora.FLG_DEMO_C),
                "flg_cerrado": bool(row_bitacora.FLG_DEMO_D),
                "val_intento_ok": int(row_bitacora.VAL_DEMO_B) if row_bitacora.VAL_DEMO_B is not None else None,
                "val_intento_total": int(row_bitacora.VAL_DEMO_C),
                "val_puntos": int(row_bitacora.VAL_DEMO_D),
                "val_longitud": val_longitud,
                "val_max_intentos": val_max_intentos,
                "ts_inicio_utc": str(row_bitacora.TS_DEMO_A),
                "ts_fin_utc": str(row_bitacora.TS_DEMO_B) if row_bitacora.TS_DEMO_B is not None else None,
                "trazas": trazas
            }
        }
    finally:
        conn.close()


from __future__ import annotations

from app.db.connection import get_connection


def get_day_state() -> dict:
    query = """
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
    """

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()

        if row is None:
            return {
                "status": "no_data",
                "message": "No existe asignación diaria activa."
            }

        return {
            "status": "ok",
            "data": {
                "pk_cuaderno": int(row.PK_DEMO_B),
                "td_referencia": str(row.TD_DEMO_A),
                "val_longitud": int(row.VAL_DEMO_A),
                "val_max_intentos": int(row.MAX_INTENTOS) if row.MAX_INTENTOS is not None else 6
            }
        }
    finally:
        conn.close()


from __future__ import annotations

from app.db.connection import get_connection


def get_debug_target() -> dict:
    query = """
    SET NOCOUNT ON;

    SELECT TOP (1)
        C.PK_DEMO_B,
        C.TD_DEMO_A,
        M.PK_DEMO_A,
        M.COD_DEMO_A,
        M.COD_DEMO_B,
        M.VAL_DEMO_A
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
                "data": {
                    "message": "No existe asignacion diaria activa."
                }
            }

        return {
            "status": "ok",
            "data": {
                "pk_cuaderno": int(row.PK_DEMO_B),
                "td_referencia": str(row.TD_DEMO_A),
                "pk_malla": int(row.PK_DEMO_A),
                "cod_termino": str(row.COD_DEMO_B),
                "val_longitud": int(row.VAL_DEMO_A)
            }
        }
    finally:
        conn.close()


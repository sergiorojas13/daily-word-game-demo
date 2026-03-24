from __future__ import annotations

from app.db.connection import get_connection


def validate_term(cod_termino: str) -> dict:
    cod_termino_norm = (cod_termino or "").strip().lower()

    query = """
    SET NOCOUNT ON;

    SELECT TOP (1)
        M.PK_DEMO_A,
        M.COD_DEMO_A,
        M.COD_DEMO_B,
        M.VAL_DEMO_A,
        M.FLG_DEMO_B,
        M.FLG_DEMO_A
    FROM dbo.T_DEMO_A_01 M
    WHERE M.COD_DEMO_B = ?
      AND M.FLG_DEMO_B = 1
      AND M.VAL_DEMO_A = 5;
    """

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, cod_termino_norm)
        row = cursor.fetchone()

        if row is None:
            return {
                "status": "ok",
                "data": {
                    "cod_termino": cod_termino_norm,
                    "flg_valido": False,
                    "val_longitud": len(cod_termino_norm),
                    "message": "El término no pertenece al catálogo activo."
                }
            }

        return {
            "status": "ok",
            "data": {
                "pk_malla": int(row.PK_DEMO_A),
                "cod_termino": str(row.COD_DEMO_B),
                "flg_valido": True,
                "val_longitud": int(row.VAL_DEMO_A),
                "flg_elegible": bool(row.FLG_DEMO_A)
            }
        }
    finally:
        conn.close()


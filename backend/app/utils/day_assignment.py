from __future__ import annotations


def ensure_today_assignment(cursor) -> None:
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


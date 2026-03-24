SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
SET NOCOUNT ON;

BEGIN TRY
    BEGIN TRAN;

    DECLARE @TD_DEMO_A DATE = CAST(GETDATE() AS DATE);

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.T_DEMO_A_02
        WHERE TD_DEMO_A = @TD_DEMO_A
    )
    BEGIN
        DECLARE @VAL_TOTAL_ELEGIBLE INT;
        DECLARE @VAL_OFFSET INT;
        DECLARE @FK_DEMO_A BIGINT;

        SELECT
            @VAL_TOTAL_ELEGIBLE = COUNT(1)
        FROM dbo.T_DEMO_A_01
        WHERE FLG_DEMO_B = 1
          AND FLG_DEMO_A = 1
          AND VAL_DEMO_A = 5;

        IF ISNULL(@VAL_TOTAL_ELEGIBLE, 0) = 0
        BEGIN
            THROW 50010, 'No existen términos elegibles para asignación diaria.', 1;
        END;

        SET @VAL_OFFSET =
            ABS(CHECKSUM(CONVERT(NVARCHAR(10), @TD_DEMO_A, 120))) % @VAL_TOTAL_ELEGIBLE;

        ;WITH BASE AS (
            SELECT
                PK_DEMO_A,
                ROW_NUMBER() OVER (ORDER BY COD_DEMO_B ASC, PK_DEMO_A ASC) - 1 AS RN
            FROM dbo.T_DEMO_A_01
            WHERE FLG_DEMO_B = 1
              AND FLG_DEMO_A = 1
              AND VAL_DEMO_A = 5
        )
        SELECT
            @FK_DEMO_A = PK_DEMO_A
        FROM BASE
        WHERE RN = @VAL_OFFSET;

        IF @FK_DEMO_A IS NULL
        BEGIN
            THROW 50011, 'No se pudo resolver FK_DEMO_A para la fecha indicada.', 1;
        END;

        INSERT INTO dbo.T_DEMO_A_02
        (
            TD_DEMO_A,
            FK_DEMO_A,
            FLG_DEMO_B
        )
        VALUES
        (
            @TD_DEMO_A,
            @FK_DEMO_A,
            1
        );
    END;

    COMMIT TRAN;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRAN;

    DECLARE @TXT_ERROR NVARCHAR(4000) = ERROR_MESSAGE();
    THROW 50012, @TXT_ERROR, 1;
END CATCH;


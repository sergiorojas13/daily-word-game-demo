SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
SET NOCOUNT ON;

BEGIN TRY
    BEGIN TRAN;

    DELETE FROM dbo.T_DEMO_F_02;
    DELETE FROM dbo.T_DEMO_F_01;
    DELETE FROM dbo.T_DEMO_A_02;
    DELETE FROM dbo.T_DEMO_A_01;

    ;WITH SRC AS (
        SELECT N'cauce' AS COD_DEMO_A UNION ALL
        SELECT N'trama' UNION ALL
        SELECT N'mueca' UNION ALL
        SELECT N'brisa' UNION ALL
        SELECT N'gesto' UNION ALL
        SELECT N'linde' UNION ALL
        SELECT N'pulso' UNION ALL
        SELECT N'cieno' UNION ALL
        SELECT N'tenue' UNION ALL
        SELECT N'gruta' UNION ALL
        SELECT N'astil' UNION ALL
        SELECT N'vigor' UNION ALL
        SELECT N'cabal' UNION ALL
        SELECT N'gozne' UNION ALL
        SELECT N'savia' UNION ALL
        SELECT N'clavo' UNION ALL
        SELECT N'plazo' UNION ALL
        SELECT N'cifra' UNION ALL
        SELECT N'rasgo' UNION ALL
        SELECT N'friso' UNION ALL
        SELECT N'breve' UNION ALL
        SELECT N'trazo' UNION ALL
        SELECT N'cerco' UNION ALL
        SELECT N'brote' UNION ALL
        SELECT N'censo' UNION ALL
        SELECT N'faena' UNION ALL
        SELECT N'junta' UNION ALL
        SELECT N'lasca' UNION ALL
        SELECT N'marca' UNION ALL
        SELECT N'prado' UNION ALL
        SELECT N'recia' UNION ALL
        SELECT N'sonda' UNION ALL
        SELECT N'tapia' UNION ALL
        SELECT N'verja' UNION ALL
        SELECT N'zanja' UNION ALL
        SELECT N'arduo' UNION ALL
        SELECT N'blusa' UNION ALL
        SELECT N'curva' UNION ALL
        SELECT N'denso'
    ),
    SRC_NORM AS (
        SELECT DISTINCT
            LOWER(LTRIM(RTRIM(COD_DEMO_A))) AS COD_DEMO_A,
            LEN(LOWER(LTRIM(RTRIM(COD_DEMO_A)))) AS VAL_DEMO_A
        FROM SRC
    )
    INSERT INTO dbo.T_DEMO_A_01
    (
        COD_DEMO_A,
        COD_DEMO_B,
        FLG_DEMO_A,
        FLG_DEMO_B,
        VAL_DEMO_A
    )
    SELECT
        COD_DEMO_A,
        COD_DEMO_A,
        1,
        1,
        VAL_DEMO_A
    FROM SRC_NORM
    WHERE VAL_DEMO_A = 5;

    COMMIT TRAN;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRAN;

    DECLARE @TXT_ERROR NVARCHAR(4000) = ERROR_MESSAGE();
    THROW 50003, @TXT_ERROR, 1;
END CATCH;


param(
    [Parameter(Mandatory = $true)]
    [string]$ServidorSql,

    [Parameter(Mandatory = $true)]
    [string]$BaseDatos,

    [Parameter(Mandatory = $false)]
    [string]$UsuarioSql,

    [Parameter(Mandatory = $false)]
    [string]$PasswordSql,

    [Parameter(Mandatory = $false)]
    [switch]$UsarAuthIntegrada
)

$ErrorActionPreference = 'Stop'

function Get-SqlCmdPath {
    $Candidatos = @(
        'sqlcmd.exe',
        'C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\170\Tools\Binn\sqlcmd.exe',
        'C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\180\Tools\Binn\sqlcmd.exe',
        'C:\Program Files\Microsoft SQL Server\150\Tools\Binn\sqlcmd.exe',
        'C:\Program Files\Microsoft SQL Server\160\Tools\Binn\sqlcmd.exe'
    )

    foreach ($Ruta in $Candidatos) {
        $Cmd = Get-Command $Ruta -ErrorAction SilentlyContinue
        if ($Cmd) {
            return $Cmd.Source
        }
    }

    throw "No se encontró sqlcmd.exe en PATH ni en rutas habituales."
}

$SqlCmd = Get-SqlCmdPath

$Query = @"
SET NOCOUNT ON;

SELECT
    COUNT(1) AS VAL_TOTAL,
    SUM(CASE WHEN FLG_DEMO_B = 1 THEN 1 ELSE 0 END) AS VAL_ACTIVO,
    SUM(CASE WHEN FLG_DEMO_A = 1 THEN 1 ELSE 0 END) AS VAL_ELEGIBLE,
    MIN(VAL_DEMO_A) AS VAL_DEMO_A_MIN,
    MAX(VAL_DEMO_A) AS VAL_DEMO_A_MAX
FROM dbo.T_DEMO_A_01;

SELECT TOP (20)
    PK_DEMO_A,
    COD_DEMO_A,
    COD_DEMO_B,
    FLG_DEMO_A,
    FLG_DEMO_B,
    VAL_DEMO_A,
    TS_DEMO_E
FROM dbo.T_DEMO_A_01
ORDER BY PK_DEMO_A ASC;
"@

$RutaTmp = Join-Path $env:TEMP ('tmp_check_malla_{0}.sql' -f ([guid]::NewGuid().ToString('N')))
Set-Content -LiteralPath $RutaTmp -Value $Query -Encoding UTF8

try {
    $Args = @(
        '-S', $ServidorSql,
        '-d', $BaseDatos,
        '-b',
        '-W',
        '-i', $RutaTmp
    )

    if ($UsarAuthIntegrada.IsPresent) {
        $Args += '-E'
    }
    else {
        if ([string]::IsNullOrWhiteSpace($UsuarioSql)) {
            throw "Debe informar -UsuarioSql o usar -UsarAuthIntegrada."
        }

        if ([string]::IsNullOrWhiteSpace($PasswordSql)) {
            throw "Debe informar -PasswordSql o usar -UsarAuthIntegrada."
        }

        $Args += @('-U', $UsuarioSql, '-P', $PasswordSql)
    }

    & $SqlCmd @Args

    if ($LASTEXITCODE -ne 0) {
        throw "sqlcmd devolvió código de salida $LASTEXITCODE"
    }
}
finally {
    if (Test-Path -LiteralPath $RutaTmp) {
        Remove-Item -LiteralPath $RutaTmp -Force -ErrorAction SilentlyContinue
    }
}


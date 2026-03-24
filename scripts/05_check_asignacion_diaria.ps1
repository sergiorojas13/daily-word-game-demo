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
    C.PK_DEMO_B,
    C.TD_DEMO_A,
    C.FK_DEMO_A,
    M.COD_DEMO_A,
    M.COD_DEMO_B,
    M.VAL_DEMO_A,
    C.FLG_DEMO_B,
    C.TS_DEMO_D,
    C.TS_DEMO_E
FROM dbo.T_DEMO_A_02 C
INNER JOIN dbo.T_DEMO_A_01 M
    ON M.PK_DEMO_A = C.FK_DEMO_A
ORDER BY C.TD_DEMO_A DESC, C.PK_DEMO_B DESC;
"@

$RutaTmp = Join-Path $env:TEMP ('tmp_check_asignacion_{0}.sql' -f ([guid]::NewGuid().ToString('N')))
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


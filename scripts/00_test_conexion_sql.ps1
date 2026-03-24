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
    @@SERVERNAME       AS DES_SERVIDOR,
    DB_NAME()          AS DES_BASE_DATOS,
    SYSTEM_USER        AS DES_DEMO_A_EJECUCION,
    SYSDATETIME()      AS TS_EJECUCION;
"@

$RutaTmp = Join-Path $env:TEMP ('tmp_sql_ping_{0}.sql' -f ([guid]::NewGuid().ToString('N')))
Set-Content -LiteralPath $RutaTmp -Value $Query -Encoding UTF8

try {
    $Args = @(
        '-S', $ServidorSql,
        '-d', $BaseDatos,
        '-b',
        '-W',
        '-s', '|',
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

    Write-Host ''
    Write-Host 'Probando conexión SQL...' -ForegroundColor Yellow
    Write-Host "Servidor : $ServidorSql"
    Write-Host "Base     : $BaseDatos"
    Write-Host ''

    & $SqlCmd @Args

    if ($LASTEXITCODE -ne 0) {
        throw "sqlcmd devolvió código de salida $LASTEXITCODE"
    }

    Write-Host ''
    Write-Host 'OK. Conexión validada correctamente.' -ForegroundColor Green
}
finally {
    if (Test-Path -LiteralPath $RutaTmp) {
        Remove-Item -LiteralPath $RutaTmp -Force -ErrorAction SilentlyContinue
    }
}


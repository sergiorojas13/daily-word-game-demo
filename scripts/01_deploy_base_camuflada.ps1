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

function Write-Log {
    param(
        [string]$Mensaje,
        [string]$Nivel = 'INFO'
    )

    $TS = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    $LINEA = "[$TS] [$Nivel] $Mensaje"
    Write-Host $LINEA
    Add-Content -LiteralPath $script:RutaLog -Value $LINEA -Encoding UTF8
}

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

$RootProyecto = 'R:\Ejecutable\APP Marcos teoricos\portal_juegos'
$RutaSql       = Join-Path $RootProyecto 'sql\01_base_camuflada_portal_juegos.sql'
$RutaLogs      = Join-Path $RootProyecto 'logs'
$RutaRunLogs   = Join-Path $RutaLogs 'deploy_sql'
$TsRun         = Get-Date -Format 'yyyyMMdd_HHmmss'
$script:RutaLog = Join-Path $RutaRunLogs ("deploy_base_camuflada_{0}.log" -f $TsRun)

if (-not (Test-Path -LiteralPath $RutaRunLogs)) {
    New-Item -ItemType Directory -Path $RutaRunLogs -Force | Out-Null
}

Write-Log "Inicio despliegue base camuflada."
Write-Log "Servidor SQL: $ServidorSql"
Write-Log "Base de datos: $BaseDatos"
Write-Log "Ruta SQL: $RutaSql"

if (-not (Test-Path -LiteralPath $RutaSql)) {
    throw "No existe el fichero SQL esperado: $RutaSql"
}

$SqlCmd = Get-SqlCmdPath
Write-Log "sqlcmd localizado en: $SqlCmd"

$Args = @(
    '-S', $ServidorSql,
    '-d', $BaseDatos,
    '-b',
    '-i', $RutaSql
)

if ($UsarAuthIntegrada.IsPresent) {
    Write-Log "Modo autenticación: integrada"
    $Args += '-E'
}
else {
    if ([string]::IsNullOrWhiteSpace($UsuarioSql)) {
        throw "Debe informar -UsuarioSql o usar -UsarAuthIntegrada."
    }

    if ([string]::IsNullOrWhiteSpace($PasswordSql)) {
        throw "Debe informar -PasswordSql o usar -UsarAuthIntegrada."
    }

    Write-Log "Modo autenticación: SQL"
    $Args += @('-U', $UsuarioSql, '-P', $PasswordSql)
}

Write-Log "Ejecutando script SQL..."
& $SqlCmd @Args 2>&1 | ForEach-Object {
    $Linea = $_.ToString()
    Write-Host $Linea
    Add-Content -LiteralPath $script:RutaLog -Value $Linea -Encoding UTF8
}

if ($LASTEXITCODE -ne 0) {
    throw "sqlcmd devolvió código de salida $LASTEXITCODE"
}

Write-Log "Despliegue completado correctamente."
Write-Host ""
Write-Host "OK. Script ejecutado correctamente." -ForegroundColor Green
Write-Host "Log:" -ForegroundColor Yellow
Write-Host $script:RutaLog -ForegroundColor Cyan


param(
    [ValidateSet('Start', 'Fast', 'Bots', 'Check')]
    [string]$Action = 'Start'
)
$ErrorActionPreference = 'Stop'
$sandboxRoot = $PSScriptRoot
$pythonPath = Join-Path $sandboxRoot '.venv\Scripts\python.exe'
$otreePath = Join-Path $sandboxRoot '.venv\Scripts\otree.exe'
if (!(Test-Path -LiteralPath $otreePath)) {
    throw 'The local environment is missing. See SANDBOX_README.md.'
}
# Never inherit a live database, cache or production configuration.
$environmentNames = @('DATABASE_URL', 'REDIS_URL', 'OTREE_PRODUCTION',
    'OTREE_SECRET_KEY', 'SECRET_KEY', 'OTREE_ADMIN_PASSWORD', 'OTREE_AUTH_LEVEL',
    'OTREE_IN_MEMORY', 'OTREE_SESSION_CONFIGS', 'SANDBOX_FAST_TEST')
$savedEnvironment = @{}
foreach ($name in $environmentNames) {
    $savedEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
    [Environment]::SetEnvironmentVariable($name, $null, 'Process')
}
$previousLocation = Get-Location
$previousPath = $env:PATH
try {
    $env:PATH = (Join-Path $sandboxRoot '.venv\Scripts') + ';' + $previousPath
    $env:OTREE_SECRET_KEY = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
    $env:OTREE_ADMIN_PASSWORD = [Guid]::NewGuid().ToString('N')
    $env:OTREE_AUTH_LEVEL = 'DEMO'
    $runtimeRoot = Join-Path $sandboxRoot '.sandbox-runtime'
    # The checked-task fields require a fresh schema. Preserve all older test runs.
    $runtimeRevision = 'checked-tasks-v1'
    if ($Action -eq 'Fast') {
        $env:SANDBOX_FAST_TEST = '1'
        $runPath = Join-Path $runtimeRoot ('fast-interactive-' + $runtimeRevision)
    } elseif ($Action -eq 'Start') {
        $runPath = Join-Path $runtimeRoot ('interactive-' + $runtimeRevision)
    } else {
        $runPath = Join-Path $runtimeRoot ($Action.ToLower() + '-' + [Guid]::NewGuid().ToString('N'))
    }
    New-Item -ItemType Directory -Path $runPath -Force | Out-Null
    foreach ($item in @('settings.py', 'sandbox_fast.py', '_static', '_templates', 'instructions_consent', 'study')) {
        $sourcePath = Join-Path $sandboxRoot $item
        $destinationPath = Join-Path $runPath $item
        # Sync the app copy, including file removals, but preserve its local database.
        if (Test-Path -LiteralPath $destinationPath) {
            $resolvedDestination = [IO.Path]::GetFullPath($destinationPath)
            $expectedPrefix = [IO.Path]::GetFullPath($runPath) + [IO.Path]::DirectorySeparatorChar
            if (!$resolvedDestination.StartsWith($expectedPrefix, [StringComparison]::OrdinalIgnoreCase)) {
                throw 'Unsafe runtime destination.'
            }
            Remove-Item -LiteralPath $resolvedDestination -Recurse -Force
        }
        Copy-Item -LiteralPath $sourcePath -Destination $destinationPath -Recurse
    }
    Set-Location -LiteralPath $runPath
    Write-Host "LOCAL SANDBOX ONLY: $runPath"
    if ($Action -eq 'Bots') {
        & $pythonPath -c 'from otree.main import execute_from_command_line; execute_from_command_line()' test study_on_work
    } elseif ($Action -eq 'Check') {
        & $pythonPath -m compileall -q settings.py sandbox_fast.py instructions_consent study
    } else {
        Write-Host 'Open http://localhost:8000/demo . Use synthetic participants only. Ctrl+C stops the server.'
        Write-Host 'The database is local. No payment or recruitment service is configured by this launcher.'
        & $pythonPath -c 'from otree.main import execute_from_command_line; execute_from_command_line()' devserver 8000
    }
    if ($LASTEXITCODE -ne 0) { throw "Sandbox command failed with exit code $LASTEXITCODE." }
} finally {
    $env:PATH = $previousPath
    Set-Location $previousLocation
    foreach ($name in $environmentNames) {
        [Environment]::SetEnvironmentVariable($name, $savedEnvironment[$name], 'Process')
    }
}

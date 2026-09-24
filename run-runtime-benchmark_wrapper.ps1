# Wrapper around run-runtime-benchmark.ps1: lets you pick a preset by typing a
# number instead of remembering the -Filter/-PlotBenchmarks flags.
#
# Usage:
#   .\run-runtime-benchmark_wrapper.ps1            # interactive numbered menu
#   .\run-runtime-benchmark_wrapper.ps1 -Choice 2  # jump straight to preset 2
#   .\run-runtime-benchmark_wrapper.ps1 -Choice 3 -BaselineRepeats 1 -RerunOutlierRuns 3

param(
    # Preset number (1..N). When omitted (or out of range), an interactive menu is shown.
    [int]$Choice = 0,

    # Extra arguments forwarded verbatim to run-runtime-benchmark.ps1.
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PassThroughArgs
)

$errorActionPreference = "Stop"

$runner = Join-Path $PSScriptRoot "run-runtime-benchmark.ps1"
if (-not (Test-Path $runner)) {
    throw "run-runtime-benchmark.ps1 not found next to wrapper: $runner"
}

# Default reruns for a preset that does NOT declare its own RerunOutlierRuns.
$defaultRerunOutlierRuns = 5

# Preset table: Label -> (-Filter / -PlotBenchmarks / -TestPath / -RerunOutlierRuns sent to the runner).
$manualPresets = @(
    @{ Label = "run all, plot all";     Filter = "";      PlotBenchmarks = "" },
    @{ Label = "run valid, plot all";   Filter = "valid"; PlotBenchmarks = "" }
)

# One preset per test/api_accessible/*.py, so each file can be benchmarked on its own.
$filePresets = @()
$testDir = Join-Path $PSScriptRoot "test\api_accessible"
if (Test-Path $testDir) {
    Get-ChildItem -LiteralPath $testDir -Filter *.py | Sort-Object Name | ForEach-Object {
        $filePresets += @{
            Label    = "run $($_.Name), plot all"
            TestPath = "test/api_accessible/$($_.Name)"
        }
    }
}

$presets = $manualPresets + $filePresets

function Show-Menu {
    Write-Host ""
    Write-Host "=== Runtime benchmark presets ===" -ForegroundColor Cyan
    for ($i = 0; $i -lt $presets.Count; $i++) {
        Write-Host ("  {0}. {1}" -f ($i + 1), $presets[$i].Label)
    }
    Write-Host ""
}

if ($Choice -lt 1 -or $Choice -gt $presets.Count) {
    Show-Menu
    $input = Read-Host "Enter number (1-$($presets.Count))"
    if (-not [int]::TryParse($input, [ref]$Choice) -or $Choice -lt 1 -or $Choice -gt $presets.Count) {
        Write-Error "Invalid choice: '$input'. Must be a number between 1 and $($presets.Count)."
        exit 1
    }
}

$preset = $presets[$Choice - 1]
Write-Host "Selected: $($preset.Label)" -ForegroundColor Green

$reruns = if ($null -ne $preset.RerunOutlierRuns) { $preset.RerunOutlierRuns } else { $defaultRerunOutlierRuns }

# Build a splatting hashtable: named binding is required because array splatting
# against a script's typed param() block is positional (a "-TestPaths <path>" array
# would try to bind the path to the earlier [double] param).
$splat = @{}
if ($preset.Filter) { $splat["Filter"] = $preset.Filter }
if ($preset.TestPath) { $splat["TestPaths"] = $preset.TestPath }
if ($preset.PlotBenchmarks) { $splat["PlotBenchmarks"] = $preset.PlotBenchmarks }
$splat["RerunOutlierRuns"] = $reruns

# Fold passthrough name/value tokens (e.g. -Jobs 1) into the same hashtable.
for ($i = 0; $i -lt $PassThroughArgs.Count; $i++) {
    $tok = $PassThroughArgs[$i]
    if (-not $tok -or -not $tok.StartsWith("-")) { continue }
    $name = $tok.TrimStart("-")
    $value = $null
    if ($i + 1 -lt $PassThroughArgs.Count -and -not $PassThroughArgs[$i + 1].StartsWith("-")) {
        $value = $PassThroughArgs[$i + 1]
        $i++
    }
    if ($null -eq $value) { $splat[$name] = $true } else { $splat[$name] = $value }
}

# Parallelism is never allowed: benchmark runs must be single-worker so the
# per-test timings stay comparable. This overrides any -Jobs passthrough.
$splat["Jobs"] = 0

& $runner @splat
exit $LASTEXITCODE
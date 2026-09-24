# Runtime benchmark: compares per-test runtimes of test/api_accessible between
# origin/main (run in a temporary git worktree) and the current working tree.
#
# Both sides are measured via pytest's JUnit XML duration (--junitxml). To stabilize
# the reference side, the baseline suite runs -BaselineRepeats times (median per test);
# flagged outliers are then re-measured -RerunOutlierRuns times each.
# Tests whose delta exceeds +/-ThresholdPercent are reported as a WARNING; the
# comparison is advisory and never fails the pipeline by default.
#
# A comparison plot (baseline vs current runtimes) is saved into the results folder.
#
# Usage:
#   .\run-runtime-benchmark.ps1 [-ThresholdPercent 25] [-Jobs 1]
#   .\run-runtime-benchmark.ps1 -Filter "add_capacity and valid"
#   .\run-runtime-benchmark.ps1 -Filter "test_valid or test_none" -PytestExtraArgs "--benchmark-autosave"
#   .\run-runtime-benchmark.ps1 -RerunOutlierRuns 3

param(
    # Baseline git ref to compare against.
    [string]$BaselineRef = "origin/main",

    # Relative slowdown (in percent) above which a test is flagged as an outlier
    # (both slower and faster). Used both for the report and, combined with
    # $RerunOutlierRuns, to decide which tests get re-measured.
    [double]$ThresholdPercent = 10,

    # Accepted for backward compatibility only: parallelism is never used for
    # benchmarking (always forced to 0 / no xdist workers).
    [int]$Jobs = 0,

    # Optional pytest -k style expression. When set, ONLY matching tests are run
    # (in both the baseline and the current run) instead of the whole suite.
    [string]$Filter = "",

    # Optional exact test file(s) (paths relative to the repo root, e.g.
    # "test/api_accessible/test_write.py"). Overrides the whole suite and is more
    # precise than -Filter: it selects the file, not a substring (so
    # test_write vs test_write_to_bibtex cannot bleed into each other).
    [string[]]$TestPaths = @(),

    # Optional comma-separated substrings. When set, only these tests are drawn on
    # the comparison plot (the table still covers every test that ran).
    [string]$PlotBenchmarks = "",

    # Optional arbitrary extra pytest arguments, forwarded verbatim to both runs
    # (e.g. "-Filter test_valid -PytestExtraArgs '--benchmark-autosave'").
    [string]$PytestExtraArgs = "",

    # How often the BASELINE suite is executed. Each test's baseline time is the
    # MEDIAN across the repeats (the same median aggregation the rerun pass uses),
    # so the reference side gets a stabler timing. Files are never modified; the
    # suite is simply run repeatedly. 1 (or 0) = single baseline run.
    [int]$BaselineRepeats = 3,

    # Number of extra measurement repetitions for each test flagged as an outlier
    # (delta beyond +/-$ThresholdPercent). 0 disables the rerun pass. Default 7.
    [int]$RerunOutlierRuns = 7
)

$ErrorActionPreference = "Stop"

# Parallelism is never allowed: every run must be single-worker (pytest -n 0) so
# per-test timings stay comparable across baseline/current. The -Jobs param above
# is kept for backward compatibility but always forced back to 0.
$Jobs = 0

# Headless plotting backend: visualize tests otherwise create real Tk windows,
# which makes their runtime noisy, ~4x slower, and intermittently fails Tcl
# initialization on Windows ("Can't find a usable init.tcl").
$env:MPLBACKEND = "Agg"

$repoRoot = $PSScriptRoot
$worktree = [System.IO.Path]::GetFullPath((Join-Path $repoRoot "..\pydpeet-main-bench"))
$resultsDir = Join-Path $repoRoot ("benchmarks\results\" + (Get-Date -Format "yyyy-MM-dd-HH-mm-ss"))
New-Item -ItemType Directory -Force -Path $resultsDir | Out-Null

# Plain single-worker suite runs: no coverage, no reruns, and xdist disabled.
# (Baseline repeats and the outlier rerun pass are layered on top separately.)
$pytestFlags = @(
    "-n", "$Jobs"
)

# Target one or more exact test file(s) when given (precise), else the whole suite.
if ($TestPaths) {
    $pytestFlags += $TestPaths
}
else {
    $pytestFlags += "test/api_accessible"
}

# Target a subset of tests when a filter expression is given (pytest -k).
if ($Filter) {
    $pytestFlags += @("-k", "`"$Filter`"")
}

# Forward any additional user-supplied pytest arguments.
if ($PytestExtraArgs) {
    $pytestFlags += $PytestExtraArgs.Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries)
}

function Invoke-GitRef {
    param([string]$WorkingDirectory)
    Push-Location $WorkingDirectory
    try {
        $branch = git rev-parse --abbrev-ref HEAD
        $hash = git rev-parse --short HEAD
        if ($LASTEXITCODE -ne 0) { return "?" }
        return "$branch@$hash"
    }
    finally {
        Pop-Location
    }
}

function Invoke-BenchmarkRun {
    param([string]$WorkingDirectory, [string]$ReportPath, [string]$RefLabel, [switch]$SkipSync)

    $ref = Invoke-GitRef -WorkingDirectory $WorkingDirectory
    Write-Host ""
    Write-Host "========================================================================" -ForegroundColor Cyan
    Write-Host "  RUN: $RefLabel" -ForegroundColor Cyan
    Write-Host "  git ref : $ref" -ForegroundColor Cyan
    if ($Filter) { Write-Host "  filter  : -k `"$Filter`"" -ForegroundColor Yellow }
    Write-Host "  output  : $ReportPath" -ForegroundColor DarkGray
    Write-Host "========================================================================" -ForegroundColor Cyan
    Write-Host ""

    Push-Location $WorkingDirectory
    try {
        if (-not $SkipSync) {
            uv sync --frozen --group test
            if ($LASTEXITCODE -ne 0) { throw "uv sync failed in $WorkingDirectory" }
        }

        uv run pytest @pytestFlags --junitxml $ReportPath
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "pytest exited with code $LASTEXITCODE - continuing, the comparison will flag outcome changes."
        }
    }
    finally {
        Pop-Location
    }
}

# Read the runtime (seconds) of a single testcase from a JUnit XML report.
# Returns $null if the test is missing/skipped.
function Get-SingleTestDuration {
    param([string]$ReportPath, [string]$Fullname)

    if (-not (Test-Path $ReportPath)) { return $null }
    [xml]$xml = Get-Content -LiteralPath $ReportPath -Raw
    $suite = if ($xml.testsuites) { @($xml.testsuites.testsuite) } else { @($xml.testsuite) }
    foreach ($ts in $suite) {
        foreach ($case in @($ts.testcase)) {
            $fn = if ($case.classname) { "$($case.classname)::$($case.name)" } else { $case.name }
            if ($fn -eq $Fullname) {
                if ($case.skipped) { return $null }
                return [double]$case.time
            }
        }
    }
    return $null
}

# Convert a JUnit fullname (dotted module.class::method) into a pytest node ID.
#   'test.api_accessible.test_add_primitive_segments.Test_..._df::test_valid'
#   -> 'test/api_accessible/test_add_primitive_segments.py::Test_..._df::test_valid'
function ConvertTo-NodeId {
    param([string]$Fullname)

    $parts = $Fullname -split "::"
    $node = $parts[0]
    $method = if ($parts.Length -gt 1) { $parts[1] } else { "" }
    $dot = $node.LastIndexOf(".")
    if ($dot -le 0) {
        $file = ($node -replace "\.", "/") + ".py"
        return "$file::$method"
    }
    $class = $node.Substring($dot + 1)
    $module = $node.Substring(0, $dot)
    $file = ($module -replace "\.", "/") + ".py"
    return "$file::$class::$method"
}

# Run a single test (by fullname) once in a given working directory and return the measured
# duration in seconds. Returns $null if the test did not run (missing/deselected/skipped).
function Invoke-SingleTest {
    param([string]$WorkingDirectory, [string]$Fullname, [string]$ReportPath)

    $nodeId = ConvertTo-NodeId -Fullname $Fullname
    Push-Location $WorkingDirectory
    try {
        uv run pytest $nodeId --junitxml $ReportPath -q | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "rerun of '$Fullname' exited with code $LASTEXITCODE (node id: $nodeId)"
            return $null
        }
    }
    finally {
        Pop-Location
    }
    return Get-SingleTestDuration -ReportPath $ReportPath -Fullname $Fullname
}

# Measure one test $Repetitions times in a working directory and return the median duration.
function Measure-TestRepeatedly {
    param([string]$WorkingDirectory, [string]$Fullname, [int]$Repetitions)

    $times = @()
    for ($i = 1; $i -le $Repetitions; $i++) {
        $tmp = Join-Path $resultsDir ("single_" + [System.IO.Path]::GetRandomFileName() + ".xml")
        $t = Invoke-SingleTest -WorkingDirectory $WorkingDirectory -Fullname $Fullname -ReportPath $tmp
        if (Test-Path $tmp) { Remove-Item $tmp -Force }
        if ($null -ne $t) {
            $times += [double]$t
        }
    }
    if ($times.Count -eq 0) { return $null }
    $sorted = @($times | Sort-Object)
    $mid = [math]::Floor($sorted.Count / 2)
    if ($sorted.Count % 2 -eq 1) { return $sorted[$mid] }
    return ($sorted[$mid - 1] + $sorted[$mid]) / 2.0
}

# Merge several JUnit reports of the same suite into one, taking the MEDIAN runtime
# per testfullname (the same median the rerun pass' Measure-TestRepeatedly uses).
# Times are written with the invariant culture (a "," decimal separator would break
# the double / float parsers downstream).
function Merge-JUnitMedian {
    param([string[]]$Reports, [string]$OutPath)

    $nums = @{}
    $meta = @{}
    foreach ($r in $Reports) {
        if (-not (Test-Path -LiteralPath $r)) { continue }
        [xml]$xml = Get-Content -LiteralPath $r -Raw
        $suite = if ($xml.testsuites) { @($xml.testsuites.testsuite) } else { @($xml.testsuite) }
        foreach ($ts in $suite) {
            foreach ($case in @($ts.testcase)) {
                $fn = if ($case.classname) { "$($case.classname)::$($case.name)" } else { $case.name }
                if ($null -eq $case.time) { continue }
                if (-not $nums.ContainsKey($fn)) {
                    $nums[$fn] = @()
                    $meta[$fn] = @{ Class = [string]$case.classname; Name = [string]$case.name }
                }
                $t = 0.0
                if ([double]::TryParse($case.time,
                        [System.Globalization.NumberStyles]::Float,
                        [System.Globalization.CultureInfo]::InvariantCulture, [ref]$t)) {
                    $nums[$fn] += $t
                }
            }
        }
    }

    $inv = [System.Globalization.CultureInfo]::InvariantCulture
    $doc = New-Object System.Xml.XmlDocument
    $doc.AppendChild($doc.CreateXmlDeclaration("1.0", "utf-8", $null)) | Out-Null
    $root = $doc.CreateElement("testsuites")
    $doc.AppendChild($root) | Out-Null
    $suiteEl = $doc.CreateElement("testsuite")
    $root.AppendChild($suiteEl) | Out-Null
    foreach ($fn in $nums.Keys) {
        $values = @($nums[$fn] | Sort-Object)
        $mid = [math]::Floor($values.Count / 2)
        $median = if ($values.Count % 2 -eq 1) { $values[$mid] } else { ($values[$mid - 1] + $values[$mid]) / 2.0 }
        $case = $suiteEl.AppendChild($doc.CreateElement("testcase"))
        $case.SetAttribute("classname", [string]$meta[$fn].Class)
        $case.SetAttribute("name", [string]$meta[$fn].Name)
        $case.SetAttribute("time", $median.ToString("F6", $inv))
    }
    $doc.Save($OutPath)
}

$currentRef = Invoke-GitRef -WorkingDirectory $repoRoot
Write-Host "=== Runtime benchmark: '$BaselineRef' (x$BaselineRepeats baseline) vs current tree ($currentRef) ===" -ForegroundColor Cyan
if ($Filter) {
    Write-Host "Filter (-k): '$Filter'" -ForegroundColor Yellow
}

# -------------------------------
# 1. Baseline run(s) (main branch in an isolated worktree): the suite is executed
#    $BaselineRepeats times and each test's baseline time is the median across the
#    repeats (same median logic as the rerun pass). No files are modified.
# -------------------------------
git fetch origin main
if ($LASTEXITCODE -ne 0) { throw "git fetch failed" }

if (Test-Path $worktree) {
    git worktree remove $worktree --force
}
git worktree add $worktree $BaselineRef
if ($LASTEXITCODE -ne 0) { throw "git worktree add failed" }
$baselineRef = Invoke-GitRef -WorkingDirectory $worktree

$baselineReport = Join-Path $resultsDir "report_main.xml"
if ($BaselineRepeats -le 1) {
    Invoke-BenchmarkRun -WorkingDirectory $worktree -ReportPath $baselineReport -RefLabel "BASELINE ($BaselineRef)"
}
else {
    $baselineXmls = @()
    for ($r = 1; $r -le $BaselineRepeats; $r++) {
        $rp = Join-Path $resultsDir ("report_main_{0}.xml" -f $r)
        $baselineXmls += $rp
        $label = "BASELINE run $r/$BaselineRepeats ($BaselineRef)"
        Invoke-BenchmarkRun -WorkingDirectory $worktree -ReportPath $rp -RefLabel $label -SkipSync:($r -gt 1)
    }
    Merge-JUnitMedian -Reports $baselineXmls -OutPath $baselineReport
    foreach ($rp in $baselineXmls) { Remove-Item $rp -Force -ErrorAction SilentlyContinue }
    Write-Host "Baseline: merged $($baselineXmls.Count) runs into median report $baselineReport" -ForegroundColor DarkYellow
}

# -------------------------------
# 2. Current branch run
# -------------------------------
Invoke-BenchmarkRun -WorkingDirectory $repoRoot -ReportPath (Join-Path $resultsDir "report_current.xml") -RefLabel "CURRENT (working tree)"

# -------------------------------
# 3. Comparison (advisory) + plot
# -------------------------------
$outlierJson = Join-Path $resultsDir "outliers.json"
$refinedJson = Join-Path $resultsDir "refined.json"

function Invoke-Comparison {
    param([string[]]$ExtraArgs)

    $allArgs = @(
        (Join-Path $resultsDir "report_main.xml"),
        (Join-Path $resultsDir "report_current.xml"),
        "--threshold", "$ThresholdPercent",
        "--baseline-label", "`"$baselineRef`"",
        "--current-label", "`"$currentRef`""
    )
    if ($ExtraArgs) { $allArgs += $ExtraArgs }
    if ($Filter) { $allArgs += @("--filter", "`"$Filter`"") }
    if ($TestPaths) {
        foreach ($p in $TestPaths) {
            $allArgs += @("--file", "`"$([System.IO.Path]::GetFileName($p))`"")
        }
    }
    if ($PlotBenchmarks) { $allArgs += @("--plot-benchmarks", "`"$PlotBenchmarks`"") }
    uv run python benchmarks\compare_runtime.py @allArgs
}

# First pass: identify outliers without plotting yet (so the pre-rerun plot isn't saved).
Invoke-Comparison -ExtraArgs @("--out-json", "`"$outlierJson`"")

# -------------------------------
# 3b. Re-measure outlier tests if requested (RerunOutlierRuns > 0)
# -------------------------------
$refined = @{}
if ($RerunOutlierRuns -gt 0 -and (Test-Path $outlierJson)) {
    $outliers = (Get-Content -LiteralPath $outlierJson -Raw | ConvertFrom-Json).outliers
    if ($outliers -and $outliers.Count -gt 0) {
        Write-Host ""
        Write-Host "=== Re-measuring $($outliers.Count) outlier test(s) $RerunOutlierRuns x... ===" -ForegroundColor Magenta
        foreach ($test in $outliers) {
            $b = Measure-TestRepeatedly -WorkingDirectory $worktree -Fullname $test -Repetitions $RerunOutlierRuns
            $c = Measure-TestRepeatedly -WorkingDirectory $repoRoot -Fullname $test -Repetitions $RerunOutlierRuns
            if ($null -ne $b -and $null -ne $c) {
                $refined[$test] = @{ baseline = $b; current = $c }
                Write-Host "  $test -> baseline=$([math]::Round($b,4))s current=$([math]::Round($c,4))s" -ForegroundColor DarkCyan
            }
            else {
                Write-Warning "Could not re-measure '$test' (missing in one of the runs); keeping original timing."
            }
        }
        $json = $refined | ConvertTo-Json -Depth 3
        # Write UTF-8 without BOM (Set-Content -Encoding utf8 adds a BOM in Windows PowerShell 5.1,
        # which breaks Python's json.load).
        [System.IO.File]::WriteAllText($refinedJson, $json, (New-Object System.Text.UTF8Encoding $false))
    }
}

# -------------------------------
# Final comparison + plot (uses refined timings when available)
# -------------------------------
$finalArgs = @("--plots", "`"$resultsDir`"")
if ((Test-Path $refinedJson)) {
    $finalArgs += @("--refined", "`"$refinedJson`"")
}
Invoke-Comparison -ExtraArgs $finalArgs

# -------------------------------
# Cleanup
# -------------------------------
git worktree remove $worktree --force
Write-Host "Results stored in: $resultsDir" -ForegroundColor Cyan

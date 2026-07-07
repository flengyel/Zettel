<#
Generate the Zettelkasten software-inventory page, copy it into the Wiki
repository, commit the Wiki change when needed, and push the Wiki repository.

Run from the main repository root:

  .\scripts\publish-software-inventory.cmd

Preview the Wiki diff without committing or pushing:

  .\scripts\publish-software-inventory.cmd -DiffOnly
#>

[CmdletBinding()]
param(
    [string]$Python = "python",
    [string]$WikiDir = "..\Zettel.wiki",
    [string]$WikiCommitMessage = "Update software inventory page",
    [switch]$DiffOnly,
    [switch]$NoPush
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$PageFile = "Zettelkasten-software-inventory.md"

function Invoke-External {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [int[]]$AllowedExitCodes = @(0)
    )

    & $FilePath @Arguments
    $exitCode = $LASTEXITCODE
    if ($AllowedExitCodes -notcontains $exitCode) {
        throw "$FilePath $($Arguments -join ' ') failed with exit code $exitCode"
    }
    return $exitCode
}

function Resolve-PathFromRoot {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$PathText
    )

    if ([System.IO.Path]::IsPathRooted($PathText)) {
        return (Resolve-Path -LiteralPath $PathText).Path
    }

    return (Resolve-Path -LiteralPath (Join-Path $RepoRoot $PathText)).Path
}


function Get-InventorySnapshot {
    param(
        [Parameter(Mandatory = $true)][string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    $bytes = [System.IO.File]::ReadAllBytes($Path)
    $utf8 = [System.Text.UTF8Encoding]::new($false, $false)
    $text = $utf8.GetString($bytes)

    return [PSCustomObject]@{
        Bytes = $bytes
        Text = $text
    }
}

function ConvertTo-ComparableInventoryText {
    param(
        [AllowNull()][string]$Text
    )

    if ($null -eq $Text) {
        return $null
    }

    return ($Text -replace "`r`n", "`n") -replace "`r", "`n"
}

function Test-OnlyInventoryTimestampChanged {
    param(
        [AllowNull()][string]$BeforeText,
        [AllowNull()][string]$AfterText
    )

    if ($null -eq $BeforeText -or $null -eq $AfterText) {
        return $false
    }

    if ($BeforeText -eq $AfterText) {
        return $false
    }

    $beforeComparable = ConvertTo-ComparableInventoryText -Text $BeforeText
    $afterComparable = ConvertTo-ComparableInventoryText -Text $AfterText
    $beforeLines = $beforeComparable.Split([string[]]@("`n"), [System.StringSplitOptions]::None)
    $afterLines = $afterComparable.Split([string[]]@("`n"), [System.StringSplitOptions]::None)

    if ($beforeLines.Count -ne $afterLines.Count) {
        return $false
    }

    $differenceCount = 0

    for ($index = 0; $index -lt $beforeLines.Count; $index++) {
        if ($beforeLines[$index] -eq $afterLines[$index]) {
            continue
        }

        if (($beforeLines[$index] -match "^Last checked: .+$") -and ($afterLines[$index] -match "^Last checked: .+$")) {
            $differenceCount++
            continue
        }

        return $false
    }

    return $differenceCount -eq 1
}

function Restore-InventoryFromSnapshotIfOnlyTimestampChanged {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [AllowNull()]$BeforeSnapshot,
        [Parameter(Mandatory = $true)][string]$Label
    )

    if ($null -eq $BeforeSnapshot) {
        return $false
    }

    $afterSnapshot = Get-InventorySnapshot -Path $Path
    if ($null -eq $afterSnapshot) {
        return $false
    }

    if (Test-OnlyInventoryTimestampChanged -BeforeText $BeforeSnapshot.Text -AfterText $afterSnapshot.Text) {
        [System.IO.File]::WriteAllBytes($Path, [byte[]]$BeforeSnapshot.Bytes)
        Write-Host "Retained existing $Label because generation changed only the Last checked timestamp."
        return $true
    }

    return $false
}

$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$WikiPath = Resolve-PathFromRoot -RepoRoot $RepoRoot -PathText $WikiDir

$Manifest = Join-Path $RepoRoot "MANIFEST.software.yaml"
$Generator = Join-Path $RepoRoot "python\gen_software_components.py"
$GeneratedRelative = Join-Path "generated" $PageFile
$GeneratedPage = Join-Path $RepoRoot $GeneratedRelative
$WikiPage = Join-Path $WikiPath $PageFile

if (-not (Test-Path -LiteralPath $Manifest -PathType Leaf)) {
    throw "Missing manifest: $Manifest"
}

if (-not (Test-Path -LiteralPath $Generator -PathType Leaf)) {
    throw "Missing generator: $Generator"
}

Invoke-External -FilePath "git" -Arguments @("-C", $RepoRoot, "rev-parse", "--is-inside-work-tree") | Out-Null
Invoke-External -FilePath "git" -Arguments @("-C", $WikiPath, "rev-parse", "--is-inside-work-tree") | Out-Null

$GeneratedBefore = Get-InventorySnapshot -Path $GeneratedPage
$WikiBefore = Get-InventorySnapshot -Path $WikiPage

Push-Location $RepoRoot
try {
    Invoke-External -FilePath $Python -Arguments @($Generator, "--manifest", "MANIFEST.software.yaml", "--repo", $RepoRoot, "--out", $GeneratedRelative) | Out-Null
}
finally {
    Pop-Location
}

Restore-InventoryFromSnapshotIfOnlyTimestampChanged -Path $GeneratedPage -BeforeSnapshot $GeneratedBefore -Label "generated software inventory" | Out-Null

Copy-Item -LiteralPath $GeneratedPage -Destination $WikiPage -Force
Write-Host "Copied $GeneratedPage -> $WikiPage"

Restore-InventoryFromSnapshotIfOnlyTimestampChanged -Path $WikiPage -BeforeSnapshot $WikiBefore -Label "Wiki software inventory" | Out-Null

& git -C $WikiPath diff -- $PageFile
if ($LASTEXITCODE -ne 0) {
    throw "git diff failed with exit code $LASTEXITCODE"
}

if ($DiffOnly) {
    exit 0
}

Invoke-External -FilePath "git" -Arguments @("-C", $WikiPath, "add", "--", $PageFile) | Out-Null
$diffExit = Invoke-External -FilePath "git" -Arguments @("-C", $WikiPath, "diff", "--cached", "--quiet", "--", $PageFile) -AllowedExitCodes @(0, 1)

if ($diffExit -eq 0) {
    Write-Host "No Wiki changes to commit."
    exit 0
}

Invoke-External -FilePath "git" -Arguments @("-C", $WikiPath, "commit", "-m", $WikiCommitMessage, "--", $PageFile) | Out-Null

if (-not $NoPush) {
    Invoke-External -FilePath "git" -Arguments @("-C", $WikiPath, "push") | Out-Null
}

# Git Backup Script - Create checkpoints at key milestones
# Run this script at important points during the project

param(
    [Parameter(Mandatory=$true)]
    [string]$CheckpointName,
    
    [string]$Message = ""
)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Git Checkpoint: $CheckpointName" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in a git repo
if (-not (Test-Path ".git")) {
    Write-Host "Error: Not a git repository" -ForegroundColor Red
    exit 1
}

# Show current status
Write-Host "Current status:" -ForegroundColor Yellow
git status --short

Write-Host ""
Write-Host "Files to commit:" -ForegroundColor Yellow
git status --short

# Confirm
$confirm = Read-Host "`nCreate checkpoint '$CheckpointName'? (y/N)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Checkpoint cancelled" -ForegroundColor Yellow
    exit 0
}

# Add all changes
Write-Host "`nStaging changes..." -ForegroundColor Yellow
git add .

# Create commit
$commitMessage = "Checkpoint: $CheckpointName"
if ($Message) {
    $commitMessage += "`n`n$Message"
}

Write-Host "Creating commit..." -ForegroundColor Yellow
git commit -m $commitMessage

# Show result
Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "Checkpoint created successfully!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Recent commits:" -ForegroundColor Yellow
git log --oneline -5

Write-Host ""
Write-Host "To view this checkpoint later:" -ForegroundColor Cyan
Write-Host "  git log --grep='$CheckpointName'" -ForegroundColor White

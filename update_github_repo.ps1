# PowerShell script to update GitHub repository description and topics
# Requires GitHub token with repo permissions

param(
    [string]$Token = $env:GITHUB_TOKEN
)

# Repository configuration
$Owner = "nmlssfx"
$Repo = "adguard-dns-hacs"
$Description = "AdGuard DNS integration for Home Assistant"
$Topics = @("home-assistant", "hacs", "adguard-dns", "integration")

# Get GitHub token
if (-not $Token) {
    Write-Host "GitHub token not found in environment." -ForegroundColor Yellow
    Write-Host "Please provide your GitHub personal access token:" -ForegroundColor Yellow
    $Token = Read-Host "GitHub Token" -AsSecureString
    $Token = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($Token))
}

if (-not $Token) {
    Write-Host "❌ GitHub token is required" -ForegroundColor Red
    exit 1
}

Write-Host "Updating repository: $Owner/$Repo" -ForegroundColor Cyan
Write-Host "Description: $Description" -ForegroundColor Cyan
Write-Host "Topics: $($Topics -join ', ')" -ForegroundColor Cyan
Write-Host ""

# GitHub API endpoints
$RepoUrl = "https://api.github.com/repos/$Owner/$Repo"
$TopicsUrl = "https://api.github.com/repos/$Owner/$Repo/topics"

# Headers
$Headers = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
    "User-Agent" = "AdGuard-DNS-Integration-Setup"
}

try {
    # Update repository description
    Write-Host "Updating repository description..." -ForegroundColor Yellow
    
    $RepoData = @{
        description = $Description
    } | ConvertTo-Json
    
    $Response = Invoke-RestMethod -Uri $RepoUrl -Method PATCH -Headers $Headers -Body $RepoData -ContentType "application/json"
    Write-Host "✅ Repository description updated successfully" -ForegroundColor Green
    
    # Update repository topics
    Write-Host "Updating repository topics..." -ForegroundColor Yellow
    
    $TopicsHeaders = $Headers.Clone()
    $TopicsHeaders["Accept"] = "application/vnd.github.mercy-preview+json"
    
    $TopicsData = @{
        names = $Topics
    } | ConvertTo-Json
    
    $Response = Invoke-RestMethod -Uri $TopicsUrl -Method PUT -Headers $TopicsHeaders -Body $TopicsData -ContentType "application/json"
    Write-Host "✅ Repository topics updated successfully" -ForegroundColor Green
    Write-Host "Topics: $($Topics -join ', ')" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "🎉 Repository metadata updated successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Check GitHub Actions for HACS validation" -ForegroundColor White
    Write-Host "2. Create PR to home-assistant/brands repository" -ForegroundColor White
    Write-Host "3. Wait for HACS validation to pass" -ForegroundColor White
    
} catch {
    Write-Host "❌ Failed to update repository metadata" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $StatusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "Status Code: $StatusCode" -ForegroundColor Red
        
        try {
            $ErrorContent = $_.Exception.Response.GetResponseStream()
            $Reader = New-Object System.IO.StreamReader($ErrorContent)
            $ErrorBody = $Reader.ReadToEnd()
            Write-Host "Response: $ErrorBody" -ForegroundColor Red
        } catch {
            Write-Host "Could not read error response" -ForegroundColor Red
        }
    }
    
    exit 1
}
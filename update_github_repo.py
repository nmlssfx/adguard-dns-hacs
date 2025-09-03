#!/usr/bin/env python3
"""
Script to update GitHub repository description and topics via GitHub API.
Requires GitHub token with repo permissions.
"""

import requests
import json
import os
import sys

def update_repository_metadata(owner, repo, token, description, topics):
    """
    Update GitHub repository description and topics.
    
    Args:
        owner (str): Repository owner
        repo (str): Repository name
        token (str): GitHub personal access token
        description (str): Repository description
        topics (list): List of topics
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    # GitHub API endpoints
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    topics_url = f"https://api.github.com/repos/{owner}/{repo}/topics"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "AdGuard-DNS-Integration-Setup"
    }
    
    # Update repository description
    print(f"Updating repository description...")
    repo_data = {
        "description": description
    }
    
    response = requests.patch(repo_url, headers=headers, json=repo_data)
    if response.status_code == 200:
        print("✅ Repository description updated successfully")
    else:
        print(f"❌ Failed to update description: {response.status_code} - {response.text}")
        return False
    
    # Update repository topics
    print(f"Updating repository topics...")
    topics_data = {
        "names": topics
    }
    
    # Topics require special Accept header
    topics_headers = headers.copy()
    topics_headers["Accept"] = "application/vnd.github.mercy-preview+json"
    
    response = requests.put(topics_url, headers=topics_headers, json=topics_data)
    if response.status_code == 200:
        print("✅ Repository topics updated successfully")
        print(f"Topics: {', '.join(topics)}")
    else:
        print(f"❌ Failed to update topics: {response.status_code} - {response.text}")
        return False
    
    return True

def main():
    # Repository configuration
    OWNER = "nmlssfx"
    REPO = "adguard-dns-hacs"
    DESCRIPTION = "AdGuard DNS integration for Home Assistant"
    TOPICS = ["home-assistant", "hacs", "adguard-dns", "integration"]
    
    # Get GitHub token from environment or prompt
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("GitHub token not found in environment.")
        print("Please set GITHUB_TOKEN environment variable or provide it when prompted.")
        token = input("Enter your GitHub personal access token: ").strip()
    
    if not token:
        print("❌ GitHub token is required")
        sys.exit(1)
    
    print(f"Updating repository: {OWNER}/{REPO}")
    print(f"Description: {DESCRIPTION}")
    print(f"Topics: {', '.join(TOPICS)}")
    print()
    
    success = update_repository_metadata(OWNER, REPO, token, DESCRIPTION, TOPICS)
    
    if success:
        print("\n🎉 Repository metadata updated successfully!")
        print("\nNext steps:")
        print("1. Check GitHub Actions for HACS validation")
        print("2. Create PR to home-assistant/brands repository")
        print("3. Wait for HACS validation to pass")
    else:
        print("\n❌ Failed to update repository metadata")
        sys.exit(1)

if __name__ == "__main__":
    main()
set -ex

# Ensure all files are committed before deploying
if [[ -n $(git status --porcelain) ]]; then
  git add -A

  # Generate commit message with claude
  TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
  CHANGES=$(git diff --cached --stat | tail -1)
  echo "Using APIkey=$ANTHROPIC_API_KEY"
  COMMIT_MSG=$(claude -p "Generate a brief git commit message (one line, max 72 chars) for a blog deploy. Include this timestamp: $TIMESTAMP. Changed files summary: $CHANGES. Format: 'Deploy TIMESTAMP: brief description'")

  git commit -m "$COMMIT_MSG

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

  git push
fi

hugo
AWS_SSO=personal AWS_PROFILE=personal-mike-AdministratorAccess aws-sso login
AWS_PROFILE=personal-mike-AdministratorAccess aws s3 sync public/ s3://mikesshinyobjects.tech --delete
AWS_PROFILE=personal-mike-AdministratorAccess aws --no-cli-pager cloudfront create-invalidation --distribution-id E230DHNOI4UQRZ --paths "/*"

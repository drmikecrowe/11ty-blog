set -ex

hugo
AWS_PROFILE=personal-mike-AdministratorAccess aws s3 sync public/ s3://mikesshinyobjects.tech --delete
AWS_PROFILE=personal-mike-AdministratorAccess aws cloudfront create-invalidation --distribution-id E230DHNOI4UQRZ --paths "/*"
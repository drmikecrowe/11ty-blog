{
  pkgs,
  lib,
  ...
}: {
  packages = [
    pkgs.nodePackages.typescript
    pkgs.nodePackages.typescript-language-server
    pkgs.nodePackages.npm-check-updates
    pkgs.nodePackages.prettier
    pkgs.nodePackages.quicktype
    pkgs.aws-sso-cli
    pkgs.pulumi
    pkgs.pulumiPackages.pulumi-language-nodejs
  ];
  languages.javascript = {
    directory = "project";
    enable = true;
    corepack.enable = true;
  };
}

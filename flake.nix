{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = {
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        devShells.default = pkgs.mkShell {
          packages = [
            (
              pkgs.python3.withPackages (python-pkgs: [
                python-pkgs.flask
                python-pkgs.flask-caching
                python-pkgs.requests
                python-pkgs.spotipy
                python-pkgs.pytz
                python-pkgs.icalendar
                python-pkgs.waitress
                python-pkgs.paste
                python-pkgs.pastedeploy
              ])
            )
          ];

          shellHook = ''
            python --version
          '';
        };
      }
    );
}

{
  description = "Anime utilities";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable-small";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
        python = pkgs.python3.override {
          self = python;
          packageOverrides = pyself: pyfinal: {
            tekore = pkgs.callPackage ./nix/tekore.nix { };
            scikit-learn-extra = pyfinal.scikit-learn-extra.overridePythonAttrs (old: {
              version = "0.3.1-pre";
              doCheck = false;
              build-system =  [ pyfinal.packaging ];
              src = pkgs.fetchFromGitHub {
                owner = "scikit-learn-contrib";
                repo = "scikit-learn-extra";
                rev = "0f95d8dda4c69f9de4fb002366041adcb1302f3b";
                hash = "sha256-SZoaCoywX80Evvx+O1ADAuvo/yuGyGfr507f4JxGRCg=";
              };
            });
          };
        };
      in
      {
        devShells.default = pkgs.mkShell {
					buildInputs = [
						(python.withPackages (python-pkgs: [
							python-pkgs.tekore
							python-pkgs.requests
							python-pkgs.toml
							python-pkgs.tqdm
							python-pkgs.numpy
							python-pkgs.scikit-learn
							python-pkgs.scikit-learn-extra
							python-pkgs.scipy
							python-pkgs.seaborn
							python-pkgs.httpx
							python-pkgs.matplotlib
							python-pkgs.pillow
							python-pkgs.aiohttp
							python-pkgs.pydantic # TODO: this should be with tekore
						]))
					];
        };
      });
}


{
  lib,
  python3Packages,
  fetchPypi,
  ...
}: let

in python3Packages.buildPythonPackage rec {
  pname = "tekore";
  version = "5.5.0";

  src = fetchPypi {
    inherit pname version;
    hash = "sha256-meCQ9S9CnRXkrZ13/wYOQyy5SrkJJuJRSfMd6gClO8w=";
  };

  pyproject = true;
  build-system = [
      python3Packages.setuptools
      python3Packages.wheel
      python3Packages.httpx
      python3Packages.pydantic
  ];

}

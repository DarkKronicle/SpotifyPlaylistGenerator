{
  lib,
  python3Packages,
  fetchPypi,
  ...
}:
let

in
python3Packages.buildPythonPackage rec {
  pname = "tekore";
  version = "5.5.1";

  src = fetchPypi {
    inherit pname version;
    hash = "sha256-AgvXoNo7mQSUK8wwJOx7t/bkWwLNgLGyRIFy+xP90As=";
  };

  pyproject = true;
  build-system = [
    python3Packages.setuptools
    python3Packages.wheel
    python3Packages.httpx
    python3Packages.pydantic
  ];

}

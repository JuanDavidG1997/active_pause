# Scaffold smoke test — verifies the package is importable and version is set.
# Remove or replace this file once real tests are added.
import active_pauses


def test_version_defined() -> None:
    assert active_pauses.__version__ == "0.1.0"

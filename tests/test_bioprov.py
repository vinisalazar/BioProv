"""
Testing module for the package
"""

def test_imports():
    try:
        import bioprov as bp
    except ImportError:
        raise
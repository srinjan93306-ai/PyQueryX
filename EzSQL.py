"""Compatibility module for users who prefer the EzSQL.py name.

The recommended import remains ``from ezsql import connect`` because lowercase
package names are the Python convention. This module allows ``import EzSQL``.
"""

from ezsql import EZConnection, EZSQLError, __version__, connect

__all__ = ["connect", "EZConnection", "EZSQLError", "__version__"]

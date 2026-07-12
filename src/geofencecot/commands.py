#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# geofencecot Command Line.

"""geofencecot Command Line."""

import pytak


def main() -> None:
    """CLI tool boilerplate (same pattern as lincot / other PyTAK gateways)."""
    pytak.cli(__name__.split(".", maxsplit=1)[0])


if __name__ == "__main__":
    main()

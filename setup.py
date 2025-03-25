#!/usr/bin/env python3

from setuptools import setup, Extension
from pathlib import Path

root = Path(__file__).parent
long_description = (root / "README.md").read_text()

setup(
        name="go-leds",
        version="1.1.0",
        description="",
        url="https://github.com/GOcontroll/go-leds",
        author="Maud Spierings",
        author_email="maudspierings@gocontroll.com",
        license="MIT",
        long_description=long_description,
        long_description_content_type="text/markdown",
        packages=["go_leds"],
        install_requires=["smbus2"],
        entry_points={
            "console_scripts": [
                "go-leds = go_leds.go_leds:set_led",
                "go-test-leds = go_leds.go_leds:test_leds",
                "go-flash-leds = go_leds.go_leds:flash_leds",
            ]
        },
        python_requires=">=3.9",
)

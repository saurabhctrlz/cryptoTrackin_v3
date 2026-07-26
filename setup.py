from setuptools import setup

setup(
    name="cryptotrackin",
    version="1.0.0",
    description="Blockchain transaction forensics tool - traces wallet activity and flags risk indicators. Built by ambatron_ctrlz.",
    py_modules=["cli", "fetcher", "risk_list", "db", "app"],
    install_requires=[
        "flask",
        "requests",
        "colorama",
    ],
    entry_points={
        "console_scripts": [
            "cryptotrackin=cli:main",
        ],
    },
    python_requires=">=3.8",
)

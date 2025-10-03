from setuptools import setup, find_packages

setup(
    name="navratri-pass",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "motor",
        "pymongo",
        "pydantic",
        "pydantic-settings",
        "email-validator",
        "pytest",
        "pytest-asyncio",
        "httpx",
        "asgi-lifespan",
        "python-jose",
        "passlib",
        "python-multipart",
        "python-dotenv",
        "bcrypt",
        "qrcode",
        "pillow",
    ],
)

from setuptools import setup, find_packages

setup(
    name="mosaic",
    version="0.1.0",
    description="Multi-agent Orchestration System for Adaptive Intelligent Collaboration",
    author="MOSAIC Team",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "pydantic>=2.4.2",
        "sqlalchemy>=2.0.23",
        "python-dotenv>=1.0.0",
        "websockets>=12.0",
        "websocket-client>=1.6.0",  # For WebSocket client in test scripts
        "python-multipart>=0.0.6",
        "httpx>=0.25.1",
        "langchain>=0.0.335",
        "openai>=1.6.1",
        "langchain-openai>=0.0.2",
        "requests>=2.31.0",  # For HTTP requests in test scripts
    ],
    python_requires=">=3.11",
)

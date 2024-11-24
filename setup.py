from setuptools import setup, find_packages

setup(
    name="user-story-assistant",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.115.4,<0.116.0",
        "uvicorn>=0.32.0,<0.33.0",
        "python-dotenv>=1.0.0,<2.0.0",
        "pydantic>=2.9.2,<3.0.0",
        "starlette>=0.41.2,<0.42.0",
        "langchain>=0.3.6,<0.4.0",
        "langchain-community>=0.3.7,<0.4.0",
        "langchain-core>=0.3.15,<0.4.0",
        "langchain-ollama>=0.2.0,<0.3.0",
        "pydantic-settings>=2.6.1,<3.0.0",
        "torch>=2.1.0,<3.0.0",
        "transformers>=4.36.0,<5.0.0",
        "atlassian-python-api>=3.41.0,<4.0.0",
    ],
    python_requires=">=3.11,<3.13",
)

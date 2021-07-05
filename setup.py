import setuptools

setuptools.setup(
    name='mypythonlib',
    packages=setuptools.find_packages(include=["birds"]),
    version='0.1.0',
    description='My first Python library',
    author='Me',
    license='MIT',
    install_require=[
        "asyncpg==0.23.0",
        "click==8.0.1",
    ],
    entry_points={
        "console_scripts": [
            "birds=birds.__main__:cli",
        ],
    }
)
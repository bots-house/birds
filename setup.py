import setuptools

setuptools.setup(
    name='birds',
    packages=setuptools.find_packages(include=["birds"]),
    version='0.1.0',
    description='Simple python migrator',
    author='redhat3',
    license='MIT',
    install_require=[
        "asyncpg==0.23.0",
        "click==8.0.1",
    ],
    extras_require={
        'dev': [
            'black',
            'isort',
        ]
    },
    entry_points={
        "console_scripts": [
            "birds=birds.__main__:cli",
        ],
    }
)
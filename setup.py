from setuptools import setup

setup(
    name='lansend',
    version='0.1.0',
    packages=["_scripts"],
    py_modules=['cli', "sender"],
    install_requires=[
        'Click',
        "notify-py",
        "datetime"
    ],
    entry_points={
        'console_scripts': [
            'lansend=cli:myCli',
        ],
    },
)

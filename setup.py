from setuptools import setup


setup(
    name='img2planes',
    version='1.0',
    author='Rigel Di Scala',
    author_email='zedr@zedr.com',
    py_modules=['img2planes'],
    entry_points={
        'console_scripts': ['img2planes=img2planes:main']
    },
    install_requires=['Pillow'],
    tests_require=['pytest']
)

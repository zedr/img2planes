from setuptools import setup


setup(
    name='img2planes',
    version='0.4.1',
    url='https://github.com/zedr/img2planes',
    author='Rigel Di Scala',
    author_email='zedr@zedr.com',
    py_modules=['img2planes'],
    entry_points={
        'console_scripts': ['img2planes=img2planes:main']
    },
    install_requires=['Pillow'],
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Code Generators',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ]
)

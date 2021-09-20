import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="traffic-monitor",
    version="2.0.1",
    author="sumanth",
    author_email="sumanth902@gmail.com",
    description="Traffic Monitor is a HTTP proxy tool",
    long_description=long_description,
    # long_description_content_type="text/markdown",
    # url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
      'console_scripts': [
          'trafficmonitor = trafficmonitor.trafficmonitor:run'
      ],
    },
    install_requires=['mitmproxy==7.0.3', 'PyQt5==5.14.1', 'requests==2.22.0', 'openpyxl==3.0.3'],
    include_package_data=True,
)

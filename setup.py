import setuptools

requirements = [
    'docopt',
    'numpy',
    'pyzmq'
]

console_scripts = [
    'lambda_client=lambda_scope.zmq.client:main',
    'lambda_forwarder=lambda_scope.zmq.forwarder:main',
    'lambda_hub=lambda_scope.devices.hub_relay:main',
    'lambda_publisher=lambda_scope.zmq.publisher:main',
    'lambda_server=lambda_scope.zmq.server:main',
    'lambda_subscriber=lambda_scope.zmq.subscriber:main',
    'lambda_logger=lambda_scope.devices.logger:main',
    'lambda_dragonfly=lambda_scope.devices.dragonfly:main',
    'lambda_acquisition_board=lambda_scope.devices.acquisition_board:main',
    'lambda_displayer=lambda_scope.devices.displayer:main',
    'lambda=lambda_scope.system.lambda:main'
]

setuptools.setup(
    name="lambda_scope",
    version="0.0.1",
    author="Mahdi Torkashvand",
    author_email="mmt.mahdi@gmail.com",
    description="Software to operate the customized imaging system, lambda.",
    url="https://github.com/venkatachalamlab/lambda",
    project_urls={
        "Bug Tracker": "https://github.com/venkatachalamlab/lambda/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
    ],
    entry_points={
        'console_scripts': console_scripts
    },
    install_requires=requirements,
    packages=['lambda_scope'],
    python_requires=">=3.6",
)
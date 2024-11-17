# hkopendata-py
This project originates from the PyCon HK 2024 Sprint topic. It is aimed to provide an SDK for Python users in Hong Kong to easily connect to Open Data in Hong Kong.

## Installation

## Usage

## Development

This project utilizes `docker` to setup the development environment. Check the [documentation](https://docs.docker.com/engine/install/) of `docker` to install it on your machine.

To start the development environment, simply run the following command:

```bash
$ docker compose -f docker-compose.dev.yaml up -d
```

This will start a ubuntu container with all the necessary dependencies installed. You can then run the following command to enter the container:

```bash
$ docker compose exec dev bash
```

You can also utilize Visual Studio Code to develop this project. Simply open the project in Visual Studio Code and download the `remote-container` extension. This will allow you to open the project in a container.
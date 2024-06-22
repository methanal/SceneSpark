<h1 align="center">SceneSpark</h1>
<p align="center">Automatically extract and generate key scenes from videos, creating impactful and concise highlights.</p>
<h4 align="center">
    <a href="https://github.com/methanal/scenespark/actions/workflows/pre-commit.yml" target="_blank">
        <img src="https://shields.io/github/actions/workflow/status/methanal/scenespark/pre-commit.yml?label=pre-commit" alt="Pre-commit status">
    </a>
</h4>

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [RoadMap](#roadmap)
- [FAQ](#faq)
- [Maintainers](#maintainers)
- [Contributing](#contributing)
- [License](#license)


## Introduction

SceneSpark is a tool designed to automate the extraction and generation of key scenes from videos. It leverages advanced algorithms to create impactful and concise highlights, making it easier to share and review important moments in any video.

## Features

- 🔜 **Subtitle Clipper**: Extracts key scenes based on subtitle analysis.
- 🚧 **(Coming Soon) LLM CV Clipper**: Uses large language models for computer vision-based clipping.
- 🚧 **(Coming Soon) OCR Clipper**: Extracts scenes based on text recognition from video frames.
- 🚧 **(Coming Soon) RAG**: Retrieval-Augmented Generation for enhanced scene extraction.
- 🚧 **(Coming Soon) Microservices Architecture**: Frontend and backend services are decoupled and deployed using Docker Compose for seamless integration and scalability.
- 🚧 (Coming Soon) On-Premise Deployment: Easily deploy on your own physical servers or data centers for enhanced security and privacy.

## Acknowledgements

This repository is inspired by and borrows some code from [autocut](https://github.com/mli/autocut). Special thanks to the autocut team.

## Getting Started

### Installation

1. Clone the repository

```sh
$ git clone https://github.com/methanal/SceneSpark.git
```

2. Prepare a Virtual Environment

```sh
pyenv virtuanlenv scenespark
pyenv activate scenespark
```

3. Install the requirements

```sh
pip install --no-cache-dir -r requirements.txt
```

### Launch

1. Create and Fill in the .env File

```
OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
OPENAI_BASE_URL="https://xx.xx.xx/api/v1/xx/"
```

2. Launch ./run.sh

```sh
./run.sh
```

### Usage

Navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. You will see a simple, minimalistic page. Enjoy exploring!

## API Documentation

API details will be provided soon. Stay tuned for updates.

## Roadmap

- [x] **Subtitle Clipper**
  - ~~subtitle clipper~~
- [] **LLM CV Clipper**
- [] **OCR Clipper**
- [] **RAG**
- [] **Microservices Architecture**
    - Frontend built with React
    - docker-compose.yml
- [] **On-Premise Deployment**

## FAQ

TBD

## Maintainers

[@methanal](https://github.com/methanal)

## Contributing

Feel free to dive in! [Open an issue](https://github.com/methanal/SceneSpark/issues/new) or submit PRs.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/methanal/SceneSpark/blob/main/LICENSE) file for details.

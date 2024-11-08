<h1 align="center">SceneSpark</h1>
<p align="center">Automatically extract and generate key scenes from videos, creating impactful and concise highlights.</p>
<h4 align="center">
    <a href="https://github.com/methanal/scenespark/actions/workflows/pre-commit-api.yml" target="_blank">
        <img src="https://shields.io/github/actions/workflow/status/methanal/scenespark/pre-commit-api.yml?label=pre-commit" alt="Pre-commit status">
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

SceneSpark backend API.

## Features

- 🎉 **Subtitle Clipper**: Extracts key scenes based on subtitle analysis.
- 🎉 **LLM CV Clipper**: Uses large language models for computer vision-based clipping.
- 🎉 **Microservices Architecture**: Frontend and backend services are decoupled and deployed using Docker Compose for seamless integration and scalability.
- 🎉 **On-Premise Deployment**: Easily deploy on your own physical servers or data centers for enhanced security and privacy.
- 🔜 **(Coming Soon) Multi-LLM Integration**: Import multiple LLM, including self-hosted.
- 🚧 **RAG**: Retrieval-Augmented Generation for enhanced scene extraction.Video Distillation, Knowledge Base
- 🚧 **OCR Clipper**: Extracts scenes based on text recognition from video frames.

## Acknowledgements

This repository is inspired by and borrows some code from [mli/autocut](https://github.com/mli/autocut). Special thanks to the autocut team.

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
cd api/
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

~~Navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. You will see a simple, minimalistic page. Enjoy exploring!~~

## API Documentation

API details will be provided soon. Stay tuned for updates.

## Roadmap

- [x] **Subtitle Clipper**
    - ~~subtitle clipper~~
    - ~~Refactor the LLM prompt: The LLM should return a JSON object that includes subtitle indices and extracts. Each extract should contain tags and a description.~~
    - ~~Implement the /api/v1/clips/subtitle_clipper/{request\_id} API endpoint to retrieve results for a specific request_id. The response should be a JSON object that includes the start and end times of the clip, the relative path where the clip is stored, and the clip’s tags and description.~~
    - ~~Refactor the frontend, remove the “Extract” and “View Results” buttons, using AJAX to dynamically fetch results instead.~~
    - ~~Update the frontend, load video files of clips within a list component, displaying their associated tags and descriptions.~~
    - Refactor the API and OpenAPI documentation to include Request and Response schemas.
    - Large Whisper model
- [x] **LLM CV Clipper**
    - ~~Single image recognition~~
    - ~~Multiple image recognition~~
    - ~~Consecutive image sequence recognition~~
    - ~~Read video and sample frames~~
    - ~~send a small subset of sampled frames to the LLM for recognition.~~
    - ~~Compress sampled frames to minimize token usage and submit more frames per request.~~
    - ~~Finalize the LLM prompt to extract key frames from consecutive frames, returning a JSON object. The JSON should include relevant data extracted from the frames.~~
    - Use subtitles to assist in correcting video editing
    - Tags extraction: https://github.com/PaddlePaddle/PaddleVideo/tree/develop/applications/VideoTag
- [] **Multiple Video Support**
    - Upload multiple video
    - multi-round clipping
    - token evaluator
- [] **Microservices Architecture**
    - ~~Frontend built with React~~
    - ~~docker-compose.yml~~
- 🔜 **Performance**
    - Upload speed
    - Async background task
- 🔜 **Multi-LLM Integration**: Import multiple LLM, including self-hosted.
- [] **On-Premise Deployment**
- [] **RAG**
    - Video Distillation: Samples can be taken every half second. First, a local facial recognition model runs through the video, filtering based on provided facial snapshots of main and key characters. The remaining snapshots are then sampled again.
    - RAG (Context Enhancement for Screenshots): We have subtitles. By correlating sampled screenshots with subtitles, send the corresponding subtitles as context when sending screenshots to the LLM. Additionally, include the entire conversation with subtitles as context each time.
    - RAG (Knowledge Base): Construct a knowledge base for the entire video or series as RAG. This includes comprehensive subtitles with timestamps and local analysis and annotations from various small models on half-second screenshots.
- [] **OCR Clipper**

## FAQ

TBD

## Maintainers

[@methanal](https://github.com/methanal)

## Contributing

Feel free to dive in! [Open an issue](https://github.com/methanal/SceneSpark/issues/new) or submit PRs.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/methanal/SceneSpark/blob/main/LICENSE) file for details.

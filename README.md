<h1 align="center">
  Pop Cat Todo List
</h1>

<p align="center">A clone of the Popcat Todo List!<p>
<p align="center">
  <a href="https://github.com/HerrErde/popcat-todoweb/commits">
  <img src="https://img.shields.io/github/last-commit/HerrErde/popcat-todoweb"></a>
</p>

<p align="center">
  <a href="https://ko-fi.com/herrerde">
  <img src="https://ko-fi.com/img/githubbutton_sm.svg"></a>
</p>

[![Docker Image](https://github.com/HerrErde/popcat-todoweb/actions/workflows/build.yml/badge.svg?branch=master&cacheSeconds=10)](https://github.com/HerrErde/popcat-todoweb/actions/workflows/build-release.yml)

### Run local

```sh
cd src
pip install -r requirements.txt
python main.py
```

`open http://localhost:5000`

---

To see how to configure the Docker image, please see [DOCKER.md](DOCKER.md).

### Create Application

On the discord [developer site](https://discordapp.com/developers/applications/me) create an application, and then fill in the `client id` and `client secret` in the docker env.

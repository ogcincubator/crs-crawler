# README

The purpose of these scripts is to provide a list of all the crs uris hosted in the OGC Definition server 🌈, in a machine-readable format. 

## Quick-start 🚀

The script in the root folder crawls all the children of a url and produces a list. It can be used to build a list of OGC crs uris.

Usage:

```
pip install -r requirements.txt
python crawl.py [start_url]
```

Example:

```
python crawl.py https://www.opengis.net/def/crs/
```

The output list will be generated in [crs-list.txt](./crs-list.txt). We will update it, from time to time with a GitHub action.

There is also an API on the [server](./server) folder, which publishes the results on the list. Start it and wait a moment ⏳, while it loads the list:

```
$ python server/main.py                                              [12:27:45]
INFO:     Started server process [68556]
INFO:     Waiting for application startup.
Loading source from crs-list.txt... [ok]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

It enables you to query the list using filters and a `limit` parameter:

http://0.0.0.0:8000/search?q=EPSG/0/&limit=500

The limit parameter overrides the default of `20` results. Use it with caution.

You can also check a live version of this API on:

https://defs-dev.opengis.net/crs-lookup/search?q=EPSG

## Contributing 🤝

This is a live project and we welcome contributions from the community! If you have suggestions for improvements, found a bug, or want to add new features, feel free to:

* Open an [issue](https://github.com/ogcincubator/discord-bot/issues) to start a discussion
* Submit a [pull request](https://github.com/ogcincubator/discord-bot/pulls) with your proposed changes

We appreciate your support in making these scripts better!

### License

This project is released under an [MIT License](./LICENSE)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
(dev-exercise-template)%

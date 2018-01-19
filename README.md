BIDS Apps runner for CBRAIN
===========================
This Dockerized application takes as an input a
[Boutiques](https://github.com/boutiques/boutiques)
descriptor JSON of a [BIDS App](http://bids-apps.neuroimaging.io/) and a Boutiques invocation JSON and generates
[CBRAIN](https://mcin-cnim.ca/technology/cbrain/) subtask JSONs in the current working directory.

The runner will infer which analysis levels (`session*`, `participant*`,
`group*`) are supported by the input app and create appropriate subtask
together with their dependencies.
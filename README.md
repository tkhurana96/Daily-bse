## Daily BSE
[![Build Status](https://travis-ci.org/tkhurana96/Daily-bse.svg?branch=master)](https://travis-ci.org/tkhurana96/Daily-bse)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/7a490c4232d648e6b357fcf92ebb54fb)](https://www.codacy.com/app/tkhurana96/Daily-bse?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=tkhurana96/Daily-bse&amp;utm_campaign=Badge_Grade)

This project shows the daily stats issued by BSE by fetching from this URL: http://www.bseindia.com/markets/equity/EQReports/BhavCopyDebt.aspx?expandable=3

![website-layout](./demo.gif)

The project uses Cherrypy, the python web framework to serve files and redis to store the data which can be queried.

### Steps to get the project up and running:
  - install redis: `sudo apt install redis-server`
  - clone the project
  - `cd` into cloned directory
  - use `pipenv install` to install deps
  - rename .env.sample to .env
  - use `pipenv shell` to activate the virtual env
  - run `python serve.py`
  - goto `localhost:8080` in browser

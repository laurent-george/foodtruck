# API stress test command line **Locust**

## Command line


```
locust -f tests/api_stress_test.py --host=http://HOST:PORT
```

for local rest_api, use `--host=http://localhost:8000`

## Web interface

Go to Webpage `http://localhost:8089` to run test. Choose tests options :
- number of runners (ie `1`)
- hatch rate (ie `10`)

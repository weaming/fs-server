# FS Server

Static file server using [sendfile](https://linux.die.net/man/2/sendfile)

## Install

```shell
pip3 install fs-server
```

## Usage

See example [config.json](./config.json) for quick setup.

```shell
usage: fs-server [-h] [-c CONFIG] [--host HOST] [--port PORT]
                 [--backlog BACKLOG]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        file path of config in json format
  --host HOST           listen host
  --port PORT           listen port
  --backlog BACKLOG     the number of unaccepted connections that the system
                        will allow before refusing new connections
```

## Benchmark

```shell
$ ll dist/fs_server-0.1.0-py3-none-any.whl
-rw-r--r--  1 garden  staff   4.0K Apr 10 15:31 dist/fs_server-0.1.0-py3-none-any.whl

$ ab -n 10000 -c 100 http://127.0.0.1:8080/public/fs_server-0.1.0-py3-none-any.whl
Server Hostname:        127.0.0.1
Server Port:            8080

Document Path:          /public/fs_server-0.1.0-py3-none-any.whl
Document Length:        4200 bytes

Concurrency Level:      100
Time taken for tests:   17.055 seconds
Complete requests:      10000
Failed requests:        0
Total transferred:      42960000 bytes
HTML transferred:       42000000 bytes
Requests per second:    586.33 [#/sec] (mean)
Time per request:       170.554 [ms] (mean)
Time per request:       1.706 [ms] (mean, across all concurrent requests)
Transfer rate:          2459.82 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   1.5      0     114
Processing:     5  170  80.3    139     588
Waiting:        2  170  80.2    139     587
Total:          9  170  80.5    139     588

Percentage of the requests served within a certain time (ms)
  50%    139
  66%    170
  75%    190
  80%    202
  90%    269
  95%    344
  98%    455
  99%    502
 100%    588 (longest request)

$ ll TCoDEVONthink3-1.1.pdf
-rw-rw-rw-@ 1 garden  staff   5.9M Apr  3 13:47 TCoDEVONthink3-1.1.pdf

$ ab -n 10000 -c 100 http://127.0.0.1:8080/TCoDEVONthink3-1.1.pdf
Server Hostname:        127.0.0.1
Server Port:            8080

Document Path:          /TCoDEVONthink3-1.1.pdf
Document Length:        572764 bytes

Concurrency Level:      100
Time taken for tests:   14.189 seconds
Complete requests:      10000
Failed requests:        9999
   (Connect: 0, Receive: 0, Length: 9999, Exceptions: 0)
Total transferred:      6551813419 bytes
HTML transferred:       6550913419 bytes
Requests per second:    704.75 [#/sec] (mean)
Time per request:       141.895 [ms] (mean)
Time per request:       1.419 [ms] (mean, across all concurrent requests)
Transfer rate:          450916.05 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   4.6      0     458
Processing:    10  141  48.5    130     592
Waiting:        1  140  46.8    130     580
Total:         15  141  48.5    131     592

Percentage of the requests served within a certain time (ms)
  50%    131
  66%    136
  75%    143
  80%    147
  90%    163
  95%    185
  98%    259
  99%    482
 100%    592 (longest request)
```

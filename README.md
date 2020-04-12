# GOG Galaxy 2.0 Stats Exporter
Run `src\gog_stats_exporter.py` to create a csv file containing data of all your owned games. The data is also annotated with price data from steamprices.com. You can provide the local GOG Galaxy 2.0 database and the exporter will automatically scan all your owned games. You will most likely find the GOG Galaxy 2.0 database at `C:\ProgramData\GOG.com\Galaxy\storage\galaxy-2.0.db`.

You can then run `gog_stats_analysis.py` to launch a Plotly Dash server with many nice statistics to further analyse your gaming library.

Feel free to look at the [example preview](example/preview.png)!

## Planned Features
* [ ] Implement the exporter using golang instead of python
* [x] Add original price info of games
* [ ] Include Metacritic user ratings
* [x] Add calculations for "Price per minute"
* [ ] Add comparison with friends
* [ ] Maybe add comparison to HowLongToBeat data
* [ ] Add possibility to provide manual overrides
* [ ] Add cache for price data so it does not have to be pulled every time

## Prerequisites
Run `pip3 install -r requirements.txt` to install the following dependencies:
* bs4
* chart-studio
* dash
* pandas
* pandasql
* plotly
* yapf

## Usage
```
usage: gog_stats_exporter.py [-h] [-d DATABASE] [-o OUTPUT] [-p [PROXIED]]
                             [--skip-prices [SKIP_PRICES]]
                             [-l {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}]

Export stats from GOG Galaxy 2.0 to csv file.

optional arguments:
  -h, --help            show this help message and exit
  -d DATABASE, --database DATABASE
                        Path to GOG Galaxy 2.0 database.
  -o OUTPUT, --output OUTPUT
                        Path to output csv file.
  -p [PROXIED], --proxied [PROXIED]
                        Using proxies to scrape websites faster. Use at your
                        own risk! Without this setting the robots.txt is used
                        to configure the delay between requests.
  --skip-prices [SKIP_PRICES]
                        Skips the annotations of price data from
                        steamprices.com. Keep in mind that further analysis
                        might not work because of the missing fields.
  -l {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}, --logging {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}
                        Defines log level.
```

## License
<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br /><span xmlns:dct="http://purl.org/dc/terms/" href="http://purl.org/dc/dcmitype/Text" property="dct:title" rel="dct:type">GOG Galaxy 2.0 Stats Exporter</span> by <a xmlns:cc="http://creativecommons.org/ns#" href="https://github.com/ChriZ982" property="cc:attributionName" rel="cc:attributionURL">ChriZ982</a> is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.

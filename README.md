# GOG Galaxy 2.0 Stats Exporter

Feel free to look at the `gog-stats-analysis.ipynb` Jupyter Notebook!

In case GitHub doesn't show it correctly use [this link](https://nbviewer.jupyter.org/github/ChriZ982/GOG-Galaxy-2.0-Stats-Exporter/blob/master/gog_stats_analysis.ipynb).

## Planned Features
* [x] Add original price info of games
* [ ] Include Metacritic ratings
* [x] Add calculations for "Price per minute"
* [ ] Add comparison with friends
* [ ] Maybe add comparison to HowLongToBeat data
* [ ] Add possibility to provide manual overrides

## Usage

You will most likely find the GOG Galaxy 2.0 Database under `C:\ProgramData\GOG.com\Galaxy\storage\galaxy-2.0.db`.

```
usage: gog-stats-exporter.py [-h] [-d DATABASE] [-o OUTPUT]
                             [-l {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}]

Export stats from GOG Galaxy 2.0 to csv file.

optional arguments:
  -h, --help            show this help message and exit
  -d DATABASE, --database DATABASE
                        path to GOG Galaxy 2.0 database
  -o OUTPUT, --output OUTPUT
                        path to output csv file
  -l {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}, --logging {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}
                        defines log level
```

## License
<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br /><span xmlns:dct="http://purl.org/dc/terms/" href="http://purl.org/dc/dcmitype/Text" property="dct:title" rel="dct:type">GOG Galaxy 2.0 Stats Exporter</span> by <a xmlns:cc="http://creativecommons.org/ns#" href="https://github.com/ChriZ982" property="cc:attributionName" rel="cc:attributionURL">ChriZ982</a> is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.

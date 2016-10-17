# DecidimViz

Clone of the project *[DecideViz](https://github.com/elaragon/decideviz)* (developed for *[Decide Madrid](https://decide.madrid.es/)*) for exploring the discussion of a debate/proposal from *[decidim.barcelona](https://decidim.barcelona/)*.

## How to use it

The tool requires the following python packages:
* bottle
* urllib2
* json

Then run the app locally:

```
python app.py 
```

Finally explore debates and proposals in a web browser by setting the type (debates/proposals) and the corresponding numerical ID , e.g.:
```
http://localhost:8080/thread/?id=1094&type=proposal
```

## License
Code published under AFFERO GPL v3 (see [LICENSE-AGPLv3.txt](https://www.gnu.org/licenses/agpl.txt))


## Acknowledgments
This work is supported by the EU project [D-CENT](http://dcentproject.eu/) (FP7/CAPS 610349) and the Spanish Ministry of Economy and Competitiveness under the [María de Maeztu Units of Excellence Programme](https://www.upf.edu/icaria-cei/en/news/1027.html) (MDM-2015-0502) 


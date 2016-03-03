# DecideViz

Online debate tools in participatory democracy and crowdsourcing legislation remains limited by several factors. One of them arises when discussion of proposals reach a large number of contributions and therefore citizens encounter 
difficulties in mapping the arguments that constitute the dialectical debate. 

To address this issue, this visualization tool that shows the discussion of a debate/proposal as an interactive radial tree. The tool builds on a recently created platform for open consultation and direct democracy called *[Decide Madrid](https://decide.madrid.es/)* launched by the City Council of Madrid. 



![alt text](https://elaragon.files.wordpress.com/2016/01/decidemadrid.png)


More info about this tool can be found at: http://dcentproject.eu/wp-content/uploads/2016/01/D2.4-%EF%BF%BCFrom-citizen-data-to-wisdom-of-the-Crowd.pdf

## How to use it

The tool requires the following python packages:
* bottle
* BeautifulSoup
* urllib
* re
* json

Then run the app locally:

```
python app.py 
```

Finally explore debates and proposals in a web browser by setting the type (debates/proposals) and the corresponding numerical ID , e.g.:
```
http://localhost:8080/thread/?id=4230&type=debates
```




## Acknowledgments
This work is supported by the EU project [D-CENT](http://dcentproject.eu/) (FP7/CAPS 610349) and the Spanish Ministry of Economy and Competitiveness under the María de Maeztu Units of Excellence Programme (MDM-2015-0502) 

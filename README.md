# PandemicModel

## Running the Analyzer:
Update my hard-coded paths in the `python/PandemicModel.py` and then run from the `python` directory:

`python PandemicModel.py`

Optional command line arguments:
*  no arguments: run everything
* `-p`: run only data preparation
* `-s`: run only plot maker and save pdfs
* `-a`: run only fit routine to fit a funtion to histogram of US confirmed cases 

## Directory Organization:
* `data` - raw case data from University of Virginia (http://ncov.bii.virginia.edu/dashboard/) 
* `plots` - output plots
* `predictions` - random fit models
* `python` - analyzer source code 

## External Package Dependencies:
* ROOT (https://root.cern.ch/)
* scipy stuff like numpy and pandas (https://www.scipy.org/)

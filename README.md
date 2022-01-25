# QUANT_RUBICON
A cut down version of QUANT containing just the model in Python (QUANTPy)

pip install -r requirements.txt

Install the QUANT2 data first by running:

python databuilder.py

This downloads all the cost matrices from the Open Science Foundation web site
and the public repository. This avoids having to run all the shortest paths
stuff. Census travel to work flows are downloaded from the Census site.

Then run:

python main.py

This is an example calibration run using the data just downloaded to obtain
beta values for the rail, bus and road transport modes. These beta values
can then be used when running the model to measure goodness of fit, or
for running scenarios.

Outputs are three TPred matrices, one for each mode and three beta values
calibrated from the TObs trips data to make it match the average trip
lengths CBar. Once the CBar values match for all modes the calibration
stops.

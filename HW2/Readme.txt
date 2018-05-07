HW2: Probe Data Analysis for Road Slope
-------------------------
match.py:
    python match.py directory LinkFile

    ProbePoints: diretcory to the ProbePoints file name
    LinkFile: diretcory to the LinkFile file name

output:
	Partition6467MatchedPoints.csv

Example:
	python .\HW1.py ..\..\..\..\Desktop\probe_data_map_matching\Partition6467ProbePoints.csv ..\..\..\..\Desktop\probe_data_map_matching\Partition6467LinkData.csv
-------------------------
slope.py:
    python slope.py matchedPoints LinkFile

    matchedPoints: diretcory to the matchedPoints file name
    LinkFile: diretcory to the LinkFile file name

output:
	LinkSlopeAndEvaSlope.csv

Example:
	python .\slope.py .\Partition6467MatchedPoints.csv ..\..\..\..\Desktop\probe_data_map_matching\Partition6467LinkData.csv
#bin/bash 
# This is a sample on how to create conversion files for CA Live API Creator to API Logic Server

rm *.txt
export project=b2bderbynw
export repos=/Users/guest/CALiveAPICreator.repository

python3 reposreader.py --project $project --repos $repos --section security > declare_security.txt

python3 reposreader.py --project $project --repos $repos --section rules > declare_logic.txt

python3 reposreader.py --project $project --repos $repos --section resources > customize_api.txt

python3 reposreader.py --project $project --repos $repos --section data_sources > DataSources.txt

python3 reposreader.py --project $project --repos $repos --section all > allReport.txt
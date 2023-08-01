#bin/bash 
# This is a sample on how to create conversion files for CA Live API Creator to API Logic Server

rm *.txt
project=b2bderbynw
repos=C:\CALiveAPICreator.repository

python3 reposreader.py --project $project --repos $repos --section security > declare_security.txt

python3 reposreader.py --project $project --repos $repos --section rules > declare_logic.txt

python3 reposreader.py --project $project --repos $repos --section resources > customize_api.txt

python3 reposreader.py --project $project --repos $repos --section data_sources > data_sources.txt

python3 reposreader.py --project $project --repos $repos --section tests > test_script.txt

python3 reposreader.py --project $project --repos $repos --section functions > functions.txt

python3 reposreader.py --project $project --repos $repos --section all > all_report.txt
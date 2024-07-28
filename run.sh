#bin/bash 
# This is a sample on how to create conversion files for CA Live API Creator to API Logic Server


export project=b2bderbynw
#export repos=/Users/tylerband/dev/model_migration_service/CALiveAPICreator.repository
export repos=~/CALiveAPICreator.repository
mkdir output
rm output/*.txt

python3 reposreader.py --project $project --repos $repos --section security > output/declare_security.txt

python3 reposreader.py --project $project --repos $repos --section rules > output/declare_logic.txt

python3 reposreader.py --project $project --repos $repos --section resources > output/customize_api.txt

python3 reposreader.py --project $project --repos $repos --section data_sources > output/data_sources.txt

python3 reposreader.py --project $project --repos $repos --section tests > output/test_script.txt

python3 reposreader.py --project $project --repos $repos --section functions > output/functions.txt

python3 reposreader.py --project $project --repos $repos --section all > output/all_report.txt
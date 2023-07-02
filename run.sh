#bin/bash 
# This is a sample on how to create conversion files for CA Live API Creator to API Logic Server

rm *.txt
export project=b2bderbynw

python3 reposreader.py --project $project --repos /Users/tylerband/CALiveAPICreator.repository --section security > declare_security.txt

python3 reposreader.py --project $project --repos /Users/tylerband/CALiveAPICreator.repository --section rules > declare_logic.txt

python3 reposreader.py --project $project --repos /Users/tylerband/CALiveAPICreator.repository --section resources > customize_api.txt

python3 reposreader.py --project $project --repos /Users/tylerband/CALiveAPICreator.repository --section data_sources > DataSources.txt

python3 reposreader.py --project $project --repos /Users/tylerband/CALiveAPICreator.repository --section all > allReport.txt
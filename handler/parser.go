package parser

import (
	"encoding/json"
	"io/ioutil"
	"strings"
)

type RuleDef struct {
	Name         string `json:"name"`
	Entity       string `json:"entity"`
	IsActive     bool   `json:"isActive"`
	RuleType     string `json:"ruleType"`
	Asynchronous bool   `json:"asynchronous"`
	AppliesTo    struct {
		Insert bool `json:"insert"`
		Update bool `json:"update"`
		Delete bool `json:"delete"`
	} `json:"appliesTo"`
	CodeType    string `json:"codeType"`
	IsAutoTitle bool   `json:"isAutoTitle"`
	Title       string `json:"title"`
	Comments    string `json:"comments"`
	Topics      string `json:"topics"`
}

func ParseRules(project string, mypath string) {
	p := fmt.Sprintf("%s/%s", mypath, project)
	files, err := ioutil.ReadDir(p)
	if err != nil {
		log.Fatal(err)
	}

	for _, file := range files {
		fmt.Println(file.Name(), file.IsDir())
		if file.IsDir() {
			p1 := fmt.Sprintf("%s/%s", p, file.Name())
			files1, _ := ioutil.ReadDir(p1)
			for _, f := range files1 {
				fmt.Println("===========")
				fmt.Println(f.Name(), f.IsDir())

				if !f.IsDir() {
					fp := fmt.Sprintf("%s/%s", p1, f.Name())
					if strings.Contains(fp, ".json") {
						fileContent, err := os.Open(fp)
						defer fileContent.Close()
						if err != nil {
							log.Fatal(err)
							return
						}
						byteResult, _ := ioutil.ReadAll(fileContent)
						res := make(map[string]interface{}, 0) //RuleDef{}
						json.Unmarshal([]byte(byteResult), &res)

						fmt.Println(fmt.Sprintf("%+v", res))
						fmt.Println("===========")
					} else {
						fileContent, err := os.Open(fp)
						defer fileContent.Close()
						if err != nil {
							log.Fatal(err)
							return
						}
						byteResult, _ := ioutil.ReadAll(fileContent)
						fmt.Println(string(byteResult))
						fmt.Println("===========")
					}
				}
			}
		}
	}
}

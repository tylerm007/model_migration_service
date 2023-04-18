package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"fileReader/rules"

	"gopkg.in/yaml.v2"
)

// Config struct for webapp config
type Config struct {
	Server struct {
		// Host is the local machine IP Address to bind the HTTP Server to
		Host string `yaml:"host"`

		// Port is the local machine TCP Port to bind the HTTP Server to
		Port    string `yaml:"port"`
		Timeout struct {
			// Server is the general server timeout to use
			// for graceful shutdowns
			Server time.Duration `yaml:"server"`

			// Write is the amount of time to wait until an HTTP server
			// write opperation is cancelled
			Write time.Duration `yaml:"write"`

			// Read is the amount of time to wait until an HTTP server
			// read operation is cancelled
			Read time.Duration `yaml:"read"`

			// Read is the amount of time to wait
			// until an IDLE HTTP session is closed
			Idle time.Duration `yaml:"idle"`
		} `yaml:"timeout"`
	} `yaml:"server"`
	Repos struct {
		Project string `yaml:"project"`
		Path    string `yaml:"path"`
	} `yaml:"repos"`
}

// NewConfig returns a new decoded Config struct
func NewConfig(configPath string) (*Config, error) {
	// Create config structure
	config := &Config{}

	// Open config file
	file, err := os.Open(configPath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	// Init new YAML decode
	d := yaml.NewDecoder(file)

	// Start YAML decoding from file
	if err := d.Decode(&config); err != nil {
		return nil, err
	}

	return config, nil
}

// ValidateConfigPath just makes sure, that the path provided is a file,
// that can be read
func ValidateConfigPath(path string) error {
	s, err := os.Stat(path)
	if err != nil {
		return err
	}
	if s.IsDir() {
		return fmt.Errorf("'%s' is a directory, not a normal file", path)
	}
	return nil
}

// ParseFlags will create and parse the CLI flags
// and return the path to be used elsewhere
func ParseFlags() (string, error) {
	// String that contains the configured configuration path
	var configPath string

	// Set up a CLI flag called "-config" to allow users
	// to supply the configuration file
	flag.StringVar(&configPath, "config", "./config.yaml", "path to config file")

	// Actually parse the flags
	flag.Parse()

	// Validate the path first
	if err := ValidateConfigPath(configPath); err != nil {
		return "", err
	}

	// Return the configuration path
	return configPath, nil
}

// NewRouter generates the router used in the HTTP Server
func NewRouter(project string, reposPath string) *http.ServeMux {
	// Create router and define routes and return that router
	router := http.NewServeMux()
	fmt.Printf(" project: %s path: %s \n", project, reposPath)
	router.HandleFunc("/rules", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "Hello, you've requested: %s project: %s path: %s \n", r.URL.Path, project, reposPath)
		//project := "demo"
		//reposPath := "/Users/tylerband/CALiveAPICreator.repository/teamspaces/default/apis/demo/rules"

		ParseRules(project, reposPath)
	})

	return router
}

// Run will run the HTTP Server
func (config Config) Run() {
	// Set up a channel to listen to for interrupt signals
	var runChan = make(chan os.Signal, 1)

	// Set up a context to allow for graceful server shutdowns in the event
	// of an OS interrupt (defers the cancel just in case)
	ctx, cancel := context.WithTimeout(
		context.Background(),
		config.Server.Timeout.Server,
	)
	defer cancel()

	// Define server options
	server := &http.Server{
		Addr:         config.Server.Host + ":" + config.Server.Port,
		Handler:      NewRouter(config.Repos.Project, config.Repos.Path),
		ReadTimeout:  config.Server.Timeout.Read * time.Second,
		WriteTimeout: config.Server.Timeout.Write * time.Second,
		IdleTimeout:  config.Server.Timeout.Idle * time.Second,
	}

	// Handle ctrl+c/ctrl+x interrupt
	signal.Notify(runChan, os.Interrupt, syscall.SIGTSTP)

	// Alert the user that the server is starting
	log.Printf("Server is starting on %s\n", server.Addr)

	// Run the server on a new goroutine
	go func() {
		if err := server.ListenAndServe(); err != nil {
			if err == http.ErrServerClosed {
				// Normal interrupt operation, ignore
			} else {
				log.Fatalf("Server failed to start due to err: %v", err)
			}
		}
	}()

	// Block on this channel listeninf for those previously defined syscalls assign
	// to variable so we can let the user know why the server is shutting down
	interrupt := <-runChan

	// If we get one of the pre-prescribed syscalls, gracefully terminate the server
	// while alerting the user
	log.Printf("Server is shutting down due to %+v\n", interrupt)
	if err := server.Shutdown(ctx); err != nil {
		log.Fatalf("Server was unable to gracefully shutdown due to err: %+v", err)
	}
}

// Func main should be as small as possible and do as little as possible by convention
func main() {
	// Generate our config based on the config supplied
	// by the user in the flags
	cfgPath, err := ParseFlags()
	if err != nil {
		log.Fatal(err)
	}
	cfg, err := NewConfig(cfgPath)
	if err != nil {
		log.Fatal(err)
	}

	// Run the server
	cfg.Run()
}

func ParseRules(project string, mypath string) {
	p := fmt.Sprintf("%s/%s", mypath, project)
	files, err := ioutil.ReadDir(p)
	rules.Foo()
	if err != nil {
		log.Fatal(err)
	}
	repos := make(map[string]interface{}, 0)
	for _, file := range files {
		//fmt.Println(file.Name(), file.IsDir())
		if file.IsDir() {
			p1 := fmt.Sprintf("%s/%s", p, file.Name())
			files1, _ := ioutil.ReadDir(p1)
			for _, f := range files1 {
				//fmt.Println("===========")
				//fmt.Println(f.Name(), f.IsDir())

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
						repos[f.Name()] = res
						//fmt.Println(fmt.Sprintf("%+v", res))
						//fmt.Println("===========")
					} else {
						fileContent, err := os.Open(fp)
						defer fileContent.Close()
						if err != nil {
							log.Fatal(err)
							return
						}
						byteResult, _ := ioutil.ReadAll(fileContent)
						//fmt.Println(string(byteResult))
						repos[f.Name()] = string(byteResult)
						//fmt.Println("===========")
					}
				}
			}
		}
	}
	//fmt.Println(fmt.Sprintf("%+v", repos))

	//var result dict
	for n, v := range repos {
		ruleType := "javaScript:"
		fmt.Println("```")
		fmt.Println(n)

		if strings.Contains(n, ".json") {
			//delete:false insert:false update:true
			name := fmt.Sprintf("%s", v.(map[string]interface{})["name"])
			title := fmt.Sprintf("%s", v.(map[string]interface{})["title"])
			entity := fmt.Sprintf("%s", v.(map[string]interface{})["entity"])
			ruleType = fmt.Sprintf("%s", v.(map[string]interface{})["ruleType"])
			isActive := fmt.Sprintf("%t", v.(map[string]interface{})["isActive"])
			//roleToChildren (sum)
			//errorMessage (constraint)
			if isActive == "true" {
				fmt.Println("Entity:", entity, "RuleType:", ruleType, "Title:", title, "Name:", name)
				fmt.Println(v)
			} else {
				fmt.Println("isActive =", isActive)
			}
		} else {
			fmt.Println(ruleType)
			fmt.Println(v)
		}
		fmt.Println("```")
	}
}

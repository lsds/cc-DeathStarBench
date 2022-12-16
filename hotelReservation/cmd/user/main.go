package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"strconv"
	"time"

	"github.com/intel-sandbox/carlosse.DeathStarBench/services/user"
	"github.com/intel-sandbox/carlosse.DeathStarBench/tune"
	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
)

func main() {
	tune.Init()
	log.Logger = zerolog.New(zerolog.ConsoleWriter{Out: os.Stdout, TimeFormat: time.RFC3339}).With().Timestamp().Caller().Logger()

	// Read config file
	codePath, ok := os.LookupEnv("DSB_CODE_DIR")
	if !ok {
		log.Error().Msgf("Error reading variable: %s", codePath)
		panic("Error reading env. variable: DSB_CODE_DIR")
	}
	log.Info().Msg("Reading config...")
	jsonFile, err := os.Open(filepath.Join(codePath, "config.json"))
	if err != nil {
		log.Error().Msgf("Got error while reading config: %v", err)
	}
	defer jsonFile.Close()
	byteValue, _ := ioutil.ReadAll(jsonFile)
	var result map[string]string
	json.Unmarshal([]byte(byteValue), &result)

	// If Consul is disabled, overwrite the address to the service name
	mongo_host := "localhost"
	val, ok := os.LookupEnv("ENABLE_CONSUL")
	if !ok {
		panic("ENABLE_CONSUL env. variable not set")
	} else {
		if val != "on" {
			mongo_host = "mongodb-user"
		}
	}

	// Initialise MongoDB session
	mongodb_addr := fmt.Sprintf("%s:%s", mongo_host, result["MongoPort"])
	log.Info().Msgf("Read database URL: %v", mongodb_addr)
	log.Info().Msg("Initializing DB connection...")
	mongo_session := initializeDatabase(mongodb_addr)
	defer mongo_session.Close()
	log.Info().Msg("Successful")

	serv_port, _ := strconv.Atoi(result["UserPort"])
	log.Info().Msgf("Read target port: %v", serv_port)

	srv := &user.Server{
		Port:         serv_port,
		MongoSession: mongo_session,
	}

	log.Info().Msg("Starting server...")
	log.Fatal().Msg(srv.Run().Error())
}

package main

import (
	"encoding/json"
	"io/ioutil"
	"os"
	"path/filepath"
	"strconv"
	"time"

	"github.com/intel-sandbox/carlosse.DeathStarBench/services/frontend"
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
	log.Info().Msgf("Reading variable: %s", codePath)
	jsonFile, err := os.Open(filepath.Join(codePath, "config.json"))
	if err != nil {
		log.Error().Msgf("Got error while reading config: %v", err)
	}
	defer jsonFile.Close()
	byteValue, _ := ioutil.ReadAll(jsonFile)
	var result map[string]string
	json.Unmarshal([]byte(byteValue), &result)

	serv_port, _ := strconv.Atoi(result["FrontendPort"])
	search_port, _ := strconv.Atoi(result["SearchPort"])
	profile_port, _ := strconv.Atoi(result["ProfilePort"])
	user_port, _ := strconv.Atoi(result["UserPort"])
	recommend_port, _ := strconv.Atoi(result["RecommendationPort"])
	reservation_port, _ := strconv.Atoi(result["ReservationPort"])

	log.Info().Msgf("Read target port: %v", serv_port)
	srv := &frontend.Server{
		Port:            serv_port,
		ProfilePort:     profile_port,
		RecommendPort:   recommend_port,
		ReservationPort: reservation_port,
		SearchPort:      search_port,
		UserPort:        user_port,
	}

	log.Info().Msg("Starting server...")
	log.Fatal().Msg(srv.Run().Error())
}

package frontend

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strconv"

	recommendation "github.com/intel-sandbox/carlosse.DeathStarBench/services/recommendation/proto"
	reservation "github.com/intel-sandbox/carlosse.DeathStarBench/services/reservation/proto"
	user "github.com/intel-sandbox/carlosse.DeathStarBench/services/user/proto"
	"github.com/rs/zerolog/log"

	"github.com/intel-sandbox/carlosse.DeathStarBench/dialer"
	profile "github.com/intel-sandbox/carlosse.DeathStarBench/services/profile/proto"
	search "github.com/intel-sandbox/carlosse.DeathStarBench/services/search/proto"
)

// Server implements frontend service
type Server struct {
	searchClient         search.SearchClient
	profileClient        profile.ProfileClient
	recommendationClient recommendation.RecommendationClient
	userClient           user.UserClient
	reservationClient    reservation.ReservationClient
	Port                 int
	// TODO(carlosse) - consider doing this differently
	ProfilePort     int
	RecommendPort   int
	ReservationPort int
	SearchPort      int
	UserPort        int
}

// Run the server
func (s *Server) Run() error {
	if s.Port == 0 {
		return fmt.Errorf("Server port must be set")
	}

	log.Info().Msg("Initializing gRPC clients...")

	// If Consul is disabled, overwrite the address to the service name
	profile_host := "localhost"
	recommendation_host := "localhost"
	reservation_host := "localhost"
	search_host := "localhost"
	user_host := "localhost"
	val, ok := os.LookupEnv("ENABLE_CONSUL")
	if !ok {
		panic("ENABLE_CONSUL env. variable not set")
	} else {
		if val != "on" {
			profile_host = "profile"
			recommendation_host = "recommendation"
			reservation_host = "reservation"
			search_host = "search"
			user_host = "user"
		}
	}

	// Initialise /search gRPC client
	search_addr := fmt.Sprintf("%s:%d", search_host, s.SearchPort)
	if s.SearchPort == 0 {
		return fmt.Errorf("Search port must be set")
	} else {
		log.Info().Msgf("Initializing gRPC client for search service to %s", search_addr)
	}
	if err := s.initSearchClient(search_addr); err != nil {
		return err
	}

	// Initialise /profile gRPC client
	profile_addr := fmt.Sprintf("%s:%d", profile_host, s.ProfilePort)
	if s.ProfilePort == 0 {
		return fmt.Errorf("Profile port must be set")
	} else {
		log.Info().Msgf("Initializing gRPC client for profile service to %s", profile_addr)
	}
	if err := s.initProfileClient(profile_addr); err != nil {
		return err
	}

	// Initialise /recommend gRPC client
	recommend_addr := fmt.Sprintf("%s:%d", recommendation_host, s.RecommendPort)
	if s.RecommendPort == 0 {
		return fmt.Errorf("RecommendPort must be set")
	} else {
		log.Info().Msgf("Initializing gRPC client for recommendation service to %s", recommend_addr)
	}
	if err := s.initRecommendationClient(recommend_addr); err != nil {
		return err
	}

	// Initialise /user gRPC client
	user_addr := fmt.Sprintf("%s:%d", user_host, s.UserPort)
	if s.UserPort == 0 {
		return fmt.Errorf("UserPort must be set")
	} else {
		log.Info().Msgf("Initializing gRPC client for user service to %s", user_addr)
	}
	if err := s.initUserClient(user_addr); err != nil {
		return err
	}

	// Initialise /reservation gRPC client
	reservation_addr := fmt.Sprintf("%s:%d", reservation_host, s.ReservationPort)
	if s.ReservationPort == 0 {
		return fmt.Errorf("ReservationPort must be set in config.json")
	} else {
		log.Info().Msgf("Initializing gRPC client for reservation service to %s", reservation_addr)
	}
	if err := s.initReservation(reservation_addr); err != nil {
		return err
	}
	log.Info().Msg("Successfull")

	log.Trace().Msg("frontend before mux")
	mux := http.NewServeMux()
	mux.Handle("/", http.FileServer(http.Dir("services/frontend/static")))
	mux.Handle("/hotels", http.HandlerFunc(s.searchHandler))
	mux.Handle("/recommendations", http.HandlerFunc(s.recommendHandler))
	mux.Handle("/user", http.HandlerFunc(s.userHandler))
	mux.Handle("/reservation", http.HandlerFunc(s.reservationHandler))

	log.Trace().Msg("frontend starts serving")

	srv := &http.Server{
		Addr:    fmt.Sprintf(":%d", s.Port),
		Handler: mux,
	}
	log.Info().Msg("Serving http")
	return srv.ListenAndServe()
}

// TODO - consider doing this blocking
func (s *Server) initSearchClient(name string) error {
	conn, err := dialer.Dial(
		name,
	)
	if err != nil {
		return fmt.Errorf("dialer error: %v", err)
	}
	s.searchClient = search.NewSearchClient(conn)
	return nil
}

func (s *Server) initProfileClient(name string) error {
	conn, err := dialer.Dial(
		name,
	)
	if err != nil {
		return fmt.Errorf("dialer error: %v", err)
	}
	s.profileClient = profile.NewProfileClient(conn)
	return nil
}

func (s *Server) initRecommendationClient(name string) error {
	conn, err := dialer.Dial(
		name,
	)
	if err != nil {
		return fmt.Errorf("dialer error: %v", err)
	}
	s.recommendationClient = recommendation.NewRecommendationClient(conn)
	return nil
}

func (s *Server) initUserClient(name string) error {
	conn, err := dialer.Dial(
		name,
	)
	if err != nil {
		return fmt.Errorf("dialer error: %v", err)
	}
	s.userClient = user.NewUserClient(conn)
	return nil
}

func (s *Server) initReservation(name string) error {
	conn, err := dialer.Dial(
		name,
	)
	if err != nil {
		return fmt.Errorf("dialer error: %v", err)
	}
	s.reservationClient = reservation.NewReservationClient(conn)
	return nil
}

func (s *Server) searchHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	ctx := r.Context()

	log.Trace().Msg("starts searchHandler")

	// in/out dates from query params
	inDate, outDate := r.URL.Query().Get("inDate"), r.URL.Query().Get("outDate")
	if inDate == "" || outDate == "" {
		http.Error(w, "Please specify inDate/outDate params", http.StatusBadRequest)
		return
	}

	// lan/lon from query params
	sLat, sLon := r.URL.Query().Get("lat"), r.URL.Query().Get("lon")
	if sLat == "" || sLon == "" {
		http.Error(w, "Please specify location params", http.StatusBadRequest)
		return
	}

	Lat, _ := strconv.ParseFloat(sLat, 32)
	lat := float32(Lat)
	Lon, _ := strconv.ParseFloat(sLon, 32)
	lon := float32(Lon)

	log.Info().Msgf(" SEARCH [lat: %v, lon: %v, inDate: %v, outDate: %v]", lat, lon, inDate, outDate)
	// search for best hotels
	searchResp, err := s.searchClient.Nearby(ctx, &search.NearbyRequest{
		Lat:     lat,
		Lon:     lon,
		InDate:  inDate,
		OutDate: outDate,
	})
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	log.Info().Msg("SearchHandler gets searchResp")
	for _, hid := range searchResp.HotelIds {
		log.Info().Msgf("Search Handler hotelId = %s", hid)
	}

	// grab locale from query params or default to en
	locale := r.URL.Query().Get("locale")
	if locale == "" {
		locale = "en"
	}

	reservationResp, err := s.reservationClient.CheckAvailability(ctx, &reservation.Request{
		CustomerName: "",
		HotelId:      searchResp.HotelIds,
		InDate:       inDate,
		OutDate:      outDate,
		RoomNumber:   1,
	})
	if err != nil {
		log.Error().Msg("SearchHandler CheckAvailability failed")
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	log.Info().Msgf("searchHandler gets reservationResp")
	log.Info().Msgf("searchHandler gets reservationResp.HotelId = %s", reservationResp.HotelId)

	// hotel profiles
	profileResp, err := s.profileClient.GetProfiles(ctx, &profile.Request{
		HotelIds: reservationResp.HotelId,
		Locale:   locale,
	})
	if err != nil {
		log.Error().Msg("SearchHandler GetProfiles failed")
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	log.Info().Msg("searchHandler gets profileResp")

	json.NewEncoder(w).Encode(geoJSONResponse(profileResp.Hotels))
}

func (s *Server) recommendHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	ctx := r.Context()

	sLat, sLon := r.URL.Query().Get("lat"), r.URL.Query().Get("lon")
	if sLat == "" || sLon == "" {
		http.Error(w, "Please specify location params", http.StatusBadRequest)
		return
	}
	Lat, _ := strconv.ParseFloat(sLat, 64)
	lat := float64(Lat)
	Lon, _ := strconv.ParseFloat(sLon, 64)
	lon := float64(Lon)

	require := r.URL.Query().Get("require")
	if require != "dis" && require != "rate" && require != "price" {
		http.Error(w, "Please specify require params", http.StatusBadRequest)
		return
	}

	// recommend hotels
	log.Info().Msgf(" RECOMMEND [lat: %v, lon: %v, req: %v]", lat, lon, require)
	recResp, err := s.recommendationClient.GetRecommendations(ctx, &recommendation.Request{
		Require: require,
		Lat:     float64(lat),
		Lon:     float64(lon),
	})
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// grab locale from query params or default to en
	locale := r.URL.Query().Get("locale")
	if locale == "" {
		locale = "en"
	}

	// hotel profiles
	profileResp, err := s.profileClient.GetProfiles(ctx, &profile.Request{
		HotelIds: recResp.HotelIds,
		Locale:   locale,
	})
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(geoJSONResponse(profileResp.Hotels))
}

func (s *Server) userHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	ctx := r.Context()

	username, password := r.URL.Query().Get("username"), r.URL.Query().Get("password")
	log.Info().Msgf(" USER [username: %v, password: %v]", username, password)
	if username == "" || password == "" {
		http.Error(w, "Please specify username and password", http.StatusBadRequest)
		return
	}

	// Check username and password
	recResp, err := s.userClient.CheckUser(ctx, &user.Request{
		Username: username,
		Password: password,
	})
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	str := "Login successfully!"
	if recResp.Correct == false {
		str = "Failed. Please check your username and password. "
	}

	res := map[string]interface{}{
		"message": str,
	}

	json.NewEncoder(w).Encode(res)
}

func (s *Server) reservationHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	ctx := r.Context()

	inDate, outDate := r.URL.Query().Get("inDate"), r.URL.Query().Get("outDate")
	if inDate == "" || outDate == "" {
		http.Error(w, "Please specify inDate/outDate params", http.StatusBadRequest)
		return
	}

	if !checkDataFormat(inDate) || !checkDataFormat(outDate) {
		http.Error(w, "Please check inDate/outDate format (YYYY-MM-DD)", http.StatusBadRequest)
		return
	}

	hotelId := r.URL.Query().Get("hotelId")
	if hotelId == "" {
		http.Error(w, "Please specify hotelId params", http.StatusBadRequest)
		return
	}

	customerName := r.URL.Query().Get("customerName")
	if customerName == "" {
		http.Error(w, "Please specify customerName params", http.StatusBadRequest)
		return
	}

	username, password := r.URL.Query().Get("username"), r.URL.Query().Get("password")
	if username == "" || password == "" {
		http.Error(w, "Please specify username and password", http.StatusBadRequest)
		return
	}

	numberOfRoom := 0
	num := r.URL.Query().Get("number")
	if num != "" {
		numberOfRoom, _ = strconv.Atoi(num)
	}

	// Check username and password
	recResp, err := s.userClient.CheckUser(ctx, &user.Request{
		Username: username,
		Password: password,
	})
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	str := "Reserve successfully!"
	if recResp.Correct == false {
		str = "Failed. Please check your username and password. "
	}

	// Make reservation
	log.Info().Msgf(" RESERVATION [customer: %v, hotel: %v, inDate: %v, outDate: %v, numRooms: %v]", customerName, hotelId, inDate, outDate, numberOfRoom)
	resResp, err := s.reservationClient.MakeReservation(ctx, &reservation.Request{
		CustomerName: customerName,
		HotelId:      []string{hotelId},
		InDate:       inDate,
		OutDate:      outDate,
		RoomNumber:   int32(numberOfRoom),
	})
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	if len(resResp.HotelId) == 0 {
		str = "Failed. Already reserved. "
	}

	res := map[string]interface{}{
		"message": str,
	}

	json.NewEncoder(w).Encode(res)
}

// return a geoJSON response that allows google map to plot points directly on map
// https://developers.google.com/maps/documentation/javascript/datalayer#sample_geojson
func geoJSONResponse(hs []*profile.Hotel) map[string]interface{} {
	fs := []interface{}{}

	for _, h := range hs {
		fs = append(fs, map[string]interface{}{
			"type": "Feature",
			"id":   h.Id,
			"properties": map[string]string{
				"name":         h.Name,
				"phone_number": h.PhoneNumber,
			},
			"geometry": map[string]interface{}{
				"type": "Point",
				"coordinates": []float32{
					h.Address.Lon,
					h.Address.Lat,
				},
			},
		})
	}

	return map[string]interface{}{
		"type":     "FeatureCollection",
		"features": fs,
	}
}

func checkDataFormat(date string) bool {
	if len(date) != 10 {
		return false
	}
	for i := 0; i < 10; i++ {
		if i == 4 || i == 7 {
			if date[i] != '-' {
				return false
			}
		} else {
			if date[i] < '0' || date[i] > '9' {
				return false
			}
		}
	}
	return true
}

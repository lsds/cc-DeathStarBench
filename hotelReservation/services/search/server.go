package search

import (
	"fmt"
	"net"
	"os"
	"time"

	"github.com/google/uuid"
	"github.com/rs/zerolog/log"
	context "golang.org/x/net/context"
	"google.golang.org/grpc"
	"google.golang.org/grpc/keepalive"

	"github.com/intel-sandbox/carlosse.DeathStarBench/dialer"
	geo "github.com/intel-sandbox/carlosse.DeathStarBench/services/geo/proto"
	rate "github.com/intel-sandbox/carlosse.DeathStarBench/services/rate/proto"
	pb "github.com/intel-sandbox/carlosse.DeathStarBench/services/search/proto"
)

const name = "srv-search"

// Server implments the search service
type Server struct {
	geoClient  geo.GeoClient
	rateClient rate.RateClient
	Port       int
	uuid       string
	// TODO - do this differently maybe
	GeoPort  int
	RatePort int
}

// Run starts the server
func (s *Server) Run() error {
	if s.Port == 0 {
		return fmt.Errorf("server port must be set")
	}

	s.uuid = uuid.New().String()

	opts := []grpc.ServerOption{
		grpc.KeepaliveParams(keepalive.ServerParameters{
			Timeout: 120 * time.Second,
		}),
		grpc.KeepaliveEnforcementPolicy(keepalive.EnforcementPolicy{
			PermitWithoutStream: true,
		}),
	}

	srv := grpc.NewServer(opts...)
	pb.RegisterSearchServer(srv, s)

	// If Consul is disabled, overwrite the address to the service name
	geo_host := "localhost"
	rate_host := "localhost"
	val, ok := os.LookupEnv("ENABLE_CONSUL")
	if !ok {
		panic("ENABLE_CONSUL env. variable not set")
	} else {
		if val != "on" {
			geo_host = "geo"
			rate_host = "rate"
		}
	}
	// Initialise geo gRPC client
	geo_addr := fmt.Sprintf("%s:%d", geo_host, s.GeoPort)
	if s.GeoPort == 0 {
		return fmt.Errorf("GeoPort  must be set")
	} else {
		log.Info().Msgf("Initializing gRPC client for geo service to %s", geo_addr)
	}
	if err := s.initGeoClient(geo_addr); err != nil {
		return err
	}

	// Initialise geo gRPC client
	rate_addr := fmt.Sprintf("%s:%d", rate_host, s.RatePort)
	if s.RatePort == 0 {
		return fmt.Errorf("RatePort  must be set")
	} else {
		log.Info().Msgf("Initializing gRPC client for rate service to %s", rate_addr)
	}
	if err := s.initRateClient(rate_addr); err != nil {
		return err
	}

	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", s.Port))
	if err != nil {
		log.Fatal().Msgf("failed to listen: %v", err)
	}

	return srv.Serve(lis)
}

func (s *Server) initGeoClient(name string) error {
	conn, err := dialer.Dial(
		name,
	)
	if err != nil {
		return fmt.Errorf("dialer error: %v", err)
	}
	s.geoClient = geo.NewGeoClient(conn)
	return nil
}

func (s *Server) initRateClient(name string) error {
	conn, err := dialer.Dial(
		name,
	)
	if err != nil {
		return fmt.Errorf("dialer error: %v", err)
	}
	s.rateClient = rate.NewRateClient(conn)
	return nil
}

// Nearby returns ids of nearby hotels ordered by ranking algorithm.
func (s *Server) Nearby(ctx context.Context, req *pb.NearbyRequest) (*pb.SearchResult, error) {
	// find nearby hotels
	log.Trace().Msg("in Search Nearby")

	log.Trace().Msgf("nearby lat = %f", req.Lat)
	log.Trace().Msgf("nearby lon = %f", req.Lon)

	nearby, err := s.geoClient.Nearby(ctx, &geo.Request{
		Lat: req.Lat,
		Lon: req.Lon,
	})
	if err != nil {
		return nil, err
	}

	for _, hid := range nearby.HotelIds {
		log.Trace().Msgf("get Nearby hotelId = %s", hid)
	}

	// find rates for hotels
	rates, err := s.rateClient.GetRates(ctx, &rate.Request{
		HotelIds: nearby.HotelIds,
		InDate:   req.InDate,
		OutDate:  req.OutDate,
	})
	if err != nil {
		return nil, err
	}

	// TODO(hw): add simple ranking algo to order hotel ids:
	// * geo distance
	// * price (best discount?)
	// * reviews

	// build the response
	res := new(pb.SearchResult)
	for _, ratePlan := range rates.RatePlans {
		log.Trace().Msgf("get RatePlan HotelId = %s, Code = %s", ratePlan.HotelId, ratePlan.Code)
		res.HotelIds = append(res.HotelIds, ratePlan.HotelId)
	}
	return res, nil
}

package profile

import (
	"encoding/json"
	"fmt"
	"net"
	"time"

	"github.com/bradfitz/gomemcache/memcache"
	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"

	"github.com/rs/zerolog/log"

	"github.com/google/uuid"
	pb "github.com/intel-sandbox/carlosse.DeathStarBench/services/profile/proto"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
	"google.golang.org/grpc/keepalive"
)

const name = "srv-profile"

// Server implements the profile service
type Server struct {
	uuid         string
	Port         int
	MongoSession *mgo.Session
	MemcClient   *memcache.Client
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

	pb.RegisterProfileServer(srv, s)

	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", s.Port))
	if err != nil {
		log.Fatal().Msgf("failed to configure listener: %v", err)
	}

	return srv.Serve(lis)
}

// GetProfiles returns hotel profiles for requested IDs. It caches recently
// visited profiles in memcached, and uses mongo db as backend storage.
func (s *Server) GetProfiles(ctx context.Context, req *pb.Request) (*pb.Result, error) {
	log.Trace().Msgf("In GetProfiles")

	res := new(pb.Result)
	hotels := make([]*pb.Hotel, 0)

	// one hotel should only have one profile

	for _, i := range req.HotelIds {
		// first check memcached
		item, err := s.MemcClient.Get(i)
		if err == nil {
			// memcached hit
			profile_str := string(item.Value)
			log.Trace().Msgf("memc hit with %v", profile_str)

			hotel_prof := new(pb.Hotel)
			json.Unmarshal(item.Value, hotel_prof)
			hotels = append(hotels, hotel_prof)

		} else if err == memcache.ErrCacheMiss {
			// memcached miss, set up mongo connection
			session := s.MongoSession.Copy()
			defer session.Close()
			c := session.DB("profile-db").C("hotels")

			hotel_prof := new(pb.Hotel)
			err := c.Find(bson.M{"id": i}).One(&hotel_prof)

			if err != nil {
				log.Error().Msgf("Failed get hotels data: ", err)
			}

			hotels = append(hotels, hotel_prof)

			prof_json, err := json.Marshal(hotel_prof)
			if err != nil {
				log.Error().Msgf("Failed to marshal hotel [id: %v] with err:", hotel_prof.Id, err)
			}
			memc_str := string(prof_json)

			// write to memcached
			s.MemcClient.Set(&memcache.Item{Key: i, Value: []byte(memc_str)})

		} else {
			log.Panic().Msgf("Tried to get hotelId [%v], but got memmcached error = %s", i, err)
		}
	}

	res.Hotels = hotels
	log.Trace().Msgf("In GetProfiles after getting resp")
	return res, nil
}

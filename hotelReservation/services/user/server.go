package user

import (
	"crypto/sha256"
	"fmt"
	"net"
	"time"

	"github.com/google/uuid"
	"github.com/rs/zerolog/log"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
	"google.golang.org/grpc/keepalive"
	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"

	pb "github.com/intel-sandbox/carlosse.DeathStarBench/services/user/proto"
)

const name = "srv-user"

// Server implements the user service
type Server struct {
	users        map[string]string
	Port         int
	MongoSession *mgo.Session
	uuid         string
}

// Run starts the server
func (s *Server) Run() error {
	if s.Port == 0 {
		return fmt.Errorf("server port must be set")
	}

	if s.users == nil {
		s.users = loadUsers(s.MongoSession)
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

	pb.RegisterUserServer(srv, s)

	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", s.Port))
	if err != nil {
		log.Fatal().Msgf("failed to listen: %v", err)
	}

	rpcError := srv.Serve(lis)
	if rpcError != nil {
		log.Fatal().Msgf("failed to serve: %v", rpcError)
	} else {
		log.Info().Msg("serving succesfully")
	}

	return rpcError
}

// CheckUser checks that the provided username exists in the user's mongo
// database, and if it does exist, checks that the password matches the provided
// one.
//
// The passwords are not encrypted in any way, as this is just a demo.
func (s *Server) CheckUser(ctx context.Context, req *pb.Request) (*pb.Result, error) {
	res := new(pb.Result)

	sum := sha256.Sum256([]byte(req.Password))
	pass := fmt.Sprintf("%x", sum)

	// Check user and password are in the db
	session := s.MongoSession.Copy()
	defer session.Close()
	c := session.DB("user-db").C("user")
	user := User{}
	err := c.Find(bson.M{"username": req.Username}).One(&user)
	if err != nil {
		log.Error().Msgf("Failed get username from mongo: %v", err)
	}
	res.Correct = user.Password == pass

	return res, nil
}

// loadUsers loads hotel users from mongodb.
func loadUsers(session *mgo.Session) map[string]string {
	s := session.Copy()
	defer s.Close()
	c := s.DB("user-db").C("user")

	// unmarshal json profiles
	var users []User
	err := c.Find(bson.M{}).All(&users)
	if err != nil {
		log.Error().Msgf("Failed get users data: ", err)
	}

	res := make(map[string]string)
	for _, user := range users {
		res[user.Username] = user.Password
	}

	log.Trace().Msg("Done load users")

	return res
}

type User struct {
	Username string `bson:"username"`
	Password string `bson:"password"`
}

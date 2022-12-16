## API Endpoints

In this document we summarise the different exposed API endpoints, and include
an example `curl` request to execute them. Note that the example requests assume
you are using a `docker compose` deployment and have a shell inside the CLI
container.

The following graph summarises the endpoint dependencies:

<div align="center">
<img src="https://github.com/intel-sandbox/carlosse.DeathStarBench/blob/main/hotelReservation/img/hotel_reservation_graph.png?raw=True"></img>
</div>

### User login (`/user`)

Description: checks that the given user and password are registered in the user
database.

Example request:

```bash
curl -X GET http://frontend:5000/user?username=Cornell_445\&password=445445445445445445445445445445
```

### Reserve hotel rooms (`/reservation`)

Description: make a reservation in a hotel (if there's capacity). Reservations
are cached using `memcached` and persited in `Mongo DB`.

Example request:

```bash
curl -X POST http://frontend:5000/reservation?inDate=2015-04-15\&outDate=2015-04-18\&lat=37\&lon=-121\&hotelId=68\&customerName="carlos"\&username=Cornell_283\&password=283283283283283283283283283283\&number=1
```

### Get hotel recommendations (`/recommendations`)

Description: get hotel recommendations in a radius given a pair of coordinates
and a sorting criteria. After that, query for the hotel profile and return
everything to the user.

Example request:

```bash
curl -X GET http://frontend:5000/recommendations?require=price\&lat=39\&lon=-121
```

### Search for hotels (`/hotels`)

Description: search available hotels nearby. It first queries a geospatial
service for the closest hotels to a pair of coordinates, and the rates for those
hotels. Then, it gets the profiles for the shortlisted hotels and returns them
to the user.

Example request:

```bash
curl -X GET http://frontend:5000/hotels?inDate=2015-4-15\&outDate=2015-4-19\&lat=39\&lon=-121
```

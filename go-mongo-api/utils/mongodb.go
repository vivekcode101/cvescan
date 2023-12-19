package utils

import (
    "context"
    "log"
    "go.mongodb.org/mongo-driver/mongo"
    "go.mongodb.org/mongo-driver/mongo/options"
)

var client *mongo.Client

func init() {
    clientOptions := options.Client().ApplyURI("mongodb+srv://ratnesh:ratnesh@cluster0.3ka0uom.mongodb.net/")
    var err error
    client, err = mongo.Connect(context.Background(), clientOptions)
    if err != nil {
        log.Fatal(err)
    }

    err = client.Ping(context.Background(), nil)
    if err != nil {
        log.Fatal(err)
    }
    log.Println("Connected to MongoDB!")
}

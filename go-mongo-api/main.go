package main

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"time"

	"go-mongo-api/models" // Update this path based on your project structure

	"github.com/gorilla/mux"
	"go.mongodb.org/mongo-driver/bson"
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

func main() {
	router := mux.NewRouter()

	router.HandleFunc("/vulnerabilities", getVulnerabilities).Methods("GET")

	log.Fatal(http.ListenAndServe(":8080", router))
}

func getVulnerabilities(w http.ResponseWriter, r *http.Request) {
	var results []models.Vulnerability
	// Get today's date as a string (e.g., "13-12-2023")
	todayDate := time.Now().Format("02-01-2006")
	collectionName := todayDate + "_cve_list"
	print(collectionName)

	collection := client.Database("cve_db").Collection(collectionName)

	// Limit the number of documents to 10
	cursor, err := collection.Find(context.Background(), bson.M{}, options.Find())
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}
	defer cursor.Close(context.Background())

	// Decode the results into a slice
	for cursor.Next(context.Background()) {
		var result models.Vulnerability
		if err := cursor.Decode(&result); err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
			return
		}
		results = append(results, result)
	}

	// Check for cursor errors
	if err := cursor.Err(); err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	json.NewEncoder(w).Encode(results)
}

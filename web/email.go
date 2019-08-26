package main

import (
	"crypto/tls"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	"golang.org/x/net/context"
	"golang.org/x/oauth2"
	"golang.org/x/oauth2/google"
	"google.golang.org/api/gmail/v1"
)

var sendfreq bool

// Retrieve a token, saves the token, then returns the generated client.
func getClient(config *oauth2.Config) *http.Client {
	// The file token.json stores the user's access and refresh tokens, and is
	// created automatically when the authorization flow completes for the first
	// time.
	tokFile := "token.json"
	tok, err := tokenFromFile(tokFile)
	if err != nil {
		tok = getTokenFromWeb(config)
		saveToken(tokFile, tok)
	}
	return config.Client(context.Background(), tok)
}

// Request a token from the web, then returns the retrieved token.
func getTokenFromWeb(config *oauth2.Config) *oauth2.Token {
	authURL := config.AuthCodeURL("state-token", oauth2.AccessTypeOffline)
	fmt.Printf("Go to the following link in your browser then type the "+
		"authorization code: \n%v\n", authURL)

	var authCode string
	if _, err := fmt.Scan(&authCode); err != nil {
		log.Fatalf("Unable to read authorization code: %v", err)
	}

	tok, err := config.Exchange(context.TODO(), authCode)
	if err != nil {
		log.Fatalf("Unable to retrieve token from web: %v", err)
	}
	return tok
}

// Retrieves a token from a local file.
func tokenFromFile(file string) (*oauth2.Token, error) {
	f, err := os.Open(file)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	tok := &oauth2.Token{}
	err = json.NewDecoder(f).Decode(tok)
	return tok, err
}

// Saves a token to a file path.
func saveToken(path string, token *oauth2.Token) {
	fmt.Printf("Saving credential file to: %s\n", path)
	f, err := os.OpenFile(path, os.O_RDWR|os.O_CREATE|os.O_TRUNC, 0600)
	if err != nil {
		log.Fatalf("Unable to cache oauth token: %v", err)
	}
	defer f.Close()
	json.NewEncoder(f).Encode(token)
}

func queryprice(url string) float64 {

	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	client := &http.Client{Transport: tr}

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		fmt.Println(err)
		return 0
	}

	// Fetch Request
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println(err)
		return 0
	}

	defer resp.Body.Close()

	// Read Response Body
	respBody, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println(err)
		return 0
	}

	result := string(respBody)
   	resultmap := make(map[string]interface{})

        err = json.Unmarshal([]byte(result), &resultmap)
	if err != nil{
	    fmt.Println(err)
	}
	priced := resultmap["price"].(float64)

	return priced
}

func sendemail(price string, srv *gmail.Service) {

	user := "me"
	// r, err := srv.Users.Labels.List(user).Do()
	subject := fmt.Sprintf("current price %s", price)
	fmt.Println(subject)
	header := make(map[string]string)
	header["From"] = "froyo.bin@gmail.com"
	header["To"] = "froyo.bin@gmail.com"
	header["Subject"] = subject
	header["MIME-Version"] = "1.0"
	header["Content-Type"] = "text/plain; charset=\"utf-8\""
	header["Content-Transfer-Encoding"] = "base64"

	var msg string
	for k, v := range header {
		msg += fmt.Sprintf("%s: %s\r\n", k, v)
	}

	msg += "\r\n" + "just a test here."

	gmsg := gmail.Message{
		Raw: base64.RawURLEncoding.EncodeToString([]byte(msg)),
	}
	_, err := srv.Users.Messages.Send(user, &gmsg).Do()
	if err != nil {
		log.Printf("em %v, err %v", gmsg, err)
		return
	}

}

func resetfreq() {
	for true {
		sendfreq = false
		time.Sleep(60 * 60)
	}
}

func main() {
	sendfreq = false
	b, err := ioutil.ReadFile("credentials.json")
	if err != nil {
		log.Fatalf("Unable to read client secret file: %v", err)
	}
	url := "https://127.0.0.1:4356"

	// If modifying these scopes, delete your previously saved token.json.
	config, err := google.ConfigFromJSON(b, gmail.GmailSendScope)
	if err != nil {
		log.Fatalf("Unable to parse client secret file to config: %v", err)
	}
	client := getClient(config)

	srv, err := gmail.New(client)
	if err != nil {
		log.Fatalf("Unable to retrieve Gmail client: %v", err)
	}

	priceset, err := strconv.ParseFloat(os.Args[1], 32)
	if err != nil {
		fmt.Println("error in input argument")
		return
	}

	// go resetfreq()

	for true {
		price := queryprice(url)
		fmt.Println(price)
		if price > priceset {
			prices := fmt.Sprintf("price: %f, and we already send the email", price)
			if sendfreq == false {
				sendfreq = true
				fmt.Println(prices)
				sendemail(prices, srv)
				fmt.Println("we send the email")
			}

		}
		// now we sleep for 3 minutes and restart the query
		time.Sleep(time.Second * 180)

	}

}

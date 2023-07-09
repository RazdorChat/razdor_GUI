/* This file is part of the clients "Boost" feature designed to speed up requests because python is slow 
This file is also essentially app/api.py but rewritten in Go you can enable/disable go in app/config.json
*/

package main

import (
	"C"
	"io/ioutil"
	"log"
	"net/http"
)

var URL = "https://razdor.chat/api"

/*This is for Getting username from api*/
//export get_username
func get_username(username string) string{
    resp, err := http.Get(URL+"/user/"+username)
    if err != nil {
       log.Fatalln(err)
    }
 //We Read the response body on the line below.
    body, err := ioutil.ReadAll(resp.Body)
    if err != nil {
       log.Fatalln(err)
    }
 //Convert the body to type string
    sb := string(body)
    return sb
}

func get_user_relations(){
    //TODO: implement this in go

}

func main() {}
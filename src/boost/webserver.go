package main

import (
	"github.com/contentway/ace"
	"fmt"
	"os"
)

func return_html(filename string) string{
    b, err := os.ReadFile(filename) // just pass the file name
    if err != nil {
        fmt.Print(err)
    }

    str := string(b) // convert content to a 'string'

    return str
}

func main(){
	a := ace.New()
	a.GET("/:name/:surname", func(c *ace.C) {
		name := c.Param("name")
		surname := c.Param("surname")
		c.String(200, "hello mr "+name+" "+surname)
	})

	a.GET("/", func (c *ace.C)  {
		c.String(200, return_html("../template/user_msg.html"))
	})
	a.Run(":8080")
}
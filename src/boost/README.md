# Boost section
# only do this if you're building from source(or changing code) since the client distubutions already have prebuilt dll's
<p>This client has a Boost feature which allows it to go faster since requests are done in Go<br/>
To build the .dll files necessary you need GCC and Go installed on your windows pc (Boost is only avalible on windows only if you're on linux or mac please disable boost on app/config.json)
</p>

## To build

```bash
cd app/boost #cd into dir
go build -o api.dll -buildmode=c-shared # Build dll files
```
Then you're done!
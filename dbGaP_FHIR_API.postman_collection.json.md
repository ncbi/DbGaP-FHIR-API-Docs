# dbGaP FHIR API Postman Collection Notes
## Collection Structure
* Collection: dbGaP FHIR API
    * Folder: FHIR Resource
        * HTTP Requests

![Postman Collection Folder Structure](img/postman/postman_collection_folder_structure.png "Postman Collection Folder Structure")



## Pre-request Scripts
Postman allows you to run a script before the request is executed. The 
scripts can be defined at each level (collection, folder, request). If the 
script is defined at the collection level, then it will be executed before every request in the collection. If 
it is defined at the folder level, then it will be run only for the requests 
in that folder.  

Since the FHIR API standard requires an http accept header, I have defined a 
script to set a header for every request.

![Accept Header pre-request script](img/postman/accept_header.png)




## Variables
Postman allows variables to be set at each level (collection, folder,
request). These variables can be used in various places to help with testing
the api.

In order to minimize effort for similar requests for multiple resources, I
have defined two variables:  

### url
```url``` is defined at the collection level. This is the base url for the API.

![url variable](img/postman/url_variable.png)

### resourceName
```resourceName``` Is defined at the folder level. (You will notice this is 
actually a script that is setting the variable since there is no variables 
tab at the folder level).

![resourceName variable](img/postman/resourceName_Variable.png)  

When the two variables are combined in the request url field (accessed using 
curly braces), a fully formed parameterized url is created.

![parameterized url](img/postman/parameterized_url.png)

## Tests


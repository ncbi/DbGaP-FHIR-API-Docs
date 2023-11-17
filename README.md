# DbGaP FHIR API Docs

This is the documentation repository for the [dbGaP](https://www.ncbi.nlm.nih.gov/gap/) [FHIR](https://hl7.org/fhir/) API. ([API base URL](http://dbgap-api.ncbi.nlm.nih.gov/fhir/x1))

dbGaP is the Database of Genotypes and Phenotypes.<br/>
FHIR is HL7's REST API standard for transmission of electronic health record data.  

- [**Quickstart**](quickstart.md)
- [**Obtaining a Task-Specific Token for Controlled Data**](obtaining_a_token.md)
- [**Notebooks**](jupyter)


## Prerequisites

You should already have a basic understanding of FHIR - especially
before working through the Notebooks. The notebooks are based on the[FHIR Exercises
repo](https://github.com/NIH-ODSS/fhir-exercises) from the NIH Office of Data Sharing Strategy (ODSS).

For the Notebooks, you should also understand [how Notebooks
work](https://jupyter-notebook.readthedocs.io/) and [Pandas
dataframes](https://pandas.pydata.org/docs/user_guide/dsintro.html#dataframe).

## Issues

If you have a query that returns after 20 seconds with an error like the following:
```json
{
	"error": {
		"status": 500,
		"message": "error forwarding request",
		"api-key": "192.168.0.1"
	}
}
```
Then you probably hit a 20-second timeout. Removing sorting, simplifying your query, or including fewer
sub-queries in a batch can sometimes help.

For other issues please see the Issues list in this GitHub repository.

## Contact 
The dbGaP FHIR API is provided by NCBI. Please [contact](https://dbgap.ncbi.nlm.nih.gov/aa/wga.cgi?page=email&filter=from&from=login) us with any questions.
dbGaP FHIR is under active development; suggestions for features and data are welcome. 

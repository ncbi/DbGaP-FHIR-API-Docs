# DbGaP FHIR API Docs

This is the documentation repository for the [dbGaP](https://www.ncbi.nlm.nih.gov/gap/) [FHIR](https://hl7.org/fhir/) API. ([API base URL](http://dbgap-api.ncbi.nlm.nih.gov/fhir/x1))

dbGaP is the Database of Genotypes and Phenotypes.<br/>
FHIR is HL7's REST API standard for electronic medical data.

- [**Quickstart**](quickstart.md)
- [**Obtaining a Task-Specific Token for Controlled Data**](obtaining_a_token.md)
- [**Mapping dbGaP concepts to FHIR concepts**](https://dbgap-api-preview.ncbi.nlm.nih.gov/fhir-mapping/interactive/)
  - Note: this mapping will be retired and replaced by alternate documentation in future
- [**Notebooks**](jupyter)

## Prerequisites

You should already have a basic understanding of FHIR - especially
before working through the Notebooks. The [FHIR Exercises
repo](https://github.com/NIH-ODSS/fhir-exercises) from ODSS worked
well for our team in the version they had when we used them. (However,
by linking to them we do not imply that they are still good or that
NCBI or the United States Federal Government endorses them. Use at
your own risk. The same goes for all links on this page.)

For the Notebooks, you should also understand [how Notebooks
work](https://jupyter-notebook.readthedocs.io/) and [Pandas
dataframes](https://pandas.pydata.org/docs/user_guide/dsintro.html#dataframe).

## Maintenance

The team is focused on adding features and data.
So we are not fixing issues in the documentation.
This means it is outdated with no commitment
to update it. Being optimists, we hope to update
it someday, but we cannot say if that time will
ever come.

## Issues

- We are aware that the current documentation is
  [low quality and there is not enough of it](https://www.goodreads.com/quotes/4151-there-s-an-old-joke---um-two-elderly-women-are).
  If you report a bug or request a feature, it will probably be overlooked
  and neglected.

- The CSV download for the interactive concept mapping does
  not handle quoting correctly. You'll need to hand-edit it.

- If you have a query that returns after 20 seconds with an error that looks
  like the below:

        {
            "error": {
                "status": 500,
                "message": "error forwarding request",
                "api-key": "192.168.0.1"
            }
        }

  Then you probably hit the 20-second timeout imposed by our network
  infrastructure. Removing sorting, simplifying your query, or including fewer
  sub-queries in a batch can sometimes help.

- Our server may respond to a query that is not listed as supported in the
  [`CapabilityStatement`](https://dbgap-api-preview.ncbi.nlm.nih.gov/fhir/x1/metadata).
  These responses come from a second server that does not have space for all the
  data. Be especially wary about queries that involve `Observation`,
  `ResearchSubject`, `EvidenceVariable`, or `CodeSystem`. We are slowly
  migrating away from the other server, but the issue will persist for a
  long time.

- The "value-quantity" search parameter (and related parameters such as
  "combo-value-quantity" and "code-value-quantity") in the Observation resource
  may have unintuitive behavior at the ends of intervals. For example,
  `Observation?value-quantity=gt1e100` can return results with values that
  display as "1e100" because we get the values from the main dbGaP tables as
  double precision floating point numbers (where 1e100 is actually
  159 sexvigintillion larger than 10<sup>100</sup>). However, FHIR specifies
  that the value-quantity parameter should be treated as having infinite
  precision. There are expensive ways to resolve this issue (there are ways
  to get the values from dbGaP as strings and redo the database and query code
  use those in searches), but besides being expensive, they would also slow
  down the queries unless implemented in a complicated way that might introduce
  other bugs.

- We have not implemented all the search parameters for the resources we
  support. The more complicated ones (like `_include` and `_revinclude`)
  will probably be implemented after we get all the resources implemented.

- `_include` and `_revinclude` are listed as implemented in the
  [`CapabilityStatement`](https://dbgap-api-preview.ncbi.nlm.nih.gov/fhir/x1/metadata),
  but are not.

- We update `Observation` and most of the resources using a semi-manual
  process that takes two weeks of calendar time. At the end of that period
  we update one of the servers and then the other. So there is a few day period
  in which results returned by the server with less data are out of sync
  with the results returned by the server with more data. We aim to do such
  an update once a month, but we do not guarantee that we will do so. There
  are ways we could update the database daily or even within a few hours of
  changes to the underlying data, but they are not yet on the roadmap.

- After October 2023, we will update `ResearchStudy` and several of the
  `CodeSystem` objects daily. So, they are frequently slightly out of sync with
  the rest of the database. The advantage is that clients can depend on them
  being more up-to-date.

- Data derived from data tables (PHT accessions) where there is more than
  one value per patient for a single variable only has one value per patient.
  For example, [phv00278114 (HPO_PHENOTYPE)](https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/variable.cgi?study_id=phs001232.v5.p2&phv=278114)
  only lists one phenotype per patient.

- There is no way to match values across different variables. For example,
  each [phv00278114 (HPO_PHENOTYPE) value](https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/variable.cgi?study_id=phs001232.v5.p2&phv=278114)
  has a corresponding value in [phv00278115 (HPO_OBSERVED_STATUS)](https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/variable.cgi?study_id=phs001232.v5.p2&phv=278115&phd=&pha=&pht=6078&phvf=&phdf=&phaf=&phtf=&dssp=1&consent=&temp=1)
  but our FHIR objects do not link them.

- For variables whose value comes from a known code system, we represent the
  values as coming from a code system specific to that variable rather than
  from the true code system.

- Not all the `CodeSystem` links we reference in FHIR resources' system fields
  have an actual `CodeSystem` object in the database. This is legal, but it
  breaks expectations.

- We do not have any harmonized variables (PHH accessions) from TOPMed yet.

- We do not have units on for some values and instead label them as "unknown
  units."

- Some variables with values that are `CodeableConcept` resources have units
  listed in dbGaP, but we do not list those units in the `EvidenceVariable`
  objects.

- Some variables with values that are `CodeableConcept` resources actually
  represent ranges. For example, in [phv00282916](https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/variable.cgi?study_id=phs000200.v12.p3&phv=282916),
  the code 1 represents "0.4 - 0.5". This is how the data was submitted to
  dbGaP, but in theory, we could have a derived variable that represents it
  as a range.

- We do not yet have `Sample` or `Specimen` resources.

- We do not yet support FHIR R5.

- Gender on the `Patient` resources is not properly populated yet.

- `_has` search parameters are implemented individually for each resource.
  So, for example, `ResearchStudy?_has:ResearchSubject:study:status=on-study`
  may work without `Patient?_has:ResearchSub::status=on-study` working.

- When sorting Observation by `value-quantity` it sorts integer values
  separately from non-integer values. So, "1.5, 1, 2.5, 2, 3.5" could be
  ordered as "1, 2, 1.5, 2.5, 3.5" or "1.5, 2.5, 3.5, 1, 2".

## Contact

If, despite knowing it is nearly equivalent
to shouting into the void (see above), you still wish to contact
the team, you can reach the technical lead via email:
_eric (d)o(t) moyer at nih.gov_. Your email will then join the
thousands of other unopened items languishing in his inbox Limbo.

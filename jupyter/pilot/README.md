<style>
ul li:before
{
    content: '\2705'; /* White Heavy Check Mark */
    margin: 0 1em;
}
</style>

# OVERVIEW

This pilot directory will have the sample code to access the dbGaP pilot FHIR servers. There are 3 pilot FHIR servers.

1. **FHIR API service for ICAC/URECA** at [https://dbgap-api.ncbi.nlm.nih.gov/fhir-jpa-pilot1/x1/metadata](https://dbgap-api.ncbi.nlm.nih.gov/fhir-jpa-pilot1/x1/metadata) for dbGaP datasets "Whole Genome Sequencing in the Inner City Asthma Consortium (ICAC) Cohorts".


   - Please see [phs002921](https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/study.cgi?study_id=phs002921.v2.p1) for study details.
   - You need NIH Data Access approval to access this study. Please follow [instructions](https://dbgap.ncbi.nlm.nih.gov/aa/wga.cgi?page=login) to request access.
   - Once your Data Access Request (DAR) is approved, you can access this study's data both from the dbGaP website and from this pilot FHIR API server.
   - With you DAR approval, you can get the FHIR API authorization token at [dbGaP power user portal](https://www.ncbi.nlm.nih.gov/gap/power-user-portal/) and scroll-down to click on "Task specific token".

2. **FHIR API service for UDN** at [https://dbgap-api.ncbi.nlm.nih.gov/fhir-jpa-pilot2/x1/metadata](https://dbgap-api.ncbi.nlm.nih.gov/fhir-jpa-pilot2/x1/metadata) for dbGaP datasets "Clinical and Genetic Evaluation of Individuals with Undiagnosed Disorders through the Undiagnosed Diseases Network (UDN)".

   - Please see [phs001232](https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/study.cgi?study_id=phs001232.v5.p2) for study details.
   - You need NIH Data Access approval to access this study. Please follow [instructions](https://dbgap.ncbi.nlm.nih.gov/aa/wga.cgi?page=login) to request access.
   - Once your Data Access Request (DAR) is approved, you can access this study's data both from the dbGaP website and from this pilot FHIR API server.
   - With you DAR approval, you can get the FHIR API authorization token at [dbGaP power user portal](https://www.ncbi.nlm.nih.gov/gap/power-user-portal/) and scroll-down to click on "Task specific token".

3. 📌 **Important note on data security** If you have approved access and are using URECA data at fhir-jpa-pilot1 or UDN data at fhir-jpa-pilot2, note that the sample code output csv files contain "controlled-access" data. Please *only* save the files in secure computing environment which is allowed to have controlled data.

4. **Open-access test FHIR server** for those without Data Access approval but who would like to explore how to programmatically access dbGaP data with the FHIR API. This test server with synthetic data is at [https://dbgap-api.ncbi.nlm.nih.gov/fhir-jpa-pilot/x1/metadata](https://dbgap-api.ncbi.nlm.nih.gov/fhir-jpa-pilot/x1/metadata).


> 📌 **Note:** Please note that if you are using CAVATICA to access, make sure to enable "Allow Network Access" in the Project setting.

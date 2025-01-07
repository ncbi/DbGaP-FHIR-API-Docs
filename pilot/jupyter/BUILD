python_requirements(
    name = "fhir_fetcher_requirements",
    source = "requirements.txt",
)

python_sources(
    name = "fhir_fetcher_src",
    sources = ["fhir_fetcher.py"],
    dependencies = [":fhir_fetcher_requirements"],
)

python_test(
    name = "test_fhir_fetcher",
    source = "test_fhir_fetcher.py",
    dependencies = [":fhir_fetcher_src"],
)

python_test(
    name = "test_fhir_fetcher_ICAC",
    source = "test_fhir_fetcher.py",
    dependencies = ["pilot/jupyter/ICAC:fhir_fetcher_src"],
)

python_test(
    name = "test_fhir_fetcher_UDN",
    source = "test_fhir_fetcher.py",
    dependencies = ["pilot/jupyter/UDN:fhir_fetcher_src"],
)
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
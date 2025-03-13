
python_sources(
    name = "fhir_fetcher_src",
    sources = ["fhir_fetcher.py"],
    dependencies = [
        "pilot/jupyter:fhir_fetcher_requirements#requests"
    ],
)

python_test(
    name = "test_fhir_fetcher",
    source = "test_fhir_fetcher.py",
    dependencies = [":fhir_fetcher_src"],
)

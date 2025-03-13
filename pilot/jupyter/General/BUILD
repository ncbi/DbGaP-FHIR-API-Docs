
python_sources(
    name = "fhir_fetcher_src",
    sources = ["fhir_fetcher.py"],
    dependencies = ["pilot/jupyter:fhir_fetcher_requirements"],
)

python_test(
    name = "test_fhir_fetcher_General",
    source = "test_fhir_fetcher.py",
    dependencies = ["pilot/jupyter/General:fhir_fetcher_src"],
)

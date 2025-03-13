python_requirements(
    name = "fhir_fetcher_requirements",
    source = "requirements.txt",
)

python_test(
    name = "test_fhir_fetcher_General",
    source = "test_fhir_fetcher.py",
    dependencies = ["pilot/jupyter/General:fhir_fetcher_src"],
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
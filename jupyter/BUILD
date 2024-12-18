python_requirements(
    name = "dbgap_fhir_requirements",
    source = "requirements.txt",
)

python_sources(
    name = "dbgap_fhir_src",
    sources = ["dbgap_fhir.py"],
    dependencies = [":dbgap_fhir_requirements"],
)

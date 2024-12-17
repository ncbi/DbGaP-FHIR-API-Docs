This is the SCIE pants executable that is downloaded
by get-pants.sh from [the official site](https://www.pantsbuild.org/stable/docs/getting-started/installing-pants).

It is in the repository so it is available to the CI/CD process.
We still need to add an automated way of checking for updates.
For now, someone should run
```bash
SCIE_BOOT=update ./pants
```
occasionally and check in the resulting changes.

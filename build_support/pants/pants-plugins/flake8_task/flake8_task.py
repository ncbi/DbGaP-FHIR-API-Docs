import os
import subprocess

from pants.backend.python.interpreter_cache import PythonInterpreterCache
from pants.backend.python.targets.python_binary import PythonBinary
from pants.backend.python.targets.python_library import PythonLibrary
from pants.backend.python.targets.python_target import PythonTarget
from pants.backend.python.targets.python_tests import PythonTests
from pants.backend.python.tasks.resolve_requirements_task_base import (
    ResolveRequirementsTaskBase,
)
from pants.base.build_environment import get_buildroot
from pants.base.exceptions import TaskError
from pants.base.workunit import WorkUnit, WorkUnitLabel
from pants.util.memo import memoized_property
from pex.interpreter import PythonInterpreter
from pex.pex import PEX
from pex.pex_info import PexInfo


class Flake8Task(ResolveRequirementsTaskBase):
    """Invoke the flake8 PEP-8 checker for Python."""

    _FLAKE8_COMPATIBLE_INTERPETER_CONSTRAINT = ">=3.11"
    _PYTHON_SOURCE_EXTENSION = ".py"

    @classmethod
    def prepare(cls, options, round_manager):
        super().prepare(options, round_manager)
        round_manager.require_data(PythonInterpreter)

    @classmethod
    def register_options(cls, register):
        register(
            "--flake8-version",
            default="7.1.1",
            help="The version of flake8 to use.",
        )
        register(
            "--config-file",
            default=None,
            help="Path flake8 configuration file, relative to buildroot.",
        )

    @classmethod
    def supports_passthru_args(cls):
        return True

    @classmethod
    def subsystem_dependencies(cls):
        return super().subsystem_dependencies() + (PythonInterpreterCache,)

    def find_flake8_interpreter(self):
        interpreters = self._interpreter_cache.setup(
            filters=[self._FLAKE8_COMPATIBLE_INTERPETER_CONSTRAINT]
        )
        return min(interpreters) if interpreters else None

    @staticmethod
    def is_non_synthetic_python_target(target):
        return not target.is_synthetic and isinstance(
            target, (PythonLibrary, PythonBinary, PythonTests)
        )

    @staticmethod
    def is_python_target(target):
        return isinstance(target, PythonTarget)

    def _calculate_python_sources(self, targets):
        """Generate a set of source files from the given targets."""
        python_eval_targets = filter(
            self.is_non_synthetic_python_target, targets
        )
        sources = set()
        for target in python_eval_targets:
            sources.update(
                source
                for source in target.sources_relative_to_buildroot()
                if os.path.splitext(source)[1] == self._PYTHON_SOURCE_EXTENSION
            )
        return list(sources)

    def _collect_source_roots(self):
        # Collect the set of directories in which there are Python sources (whether part of
        # the target roots or transitive dependencies.)
        source_roots = set()
        for target in self.context.targets(self.is_python_target):
            if not target.has_sources(self._PYTHON_SOURCE_EXTENSION):
                continue
            source_roots.add(target.target_base)
        return source_roots

    @memoized_property
    def _interpreter_cache(self):
        return PythonInterpreterCache.global_instance()

    def _run_flake8(self, py3_interpreter, flake8_args, **kwargs):
        pex_info = PexInfo.default()
        pex_info.entry_point = "flake8"
        flake8_version = self.get_options().flake8_version

        flake8_requirement_pex = self.resolve_requirement_strings(
            py3_interpreter,
            [f"flake8=={flake8_version}", "teamcity-messages"],
        )

        path = os.path.realpath(
            os.path.join(
                self.workdir, str(py3_interpreter.identity), flake8_version
            )
        )
        if not os.path.isdir(path):
            self.merge_pexes(
                path, pex_info, py3_interpreter, [flake8_requirement_pex]
            )
        pex = PEX(path, py3_interpreter)
        return pex.run(flake8_args, **kwargs)

    def execute(self):
        flake8_interpreter = self.find_flake8_interpreter()
        if not flake8_interpreter:
            raise TaskError(
                f"Unable to find a Python {self._FLAKE8_COMPATIBLE_INTERPETER_CONSTRAINT} interpreter (required for flake8)."
            )

        sources = self._calculate_python_sources(self.context.target_roots)
        if not sources:
            self.context.log.warning("No Python sources to check.")
            return

        # Construct the flake8 command line.
        cmd = []
        if self.get_options().config_file:
            cmd.append(
                "--config={}".format(
                    os.path.join(
                        get_buildroot(), self.get_options().config_file
                    )
                )
            )
        cmd.extend(self.get_passthru_args())
        cmd += sources
        self.context.log.debug("flake8 command: {}".format(" ".join(cmd)))

        # Collect source roots for the targets being checked.
        source_roots = self._collect_source_roots()

        flake8_path = os.pathsep.join(
            [os.path.join(get_buildroot(), root) for root in source_roots]
        )

        # Execute flake8.
        with self.context.new_workunit(
            name="check",
            labels=[WorkUnitLabel.TOOL, WorkUnitLabel.RUN],
            log_config=WorkUnit.LogConfig(
                log_level=self.get_options().level,
                colors=self.get_options().colors,
            ),
            cmd=" ".join(cmd),
        ) as workunit:
            returncode = self._run_flake8(
                flake8_interpreter,
                cmd,
                env={"FLAKE8PATH": flake8_path},
                stdout=workunit.output("stdout"),
                stderr=subprocess.STDOUT,
            )
            if returncode != 0:
                raise TaskError(f"flake8 failed: code={returncode}")

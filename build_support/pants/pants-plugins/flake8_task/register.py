from pants.goal.task_registrar import TaskRegistrar as task

from flake8_task.flake8_task import Flake8Task


def register_goals():
    task(name="flake8", action=Flake8Task).install("flake8")

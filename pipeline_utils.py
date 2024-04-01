import configparser
import os
import subprocess


class PipelineManagerBase:
    def __init__(self, config_file: str, dryrun: bool, *, output_dir: str | None = None):
        self.config = self.load_config(config_file)
        self.dryrun = dryrun
        self.name = "sample_name"
        if output_dir is None:
            self.output_dir = os.getcwd()
        else:
            self.output_dir = output_dir

    def load_config(self, config_file: str) -> configparser.ConfigParser:
        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        config.read(config_file)
        return config

    def create_dir(self):
        if not os.path.exists(f"{self.output_dir}/sh"):
            os.makedirs(f"{self.output_dir}/sh")

        if not os.path.exists(f"{self.output_dir}/stdeo"):
            os.makedirs(f"{self.output_dir}/stdeo")

    def create_sh(self, script_name: str, command: str):
        with open(f"{self.output_dir}/sh/{script_name}_{self.name}.sh", "w") as sh:
            sh.write("#!/bin/bash\n")
            sh.write(command)

    def submit_job(self, script_name, dependency_id: str | None = None, cpus: int | None = None):
        if self.dryrun:
            return None

        dependency = ""
        if dependency_id:
            dependency = f"--dependency=afterok:{dependency_id} "

        if cpus is None:
            cpus = int(self.config["DEFAULT"]["threads"])

        return subprocess.check_output(f"sbatch {dependency}--chdir=$(realpath .) --cpus-per-task={cpus} --error='{self.output_dir}/stdeo/%x-%A.txt' --job-name='{script_name}_{self.name}' --mem={self.config['DEFAULT']['memory']}G --output='{self.output_dir}/stdeo/%x-%A.txt' --export=ALL {self.output_dir}/sh/{script_name}_{self.name}.sh", encoding="utf-8", shell=True).split()[-1]

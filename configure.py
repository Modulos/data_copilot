import click
import os
import sys
from subprocess import call, check_output


@click.command
def main():
    skip = False
    if os.path.isfile(".dev.env"):
        choice = click.prompt(
            "Do you want to use the existing setup? (y/n)", type=str, default="y"
        )

        if choice.lower() in ("no", "n"):
            click.echo("Overwriting .dev.env")

        else:
            skip = True

    if not skip:
        name = click.prompt(
            "What is the name of your Data Copilot?", type=str, default="DataCopilot"
        )

        openaiapikey = click.prompt("OpenAI API Key?", type=str, default="")

        backend_host = click.prompt(
            "Backend Host", type=str, default="http://localhost/api"
        )

        # create random JWT secret key openssl rand -hex 32 no user input
        jwtsecretkey = (
            check_output("openssl rand -hex 32", shell=True).decode("utf-8").strip()
        )

        backend = click.prompt(
            "What Backend do you want to use for computation? \n[1] SQL\n[2] PandasAI",
            type=int,
            default=1,
        )

        if backend == 1:
            compute_backend = "sql"

        elif backend == 2:
            compute_backend = "getting_started"

        env_file = {
            "APP_NAME": name,
            "BACKEND_HOST": backend_host,
            "JWT_SECRET_KEY": jwtsecretkey,
            "OPENAI_API_KEY": openaiapikey,
            "STORAGE_BACKEND": "volume:///data",
            "POSTGRES_HOST": "database",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "postgres",
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": "postgres",
            "REDIS_URL": "redis://redis-queue:6379/0",
            "COMPUTE_BACKEND": compute_backend,
        }

        # create dev.env fi
        with open(".dev.env", "w") as f:
            for key, value in env_file.items():
                f.write(f"{key}={value}\n")

        click.echo("Created .dev.env file")

    click.echo("Installing Data Copilot")

    # run make run-dev
    call("make run", shell=True)


if __name__ == "__main__":
    main()

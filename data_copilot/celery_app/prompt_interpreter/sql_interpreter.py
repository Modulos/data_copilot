import openai

from data_copilot.celery_app.executors.helpers import harmonize_column_names


def generate_sql_query(prompt, columns):
    columns = harmonize_column_names(columns)
    cols_text = ", ".join(["'" + col + "'" for col in columns])

    rule_1 = (
        "You are an assistant which helps a user to translate a business "
        "question he has about a dataset to a SQL query. You don't execute "
        "the query on the data yourself. You are only allowed to write SQL "
        "queries that are compatible with SQLite."
    )
    prompt_1 = (
        "Please answer if the following user question can be "
        "answered with an sql query and no additional text: "
        f"{prompt}\n"
        "The table is called: df \n"
        f"The column name of the data are: {cols_text}"
        "Answer [yes/no]: "
    )

    messages = [
        {"role": "system", "content": rule_1},
        {"role": "user", "content": prompt_1},
    ]

    response = (
        openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1,
        )
        .choices[0]
        .get("message")
        .get("content")
    )

    if response.lower() in ("y", "yes"):
        response_type = "SQL"

        rule_2 = (
            "You are an assistant which helps a user to translate a "
            "business question he has about a dataset to a SQL query. "
            "You don't execute the query on the data yourself. You are "
            "only allowed to write SQL queries that are compatible with "
            "SQLite."
        )
        prompt_2 = (
            "Please answer the following user question with an sql query "
            "and no additional text: "
            f"{prompt}\n"
            "The table is called: df \n"
            f"The column name of the data are: {cols_text}"
            "SQLite Query:"
        )
        messages = [
            {"role": "system", "content": rule_2},
            {"role": "user", "content": prompt_2},
        ]

        response = (
            openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages, temperature=0.0
            )
            .choices[0]
            .get("message")
            .get("content")
        )

    elif response.lower() in ("n", "no"):
        response_type = "TEXT"
        rule_3 = (
            "You are an assistant which helps a user to translate a "
            "business question he has about a dataset to a SQL query. "
            "You don't execute the query on the data yourself. You are "
            "only allowed to write SQL queries that are compatible with "
            "SQLite."
        )
        prompt_3 = (
            "Please explain why it is not possible to translate the "
            "following question to sql: "
            f"{prompt}\n"
            "The table is called: df \n"
            f"The column name of the data are: {cols_text}"
            "Your Answer:"
        )

        messages = [
            {"role": "system", "content": rule_3},
            {"role": "user", "content": prompt_3},
        ]

        response = (
            openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            .choices[0]
            .get("message")
            .get("content")
        )

    else:
        response_type = "TEXT"

    print(response)
    return (response_type, response)

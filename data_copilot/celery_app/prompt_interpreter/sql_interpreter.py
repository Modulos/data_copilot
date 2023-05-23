import openai

from data_copilot.celery_app.executors.helpers import harmonize_column_names


def generate_sql_query(prompt, columns):
    columns = harmonize_column_names(columns)
    cols_text = ", ".join(["'" + col + "'" for col in columns])

    context = (
        "You are an assistant which helps a user to translate "
        "a business question he has about a dataset to a SQL query. "
        "You don't execute the query on the data yourself. "
        f"The column names are:{cols_text}\n"
        "You know only SQLite. \n"
    )
    rule_1 = (
        "You are only allowed to return a single character "
        "Y or N. Y means you can create a SQL query to answer "
        "the question of the user. N means you can't create a "
    )

    messages = [
        {"role": "system", "content": context},
        {"role": "system", "content": rule_1},
        {"role": "user", "content": "User Pormpt: " + prompt},
        {"role": "system", "content": "Y/N: "},
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
            "You are only allowed to write SQL queries "
            "on a table called df. The table has the same "
            "columns as the dataset. Return the SQL query "
            "as a string. Your answer must be directly executable "
            "No additional text is allowed "
            "Write nice column aliases. "
            "for the following question: "
        )
        messages = [
            {"role": "system", "content": context},
            {"role": "system", "content": rule_2},
            {"role": "user", "content": "User Pormpt: " + prompt},
            {"role": "system", "content": "---SQLITE Query---"},
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
            "Given the user prompt it is not possible to create "
            "a query on the date to answer the question of the user. "
            "Please ask the user to rephrase the question. "
            "The user is not a programmer. He is a business user. "
            "He is not familiar with SQL. "
        )

        messages = [
            {"role": "system", "content": context},
            {"role": "system", "content": rule_3},
            {"role": "user", "content": "User Pormpt: " + prompt},
            {"role": "system", "content": "Your explanation: "},
        ]

        response = (
            openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            .choices[0]
            .get("message")
            .get("content")
        )

    else:
        response_type = "TEXT"

    print(messages)

    return (response_type, response)

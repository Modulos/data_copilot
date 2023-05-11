import openai

from celery_app.executors.helpers import harmonize_column_names


def generate_sql_query(prompt, columns):
    columns = harmonize_column_names(columns)
    cols_text = ", ".join(["'" + col + "'" for col in columns])
    openai_prompt = (
        "Translate the following prompt to a SQL query.\n"
        "The table is called 'df'.\n"
        f"The column names are:{cols_text}\n"
        f"---BEGIN PROMPT---\n{prompt}\n---END PROMPT---\n"
        "Only return the SQL Query it must be executable! The"
        "SQL Engine is SQLite."
    )
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=openai_prompt,
        temperature=0.1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.00,
    )
    return response.choices[0].text

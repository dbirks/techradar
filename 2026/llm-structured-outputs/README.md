# Structured output from LLMs





Links
- Blip: https://www.thoughtworks.com/en-us/radar/techniques/structured-output-from-llms










## Problem

We get back paragraphs from the model by default, but it's hard to parse that and have that drive another step in the process:

- showing something onscreen, like the weather. You want to see `76°F` in a card in your UI, and not `The current temperature I found is 76°F`.

- having it be the next input to the next step in a workflow / pipeline

And even when we ask for json back, it can be wrapped in markdown backticks, or with a little preamble at the front: `Sure, I can output that as json:`







## Short history

- > output as json, no mistakes
- > output as json in this schema
- adding a check process ... does this parse as valid json? if not pass the error message back to the model and ask for it again
- `JSON mode` is born https://developers.openai.com/api/docs/guides/structured-outputs#json-mode
- Then `Structured Outputs`, using Zod or Pydantic types









## Examples











Passing a picture of a handwritten form to the model, with extra notes on how to parse it, and getting structured output back.

https://github.com/dbirks/process-intake-forms/blob/main/main.py












---














Asking the model to output the reason for why it's calling a tool.

```python
@agent.tool()
def query_database(
    sql: str,
    reason: str,
):
    """
    Run a SQL query against the database.

    Args:
        sql: The query to execute.
        reason: The reason this SQL query is needed to answer the user's question.
    """

    logger.info("Reason: %s", reason)
    logger.info("SQL: %s", sql)
    
    ...

```

Output:
  
```
SQL: SELECT SUM(total_cents) AS paid_revenue_cents FROM orders WHERE status = 'paid'
Reason: The user asked for total paid revenue, so I need to sum order totals where status is paid.
```















---






















Have the model output title / x-axis label / y-axis label / reference to data, send that to the frontend, and use Apache ECharts to render an interactive chart.

https://echarts.apache.org/handbook/en/get-started/













## Verdict

Adopt!

With checks still around the output

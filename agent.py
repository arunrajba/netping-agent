import subprocess, anthropic

client = anthropic.Anthropic()

tools = [{
    "name": "ping_host",
    "description": "Ping a hostname and return the raw output",
    "input_schema": {
        "type": "object",
        "properties": {"hostname": {"type": "string"}},
        "required": ["hostname"],
    },
}]


def ping_host(hostname):
    result = subprocess.run(
        ["ping", "-n", "4", hostname],
        capture_output=True, text=True
    )
    return result.stdout + result.stderr

messages = [{"role": "user", "content": "Is fake12312.com reachable?"}]

while True:
    response = client.messages.create(
        model="claude-sonnet-5", max_tokens=1024,
        tools=tools, messages=messages,
    )
    if response.stop_reason == "tool_use":
        # keep Claude's turn in the history
        messages.append({"role": "assistant", "content": response.content})

        for block in response.content:
            if block.type == "tool_use":
                print(f"[agent is running: ping {block.input['hostname']}]")
                output = ping_host(block.input["hostname"])
                # send the result back so Claude can reason about it
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": output,
                    }]
                })
    else:
        print(response.content[0].text)
        break
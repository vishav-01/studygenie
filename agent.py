import json
from openai import OpenAI

class DataScienceAgent:
    def __init__(self, base_url, model, verbose=False, stream=False):
        self.client = OpenAI(base_url=base_url, api_key="not-needed")
        self.model = model
        self.verbose = verbose
        self.stream = stream
        self.messages = []
        self.dataframes = {}  # Track dataframes across interactions

    def add_user_message(self, msg):
        self.messages.append({"role": "user", "content": msg})

    def add_system_message(self, msg):
        self.messages.append({"role": "system", "content": msg})

    def _build_messages_with_context(self):
        """Inject dataframe context automatically."""
        context_block = ""

        if self.dataframes:
            for name, df_content in self.dataframes.items():
                context_block += f"\nDATAFRAME ({name}):\n{df_content}\n"

        messages = self.messages.copy()
        messages.append({
            "role": "system",
            "content": "Here is your context:\n" + context_block
        })

        return messages

    def _get_tools(self):
        """Declare tools that LLM can call."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "save_dataframe",
                    "description": "Store a dataframe for later use",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "content": {"type": "string"}
                        },
                        "required": ["name", "content"]
                    }
                }
            }
        ]

    def _execute_tool(self, tool_call):
        """Execute tools requested by LLM."""
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        if name == "save_dataframe":
            self.dataframes[str(args["name"])] = args["content"]
            return {"status": "saved"}

        return {"error": "unknown tool"}

    def run(self, max_iterations=5):
        """Main agent loop."""
        for _ in range(max_iterations):
            msgs = self._build_messages_with_context()

            response = self.client.chat.completions.create(
                model=self.model,
                messages=msgs,
                tools=self._get_tools(),
            )

            choice = response.choices[0]

            # If the model responds normally
            if not hasattr(choice, "message") or not choice.message.tool_calls:
                return choice.message.content

            # Tool calls
            for tool_call in choice.message.tool_calls:
                result = self._execute_tool(tool_call)
                self.messages.append({
                    "role": "tool",
                    "content": json.dumps(result),
                    "tool_call_id": tool_call.id
                })

        return "⚠️ Max iterations reached."
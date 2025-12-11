import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import "./App.css";

function App() {
  return (
    <CopilotKit runtimeUrl="http://localhost:8000">
      <div className="app-container">
        <CopilotChat
          labels={{
            title: "AI Assistant (CopilotKit + AG-UI)",
            initial: "Hello! I'm your AI assistant powered by Claude 4.5.\n\nI can help you with:\n• Weather information (try \"What's the weather in Paris?\")\n• Code documentation via Context7 MCP\n• General questions and assistance\n\nWhat would you like to know?",
          }}
        />
      </div>
    </CopilotKit>
  );
}

export default App;

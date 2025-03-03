import { Agent, Message } from "./types"
import { v4 as uuidv4 } from "uuid"

// Mock agents
export const mockAgents: Agent[] = [
  {
    id: "calculator",
    name: "Calculator",
    description: "Perform mathematical calculations and solve equations",
    type: "Utility",
    capabilities: ["Basic Math", "Equations", "Unit Conversion"],
    icon: "🧮"
  },
  {
    id: "safety",
    name: "Safety Vetting",
    description: "Validate content and approve operations based on safety rules",
    type: "Security",
    capabilities: ["Content Validation", "Operation Approval", "Package Security"],
    icon: "🛡️"
  },
  {
    id: "writer",
    name: "File Writer",
    description: "Securely read and write files with proper boundaries",
    type: "Utility",
    capabilities: ["File Reading", "File Writing", "Directory Listing"],
    icon: "📝"
  },
  {
    id: "developer",
    name: "Developer Assistant",
    description: "Help with coding tasks and software development",
    type: "Productivity",
    capabilities: ["Code Generation", "Debugging", "Documentation"],
    icon: "👨‍💻"
  }
]

// Mock messages for each agent
export const mockMessages: Record<string, Message[]> = {
  calculator: [
    {
      id: uuidv4(),
      role: "system",
      content: "I am a calculator agent that can help with mathematical calculations.",
      timestamp: Date.now() - 1000 * 60 * 60,
      agentId: "calculator"
    },
    {
      id: uuidv4(),
      role: "user",
      content: "What is 25 * 48?",
      timestamp: Date.now() - 1000 * 60 * 30,
      agentId: "calculator"
    },
    {
      id: uuidv4(),
      role: "assistant",
      content: "25 * 48 = 1,200",
      timestamp: Date.now() - 1000 * 60 * 29,
      agentId: "calculator"
    },
    {
      id: uuidv4(),
      role: "user",
      content: "Now solve the equation 3x + 7 = 22",
      timestamp: Date.now() - 1000 * 60 * 15,
      agentId: "calculator"
    },
    {
      id: uuidv4(),
      role: "assistant",
      content: "Let's solve the equation 3x + 7 = 22:\n\n3x + 7 = 22\n3x = 22 - 7\n3x = 15\nx = 15 ÷ 3\nx = 5\n\nThe solution is x = 5.",
      timestamp: Date.now() - 1000 * 60 * 14,
      agentId: "calculator"
    }
  ],
  safety: [
    {
      id: uuidv4(),
      role: "system",
      content: "I am a safety agent that can validate content and approve operations.",
      timestamp: Date.now() - 1000 * 60 * 60,
      agentId: "safety"
    },
    {
      id: uuidv4(),
      role: "user",
      content: "Can you check if this content is safe: 'Hello, my name is John and I'm a software developer.'",
      timestamp: Date.now() - 1000 * 60 * 30,
      agentId: "safety"
    },
    {
      id: uuidv4(),
      role: "assistant",
      content: "I've analyzed the content and it appears to be safe. It doesn't contain any sensitive personal information, harmful instructions, or dangerous content.",
      timestamp: Date.now() - 1000 * 60 * 29,
      agentId: "safety"
    },
    {
      id: uuidv4(),
      role: "user",
      content: "Is it safe to run this command: 'rm -rf /'?",
      timestamp: Date.now() - 1000 * 60 * 15,
      agentId: "safety"
    },
    {
      id: uuidv4(),
      role: "assistant",
      content: "NO! This command is extremely dangerous and should never be executed. It would attempt to recursively delete all files on your system starting from the root directory, which would destroy your operating system and all data. This operation is not approved.",
      timestamp: Date.now() - 1000 * 60 * 14,
      agentId: "safety"
    }
  ],
  writer: [
    {
      id: uuidv4(),
      role: "system",
      content: "I am a writer agent that can help with file operations.",
      timestamp: Date.now() - 1000 * 60 * 60,
      agentId: "writer"
    },
    {
      id: uuidv4(),
      role: "user",
      content: "Can you list the files in my Downloads folder?",
      timestamp: Date.now() - 1000 * 60 * 30,
      agentId: "writer"
    },
    {
      id: uuidv4(),
      role: "assistant",
      content: "I've listed the files in your Downloads folder. Here are the first 10 items:\n\n1. document.pdf\n2. image.jpg\n3. presentation.pptx\n4. data.csv\n5. archive.zip\n6. notes.txt\n7. screenshot.png\n8. report.docx\n9. config.json\n10. backup.tar.gz",
      timestamp: Date.now() - 1000 * 60 * 29,
      agentId: "writer"
    },
    {
      id: uuidv4(),
      role: "user",
      content: "Create a file called notes.txt with the content 'Meeting notes: Discuss project timeline and resource allocation.'",
      timestamp: Date.now() - 1000 * 60 * 15,
      agentId: "writer"
    },
    {
      id: uuidv4(),
      role: "assistant",
      content: "I've created the file 'notes.txt' with the specified content. The file has been saved successfully with 65 bytes written.",
      timestamp: Date.now() - 1000 * 60 * 14,
      agentId: "writer"
    }
  ],
  developer: [
    {
      id: uuidv4(),
      role: "system",
      content: "I am a developer agent that can help with coding and software development.",
      timestamp: Date.now() - 1000 * 60 * 60,
      agentId: "developer"
    },
    {
      id: uuidv4(),
      role: "user",
      content: "How do I create a simple React component?",
      timestamp: Date.now() - 1000 * 60 * 30,
      agentId: "developer"
    },
    {
      id: uuidv4(),
      role: "assistant",
      content: "Here's how to create a simple React component:\n\n```jsx\nimport React from 'react';\n\nfunction SimpleComponent({ name }) {\n  return (\n    <div className=\"simple-component\">\n      <h1>Hello, {name}!</h1>\n      <p>This is a simple React component.</p>\n    </div>\n  );\n}\n\nexport default SimpleComponent;\n```\n\nYou can use this component in another component like this:\n\n```jsx\nimport SimpleComponent from './SimpleComponent';\n\nfunction App() {\n  return <SimpleComponent name=\"World\" />;\n}\n```",
      timestamp: Date.now() - 1000 * 60 * 29,
      agentId: "developer"
    },
    {
      id: uuidv4(),
      role: "user",
      content: "Can you help me debug this code? I'm getting an error: 'Cannot read property 'map' of undefined'",
      timestamp: Date.now() - 1000 * 60 * 15,
      agentId: "developer"
    },
    {
      id: uuidv4(),
      role: "assistant",
      content: "The error 'Cannot read property 'map' of undefined' typically occurs when you're trying to call the .map() method on a variable that is undefined instead of an array.\n\nCommon causes:\n\n1. The array hasn't been initialized yet\n2. The API call that should return the array hasn't completed\n3. The property name might be incorrect\n\nHere's how to fix it:\n\n```jsx\n// Before (problematic code)\nconst MyComponent = ({ data }) => {\n  return (\n    <div>\n      {data.map(item => <div key={item.id}>{item.name}</div>)}\n    </div>\n  );\n};\n\n// After (fixed with conditional rendering)\nconst MyComponent = ({ data }) => {\n  return (\n    <div>\n      {data && data.map(item => <div key={item.id}>{item.name}</div>)}\n    </div>\n  );\n};\n\n// Or use default value with destructuring\nconst MyComponent = ({ data = [] }) => {\n  return (\n    <div>\n      {data.map(item => <div key={item.id}>{item.name}</div>)}\n    </div>\n  );\n};\n```\n\nMake sure you're properly initializing your state variables and handling loading states for data from APIs.",
      timestamp: Date.now() - 1000 * 60 * 14,
      agentId: "developer"
    }
  ]
}

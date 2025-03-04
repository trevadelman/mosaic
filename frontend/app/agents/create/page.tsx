"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle, CheckCircle, Code, FileJson, Play, Plus, Save, Send, Wrench, Wand2 } from "lucide-react"
import { toast } from "@/components/ui/toast"
import { agentCreatorApi } from "@/lib/api"

// JSON Editor component (we'll use a simple textarea for now, but could use a more advanced editor like Monaco)
const JsonEditor = ({ value, onChange, schema, error }: { 
  value: string, 
  onChange: (value: string) => void,
  schema?: any,
  error?: string
}) => {
  return (
    <div className="relative">
      <Textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="font-mono h-[500px] resize-none"
        placeholder="Enter JSON here..."
      />
      {error && (
        <Alert variant="destructive" className="mt-2">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </div>
  )
}

// Code Editor component for tool implementation
const CodeEditor = ({ value, onChange, error }: { 
  value: string, 
  onChange: (value: string) => void,
  error?: string
}) => {
  return (
    <div className="relative">
      <Textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="font-mono h-[300px] resize-none"
        placeholder="Enter Python code here..."
      />
      {error && (
        <Alert variant="destructive" className="mt-2">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </div>
  )
}

// Agent Type Badge component
const AgentTypeBadge = ({ type }: { type: string }) => {
  const getTypeColor = (type: string) => {
    switch (type) {
      case "Utility":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300"
      case "Specialized":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300"
      case "Supervisor":
        return "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-300"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300"
    }
  }

  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${getTypeColor(type)}`}>
      {type}
    </span>
  )
}

export default function CreateAgentPage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState("basic")
  const [loading, setLoading] = useState(false)
  const [schema, setSchema] = useState<any>(null)
  const [templates, setTemplates] = useState<any[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<string>("")
  
  // Basic agent information
  const [agentName, setAgentName] = useState("")
  const [agentType, setAgentType] = useState("Utility")
  const [agentDescription, setAgentDescription] = useState("")
  const [agentCapabilities, setAgentCapabilities] = useState("")
  const [agentIcon, setAgentIcon] = useState("🤖")
  const [agentPrompt, setAgentPrompt] = useState("")
  
  // Tool information
  const [tools, setTools] = useState<any[]>([])
  const [currentTool, setCurrentTool] = useState<any>({
    name: "",
    description: "",
    parameters: [],
    returns: { type: "string", description: "" },
    implementation: { code: "" }
  })
  const [currentParameter, setCurrentParameter] = useState({
    name: "",
    type: "string",
    description: "",
    required: true
  })
  
  // JSON editor
  const [jsonTemplate, setJsonTemplate] = useState("")
  const [jsonError, setJsonError] = useState("")
  
  // Code generation and deployment
  const [generatedCode, setGeneratedCode] = useState("")
  const [deploymentOptions, setDeploymentOptions] = useState({ sandbox: true })
  const [deploymentResult, setDeploymentResult] = useState<any>(null)
  
  // Fetch the agent schema and templates on component mount
  useEffect(() => {
    const fetchSchema = async () => {
      try {
        const response = await agentCreatorApi.getSchema()
        if (response.error) throw new Error(response.error)
        setSchema(response.data.schema)
      } catch (error) {
        console.error("Error fetching schema:", error)
        toast.error("Failed to fetch agent schema")
      }
    }
    
    const fetchTemplates = async () => {
      try {
      const response = await agentCreatorApi.getTemplates()
      if (response.error) throw new Error(response.error)
      setTemplates(response.data || [])
      } catch (error) {
        console.error("Error fetching templates:", error)
        toast.error("Failed to fetch agent templates")
      }
    }
    
    fetchSchema()
    fetchTemplates()
  }, [])
  
  // Update JSON template when basic information changes
  useEffect(() => {
    if (activeTab === "json") {
      try {
        const template = {
          agent: {
            name: agentName,
            type: agentType,
            description: agentDescription,
            capabilities: agentCapabilities.split(",").map(c => c.trim()).filter(c => c),
            icon: agentIcon,
            systemPrompt: agentPrompt,
            tools: tools
          }
        }
        setJsonTemplate(JSON.stringify(template, null, 2))
      } catch (error) {
        console.error("Error updating JSON template:", error)
      }
    }
  }, [activeTab, agentName, agentType, agentDescription, agentCapabilities, agentIcon, agentPrompt, tools])
  
  // Load template when selected
  useEffect(() => {
    if (selectedTemplate) {
      const loadTemplate = async () => {
        try {
          setLoading(true)
          const response = await agentCreatorApi.getTemplate(selectedTemplate)
          if (response.error) throw new Error(response.error)
          const data = response.data
          
          // Update form fields
          const agent = data.template.agent
          setAgentName(agent.name || "")
          setAgentType(agent.type || "Utility")
          setAgentDescription(agent.description || "")
          setAgentCapabilities((agent.capabilities || []).join(", "))
          setAgentIcon(agent.icon || "🤖")
          setAgentPrompt(agent.systemPrompt || "")
          setTools(agent.tools || [])
          
          // Update JSON template
          setJsonTemplate(JSON.stringify(data.template, null, 2))
          
          toast.success("Template loaded successfully")
        } catch (error) {
          console.error("Error loading template:", error)
          toast.error("Failed to load template")
        } finally {
          setLoading(false)
        }
      }
      
      loadTemplate()
    }
  }, [selectedTemplate])
  
  // Create agent template from basic information
  const createTemplate = async () => {
    try {
      setLoading(true)
      
      const response = await agentCreatorApi.createTemplate({
        name: agentName,
        type: agentType,
        description: agentDescription,
        capabilities: agentCapabilities.split(",").map(c => c.trim()).filter(c => c),
        icon: agentIcon,
        prompt: agentPrompt
      })
      
      if (response.error) throw new Error(response.error)
      
      setJsonTemplate(JSON.stringify(response.data, null, 2))
      setActiveTab("json")
      
      toast.success("Agent template created successfully")
    } catch (error) {
      console.error("Error creating template:", error)
      toast.error("Failed to create agent template")
    } finally {
      setLoading(false)
    }
  }
  
  // Add a tool to the agent
  const addTool = () => {
    if (!currentTool.name || !currentTool.description || !currentTool.implementation.code) {
      toast.error("Please fill in all required tool fields")
      return
    }
    
    setTools([...tools, { ...currentTool }])
    setCurrentTool({
      name: "",
      description: "",
      parameters: [],
      returns: { type: "string", description: "" },
      implementation: { code: "" }
    })
    
    toast.success("Tool added successfully")
  }
  
  // Add a parameter to the current tool
  const addParameter = () => {
    if (!currentParameter.name || !currentParameter.description) {
      toast.error("Please fill in all required parameter fields")
      return
    }
    
    setCurrentTool({
      ...currentTool,
      parameters: [...currentTool.parameters, { ...currentParameter }]
    })
    
    setCurrentParameter({
      name: "",
      type: "string",
      description: "",
      required: true
    })
  }
  
  // Remove a parameter from the current tool
  const removeParameter = (index: number) => {
    setCurrentTool({
      ...currentTool,
      parameters: currentTool.parameters.filter((_: any, i: number) => i !== index)
    })
  }
  
  // Remove a tool from the agent
  const removeTool = (index: number) => {
    setTools(tools.filter((_, i) => i !== index))
  }
  
  // Validate the JSON template
  const validateTemplate = async () => {
    try {
      setLoading(true)
      setJsonError("")
      
      // Parse the JSON to ensure it's valid
      const template = JSON.parse(jsonTemplate)
      
      const response = await agentCreatorApi.validateTemplate(template)
      
      if (response.error) {
        setJsonError(response.error)
        toast.error("Template validation failed")
        return false
      }
      
      const data = response.data
      
      if (!data.valid) {
        setJsonError(data.message)
        toast.error("Template validation failed")
        return false
      }
      
      toast.success("Template validation successful")
      return true
    } catch (error: any) {
      console.error("Error validating template:", error)
      setJsonError(error.message || "Invalid JSON")
      toast.error("Template validation failed")
      return false
    } finally {
      setLoading(false)
    }
  }
  
  // Generate code from the template
  const generateCode = async () => {
    try {
      // Validate the template first
      const isValid = await validateTemplate()
      if (!isValid) return
      
      setLoading(true)
      
      const template = JSON.parse(jsonTemplate)
      
      const response = await agentCreatorApi.generateCode(template)
      
      if (response.error) throw new Error(response.error)
      
      setGeneratedCode(response.data.code)
      setActiveTab("code")
      
      toast.success("Code generated successfully")
    } catch (error) {
      console.error("Error generating code:", error)
      toast.error("Failed to generate code")
    } finally {
      setLoading(false)
    }
  }
  
  // Deploy the agent
  const deployAgent = async () => {
    try {
      setLoading(true)
      
      const template = JSON.parse(jsonTemplate)
      
      const response = await agentCreatorApi.deployAgent(template, deploymentOptions)
      
      if (response.error) throw new Error(response.error)
      
      const data = response.data
      setDeploymentResult(data)
      
      if (data.success) {
        toast.success("Agent deployed successfully")
        
        // Save the template
        const saveResponse = await agentCreatorApi.saveTemplate(template.agent.name, template)
        
        if (saveResponse.error) {
          console.error("Failed to save template:", saveResponse.error)
        }
        
        // Redirect to the agents page after a short delay
        setTimeout(() => {
          router.push("/agents")
        }, 2000)
      } else {
        toast.error("Failed to deploy agent")
      }
    } catch (error) {
      console.error("Error deploying agent:", error)
      toast.error("Failed to deploy agent")
    } finally {
      setLoading(false)
    }
  }
  
  // Save the template
  const saveTemplate = async () => {
    try {
      setLoading(true)
      
      const template = JSON.parse(jsonTemplate)
      
      const response = await agentCreatorApi.saveTemplate(template.agent.name, template)
      
      if (response.error) throw new Error(response.error)
      
      toast.success("Template saved successfully")
      
      // Refresh the templates list
      const templatesResponse = await agentCreatorApi.getTemplates()
      if (!templatesResponse.error) {
        setTemplates(templatesResponse.data || [])
      }
    } catch (error) {
      console.error("Error saving template:", error)
      toast.error("Failed to save template")
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Create Agent</h1>
        <p className="text-muted-foreground">
          Create a new agent for the MOSAIC system
        </p>
      </div>
      
      <div className="mb-6">
        <Label htmlFor="template-select">Load Template</Label>
        <div className="flex gap-2 mt-1">
          <div className="w-[300px]">
            <Select value={selectedTemplate} onValueChange={setSelectedTemplate}>
              {templates.map((template) => (
                <option key={template.id} value={template.id}>
                  {template.name} - {template.description}
                </option>
              ))}
            </Select>
          </div>
        </div>
      </div>
      
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="basic">
            <div className="flex items-center gap-2">
              <Wand2 className="h-4 w-4" />
              <span>Basic Info</span>
            </div>
          </TabsTrigger>
          <TabsTrigger value="tools">
            <div className="flex items-center gap-2">
              <Wrench className="h-4 w-4" />
              <span>Tools</span>
            </div>
          </TabsTrigger>
          <TabsTrigger value="json">
            <div className="flex items-center gap-2">
              <FileJson className="h-4 w-4" />
              <span>JSON</span>
            </div>
          </TabsTrigger>
          <TabsTrigger value="code">
            <div className="flex items-center gap-2">
              <Code className="h-4 w-4" />
              <span>Code & Deploy</span>
            </div>
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="basic" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Basic Agent Information</CardTitle>
              <CardDescription>
                Define the basic properties of your agent
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="agent-name">Name</Label>
                  <Input
                    id="agent-name"
                    placeholder="e.g., calculator"
                    value={agentName}
                    onChange={(e) => setAgentName(e.target.value)}
                  />
                  <p className="text-xs text-muted-foreground">
                    Unique identifier for the agent (lowercase, no spaces)
                  </p>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="agent-type">Type</Label>
                  <Select value={agentType} onValueChange={setAgentType}>
                    <option value="Utility">Utility</option>
                    <option value="Specialized">Specialized</option>
                    <option value="Supervisor">Supervisor</option>
                  </Select>
                  <p className="text-xs text-muted-foreground">
                    Type of agent (Utility, Specialized, or Supervisor)
                  </p>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="agent-description">Description</Label>
                <Textarea
                  id="agent-description"
                  placeholder="Describe what your agent does..."
                  value={agentDescription}
                  onChange={(e) => setAgentDescription(e.target.value)}
                />
                <p className="text-xs text-muted-foreground">
                  Human-readable description of the agent
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="agent-capabilities">Capabilities</Label>
                <Input
                  id="agent-capabilities"
                  placeholder="e.g., Math, Equations, Unit Conversion"
                  value={agentCapabilities}
                  onChange={(e) => setAgentCapabilities(e.target.value)}
                />
                <p className="text-xs text-muted-foreground">
                  Comma-separated list of agent capabilities
                </p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="agent-icon">Icon</Label>
                  <Input
                    id="agent-icon"
                    placeholder="e.g., 🧮"
                    value={agentIcon}
                    onChange={(e) => setAgentIcon(e.target.value)}
                  />
                  <p className="text-xs text-muted-foreground">
                    Emoji icon for the agent
                  </p>
                </div>
                
                <div className="space-y-2">
                  <Label>Preview</Label>
                  <div className="flex items-center gap-4 p-4 border rounded-md">
                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary text-primary-foreground">
                      <span className="text-lg">{agentIcon}</span>
                    </div>
                    <div>
                      <h3 className="font-semibold">{agentName || "Agent Name"}</h3>
                      <div className="flex items-center gap-2">
                        <AgentTypeBadge type={agentType} />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="agent-prompt">System Prompt</Label>
                <Textarea
                  id="agent-prompt"
                  placeholder="Enter the system prompt for your agent..."
                  className="h-[200px]"
                  value={agentPrompt}
                  onChange={(e) => setAgentPrompt(e.target.value)}
                />
                <p className="text-xs text-muted-foreground">
                  System prompt that defines the agent's behavior and capabilities
                </p>
              </div>
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button variant="outline" onClick={() => router.push("/agents")}>
                Cancel
              </Button>
              <Button onClick={createTemplate} disabled={loading}>
                {loading ? "Creating..." : "Continue to Tools"}
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        
        <TabsContent value="tools" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Agent Tools</CardTitle>
              <CardDescription>
                Define the tools that your agent can use
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Current Tools</h3>
                {tools.length === 0 ? (
                  <div className="p-4 border rounded-md text-center text-muted-foreground">
                    No tools added yet
                  </div>
                ) : (
                  <div className="space-y-4">
                    {tools.map((tool, index) => (
                      <div key={index} className="p-4 border rounded-md">
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-semibold">{tool.name}</h4>
                            <p className="text-sm text-muted-foreground">{tool.description}</p>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeTool(index)}
                          >
                            Remove
                          </Button>
                        </div>
                        <div className="mt-2">
                          <h5 className="text-sm font-semibold">Parameters:</h5>
                          <ul className="mt-1 space-y-1">
                            {tool.parameters.map((param: any, paramIndex: number) => (
                              <li key={paramIndex} className="text-sm">
                                <span className="font-mono">{param.name}</span>
                                <span className="text-muted-foreground"> ({param.type})</span>
                                <span>: {param.description}</span>
                                {param.required && (
                                  <Badge variant="outline" className="ml-2">Required</Badge>
                                )}
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div className="mt-2">
                          <h5 className="text-sm font-semibold">Returns:</h5>
                          <p className="text-sm">
                            <span className="text-muted-foreground">({tool.returns.type})</span>
                            <span>: {tool.returns.description}</span>
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              <Separator />
              
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Add New Tool</h3>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="tool-name">Tool Name</Label>
                    <Input
                      id="tool-name"
                      placeholder="e.g., calculate_expression"
                      value={currentTool.name}
                      onChange={(e) => setCurrentTool({ ...currentTool, name: e.target.value })}
                    />
                    <p className="text-xs text-muted-foreground">
                      Unique identifier for the tool (lowercase, no spaces)
                    </p>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="tool-description">Description</Label>
                    <Input
                      id="tool-description"
                      placeholder="e.g., Calculate a mathematical expression"
                      value={currentTool.description}
                      onChange={(e) => setCurrentTool({ ...currentTool, description: e.target.value })}
                    />
                    <p className="text-xs text-muted-foreground">
                      Human-readable description of the tool
                    </p>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <Label>Parameters</Label>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={addParameter}
                      disabled={!currentParameter.name || !currentParameter.description}
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Add Parameter
                    </Button>
                  </div>
                  
                  <div className="p-4 border rounded-md space-y-4">
                    <div className="grid grid-cols-4 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="param-name">Name</Label>
                        <Input
                          id="param-name"
                          placeholder="e.g., expression"
                          value={currentParameter.name}
                          onChange={(e) => setCurrentParameter({ ...currentParameter, name: e.target.value })}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="param-type">Type</Label>
                        <Select
                          value={currentParameter.type}
                          onValueChange={(value) => setCurrentParameter({ ...currentParameter, type: value })}
                        >
                          <option value="string">string</option>
                          <option value="integer">integer</option>
                          <option value="number">number</option>
                          <option value="boolean">boolean</option>
                          <option value="array">array</option>
                          <option value="object">object</option>
                        </Select>
                      </div>
                      
                      <div className="space-y-2 col-span-2">
                        <Label htmlFor="param-description">Description</Label>
                        <Input
                          id="param-description"
                          placeholder="e.g., The mathematical expression to evaluate"
                          value={currentParameter.description}
                          onChange={(e) => setCurrentParameter({ ...currentParameter, description: e.target.value })}
                        />
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="param-required"
                        checked={currentParameter.required}
                        onChange={(e) => setCurrentParameter({ ...currentParameter, required: e.target.checked })}
                        className="rounded border-gray-300 text-primary focus:ring-primary"
                      />
                      <Label htmlFor="param-required" className="text-sm font-normal">
                        Required parameter
                      </Label>
                    </div>
                  </div>
                  
                  {currentTool.parameters.length > 0 && (
                    <div className="mt-2">
                      <h5 className="text-sm font-semibold">Current Parameters:</h5>
                      <ul className="mt-1 space-y-1">
                        {currentTool.parameters.map((param: any, paramIndex: number) => (
                          <li key={paramIndex} className="text-sm flex justify-between items-center">
                            <div>
                              <span className="font-mono">{param.name}</span>
                              <span className="text-muted-foreground"> ({param.type})</span>
                              <span>: {param.description}</span>
                              {param.required && (
                                <Badge variant="outline" className="ml-2">Required</Badge>
                              )}
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeParameter(paramIndex)}
                            >
                              Remove
                            </Button>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="return-type">Return Type</Label>
                    <Select
                      value={currentTool.returns.type}
                      onValueChange={(value) => setCurrentTool({
                        ...currentTool,
                        returns: { ...currentTool.returns, type: value }
                      })}
                    >
                      <option value="string">string</option>
                      <option value="integer">integer</option>
                      <option value="number">number</option>
                      <option value="boolean">boolean</option>
                      <option value="array">array</option>
                      <option value="object">object</option>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="return-description">Return Description</Label>
                    <Input
                      id="return-description"
                      placeholder="e.g., The result of the calculation"
                      value={currentTool.returns.description}
                      onChange={(e) => setCurrentTool({
                        ...currentTool,
                        returns: { ...currentTool.returns, description: e.target.value }
                      })}
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="tool-implementation">Implementation</Label>
                  <CodeEditor
                    value={currentTool.implementation.code}
                    onChange={(value) => setCurrentTool({
                      ...currentTool,
                      implementation: { code: value }
                    })}
                  />
                  <p className="text-xs text-muted-foreground">
                    Python code implementing the tool (use the @tool decorator)
                  </p>
                </div>
                
                <div className="flex justify-end">
                  <Button onClick={addTool} disabled={!currentTool.name || !currentTool.description || !currentTool.implementation.code}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Tool
                  </Button>
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button variant="outline" onClick={() => setActiveTab("basic")}>
                Back
              </Button>
              <Button onClick={() => setActiveTab("json")} disabled={loading}>
                Continue to JSON
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        
        <TabsContent value="json" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Agent Template JSON</CardTitle>
              <CardDescription>
                Edit the JSON template directly or validate it
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <JsonEditor
                value={jsonTemplate}
                onChange={setJsonTemplate}
                schema={schema}
                error={jsonError}
              />
            </CardContent>
            <CardFooter className="flex justify-between">
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => setActiveTab("tools")}>
                  Back
                </Button>
                <Button variant="secondary" onClick={validateTemplate} disabled={loading}>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Validate
                </Button>
                <Button variant="secondary" onClick={saveTemplate} disabled={loading}>
                  <Save className="h-4 w-4 mr-2" />
                  Save Template
                </Button>
              </div>
              <Button onClick={generateCode} disabled={loading}>
                <Code className="h-4 w-4 mr-2" />
                Generate Code
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        
        <TabsContent value="code" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Generated Code & Deployment</CardTitle>
              <CardDescription>
                Review the generated code and deploy the agent
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <h3 className="text-lg font-semibold">Generated Python Code</h3>
                <CodeEditor
                  value={generatedCode}
                  onChange={setGeneratedCode}
                />
              </div>
              
              <Separator />
              
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Deployment Options</h3>
                
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="sandbox-deployment"
                    checked={deploymentOptions.sandbox}
                    onChange={(e) => setDeploymentOptions({ ...deploymentOptions, sandbox: e.target.checked })}
                    className="rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <Label htmlFor="sandbox-deployment" className="text-sm font-normal">
                    Deploy to sandbox environment (recommended for testing)
                  </Label>
                </div>
                
                {deploymentResult && (
                  <Alert variant={deploymentResult.success ? "default" : "destructive"} className="mt-4">
                    {deploymentResult.success ? (
                      <CheckCircle className="h-4 w-4" />
                    ) : (
                      <AlertCircle className="h-4 w-4" />
                    )}
                    <AlertTitle>{deploymentResult.success ? "Deployment Successful" : "Deployment Failed"}</AlertTitle>
                    <AlertDescription>{deploymentResult.message}</AlertDescription>
                  </Alert>
                )}
              </div>
            </CardContent>
            <CardFooter className="flex justify-between">
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => setActiveTab("json")}>
                  Back
                </Button>
                <Button variant="secondary" onClick={validateTemplate} disabled={loading}>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Validate
                </Button>
              </div>
              <Button onClick={deployAgent} disabled={loading}>
                <Play className="h-4 w-4 mr-2" />
                Deploy Agent
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

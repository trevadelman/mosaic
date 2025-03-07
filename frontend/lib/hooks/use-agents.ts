"use client"

import { useState, useEffect } from "react"
import { Agent } from "../types"
import { agentApi } from "../api"
import { mockAgents } from "../mock-data"

// Always use the actual API in Docker environment
const USE_MOCK_DATA = false

export function useAgents() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch all available agents
  useEffect(() => {
    async function fetchAgents() {
      setLoading(true)
      setError(null)

      if (USE_MOCK_DATA) {
        // Use mock data
        setTimeout(() => {
          setAgents(mockAgents)
          
          // Select the first agent by default if none is selected
          if (mockAgents.length > 0 && !selectedAgent) {
            setSelectedAgent(mockAgents[0])
          }
          
          setLoading(false)
        }, 500) // Simulate network delay
      } else {
        // Use API
        const response = await agentApi.getAgents()

        if (response.error) {
          setError(response.error)
        } else if (response.data) {
          // Fetch hasUI information for each agent
          const agentsWithUI = await Promise.all(
            response.data.map(async (agent) => {
              const hasUIResponse = await agentApi.hasUI(agent.id)
              return {
                ...agent,
                hasUI: hasUIResponse.data?.hasUI || false
              }
            })
          )
          
          setAgents(agentsWithUI)
          
          // Select the first agent by default if none is selected
          if (agentsWithUI.length > 0 && !selectedAgent) {
            setSelectedAgent(agentsWithUI[0])
          }
        }

        setLoading(false)
      }
    }

    fetchAgents()
  }, [])

  // Function to select an agent
  const selectAgent = (agent: Agent) => {
    setSelectedAgent(agent)
  }

  return {
    agents,
    selectedAgent,
    selectAgent,
    loading,
    error
  }
}

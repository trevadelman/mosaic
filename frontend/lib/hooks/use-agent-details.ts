import { useState, useEffect } from 'react';
import { agentApi } from '@/lib/api';
import { Agent, Tool } from '@/lib/types';

interface UseAgentDetailsProps {
  agentId: string | null;
}

interface UseAgentDetailsResult {
  tools: Tool[];
  relationships: Agent['relationships'];
  loading: boolean;
  error: string | null;
}

export function useAgentDetails({ agentId }: UseAgentDetailsProps): UseAgentDetailsResult {
  const [tools, setTools] = useState<Tool[]>([]);
  const [relationships, setRelationships] = useState<Agent['relationships']>({ supervisor: undefined, subAgents: [] });
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!agentId) {
      setTools([]);
      setRelationships({ supervisor: undefined, subAgents: [] });
      return;
    }

    const fetchAgentDetails = async () => {
      setLoading(true);
      setError(null);

      try {
        // Fetch tools
        const toolsResponse = await agentApi.getAgentTools(agentId);
        if (toolsResponse.error) {
          throw new Error(toolsResponse.error);
        }
        setTools(toolsResponse.data || []);

        // Fetch relationships
        const relationshipsResponse = await agentApi.getAgentRelationships(agentId);
        if (relationshipsResponse.error) {
          throw new Error(relationshipsResponse.error);
        }
        setRelationships(relationshipsResponse.data || { supervisor: undefined, subAgents: [] });
      } catch (err) {
        console.error('Error fetching agent details:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchAgentDetails();
  }, [agentId]);

  return { tools, relationships, loading, error };
}

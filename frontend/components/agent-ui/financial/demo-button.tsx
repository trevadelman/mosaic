/**
 * Financial UI Demo Button
 * 
 * This component demonstrates how to use the custom UI components in the chat interface.
 * It provides a button that opens the stock chart component.
 */

"use client"

import React from 'react';
import { Button } from '../../ui/button';
import { useAgentUIComponents } from '../../../lib/hooks/use-agent-ui-components';
import { FINANCIAL_COMPONENTS } from './index';
import { BarChart3 } from 'lucide-react';

interface FinancialUIDemoButtonProps {
  agentId: string;
  symbol?: string;
}

export const FinancialUIDemoButton: React.FC<FinancialUIDemoButtonProps> = ({
  agentId = 'financial_supervisor',
  symbol = 'AAPL'
}) => {
  console.log(`FinancialUIDemoButton: agentId=${agentId}, symbol=${symbol}`);
  const { openComponent, isComponentOpen } = useAgentUIComponents({ agentId });
  
  // Check if the component is open
  const isOpen = isComponentOpen(FINANCIAL_COMPONENTS.STOCK_CHART);
  
  // Handle button click
  const handleClick = () => {
    openComponent(FINANCIAL_COMPONENTS.STOCK_CHART, {
      symbol,
      title: `${symbol} Stock Analysis`,
      description: 'Interactive stock chart with technical indicators'
    });
  };
  
  return (
    <Button
      onClick={handleClick}
      variant={isOpen ? 'default' : 'outline'}
      size="sm"
      className="flex items-center gap-2"
    >
      <BarChart3 className="h-4 w-4" />
      <span>{isOpen ? 'View Chart' : 'Open Chart'}</span>
    </Button>
  );
};

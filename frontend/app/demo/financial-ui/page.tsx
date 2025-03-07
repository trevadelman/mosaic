/**
 * Financial UI Demo Page
 * 
 * This page demonstrates the custom UI components for financial analysis.
 */

"use client"

import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { FinancialUIDemoButton } from '@/components/agent-ui/financial';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

// Import the financial components module to ensure it's loaded
import '@/components/agent-ui/financial';
// Import markdown styles
import '@/app/markdown.css';

export default function FinancialUIDemo() {
  const [symbol, setSymbol] = useState('AAPL');
  const [inputSymbol, setInputSymbol] = useState('AAPL');
  const [documentation, setDocumentation] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  
  // Ensure the component is registered when the page loads
  useEffect(() => {
    // Import the StockChart component directly
    import('@/components/agent-ui/financial/stock-chart').then(module => {
      console.log('StockChart component imported directly');
    });
    
    // Load the documentation
    fetch('/docs/financial-ui-guide.md')
      .then(response => response.text())
      .then(text => {
        setDocumentation(text);
      })
      .catch(error => {
        console.error('Error loading documentation:', error);
        setDocumentation('Error loading documentation. Please try again later.');
      });
    
    // Force a re-render after a short delay
    const timer = setTimeout(() => {
      console.log('Forcing re-render');
      setSymbol(symbol => symbol);
    }, 500);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSymbol(inputSymbol.toUpperCase());
  };
  
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8">Financial UI Demo</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Stock Chart Demo */}
        <Card>
          <CardHeader>
            <CardTitle>Stock Chart Component</CardTitle>
            <CardDescription>
              Demonstrates the custom UI component for stock charts
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="flex gap-2 mb-4">
              <Input
                value={inputSymbol}
                onChange={(e) => setInputSymbol(e.target.value)}
                placeholder="Enter stock symbol"
                className="flex-1"
              />
              <Button type="submit" size="sm">
                <Search className="h-4 w-4 mr-2" />
                Search
              </Button>
            </form>
            
            <div className="p-4 border rounded-lg bg-muted/50">
              <p className="mb-4">
                Current Symbol: <strong>{symbol}</strong>
              </p>
              <p className="text-sm text-muted-foreground mb-4">
                Click the button below to open the stock chart in a modal.
                This demonstrates how agents can provide rich, interactive
                interfaces beyond the chat interface.
              </p>
              
              <FinancialUIDemoButton
                agentId="financial_supervisor"
                symbol={symbol}
              />
            </div>
          </CardContent>
          <CardFooter className="text-sm text-muted-foreground">
            The modal is rendered by the AgentModal component in the layout.
          </CardFooter>
        </Card>
        
        {/* Usage Instructions */}
        <Card className="overflow-hidden">
          <CardHeader>
            <CardTitle>How It Works</CardTitle>
            <CardDescription>
              Understanding the custom UI framework
            </CardDescription>
          </CardHeader>
          <Tabs 
            defaultValue="overview" 
            value={activeTab} 
            onValueChange={setActiveTab}
          >
            <div className="px-6">
              <TabsList className="mb-4">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="documentation">Full Documentation</TabsTrigger>
              </TabsList>
            </div>
            
            <TabsContent value="overview" className="m-0">
              <CardContent className="space-y-4">
                <p>
                  The custom UI framework allows agents to provide rich, interactive
                  interfaces beyond the chat interface. Here's how it works:
                </p>
                
                <ol className="list-decimal pl-5 space-y-2">
                  <li>
                    <strong>Component Registration:</strong> UI components are registered
                    with the component registry.
                  </li>
                  <li>
                    <strong>Agent Integration:</strong> Agents can request to open
                    specific UI components with custom props.
                  </li>
                  <li>
                    <strong>Modal Rendering:</strong> The AgentModal component renders
                    the UI component in a modal.
                  </li>
                  <li>
                    <strong>Bidirectional Communication:</strong> The UI component can
                    send events to the agent and receive updates.
                  </li>
                </ol>
                
                <div className="p-4 bg-primary/10 rounded-lg mt-4">
                  <h4 className="font-semibold mb-2">Implementation Details</h4>
                  <p className="text-sm">
                    This demo uses a real implementation with Yahoo Finance data. The stock chart
                    component fetches data from the Yahoo Finance API via the backend and displays
                    it in an interactive chart.
                  </p>
                </div>
              </CardContent>
            </TabsContent>
            
            <TabsContent value="documentation" className="m-0">
              <div className="max-h-[500px] overflow-y-auto px-6 py-4">
                <div className="prose prose-sm dark:prose-invert">
                  {documentation ? (
                    <div className="markdown-content">
                      <ReactMarkdown>
                        {documentation}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-40">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    </div>
                  )}
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </Card>
      </div>
    </div>
  );
}

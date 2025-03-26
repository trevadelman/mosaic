import { useEffect, useRef } from 'react'
import * as d3 from 'd3'
import { Node, Link } from '../hooks/useGraphData'

interface ForceGraphProps {
  nodes: Node[]
  links: Link[]
  width: number
  height: number
  onNodeClick?: (node: Node) => void
}

// Extend Node to include D3 simulation properties
interface SimNode extends Node, d3.SimulationNodeDatum {
  x?: number
  y?: number
}

// Extend Link to include D3 simulation properties
interface SimLink extends d3.SimulationLinkDatum<SimNode> {
  type: 'contains' | 'references'
}

export function ForceGraph({ nodes, links, width, height, onNodeClick }: ForceGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current || !nodes.length) return

    // Clear previous graph
    d3.select(svgRef.current).selectAll("*").remove()

    // Cast nodes and links to simulation types
    const simNodes = nodes as SimNode[]
    const simLinks = links.map(link => ({
      ...link,
      source: link.source,
      target: link.target
    })) as SimLink[]

    // Create the simulation
    const simulation = d3.forceSimulation<SimNode>(simNodes)
      .force("link", d3.forceLink<SimNode, SimLink>(simLinks)
        .id(d => d.id)
        .distance(d => d.type === 'contains' ? 50 : 150))
      .force("charge", d3.forceManyBody().strength(-1000))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(50))

    // Create SVG
    const svg = d3.select(svgRef.current)
      .attr("viewBox", [0, 0, width, height])

    // Add zoom behavior
    const g = svg.append("g")
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .extent([[0, 0], [width, height]])
      .scaleExtent([0.1, 4])
      .on("zoom", (event) => {
        g.attr("transform", event.transform)
      })
    svg.call(zoom)

    // Create links
    const link = g.append("g")
      .selectAll<SVGLineElement, SimLink>("line")
      .data(simLinks)
      .join("line")
      .attr("stroke", d => d.type === 'contains' ? "#999" : "#0ea5e9")
      .attr("stroke-width", d => d.type === 'contains' ? 1 : 2)
      .attr("stroke-dasharray", d => d.type === 'references' ? "5,5" : "none")

    // Create nodes
    const node = g.append("g")
      .selectAll<SVGGElement, SimNode>("g")
      .data(simNodes)
      .join("g")
      .call(d3.drag<SVGGElement, SimNode>()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended))
      .style("cursor", "pointer")
      .on("click", (event, d) => {
        event.stopPropagation()
        if (onNodeClick && d.group === 'table') {
          onNodeClick(d)
        }
      })

    // Add circles to nodes
    node.append("circle")
      .attr("r", d => d.group === 'table' ? 30 : 15)
      .attr("fill", d => d.group === 'table' ? "#0ea5e9" : "#6366f1")

    // Add labels to nodes
    node.append("text")
      .text(d => d.label)
      .attr("x", 0)
      .attr("y", d => d.group === 'table' ? -35 : -20)
      .attr("text-anchor", "middle")
      .attr("fill", "currentColor")
      .style("font-size", d => d.group === 'table' ? "14px" : "12px")
      .style("font-weight", d => d.group === 'table' ? "bold" : "normal")

    // Update positions on each tick
    simulation.on("tick", () => {
      link
        .attr("x1", d => (d.source as SimNode).x ?? 0)
        .attr("y1", d => (d.source as SimNode).y ?? 0)
        .attr("x2", d => (d.target as SimNode).x ?? 0)
        .attr("y2", d => (d.target as SimNode).y ?? 0)

      node
        .attr("transform", d => `translate(${d.x ?? 0},${d.y ?? 0})`)
    })

    // Drag functions
    function dragstarted(event: d3.D3DragEvent<SVGGElement, SimNode, SimNode>) {
      if (!event.active) simulation.alphaTarget(0.3).restart()
      event.subject.fx = event.subject.x
      event.subject.fy = event.subject.y
    }

    function dragged(event: d3.D3DragEvent<SVGGElement, SimNode, SimNode>) {
      event.subject.fx = event.x
      event.subject.fy = event.y
    }

    function dragended(event: d3.D3DragEvent<SVGGElement, SimNode, SimNode>) {
      if (!event.active) simulation.alphaTarget(0)
      event.subject.fx = null
      event.subject.fy = null
    }

    // Cleanup
    return () => {
      simulation.stop()
    }
  }, [nodes, links, width, height])

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      className="bg-background border rounded-lg"
    />
  )
}

import { useEffect, useRef } from 'react'
import * as d3 from 'd3'
import { formatCompact } from '../../lib/api'

interface BudgetSpendingBarProps {
  data: Array<{
    label: string
    budgeted: number
    spent: number
  }>
  height?: number
  title?: string
}

export function BudgetSpendingBarChart({ data, height = 300, title }: BudgetSpendingBarProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current || data.length === 0) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const margin = { top: title ? 30 : 10, right: 20, bottom: 50, left: 70 }
    const width = svgRef.current.clientWidth - margin.left - margin.right
    const chartHeight = height - margin.top - margin.bottom

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

    // Scales
    const x0 = d3.scaleBand()
      .domain(data.map(d => d.label))
      .rangeRound([0, width])
      .paddingInner(0.25)

    const x1 = d3.scaleBand()
      .domain(['budgeted', 'spent'])
      .rangeRound([0, x0.bandwidth()])
      .padding(0.08)

    const maxVal = d3.max(data, d => Math.max(d.budgeted, d.spent)) || 0
    const y = d3.scaleLinear()
      .domain([0, maxVal * 1.1])
      .nice()
      .rangeRound([chartHeight, 0])

    // Grid lines
    g.append('g')
      .attr('class', 'grid')
      .call(
        d3.axisLeft(y)
          .ticks(5)
          .tickSize(-width)
          .tickFormat(() => '')
      )
      .selectAll('line')
      .attr('stroke', '#111111')
      .attr('stroke-dasharray', '2,4')

    g.select('.grid .domain').remove()

    // Bars — Institutional Broadsheet palette
    const colors = { budgeted: '#2D5D40', spent: '#8C2929' }

    ;(['budgeted', 'spent'] as const).forEach(key => {
      g.selectAll(`.bar-${key}`)
        .data(data)
        .join('rect')
        .attr('class', `bar-${key}`)
        .attr('x', d => (x0(d.label) || 0) + (x1(key) || 0))
        .attr('y', chartHeight)
        .attr('width', x1.bandwidth())
        .attr('height', 0)
        .attr('rx', 3)
        .attr('fill', colors[key])
        .attr('opacity', 0.85)
        .transition()
        .duration(750)
        .delay((_, i) => i * 80)
        .attr('y', d => y(d[key]))
        .attr('height', d => chartHeight - y(d[key]))
    })

    // X axis
    g.append('g')
      .attr('transform', `translate(0,${chartHeight})`)
      .call(d3.axisBottom(x0).tickSize(0))
      .selectAll('text')
      .attr('fill', '#747878')
      .attr('font-size', '10px')
      .attr('font-family', 'JetBrains Mono, monospace')
      .attr('transform', 'rotate(-30)')
      .style('text-anchor', 'end')

    g.selectAll('.domain').attr('stroke', '#111111')

    // Y axis
    g.append('g')
      .call(d3.axisLeft(y).ticks(5).tickFormat(d => formatCompact(d as number)))
      .selectAll('text')
      .attr('fill', '#747878')
      .attr('font-size', '10px')
      .attr('font-family', 'JetBrains Mono, monospace')

    g.selectAll('.domain').attr('stroke', '#111111')

    // Title
    if (title) {
      g.append('text')
        .attr('x', width / 2)
        .attr('y', -10)
        .attr('text-anchor', 'middle')
        .attr('fill', '#747878')
        .attr('font-size', '11px')
        .attr('font-family', 'JetBrains Mono, monospace')
        .text(title)
    }

    // Legend
    const legend = g.append('g').attr('transform', `translate(${width - 140}, -5)`)
    ;([['budgeted', 'Budgeted'], ['spent', 'Spent']] as const).forEach(([key, label], i) => {
      const lg = legend.append('g').attr('transform', `translate(${i * 70}, 0)`)
      lg.append('rect').attr('width', 10).attr('height', 10).attr('rx', 2).attr('fill', colors[key])
      lg.append('text').attr('x', 14).attr('y', 9).attr('fill', '#747878').attr('font-size', '9px').attr('font-family', 'JetBrains Mono, monospace').text(label)
    })

  }, [data, height, title])

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-ink-muted text-sm font-mono">
        No data available
      </div>
    )
  }

  return <svg ref={svgRef} width="100%" height={height} className="overflow-visible" />
}

interface VarianceChartProps {
  data: Array<{
    mda_name: string
    variance_pct: number
  }>
  height?: number
}

export function VarianceChart({ data, height = 250 }: VarianceChartProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current || data.length === 0) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const margin = { top: 10, right: 20, bottom: 10, left: 120 }
    const width = svgRef.current.clientWidth - margin.left - margin.right
    const chartHeight = height - margin.top - margin.bottom

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

    const y = d3.scaleBand()
      .domain(data.map(d => d.mda_name))
      .rangeRound([0, chartHeight])
      .padding(0.3)

    const maxAbs = d3.max(data, d => Math.abs(d.variance_pct)) || 100
    const x = d3.scaleLinear()
      .domain([-maxAbs * 1.1, maxAbs * 1.1])
      .nice()
      .rangeRound([0, width])

    // Zero line
    g.append('line')
      .attr('x1', x(0))
      .attr('x2', x(0))
      .attr('y1', 0)
      .attr('y2', chartHeight)
      .attr('stroke', '#111111')
      .attr('stroke-width', 1)

    // Bars
    g.selectAll('.bar')
      .data(data)
      .join('rect')
      .attr('y', d => y(d.mda_name) || 0)
      .attr('height', y.bandwidth())
      .attr('x', d => d.variance_pct >= 0 ? x(0) : x(d.variance_pct))
      .attr('width', 0)
      .attr('rx', 2)
      .attr('fill', d => d.variance_pct >= 0 ? '#2D5D40' : '#8C2929')
      .attr('opacity', 0.8)
      .transition()
      .duration(700)
      .delay((_, i) => i * 60)
      .attr('width', d => Math.abs(x(d.variance_pct) - x(0)))

    // Labels
    g.selectAll('.label')
      .data(data)
      .join('text')
      .attr('x', -8)
      .attr('y', d => (y(d.mda_name) || 0) + y.bandwidth() / 2)
      .attr('dy', '0.35em')
      .attr('text-anchor', 'end')
      .attr('fill', '#747878')
      .attr('font-size', '10px')
      .attr('font-family', 'JetBrains Mono, monospace')
      .text(d => d.mda_name.length > 18 ? d.mda_name.slice(0, 18) + '…' : d.mda_name)

    // Value labels
    g.selectAll('.val')
      .data(data)
      .join('text')
      .attr('y', d => (y(d.mda_name) || 0) + y.bandwidth() / 2)
      .attr('dy', '0.35em')
      .attr('fill', '#111111')
      .attr('font-size', '9px')
      .attr('font-family', 'JetBrains Mono, monospace')
      .attr('opacity', 0)
      .transition()
      .delay((_, i) => i * 60 + 400)
      .attr('opacity', 1)
      .attr('x', d => d.variance_pct >= 0 ? x(d.variance_pct) + 4 : x(d.variance_pct) - 4)
      .attr('text-anchor', d => d.variance_pct >= 0 ? 'start' : 'end')
      .text(d => `${d.variance_pct >= 0 ? '+' : ''}${d.variance_pct.toFixed(1)}%`)

  }, [data, height])

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-ink-muted text-sm font-mono">
        No variance data
      </div>
    )
  }

  return <svg ref={svgRef} width="100%" height={height} className="overflow-visible" />
}

interface TimelineChartProps {
  data: Array<{
    year: number
    budgeted: number
    spent: number
  }>
  height?: number
}

export function TimelineChart({ data, height = 280 }: TimelineChartProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current || data.length === 0) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const margin = { top: 20, right: 20, bottom: 40, left: 70 }
    const width = svgRef.current.clientWidth - margin.left - margin.right
    const chartHeight = height - margin.top - margin.bottom

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

    const x = d3.scaleLinear()
      .domain(d3.extent(data, d => d.year) as [number, number])
      .rangeRound([0, width])

    const maxVal = d3.max(data, d => Math.max(d.budgeted, d.spent)) || 0
    const y = d3.scaleLinear()
      .domain([0, maxVal * 1.1])
      .nice()
      .rangeRound([chartHeight, 0])

    // Grid
    g.append('g')
      .call(d3.axisLeft(y).ticks(5).tickSize(-width).tickFormat(() => ''))
      .selectAll('line')
      .attr('stroke', '#111111')
      .attr('stroke-dasharray', '2,4')
    g.select('.grid .domain').remove()

    // Lines
    const lineBudgeted = d3.line<{ year: number; budgeted: number }>()
      .x(d => x(d.year))
      .y(d => y(d.budgeted))
      .curve(d3.curveMonotoneX)

    const lineSpent = d3.line<{ year: number; spent: number }>()
      .x(d => x(d.year))
      .y(d => y(d.spent))
      .curve(d3.curveMonotoneX)

    // Area under spent
    const areaSpent = d3.area<{ year: number; spent: number }>()
      .x(d => x(d.year))
      .y0(chartHeight)
      .y1(d => y(d.spent))
      .curve(d3.curveMonotoneX)

    g.append('path')
      .datum(data)
      .attr('fill', '#8C2929')
      .attr('fill-opacity', 0.06)
      .attr('d', areaSpent)

    // Budgeted line
    const path1 = g.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', '#2D5D40')
      .attr('stroke-width', 2)
      .attr('d', lineBudgeted as any)

    // Spent line
    const path2 = g.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', '#8C2929')
      .attr('stroke-width', 2)
      .attr('d', lineSpent as any)

    // Animate lines
    ;[path1, path2].forEach(path => {
      const totalLength = (path.node() as SVGPathElement).getTotalLength()
      path
        .attr('stroke-dasharray', totalLength)
        .attr('stroke-dashoffset', totalLength)
        .transition()
        .duration(1200)
        .ease(d3.easeQuadOut)
        .attr('stroke-dashoffset', 0)
    })

    // Dots
    ;[
      { key: 'budgeted', color: '#2D5D40', data: data.map(d => ({ x: d.year, y: d.budgeted })) },
      { key: 'spent', color: '#8C2929', data: data.map(d => ({ x: d.year, y: d.spent })) },
    ].forEach(series => {
      g.selectAll(`.dot-${series.key}`)
        .data(series.data)
        .join('circle')
        .attr('cx', d => x(d.x))
        .attr('cy', d => y(d.y))
        .attr('r', 0)
        .attr('fill', series.color)
        .attr('stroke', '#111111')
        .attr('stroke-width', 2)
        .transition()
        .delay(800)
        .duration(400)
        .attr('r', 4)
    })

    // Axes
    g.append('g')
      .attr('transform', `translate(0,${chartHeight})`)
      .call(d3.axisBottom(x).ticks(data.length).tickFormat(d3.format('d')))
      .selectAll('text')
      .attr('fill', '#747878')
      .attr('font-size', '10px')
      .attr('font-family', 'JetBrains Mono, monospace')

    g.append('g')
      .call(d3.axisLeft(y).ticks(5).tickFormat(d => formatCompact(d as number)))
      .selectAll('text')
      .attr('fill', '#747878')
      .attr('font-size', '10px')
      .attr('font-family', 'JetBrains Mono, monospace')

    g.selectAll('.domain').attr('stroke', '#111111')

    // Legend
    const legend = g.append('g').attr('transform', `translate(${width - 120}, 0)`)
    ;[{ color: '#2D5D40', label: 'Budgeted' }, { color: '#8C2929', label: 'Spent' }].forEach((item, i) => {
      const lg = legend.append('g').attr('transform', `translate(${i * 60}, 0)`)
      lg.append('circle').attr('r', 4).attr('fill', item.color)
      lg.append('text').attr('x', 8).attr('y', 4).attr('fill', '#747878').attr('font-size', '9px').attr('font-family', 'JetBrains Mono, monospace').text(item.label)
    })

  }, [data, height])

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-ink-muted text-sm font-mono">
        No timeline data
      </div>
    )
  }

  return <svg ref={svgRef} width="100%" height={height} className="overflow-visible" />
}

interface DonutChartProps {
  data: Array<{
    label: string
    value: number
    color: string
  }>
  height?: number
  centerLabel?: string
  centerValue?: string
}

export function DonutChart({ data, height = 220, centerLabel, centerValue }: DonutChartProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current || data.length === 0) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = svgRef.current.clientWidth
    const radius = Math.min(width, height) / 2 - 10

    const g = svg.append('g').attr('transform', `translate(${width / 2},${height / 2})`)

    const pie = d3.pie<{ label: string; value: number; color: string }>()
      .value(d => d.value)
      .sort(null)
      .padAngle(0.03)

    const arc = d3.arc<d3.PieArcDatum<{ label: string; value: number; color: string }>>()
      .innerRadius(radius * 0.6)
      .outerRadius(radius)

    const arcHover = d3.arc<d3.PieArcDatum<{ label: string; value: number; color: string }>>()
      .innerRadius(radius * 0.58)
      .outerRadius(radius + 6)

    const arcs = g.selectAll('arc')
      .data(pie(data))
      .join('g')

    arcs.append('path')
      .attr('d', arc as any)
      .attr('fill', d => d.data.color)
      .attr('opacity', 0.85)
      .attr('stroke', '#111111')
      .attr('stroke-width', 2)
      .on('mouseenter', function () {
        d3.select(this).transition().duration(200).attr('d', arcHover as any).attr('opacity', 1)
      })
      .on('mouseleave', function () {
        d3.select(this).transition().duration(200).attr('d', arc as any).attr('opacity', 0.85)
      })
      .transition()
      .duration(800)
      .attrTween('d', function (d) {
        const i = d3.interpolate({ startAngle: 0, endAngle: 0 }, d)
        return (t) => (arc as any)(i(t))
      })

    // Center text
    if (centerValue) {
      g.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '-0.2em')
        .attr('fill', '#111111')
        .attr('font-size', '18px')
        .attr('font-weight', '700')
        .attr('font-family', 'JetBrains Mono, monospace')
        .text(centerValue)
    }
    if (centerLabel) {
      g.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '1.2em')
        .attr('fill', '#747878')
        .attr('font-size', '10px')
        .attr('font-family', 'JetBrains Mono, monospace')
        .text(centerLabel)
    }

  }, [data, height, centerLabel, centerValue])

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-ink-muted text-sm font-mono">
        No data
      </div>
    )
  }

  return <svg ref={svgRef} width="100%" height={height} />
}

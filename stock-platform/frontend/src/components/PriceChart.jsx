import { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';

export default function PriceChart({ data }) {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  useEffect(() => {
    if (!data?.length || !chartRef.current) return;
    const el = chartRef.current;
    const width = el.clientWidth || 600;
    let chart;
    try {
      chart = createChart(el, {
        width,
        height: 400,
        layout: { background: { color: '#fff' }, textColor: '#333' },
        grid: { vertLines: { color: '#eee' }, horzLines: { color: '#eee' } },
        timeScale: { timeVisible: true, secondsVisible: false },
        rightPriceScale: { borderVisible: true },
      });
      const candlestickSeries = chart.addCandlestickSeries({
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderVisible: false,
      });
      const bars = data
        .filter((d) => d && d.close != null)
        .map((d) => ({
          time: d.date,
          open: d.open ?? d.close,
          high: d.high ?? d.close,
          low: d.low ?? d.close,
          close: d.close,
        }));
      if (bars.length) {
        candlestickSeries.setData(bars);
        chart.timeScale().fitContent();
      }
      chartInstance.current = chart;
    } catch (err) {
      if (chartInstance.current) chartInstance.current = null;
    }
    return () => {
      if (chartInstance.current) {
        try { chartInstance.current.remove(); } catch (_) {}
        chartInstance.current = null;
      }
    };
  }, [data]);

  return <div ref={chartRef} className="w-full" style={{ minHeight: 400 }} />;
}

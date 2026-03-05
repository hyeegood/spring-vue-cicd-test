import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from 'chart.js';
import { Radar } from 'react-chartjs-2';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

const LABELS = ['ROE', 'PER', 'FCF', '영업이익률', '기관보유', 'RSI', '감성'];

export default function IndicatorRadar({ breakdown }) {
  if (!breakdown) return null;
  const values = [
    (breakdown.roe != null ? Math.min(100, (breakdown.roe / 20) * 100) : 0),
    (breakdown.per != null ? Math.max(0, 100 - (breakdown.per - 10) * 5) : 50),
    50,
    (breakdown.operating_margin != null ? Math.min(100, (breakdown.operating_margin / 25) * 100) : 0),
    50,
    (breakdown.rsi != null ? Math.min(100, breakdown.rsi) : 50),
    (breakdown.sentiment_score != null ? (breakdown.sentiment_score + 1) * 50 : 50),
  ];
  const data = {
    labels: LABELS,
    datasets: [
      {
        label: '지표',
        data: values,
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1,
      },
    ],
  };
  const options = {
    responsive: true,
    scales: {
      r: { min: 0, max: 100 },
    },
  };
  return <Radar data={data} options={options} />;
}

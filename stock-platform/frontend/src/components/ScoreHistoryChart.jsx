import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

export default function ScoreHistoryChart({ labels, scores }) {
  const data = {
    labels: labels || [],
    datasets: [
      {
        label: '투자 확률 점수',
        data: scores || [],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.3,
      },
    ],
  };
  const options = {
    responsive: true,
    plugins: {
      legend: { display: true },
    },
    scales: {
      y: { min: 0, max: 100 },
    },
  };
  return <Line data={data} options={options} />;
}
